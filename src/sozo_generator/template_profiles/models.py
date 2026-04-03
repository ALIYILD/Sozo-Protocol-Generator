"""
Schema models for template-driven AI generation.

These models capture the structure and style of uploaded DOCX templates,
enabling the system to generate new documents that match the template's
layout, tone, and section patterns for different conditions.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field


# ── Template Structure Models ──────────────────────────────────────────────


class TableSpec(BaseModel):
    """Captured table structure from a template."""

    table_index: int = 0
    parent_section_id: str = ""
    headers: list[str] = Field(default_factory=list)
    col_count: int = 0
    row_count: int = 0
    caption: str = ""
    has_header_row: bool = True
    estimated_purpose: str = ""  # "scoring", "checklist", "protocol_params", "demographics"


class FigureSpec(BaseModel):
    """Captured figure/image placement from a template."""

    figure_index: int = 0
    parent_section_id: str = ""
    approximate_position: str = ""  # "after_heading", "end_of_section", "inline"
    caption_text: str = ""
    estimated_type: str = ""  # "brain_map", "eeg_topomap", "network_diagram", etc.
    width_hint: str = ""  # "full_width", "half_width", "inline"


class FormattingProfile(BaseModel):
    """Captured formatting/style metadata from a template."""

    # Fonts
    primary_font: str = "Calibri"
    heading_font: str = "Calibri"
    body_font_size_pt: float = 11.0
    heading_sizes_pt: dict[int, float] = Field(
        default_factory=lambda: {1: 16.0, 2: 14.0, 3: 12.0, 4: 11.0}
    )

    # Spacing
    paragraph_spacing_pt: float = 6.0
    line_spacing: float = 1.15

    # Lists
    bullet_style: str = "disc"  # "disc", "dash", "checkbox"
    numbered_list_style: str = "decimal"

    # Tables
    table_header_bold: bool = True
    table_header_shading: str = "#1F3864"  # Navy by default
    table_border_style: str = "single"

    # Page
    page_orientation: str = "portrait"
    margin_cm: float = 2.54

    # Images
    image_width_cm: float = 14.0
    caption_italic: bool = True
    caption_size_pt: float = 9.0


class ToneProfile(BaseModel):
    """Captured tone/style signals from template prose."""

    audience: str = "clinician"  # "clinician", "researcher", "patient"
    formality: str = "formal"  # "formal", "semi_formal", "accessible"
    voice: str = "third_person"  # "third_person", "passive", "imperative"
    sentence_density: str = "medium"  # "dense", "medium", "sparse"
    section_depth: str = "detailed"  # "brief", "moderate", "detailed", "comprehensive"
    citation_style: str = "inline_pmid"  # "inline_pmid", "numbered", "author_year"
    clinical_tone: str = "evidence_based"  # "evidence_based", "practical", "educational"
    uses_abbreviations: bool = True
    uses_clinical_warnings: bool = True
    uses_governance_boxes: bool = True
    sample_excerpts: list[str] = Field(default_factory=list)  # Representative text samples


class TemplateSectionSpec(BaseModel):
    """Learned specification for one section in a template."""

    section_id: str
    title: str
    normalized_title: str = ""  # Condition-agnostic title
    heading_level: int = 1
    order_index: int = 0
    required: bool = True

    # Content characteristics
    content_kind: str = "prose"  # "prose", "table_heavy", "checklist", "mixed", "reference_list"
    estimated_word_count: int = 0
    estimated_paragraph_count: int = 0

    # Expected elements
    table_expected: bool = False
    table_count: int = 0
    visual_expected: bool = False
    visual_type_hint: str = ""  # "brain_map", "eeg_topomap", etc.

    # Evidence requirements
    citation_density_hint: str = "none"  # "none", "low", "medium", "high"
    requires_evidence: bool = False

    # Sample content for tone matching
    source_excerpt_sample: str = ""  # First ~200 chars of original content

    # Subsections
    subsections: list[TemplateSectionSpec] = Field(default_factory=list)


class TemplateProfile(BaseModel):
    """Complete learned profile of an uploaded DOCX template.

    This is the core model for template-driven generation. It captures
    everything the system needs to generate a new document matching
    the template's structure, tone, and layout.
    """

    # Identity
    profile_id: str
    name: str
    source_filename: str
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    version: str = "1.0"

    # Classification
    template_type: str = ""  # "handbook", "protocol", "assessment", "checklist"
    inferred_doc_type: Optional[str] = None  # DocumentType value
    tier: Optional[str] = None  # "fellow", "partners"
    source_condition: Optional[str] = None  # Condition detected in template

    # Structure
    section_map: list[TemplateSectionSpec] = Field(default_factory=list)
    heading_hierarchy: dict[int, int] = Field(default_factory=dict)  # level → count

    # Element inventories
    table_specs: list[TableSpec] = Field(default_factory=list)
    figure_specs: list[FigureSpec] = Field(default_factory=list)

    # Style
    formatting_profile: FormattingProfile = Field(default_factory=FormattingProfile)
    tone_profile: ToneProfile = Field(default_factory=ToneProfile)

    # Placeholders
    placeholder_map: dict[str, list[str]] = Field(default_factory=dict)

    # Fingerprint
    template_fingerprint: str = ""

    @computed_field
    @property
    def total_sections(self) -> int:
        return len(self.section_map)

    @computed_field
    @property
    def total_tables(self) -> int:
        return len(self.table_specs)

    @computed_field
    @property
    def total_figures(self) -> int:
        return len(self.figure_specs)

    def get_section(self, section_id: str) -> Optional[TemplateSectionSpec]:
        """Find a section by ID."""
        for s in self.section_map:
            if s.section_id == section_id:
                return s
        return None

    def section_ids(self) -> list[str]:
        """List all section IDs in order."""
        return [s.section_id for s in self.section_map]


# ── Research Models ────────────────────────────────────────────────────────


class ResearchSource(BaseModel):
    """A single retrieved source (article, guideline, web page)."""

    source_type: str = "pubmed"  # "pubmed", "guideline", "web", "internal"
    title: str = ""
    authors: str = ""
    year: Optional[int] = None
    pmid: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: str = ""
    key_finding: str = ""
    relevance_score: float = 0.0
    evidence_level: str = "medium"


class ResearchBundle(BaseModel):
    """Evidence gathered for one section of a document."""

    condition_slug: str
    section_id: str
    query_set: list[str] = Field(default_factory=list)
    sources: list[ResearchSource] = Field(default_factory=list)
    evidence_summary: str = ""
    confidence: str = "medium"  # "high", "medium", "low", "insufficient"
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    @computed_field
    @property
    def source_count(self) -> int:
        return len(self.sources)

    @computed_field
    @property
    def pmid_count(self) -> int:
        return sum(1 for s in self.sources if s.pmid)


# ── Writing Pipeline Models ───────────────────────────────────────────────


class SectionBrief(BaseModel):
    """Structured brief for AI section writing.

    Contains everything the section writer needs to draft content
    for one section of a template-driven document.
    """

    # Target
    target_condition: str
    target_condition_name: str
    tier: str
    doc_type: str

    # Template expectations
    section_spec: TemplateSectionSpec
    style_constraints: ToneProfile = Field(default_factory=ToneProfile)

    # Content inputs
    internal_condition_data: dict[str, Any] = Field(default_factory=dict)
    evidence_summary: str = ""
    citations_available: list[dict] = Field(default_factory=list)

    # Rules
    required_topics: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(
        default_factory=lambda: [
            "Do not fabricate PMIDs or citation identifiers",
            "Do not claim regulatory approval without evidence",
            "Do not invent stimulation parameters",
            "Do not make unsupported efficacy claims",
        ]
    )
    expected_visuals: list[str] = Field(default_factory=list)


class DraftedSection(BaseModel):
    """A single AI-drafted section with provenance metadata."""

    section_id: str
    title: str
    content: str = ""
    subsections: list["DraftedSection"] = Field(default_factory=list)

    # Evidence
    citations_used: list[str] = Field(default_factory=list)  # PMIDs
    claim_count: int = 0

    # Quality
    confidence: str = "medium"
    review_flags: list[str] = Field(default_factory=list)
    needs_review: bool = False
    grounding_score: float = 0.0  # 0-1, how well grounded

    # Metadata
    generation_method: str = "ai"  # "ai", "template_adapt", "internal_data", "harvested"
    model_used: str = ""
    generation_timestamp: str = ""

    # Tables and figures
    tables: list[dict] = Field(default_factory=list)
    figures: list[str] = Field(default_factory=list)


# ── Build Manifest ────────────────────────────────────────────────────────


class DocumentBuildManifest(BaseModel):
    """Complete provenance record for a template-driven document build."""

    # Identity
    build_id: str
    condition_slug: str
    condition_name: str
    tier: str
    doc_type: str

    # Template
    template_profile_id: str
    template_name: str

    # Evidence
    evidence_profile_version: str = ""
    research_bundles_used: int = 0
    total_citations: int = 0

    # Generation
    generation_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    generator_version: str = "1.1.0"
    ai_model_used: str = ""

    # Sections
    sections_generated: list[str] = Field(default_factory=list)
    sections_from_ai: int = 0
    sections_from_data: int = 0
    sections_from_template: int = 0
    sections_needing_review: int = 0

    # Visuals
    visuals_generated: list[str] = Field(default_factory=list)

    # QA
    qa_passed: Optional[bool] = None
    qa_issues: list[str] = Field(default_factory=list)

    # Output
    output_paths: dict[str, str] = Field(default_factory=dict)  # "docx" → path, "pdf" → path
