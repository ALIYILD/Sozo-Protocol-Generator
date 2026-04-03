"""
Canonical document specification models.

These models describe WHAT a document should contain and HOW each section
should be assembled. They are the prescriptive layer between the knowledge
system and the rendering pipeline.

DocumentBlueprint: declares a document type's full structure
SectionBlueprint: declares one section's requirements and data sources
VisualRequirement: declares what visual asset a section needs
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class VisualRequirement(BaseModel):
    """Declares a visual asset needed by a section."""

    visual_type: str  # qeeg_topomap, brain_map, mri_target_view, protocol_panel, etc.
    caption_template: str = ""  # e.g. "{condition} — Stimulation Target Map"
    placement: str = "after_content"  # after_content, before_content, end_of_section
    required: bool = True
    modality_filter: str = ""  # if set, only include for this modality
    rendering_hints: dict[str, Any] = Field(default_factory=dict)


class SectionBlueprint(BaseModel):
    """Declares what one section of a document should contain.

    The assembler reads this to know:
    - What knowledge fields to pull
    - What format to render (prose, table, list, checklist)
    - What evidence/claims are expected
    - What visuals to generate
    - Whether the section is tier-specific
    """
    slug: str
    title: str
    purpose: str = ""

    # Ordering and inclusion
    order: int = 0
    required: bool = True
    tier: str = "both"  # "both", "fellow", "partners"

    # Content source
    content_type: str = "prose"  # prose, table, list, checklist, mixed, reference_list
    knowledge_fields: list[str] = Field(default_factory=list)  # ConditionSchema fields to pull
    knowledge_source: str = "condition"  # condition, modality, assessment, shared_rules

    # Table rendering
    table_headers: list[str] = Field(default_factory=list)
    table_row_source: str = ""  # e.g. "protocols", "assessment_tools", "safety_rules"
    table_row_fields: list[str] = Field(default_factory=list)  # fields from each row object

    # Evidence
    requires_evidence: bool = False
    citation_density: str = "none"  # none, low, medium, high

    # Subsections
    subsections: list["SectionBlueprint"] = Field(default_factory=list)

    # Visuals
    visuals: list[VisualRequirement] = Field(default_factory=list)

    # Rendering
    preamble: str = ""  # Boilerplate text before data content
    fallback_content: str = ""  # Text if data is empty
    placeholder_if_empty: bool = True

    # Modality filtering (for protocol sections)
    modality_filter: str = ""  # if set, only include protocols for this modality


class DocumentBlueprint(BaseModel):
    """Declares the complete structure of a document type.

    This is the canonical specification that the assembler reads
    to build a document. It replaces the hardcoded dispatch logic
    in DocumentExporter._get_content().
    """
    slug: str
    title_template: str  # e.g. "SOZO Evidence-Based Protocol — {condition_name}"
    doc_type: str  # evidence_based_protocol, handbook, clinical_exam, etc.
    description: str = ""
    target_audience: str = "clinician"
    version: str = "1.0"

    # Tier applicability
    applicable_tiers: list[str] = Field(default_factory=lambda: ["fellow", "partners"])

    # Sections (ordered)
    sections: list[SectionBlueprint] = Field(default_factory=list)

    # Document-level requirements
    requires_references: bool = True
    requires_review_summary: bool = True

    # Output
    output_format: list[str] = Field(default_factory=lambda: ["docx"])
    template_ref: str = ""  # gold_standard template filename

    def get_sections_for_tier(self, tier: str) -> list[SectionBlueprint]:
        """Return sections applicable to a specific tier, in order."""
        return [
            s for s in self.sections
            if s.tier in ("both", tier)
        ]

    def section_slugs(self) -> list[str]:
        """List all section slugs."""
        return [s.slug for s in self.sections]
