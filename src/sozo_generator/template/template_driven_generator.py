"""
Template-driven document generator.

Reads an uploaded Gold Standard DOCX template, extracts its structure,
then generates condition-specific documents that mirror the template's
section layout, headings, and table structure — populated with real
clinical data from the condition registry.

SAFETY: This module NEVER fabricates PMIDs, clinical outcomes, or
references. All content comes from the condition's ConditionSchema
(which contains pre-verified clinical data). If a section cannot be
populated because the condition lacks data for it, the section is
explicitly marked as "[INSUFFICIENT DATA — REQUIRES CLINICAL INPUT]".
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

from ..core.enums import DocumentType, Tier, Modality, ConfidenceLabel
from ..schemas.condition import ConditionSchema
from ..schemas.documents import DocumentSpec, SectionContent, SectionClaim

from .parser import TemplateParser, ParsedSection

logger = logging.getLogger(__name__)

# ── Section keyword → condition field mapping ────────────────────────────

_SECTION_FIELD_MAP: dict[str, str] = {
    # Overview / intro
    "overview": "overview",
    "introduction": "overview",
    "clinical_overview": "overview",
    "condition_overview": "overview",
    # Pathophysiology
    "pathophysiology": "pathophysiology",
    "pathophys": "pathophysiology",
    "mechanism": "pathophysiology",
    "neurobiology": "pathophysiology",
    # Brain regions
    "brain_structures": "key_brain_regions",
    "brain_regions": "key_brain_regions",
    "neuroanatomy": "key_brain_regions",
    "key_brain": "key_brain_regions",
    "anatomy": "key_brain_regions",
    # Phenotypes
    "phenotype": "phenotypes",
    "clinical_phenotype": "phenotypes",
    "subtype": "phenotypes",
    "classification": "phenotypes",
    # Inclusion / exclusion
    "inclusion": "inclusion_criteria",
    "exclusion": "exclusion_criteria",
    "eligibility": "inclusion_criteria",
    # Safety
    "safety": "safety_notes",
    "side_effect": "safety_notes",
    "adverse": "safety_notes",
    "contraindication": "contraindications",
    "monitoring": "safety_notes",
    # Protocols
    "protocol": "protocols",
    "tdcs": "protocols",
    "tps": "protocols",
    "tavns": "protocols",
    "ces": "protocols",
    "stimulation": "protocols",
    "montage": "protocols",
    "treatment": "protocols",
    # Responder
    "responder": "responder_criteria",
    "response": "responder_criteria",
    "non_responder": "non_responder_pathway",
    # Assessment
    "assessment": "assessment_tools",
    "scale": "assessment_tools",
    "measure": "assessment_tools",
    "screening": "assessment_tools",
    # Networks
    "network": "network_profiles",
    "fnon": "network_profiles",
    "dmn": "network_profiles",
    "cen": "network_profiles",
    "salience": "network_profiles",
    # Evidence / references
    "reference": "references",
    "evidence": "evidence_summary",
    "citation": "references",
    "bibliography": "references",
    # Governance
    "governance": "governance_rules",
    "document_control": "_document_control",
    # Patient info (form sections)
    "patient_info": "_patient_info",
    "patient_information": "_patient_info",
}

# Modality keywords for protocol filtering
_MODALITY_KEYWORDS = {
    "tdcs": Modality.TDCS,
    "tps": Modality.TPS,
    "tavns": Modality.TAVNS,
    "ces": Modality.CES,
    "neurolith": Modality.TPS,
    "alpha_stim": Modality.CES,
    "alpha-stim": Modality.CES,
    "newronika": Modality.TDCS,
    "plato": Modality.TDCS,
}

_INSUFFICIENT_MARKER = (
    "[INSUFFICIENT DATA — REQUIRES CLINICAL INPUT]\n\n"
    "This section could not be auto-populated because the condition's "
    "clinical dataset does not contain sufficient information for this topic. "
    "A qualified clinician must provide this content before the document "
    "can be used clinically."
)


class TemplateDrivenGenerator:
    """
    Reads an uploaded DOCX template and generates per-condition documents
    that mirror its structure, populated with real clinical data.
    """

    def __init__(self, template_path: Path):
        self.template_path = Path(template_path)
        self.parser = TemplateParser(template_path)
        self.template_sections: list[ParsedSection] = []

    def parse_template(self) -> list[ParsedSection]:
        """Parse the uploaded template and return its sections."""
        self.template_sections = self.parser.parse()
        logger.info(
            "Template parsed: %d sections from %s",
            len(self.template_sections),
            self.template_path.name,
        )
        return self.template_sections

    def generate_for_condition(
        self,
        condition: ConditionSchema,
        tier: Tier = Tier.FELLOW,
    ) -> DocumentSpec:
        """
        Generate a DocumentSpec for one condition, mirroring the template structure.

        Every section in the template becomes a section in the output.
        Content comes from ConditionSchema fields — never fabricated.
        Sections that can't be populated are marked INSUFFICIENT.
        """
        if not self.template_sections:
            self.parse_template()

        sections: list[SectionContent] = []
        for ts in self.template_sections:
            section = self._build_section_from_template(ts, condition, tier)
            sections.append(section)

        # Build references from condition
        references = condition.references or []

        # Determine doc type from template name
        doc_type = self._infer_doc_type()

        title = self._build_title(condition, tier)

        spec = DocumentSpec(
            document_type=doc_type,
            tier=tier,
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=_current_month_year(),
            audience=(
                "Fellow clinician" if tier == Tier.FELLOW
                else "Partner clinician"
            ),
            confidentiality_mark="CONFIDENTIAL",
            sections=sections,
            references=references,
            review_flags=condition.review_flags,
            output_filename=self._build_filename(condition, tier),
        )
        return spec

    def _build_section_from_template(
        self,
        template_section: ParsedSection,
        condition: ConditionSchema,
        tier: Tier,
    ) -> SectionContent:
        """Map a template section to condition data."""
        section_id = template_section.section_id
        title = template_section.title

        # Replace condition-name placeholders in title
        title = self._replace_condition_placeholders(title, condition)

        # Find which condition field maps to this section
        field_name = self._match_section_to_field(section_id)

        if field_name == "_document_control":
            return self._build_document_control(condition, tier)

        if field_name == "_patient_info":
            return self._build_patient_info(condition)

        content, tables, claims = self._populate_from_field(
            field_name, condition, section_id, tier
        )

        # Section is a placeholder only if it has NO content AND NO tables
        is_placeholder = (
            (not content.strip() or content.startswith("[INSUFFICIENT"))
            and not tables
        )

        return SectionContent(
            section_id=section_id,
            title=title,
            content=content,
            tables=tables,
            claims=claims,
            review_flags=["requires_clinical_review"] if is_placeholder else [],
            confidence_label=(
                ConfidenceLabel.INSUFFICIENT.value if is_placeholder
                else self._get_section_confidence(condition, field_name)
            ),
            is_placeholder=is_placeholder,
        )

    def _match_section_to_field(self, section_id: str) -> Optional[str]:
        """Match a template section ID to a ConditionSchema field."""
        sid_lower = section_id.lower()

        # Direct match
        if sid_lower in _SECTION_FIELD_MAP:
            return _SECTION_FIELD_MAP[sid_lower]

        # Partial keyword match
        for keyword, field in _SECTION_FIELD_MAP.items():
            if keyword in sid_lower:
                return field

        return None

    def _populate_from_field(
        self,
        field_name: Optional[str],
        condition: ConditionSchema,
        section_id: str,
        tier: Tier,
    ) -> tuple[str, list[dict], list[SectionClaim]]:
        """Pull content from the matched condition field."""
        tables: list[dict] = []
        claims: list[SectionClaim] = []

        if field_name is None:
            return _INSUFFICIENT_MARKER, tables, claims

        # ── String fields ──
        if field_name in ("overview", "pathophysiology", "evidence_summary",
                          "fnon_rationale", "non_responder_pathway"):
            text = getattr(condition, field_name, "")
            if not text:
                return _INSUFFICIENT_MARKER, tables, claims
            return self._replace_condition_placeholders(text, condition), tables, claims

        # ── List of strings ──
        if field_name in ("core_symptoms", "inclusion_criteria", "exclusion_criteria",
                          "contraindications", "evidence_gaps", "responder_criteria",
                          "governance_rules", "decision_tree_notes", "clinical_tips",
                          "baseline_measures", "followup_measures"):
            items = getattr(condition, field_name, [])
            if not items:
                return _INSUFFICIENT_MARKER, tables, claims
            content = "\n".join(f"• {item}" for item in items)
            return content, tables, claims

        # ── Brain regions ──
        if field_name == "key_brain_regions":
            regions = condition.key_brain_regions
            descriptions = condition.brain_region_descriptions
            if not regions:
                return _INSUFFICIENT_MARKER, tables, claims
            lines = []
            for r in regions:
                desc = descriptions.get(r, "")
                lines.append(f"• {r}" + (f": {desc}" if desc else ""))
            return "\n".join(lines), tables, claims

        # ── Network profiles ──
        if field_name == "network_profiles":
            profiles = condition.network_profiles
            if not profiles:
                return _INSUFFICIENT_MARKER, tables, claims
            if tier == Tier.FELLOW:
                # Fellows get simplified network info
                lines = []
                for np in profiles:
                    if np.primary:
                        lines.append(
                            f"Primary network: {np.network.value.upper()} "
                            f"({np.dysfunction.value}) — {np.relevance}"
                        )
                if condition.fnon_rationale:
                    lines.append(f"\n{condition.fnon_rationale}")
                return "\n".join(lines) if lines else _INSUFFICIENT_MARKER, tables, claims
            # Partners get full table
            rows = []
            for np in profiles:
                rows.append([
                    np.network.value.upper(),
                    np.dysfunction.value,
                    np.severity,
                    "✓" if np.primary else "",
                    np.relevance,
                    np.evidence_note or "",
                ])
            tables.append({
                "headers": ["Network", "Dysfunction", "Severity", "Primary", "Relevance", "Evidence Note"],
                "rows": rows,
                "caption": f"FNON Network Profile — {condition.display_name}",
            })
            content = condition.fnon_rationale or ""
            return content, tables, claims

        # ── Phenotypes ──
        if field_name == "phenotypes":
            phenotypes = condition.phenotypes
            if not phenotypes:
                return _INSUFFICIENT_MARKER, tables, claims
            rows = []
            for p in phenotypes:
                features = "; ".join(p.key_features[:4]) if p.key_features else ""
                networks = ", ".join(n.value.upper() for n in p.primary_networks)
                modalities = ", ".join(m.value.upper() for m in p.preferred_modalities)
                rows.append([p.label, p.description[:100], features, networks, modalities])
            tables.append({
                "headers": ["Phenotype", "Description", "Key Features", "Networks", "Modalities"],
                "rows": rows,
                "caption": f"Clinical Phenotypes — {condition.display_name}",
            })
            return "", tables, claims

        # ── Assessment tools ──
        if field_name == "assessment_tools":
            tools = condition.assessment_tools
            if not tools:
                return _INSUFFICIENT_MARKER, tables, claims
            rows = []
            for t in tools:
                pmid = t.evidence_pmid or "—"
                domains = ", ".join(t.domains[:3]) if t.domains else "—"
                rows.append([t.name, t.abbreviation, domains, t.timing, f"PMID: {pmid}"])
            tables.append({
                "headers": ["Scale", "Abbreviation", "Domains", "Timing", "Evidence"],
                "rows": rows,
                "caption": f"Validated Assessment Tools — {condition.display_name}",
            })
            return "", tables, claims

        # ── Protocols ──
        if field_name == "protocols":
            protocols = condition.protocols
            if not protocols:
                return _INSUFFICIENT_MARKER, tables, claims

            # Check if section is modality-specific
            modality_filter = None
            for kw, mod in _MODALITY_KEYWORDS.items():
                if kw in section_id.lower():
                    modality_filter = mod
                    break

            if modality_filter:
                protocols = [p for p in protocols if p.modality == modality_filter]
                if not protocols:
                    return (
                        f"No {modality_filter.value.upper()} protocols defined for "
                        f"{condition.display_name}. Refer to the Evidence-Based Protocol "
                        f"for available modalities.",
                        tables, claims,
                    )

            rows = []
            for p in protocols:
                off_label = "⚠ OFF-LABEL" if p.off_label else "—"
                params = "; ".join(f"{k}: {v}" for k, v in list(p.parameters.items())[:4])
                networks = ", ".join(n.value.upper() for n in p.network_targets[:3])
                rows.append([
                    p.label,
                    p.modality.value.upper(),
                    p.target_region,
                    params or "—",
                    p.evidence_level.value,
                    off_label,
                ])
            tables.append({
                "headers": ["Protocol", "Modality", "Target", "Parameters", "Evidence", "Off-Label"],
                "rows": rows,
                "caption": f"Stimulation Protocols — {condition.display_name}",
            })
            content_lines = []
            for p in protocols:
                content_lines.append(f"• {p.label}: {p.rationale}")
            return "\n".join(content_lines), tables, claims

        # ── Safety notes ──
        if field_name == "safety_notes":
            notes = condition.safety_notes
            if not notes:
                return _INSUFFICIENT_MARKER, tables, claims
            rows = []
            for n in notes:
                rows.append([n.category, n.description, n.severity, n.source or "—"])
            tables.append({
                "headers": ["Category", "Description", "Severity", "Source"],
                "rows": rows,
                "caption": f"Safety Notes — {condition.display_name}",
            })
            return "", tables, claims

        # ── References ──
        if field_name == "references":
            refs = condition.references
            if not refs:
                return _INSUFFICIENT_MARKER, tables, claims
            lines = []
            for i, ref in enumerate(refs, 1):
                if isinstance(ref, dict):
                    text = ref.get("citation", ref.get("text", str(ref)))
                else:
                    text = str(ref)
                lines.append(f"{i}. {text}")
            return "\n".join(lines), tables, claims

        return _INSUFFICIENT_MARKER, tables, claims

    def _build_document_control(
        self, condition: ConditionSchema, tier: Tier
    ) -> SectionContent:
        tier_desc = (
            "For use by SOZO Fellow clinicians under Doctor supervision"
            if tier == Tier.FELLOW
            else "PARTNERS TIER: Full FNON framework. For authorized SOZO Partners."
        )
        return SectionContent(
            section_id="document_control",
            title="Document Control & Clinical Responsibility",
            content=(
                f"Organization: SOZO Brain Center\n"
                f"Condition: {condition.display_name} ({condition.icd10})\n"
                f"Version: {condition.version}\n"
                f"Date: {_current_month_year()}\n"
                f"Tier: {tier.value.upper()}\n"
                f"{tier_desc}\n\n"
                f"© 2026 SOZO Brain Center. All rights reserved. CONFIDENTIAL."
            ),
        )

    def _build_patient_info(self, condition: ConditionSchema) -> SectionContent:
        return SectionContent(
            section_id="patient_info",
            title="Patient Information",
            tables=[{
                "headers": ["Field", "Value"],
                "rows": [
                    ["Patient Name", ""],
                    ["Date of Birth", ""],
                    ["Assessment Date", ""],
                    ["Clinician", ""],
                    ["Condition", condition.display_name],
                    ["Assessment Type", "☐ Baseline  ☐ Follow-Up  ☐ End of Block"],
                    ["Medication State", "☐ ON  ☐ OFF  ☐ N/A"],
                ],
                "caption": "Patient identification and session metadata",
            }],
        )

    def _replace_condition_placeholders(self, text: str, condition: ConditionSchema) -> str:
        """Replace [CONDITION NAME], [ICD-10], etc. in template text."""
        text = re.sub(r"\[CONDITION[_ ]NAME\]", condition.display_name, text, flags=re.IGNORECASE)
        text = re.sub(r"\[ICD[- ]?10\]", condition.icd10, text, flags=re.IGNORECASE)
        text = re.sub(r"\[CONDITION\]", condition.display_name, text, flags=re.IGNORECASE)
        return text

    def _get_section_confidence(self, condition: ConditionSchema, field_name: Optional[str]) -> str:
        """Return a confidence label based on the condition's evidence quality."""
        quality = condition.overall_evidence_quality.value
        mapping = {
            "highest": ConfidenceLabel.HIGH.value,
            "high": ConfidenceLabel.HIGH.value,
            "medium": ConfidenceLabel.MEDIUM.value,
            "low": ConfidenceLabel.LOW.value,
            "very_low": ConfidenceLabel.INSUFFICIENT.value,
            "missing": ConfidenceLabel.INSUFFICIENT.value,
        }
        return mapping.get(quality, ConfidenceLabel.MEDIUM.value)

    def _infer_doc_type(self) -> DocumentType:
        """Infer document type from template filename or content."""
        name = self.template_path.stem.lower()
        if "handbook" in name:
            return DocumentType.HANDBOOK
        if "protocol" in name and "all" in name:
            return DocumentType.ALL_IN_ONE_PROTOCOL
        if "evidence" in name or "protocol" in name:
            return DocumentType.EVIDENCE_BASED_PROTOCOL
        if "exam" in name or "clinical" in name:
            return DocumentType.CLINICAL_EXAM
        if "phenotype" in name:
            return DocumentType.PHENOTYPE_CLASSIFICATION
        if "responder" in name:
            return DocumentType.RESPONDER_TRACKING
        if "intake" in name or "psych" in name:
            return DocumentType.PSYCH_INTAKE
        if "network" in name or "assessment" in name:
            return DocumentType.NETWORK_ASSESSMENT
        return DocumentType.EVIDENCE_BASED_PROTOCOL

    def _build_title(self, condition: ConditionSchema, tier: Tier) -> str:
        """Build a document title from template name + condition."""
        base = self.template_path.stem.replace("_", " ").replace("-", " ").title()
        # Remove any existing condition name from template title
        base = re.sub(r"(?i)parkinson'?s?\s*(disease)?", "", base).strip()
        base = re.sub(r"\s+", " ", base).strip(" -—")
        return f"{base} — {condition.display_name}" if base else condition.display_name

    def _build_filename(self, condition: ConditionSchema, tier: Tier) -> str:
        slug = condition.slug
        template_stem = self.template_path.stem
        return f"{slug}_{template_stem}_{tier.value}.docx"


def _current_month_year() -> str:
    from datetime import datetime
    return datetime.now().strftime("%B %Y")
