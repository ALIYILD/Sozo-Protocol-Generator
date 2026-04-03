"""
Canonical Document Assembler — builds documents from blueprints + knowledge.

This replaces the hardcoded dispatch logic in DocumentExporter._get_content().
Instead of switching on doc_type and explicitly listing section builders,
this assembler reads a DocumentBlueprint and pulls data from the KnowledgeBase.

The output is a standard DocumentSpec that the existing DocumentRenderer
can render to DOCX without modification.

Usage:
    from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler

    assembler = CanonicalDocumentAssembler(knowledge_base)
    spec = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from ..schemas.documents import DocumentSpec, SectionContent
from ..core.enums import DocumentType, Tier
from ..core.utils import current_month_year
from .base import KnowledgeBase
from .schemas import KnowledgeCondition
from .specs import DocumentBlueprint, SectionBlueprint


# ── Provenance Models ──────────────────────────────────────────────────────


@dataclass
class SectionProvenance:
    """Provenance trace for one assembled section."""

    section_slug: str
    blueprint_slug: str
    knowledge_fields_used: list[str] = field(default_factory=list)
    evidence_pmids: list[str] = field(default_factory=list)
    visual_types_requested: list[str] = field(default_factory=list)
    table_row_source: str = ""
    tier: str = ""
    content_type: str = ""
    has_content: bool = False
    has_tables: bool = False
    is_placeholder: bool = False
    warnings: list[str] = field(default_factory=list)

    # QA fields
    evidence_criticality: str = "optional"
    evidence_sufficient: bool = True
    min_pmid_required: int = 0
    actual_pmid_count: int = 0
    qa_status: str = "pass"  # pass, warn, fail
    visual_fulfilled: bool = True


@dataclass
class AssemblyProvenance:
    """Complete provenance trace for a document assembly."""

    condition_slug: str
    blueprint_slug: str
    tier: str
    assembled_at: str = ""
    sections: list[SectionProvenance] = field(default_factory=list)
    total_sections: int = 0
    populated_sections: int = 0
    placeholder_sections: int = 0
    total_evidence_pmids: int = 0
    total_visuals_requested: int = 0
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.assembled_at:
            self.assembled_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def readiness(self) -> str:
        """Document readiness: ready, review_required, or incomplete."""
        if any(s.qa_status == "fail" for s in self.sections):
            return "incomplete"
        if self.placeholder_sections > 0 or any(s.qa_status == "warn" for s in self.sections):
            return "review_required"
        return "ready"

    @property
    def sections_passing(self) -> int:
        return sum(1 for s in self.sections if s.qa_status == "pass")

    @property
    def sections_warning(self) -> int:
        return sum(1 for s in self.sections if s.qa_status == "warn")

    @property
    def sections_failing(self) -> int:
        return sum(1 for s in self.sections if s.qa_status == "fail")

    def to_dict(self) -> dict:
        """Serialize to dict for JSON export."""
        return {
            "condition_slug": self.condition_slug,
            "blueprint_slug": self.blueprint_slug,
            "tier": self.tier,
            "assembled_at": self.assembled_at,
            "readiness": self.readiness,
            "total_sections": self.total_sections,
            "populated_sections": self.populated_sections,
            "placeholder_sections": self.placeholder_sections,
            "sections_passing": self.sections_passing,
            "sections_warning": self.sections_warning,
            "sections_failing": self.sections_failing,
            "total_evidence_pmids": self.total_evidence_pmids,
            "total_visuals_requested": self.total_visuals_requested,
            "warnings": self.warnings,
            "sections": [
                {
                    "section_slug": s.section_slug,
                    "qa_status": s.qa_status,
                    "evidence_criticality": s.evidence_criticality,
                    "evidence_sufficient": s.evidence_sufficient,
                    "actual_pmid_count": s.actual_pmid_count,
                    "min_pmid_required": s.min_pmid_required,
                    "knowledge_fields_used": s.knowledge_fields_used,
                    "evidence_pmids": s.evidence_pmids,
                    "visual_types_requested": s.visual_types_requested,
                    "visual_fulfilled": s.visual_fulfilled,
                    "has_content": s.has_content,
                    "has_tables": s.has_tables,
                    "is_placeholder": s.is_placeholder,
                    "warnings": s.warnings,
                }
                for s in self.sections
            ],
        }

logger = logging.getLogger(__name__)

# Map of network keys to display names
_NETWORK_NAMES = {
    "dmn": "Default Mode Network (DMN)",
    "cen": "Central Executive Network (CEN)",
    "sn": "Salience Network (SN)",
    "smn": "Sensorimotor Network (SMN)",
    "limbic": "Limbic/Emotional Network",
    "attention": "Attention Networks",
}

_DYSFUNCTION_LABELS = {
    "hypo": "Hypoactivation / Underconnectivity",
    "hyper": "Hyperactivation / Overconnectivity",
    "normal": "Normal function",
}


class CanonicalDocumentAssembler:
    """Assembles a document from a blueprint and knowledge objects.

    This is the canonical generation path. It reads:
    - DocumentBlueprint (what sections to include, in what order)
    - KnowledgeCondition (clinical data for the condition)
    - KnowledgeModality (modality details for protocol sections)
    - Shared rules (governance, safety)

    And produces a DocumentSpec ready for rendering.
    """

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def assemble(
        self,
        condition_slug: str,
        blueprint_slug: str,
        tier: str = "fellow",
    ) -> tuple[DocumentSpec, AssemblyProvenance]:
        """Assemble a complete document from blueprint + knowledge.

        Args:
            condition_slug: Condition to generate for
            blueprint_slug: Document blueprint to use
            tier: "fellow" or "partners"

        Returns:
            Tuple of (DocumentSpec ready for rendering, AssemblyProvenance trace)
        """
        # Resolve inputs
        condition = self.kb.get_condition(condition_slug)
        if not condition:
            raise ValueError(f"Condition not found in knowledge base: {condition_slug}")

        blueprint = self.kb.get_blueprint(blueprint_slug)
        if not blueprint:
            raise ValueError(f"Blueprint not found: {blueprint_slug}")

        # Get tier-appropriate sections
        section_blueprints = blueprint.get_sections_for_tier(tier)

        # Provenance tracking
        provenance = AssemblyProvenance(
            condition_slug=condition_slug,
            blueprint_slug=blueprint_slug,
            tier=tier,
        )

        # Build sections
        sections = []
        for sb in section_blueprints:
            section, sec_prov = self._build_section(condition, sb, tier)
            sections.append(section)
            provenance.sections.append(sec_prov)

        # Finalize provenance
        provenance.total_sections = len(sections)
        provenance.populated_sections = sum(
            1 for s in sections if s.content or s.tables or s.subsections
        )
        provenance.placeholder_sections = sum(1 for s in sections if s.is_placeholder)
        provenance.total_evidence_pmids = sum(
            len(sp.evidence_pmids) for sp in provenance.sections
        )
        provenance.total_visuals_requested = sum(
            len(sp.visual_types_requested) for sp in provenance.sections
        )

        # Build document spec
        title = blueprint.title_template.replace("{condition_name}", condition.display_name)

        try:
            doc_type_enum = DocumentType(blueprint.doc_type)
        except ValueError:
            doc_type_enum = DocumentType.EVIDENCE_BASED_PROTOCOL

        tier_enum = Tier(tier)
        tier_desc = (
            "For use by SOZO Fellow clinicians under Doctor supervision"
            if tier == "fellow"
            else "PARTNERS TIER: Full FNON framework. For authorized SOZO Partners."
        )

        audience = (
            "Fellow clinician" if tier == "fellow"
            else "Partner clinician" if tier == "partners"
            else blueprint.target_audience
        )

        spec = DocumentSpec(
            document_type=doc_type_enum,
            tier=tier_enum,
            condition_slug=condition_slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=current_month_year(),
            audience=audience,
            confidentiality_mark="CONFIDENTIAL",
            sections=sections,
            references=[r.model_dump() for r in condition.references],
            review_flags=[],
        )

        logger.info(
            f"Canonical assembly: {condition_slug}/{blueprint_slug}/{tier} "
            f"→ {provenance.populated_sections}/{provenance.total_sections} sections populated, "
            f"{provenance.placeholder_sections} placeholders"
        )
        return spec, provenance

    def _build_section(
        self,
        condition: KnowledgeCondition,
        blueprint: SectionBlueprint,
        tier: str,
    ) -> tuple[SectionContent, SectionProvenance]:
        """Build one section from its blueprint and condition knowledge."""

        content_parts = []
        tables = []
        review_flags = []
        subsections = []
        evidence_pmids = []
        figures = []
        is_placeholder = False

        # Provenance tracking
        prov = SectionProvenance(
            section_slug=blueprint.slug,
            blueprint_slug=blueprint.slug,
            knowledge_fields_used=list(blueprint.knowledge_fields),
            visual_types_requested=[v.visual_type for v in blueprint.visuals],
            table_row_source=blueprint.table_row_source,
            tier=blueprint.tier,
            content_type=blueprint.content_type,
        )

        # Preamble from blueprint
        if blueprint.preamble:
            preamble = blueprint.preamble.replace("{condition_name}", condition.display_name)
            content_parts.append(preamble)

        # Rich section template (shared clinical text scaffolding for depth)
        template_text = self._get_section_template(blueprint.slug, condition, tier)
        if template_text:
            content_parts.append(template_text)

        # Special section: document_control gets full governance block
        if blueprint.slug == "document_control":
            tier_desc = (
                "For use by SOZO Fellow clinicians under Doctor supervision"
                if tier == "fellow"
                else "PARTNERS TIER: This document contains the complete FNON framework. For authorized SOZO Partners."
            )
            content_parts.append(
                f"Organization: SOZO Brain Center\n"
                f"Condition: {condition.display_name} ({condition.icd10})\n"
                f"Version: {condition.version}\n"
                f"Date: {current_month_year()}\n"
                f"Tier: {tier.upper()}\n"
                f"{tier_desc}\n\n"
                f"\u00a9 2026 SOZO Brain Center. All rights reserved. CONFIDENTIAL.\n\n"
                f"GOVERNANCE RULE: This document is for authorized SOZO personnel only. "
                f"No Fellow or Clinical Assistant may independently modify treatment protocols "
                f"without Doctor authorization."
            )

        # Pull knowledge fields and build content
        for field_name in blueprint.knowledge_fields:
            value = self._resolve_field(condition, field_name)
            if value is None:
                continue

            if isinstance(value, str) and value:
                content_parts.append(value)
            elif isinstance(value, list) and value:
                if blueprint.content_type == "list":
                    for item in value:
                        content_parts.append(f"\u2022 {item}")
                elif blueprint.content_type == "reference_list":
                    for i, ref in enumerate(value, 1):
                        if isinstance(ref, dict):
                            text = self._format_reference(ref, i)
                        else:
                            text = f"{i}. {ref}"
                        content_parts.append(text)
                # Tables are handled separately below

        # Build table if blueprint declares one
        if blueprint.table_row_source and blueprint.table_headers:
            table = self._build_table(
                condition, blueprint.table_row_source,
                blueprint.table_headers, blueprint.modality_filter,
            )
            if table:
                tables.append(table)

        # Rich content expansion — generate detailed prose from structured data
        expanded = self._expand_section_content(condition, blueprint, tier)
        if expanded:
            content_parts.append(expanded)

        # Build subsections recursively
        for sub_bp in blueprint.subsections:
            if sub_bp.tier not in ("both", tier):
                continue
            sub_section, _ = self._build_section(condition, sub_bp, tier)
            subsections.append(sub_section)

        # Collect evidence PMIDs from references
        for ref in condition.references:
            if ref.pmid:
                evidence_pmids.append(ref.pmid)

        # Check for empty sections
        content = "\n".join(content_parts) if content_parts else ""
        if not content and not tables and not subsections:
            if blueprint.fallback_content:
                content = blueprint.fallback_content
            elif blueprint.placeholder_if_empty:
                is_placeholder = True
                content = f"[REVIEW REQUIRED: No data available for {blueprint.title}]"
                review_flags.append(f"Section '{blueprint.title}' has no data — requires clinical input")

        # Confidence label
        confidence = None
        if blueprint.requires_evidence and evidence_pmids:
            confidence = "high_confidence" if len(evidence_pmids) >= 3 else "medium_confidence"
        elif blueprint.requires_evidence and not evidence_pmids:
            confidence = "low_confidence"

        # Finalize provenance with QA
        prov.evidence_pmids = evidence_pmids[:10]
        prov.actual_pmid_count = len(evidence_pmids)
        prov.has_content = bool(content)
        prov.has_tables = bool(tables)
        prov.is_placeholder = is_placeholder
        prov.evidence_criticality = blueprint.evidence_criticality
        prov.min_pmid_required = blueprint.min_pmid_count
        prov.visual_fulfilled = len(blueprint.visuals) == 0  # Fulfilled if none required

        # Evidence sufficiency QA
        if blueprint.requires_evidence:
            if blueprint.min_pmid_count > 0 and len(evidence_pmids) < blueprint.min_pmid_count:
                prov.evidence_sufficient = False
                prov.warnings.append(
                    f"Section '{blueprint.title}' requires {blueprint.min_pmid_count} PMIDs "
                    f"but only has {len(evidence_pmids)}"
                )

        # Determine QA status
        if is_placeholder:
            if blueprint.evidence_criticality == "critical":
                prov.qa_status = "fail"
            elif blueprint.required:
                prov.qa_status = "warn"
            prov.warnings.append(f"Section '{blueprint.title}' is a placeholder — needs data")
        elif blueprint.requires_evidence and not prov.evidence_sufficient:
            if blueprint.on_insufficient_evidence == "block":
                prov.qa_status = "fail"
            else:
                prov.qa_status = "warn"
        else:
            prov.qa_status = "pass"

        return SectionContent(
            section_id=blueprint.slug,
            title=blueprint.title,
            content=content,
            subsections=subsections,
            tables=tables,
            figures=figures,
            review_flags=review_flags,
            evidence_pmids=evidence_pmids[:10],
            confidence_label=confidence,
            is_placeholder=is_placeholder,
        ), prov

    def _resolve_field(self, condition: KnowledgeCondition, field_name: str) -> Any:
        """Resolve a knowledge field from the condition object."""
        # Direct attribute access
        if hasattr(condition, field_name):
            return getattr(condition, field_name)

        # Mapped fields
        field_map = {
            "brain_region_details": condition.brain_region_details,
        }
        return field_map.get(field_name)

    def _build_table(
        self,
        condition: KnowledgeCondition,
        row_source: str,
        headers: list[str],
        modality_filter: str = "",
    ) -> Optional[dict]:
        """Build a table from condition data."""

        if row_source == "protocols":
            rows = []
            for p in condition.protocols:
                if modality_filter and p.modality != modality_filter:
                    continue
                params_str = ", ".join(f"{k}: {v}" for k, v in p.parameters.items()) if p.parameters else ""
                status = "OFF-LABEL" if p.off_label else "On-label"
                rows.append([
                    p.protocol_id, p.label, p.target_region,
                    params_str or "See protocol specification",
                    p.evidence_level, status,
                ])
            if not rows:
                return None
            return {"headers": headers, "rows": rows, "caption": f"Protocols ({modality_filter.upper() if modality_filter else 'All'})"}

        elif row_source == "network_profiles":
            rows = []
            for np in condition.network_profiles:
                net_name = _NETWORK_NAMES.get(np.network, np.network.upper())
                dys_label = _DYSFUNCTION_LABELS.get(np.dysfunction, np.dysfunction)
                rows.append([net_name, dys_label, np.severity.title(), np.relevance[:100]])
            return {"headers": headers, "rows": rows, "caption": "FNON Network Profile"} if rows else None

        elif row_source == "phenotypes":
            rows = []
            for p in condition.phenotypes:
                features = "; ".join(p.key_features[:3])
                networks = ", ".join(n.upper() for n in p.primary_networks)
                modalities = ", ".join(m.upper() for m in p.preferred_modalities)
                rows.append([p.label, p.description[:80], features, networks, modalities])
            return {"headers": headers, "rows": rows, "caption": "Phenotype Classification"} if rows else None

        elif row_source == "safety_rules":
            rows = []
            for sr in condition.safety_rules:
                rows.append([sr.category.title(), sr.severity.upper(), sr.description, sr.source or "SOZO protocol"])
            # Also include shared contraindications from KB
            for c_name in condition.contraindications[:5]:
                rows.append(["Contraindication", "ABSOLUTE", c_name, "Clinical guidelines"])
            return {"headers": headers, "rows": rows, "caption": "Safety & Contraindications"} if rows else None

        elif row_source == "assessments":
            rows = []
            for a_ref in condition.assessments:
                # Try to resolve from KB
                asmt = self.kb.assessments.get(a_ref.scale_key)
                if asmt:
                    rows.append([asmt.abbreviation, asmt.name, ", ".join(asmt.domains), a_ref.timing, asmt.validation_pmid or ""])
                else:
                    rows.append([a_ref.scale_key, a_ref.scale_key, "", a_ref.timing, ""])
            return {"headers": headers, "rows": rows, "caption": "Assessment Tools"} if rows else None

        elif row_source == "brain_regions":
            rows = []
            for region in condition.brain_regions:
                desc = condition.brain_region_details.get(region, "")
                rows.append([region, desc])
            return {"headers": headers, "rows": rows, "caption": "Key Brain Regions"} if rows else None

        return None

    def _format_reference(self, ref: dict, index: int) -> str:
        """Format a single reference entry."""
        authors = ref.get("authors", "")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "[Title not available]")
        journal = ref.get("journal", "")
        pmid = ref.get("pmid", "")

        text = f"{index}. {authors} ({year}). {title}."
        if journal:
            text += f" {journal}."
        if pmid and not str(pmid).startswith("placeholder"):
            text += f" PMID: {pmid}."
        return text

    # ── Rich content expansion ─────────────────────────────────────

    def _expand_section_content(self, condition: KnowledgeCondition, blueprint: SectionBlueprint, tier: str) -> str:
        """Generate detailed prose from structured condition data for section depth."""
        slug = blueprint.slug
        parts = []

        # Expand protocol sections with per-protocol detail blocks
        if slug.startswith("protocols_") or slug == "protocols":
            mod_filter = blueprint.modality_filter
            for proto in condition.protocols:
                if mod_filter and proto.modality != mod_filter:
                    continue
                block = self._expand_protocol_detail(proto, condition, tier)
                if block:
                    parts.append(block)

        # Expand network profiles with per-network analysis
        elif slug == "network_profiles":
            for np in condition.network_profiles:
                block = self._expand_network_detail(np, condition)
                if block:
                    parts.append(block)

        # Expand phenotypes with per-phenotype clinical description
        elif slug == "phenotypes":
            for pheno in condition.phenotypes:
                block = self._expand_phenotype_detail(pheno, condition)
                if block:
                    parts.append(block)

        # Expand brain anatomy with per-region detail
        elif slug == "brain_anatomy":
            for region in condition.brain_regions:
                desc = condition.brain_region_details.get(region, "")
                if desc:
                    parts.append(f"\n{region}: {desc}")

        # Expand safety with detailed rule descriptions
        elif slug == "safety":
            for rule in condition.safety_rules:
                parts.append(f"\n{rule.category.title()} ({rule.severity.upper()}): {rule.description}")
                if rule.source:
                    parts.append(f"  Source: {rule.source}")

        return "\n".join(parts)

    def _expand_protocol_detail(self, proto, condition: KnowledgeCondition, tier: str) -> str:
        """Generate a detailed description block for one protocol."""
        lines = [
            f"\nProtocol {proto.protocol_id}: {proto.label}",
            f"Modality: {proto.modality.upper()}",
            f"Target Region: {proto.target_region} ({proto.target_abbreviation})",
        ]

        # Parameters
        if proto.parameters:
            param_strs = [f"{k}: {v}" for k, v in proto.parameters.items()]
            lines.append(f"Parameters: {', '.join(param_strs)}")

        # Evidence
        lines.append(f"Evidence Level: {proto.evidence_level}")
        if proto.off_label:
            lines.append(f"Regulatory Status: OFF-LABEL — requires informed consent and Doctor authorisation")

        # Rationale (the clinical reasoning)
        if proto.rationale:
            lines.append(f"Clinical Rationale: {proto.rationale}")

        # Network targets
        if proto.network_targets:
            nets = ", ".join(n.upper() if isinstance(n, str) else n for n in proto.network_targets)
            lines.append(f"Network Targets: {nets}")

        # Phenotype match
        if proto.phenotype_slugs:
            lines.append(f"Phenotype Match: {', '.join(proto.phenotype_slugs)}")

        # Session info
        if proto.session_count:
            lines.append(f"Recommended Sessions: {proto.session_count}")

        # Notes
        if proto.notes:
            lines.append(f"Clinical Notes: {proto.notes}")

        return "\n".join(lines)

    def _expand_network_detail(self, np, condition: KnowledgeCondition) -> str:
        """Generate a detailed description for one network profile."""
        net_name = _NETWORK_NAMES.get(np.network, np.network.upper())
        dys_label = _DYSFUNCTION_LABELS.get(np.dysfunction, np.dysfunction)

        lines = [
            f"\n{net_name}",
            f"Dysfunction Pattern: {dys_label}",
            f"Severity: {np.severity.title()}",
            f"Primary Network: {'Yes' if np.primary else 'No'}",
        ]

        if np.relevance:
            lines.append(f"Clinical Relevance: {np.relevance}")

        if np.evidence_note:
            lines.append(f"Evidence Note: {np.evidence_note}")

        return "\n".join(lines)

    def _expand_phenotype_detail(self, pheno, condition: KnowledgeCondition) -> str:
        """Generate a detailed description for one phenotype."""
        lines = [
            f"\nPhenotype: {pheno.label}",
        ]

        if pheno.description:
            lines.append(f"Description: {pheno.description}")

        if pheno.key_features:
            lines.append(f"Key Features: {'; '.join(pheno.key_features)}")

        if pheno.primary_networks:
            nets = ", ".join(n.upper() if isinstance(n, str) else n for n in pheno.primary_networks)
            lines.append(f"Primary Network Targets: {nets}")

        if pheno.preferred_modalities:
            mods = ", ".join(m.upper() if isinstance(m, str) else m for m in pheno.preferred_modalities)
            lines.append(f"Preferred Modalities: {mods}")

        if pheno.tdcs_target:
            lines.append(f"tDCS Target: {pheno.tdcs_target}")

        if pheno.tps_target:
            lines.append(f"TPS Target: {pheno.tps_target}")

        return "\n".join(lines)

    # ── Section template enrichment ──────────────────────────────────

    _SECTION_TEMPLATE_MAP = {
        "clinical_overview": "overview_template",
        "pathophysiology": "pathophysiology_template",
        "protocols_tdcs": "protocol_preamble_template",
        "protocols_tps": "protocol_preamble_template",
        "protocols_tavns": "protocol_preamble_template",
        "protocols_ces": "protocol_preamble_template",
        "safety": "safety_preamble_template",
        "assessments": "assessment_preamble_template",
        "responder_criteria": "responder_preamble_template",
        "inclusion_exclusion": "inclusion_exclusion_template",
    }

    def _get_section_template(self, section_slug: str, condition: KnowledgeCondition, tier: str) -> str:
        """Load rich section template text from shared knowledge rules."""
        template_slug = self._SECTION_TEMPLATE_MAP.get(section_slug)
        if not template_slug:
            return ""

        # Look up template in shared rules
        for rule in self.kb.get_shared_rules("section_content"):
            if rule.slug == template_slug:
                text = rule.rule_text
                # Replace variables
                text = text.replace("{condition_name}", condition.display_name)
                text = text.replace("{icd10}", condition.icd10)
                text = text.replace("{category}", condition.category or "clinical")
                return text

        return ""
