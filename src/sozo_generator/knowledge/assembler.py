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
from typing import Any, Optional

from ..schemas.documents import DocumentSpec, SectionContent
from ..core.enums import DocumentType, Tier
from ..core.utils import current_month_year
from .base import KnowledgeBase
from .schemas import KnowledgeCondition
from .specs import DocumentBlueprint, SectionBlueprint

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
    ) -> DocumentSpec:
        """Assemble a complete document from blueprint + knowledge.

        Args:
            condition_slug: Condition to generate for
            blueprint_slug: Document blueprint to use
            tier: "fellow" or "partners"

        Returns:
            DocumentSpec ready for rendering
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

        # Build sections
        sections = []
        for sb in section_blueprints:
            section = self._build_section(condition, sb, tier)
            sections.append(section)

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

        spec = DocumentSpec(
            document_type=doc_type_enum,
            tier=tier_enum,
            condition_slug=condition_slug,
            condition_name=condition.display_name,
            title=title,
            version=condition.version,
            date_label=current_month_year(),
            audience=blueprint.target_audience,
            confidentiality_mark="CONFIDENTIAL",
            sections=sections,
            references=[r.model_dump() for r in condition.references],
            review_flags=[],
        )

        logger.info(
            f"Canonical assembly: {condition_slug}/{blueprint_slug}/{tier} "
            f"→ {len(sections)} sections"
        )
        return spec

    def _build_section(
        self,
        condition: KnowledgeCondition,
        blueprint: SectionBlueprint,
        tier: str,
    ) -> SectionContent:
        """Build one section from its blueprint and condition knowledge."""

        content_parts = []
        tables = []
        review_flags = []
        subsections = []
        evidence_pmids = []
        figures = []
        is_placeholder = False

        # Preamble
        if blueprint.preamble:
            preamble = blueprint.preamble.replace("{condition_name}", condition.display_name)
            content_parts.append(preamble)

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
                        content_parts.append(f"• {item}")
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

        # Build subsections recursively
        for sub_bp in blueprint.subsections:
            if sub_bp.tier not in ("both", tier):
                continue
            sub_section = self._build_section(condition, sub_bp, tier)
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
        )

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
