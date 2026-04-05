"""Canonical data models for the SOZO long-document production pipeline.

This module defines all Pydantic v2 models used at every stage of the
long-document pipeline: planning (blueprints, specs), generation
(canonical blocks/sections/documents), asset tracking (AssetRecord),
QA (validation issues, reports), and assembly provenance.

Model hierarchy (high-level):
  DocumentBlueprint
    └── SectionSpec
          └── SubsectionSpec
                └── ContentBlockSpec

  CanonicalDocument
    ├── CanonicalSection
    │     └── CanonicalBlock
    ├── AssetRecord
    ├── CanonicalCitation
    ├── AssemblyProvenance
    └── DocumentQAReport
          └── QAValidationResult
                └── QAValidationIssue
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Literal type aliases
# ---------------------------------------------------------------------------

BlockType = Literal[
    "text",
    "table",
    "figure",
    "chart",
    "image",
    "list",
    "callout",
    "heading",
    "divider",
    "pagebreak",
    "appendix_entry",
    "toc_entry",
]

AssetType = Literal[
    "table",
    "figure",
    "chart",
    "image",
    "diagram",
    "topomap",
    "montage",
    "timeline",
    "flowchart",
]

AssetStatus = Literal[
    "pending",
    "generating",
    "generated",
    "failed",
    "validated",
    "missing",
]

ValidationSeverity = Literal["block", "warning", "info"]

SectionVariant = Literal["fellow", "partners", "shared"]

AssemblyStatus = Literal["pending", "in_progress", "complete", "failed"]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _new_id() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


# ===========================================================================
# SECTION 1 — Planning-time spec models
# ===========================================================================


class ContentBlockSpec(BaseModel):
    """Planning-time specification for a single block within a section.

    Describes *what* should be generated at this position.  The generator
    reads these specs and produces ``CanonicalBlock`` instances from them.
    ``asset_id`` links to a pre-registered ``AssetRecord`` when the block
    will be rendered as a non-text asset.
    """

    block_id: str = Field(default_factory=_new_id)
    block_type: BlockType = "text"
    heading: Optional[str] = None
    heading_level: int = 0
    content_hint: str = Field(
        default="",
        description="Human- or LLM-readable guidance on what to write here.",
    )
    asset_id: Optional[str] = Field(
        default=None,
        description="Reference to an AssetRecord that will be embedded here.",
    )
    placeholder: bool = False
    variant_tags: list[str] = Field(
        default_factory=list,
        description='Audience tags, e.g. ["fellow"] or ["partners"]. Empty = shared.',
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    target_word_count: int = 0


class SubsectionSpec(BaseModel):
    """Planning-time specification for a subsection inside a ``SectionSpec``.

    Subsections allow fine-grained control of word-count targets, evidence
    requirements, and allowed claim categories at a level below full sections.
    """

    subsection_id: str = Field(default_factory=_new_id)
    title: str
    purpose: str = Field(
        default="",
        description="Why this subsection exists (e.g. 'Define the pathophysiology rationale').",
    )
    target_word_count: int = 300
    variant_tags: list[str] = Field(default_factory=list)
    required_evidence_pmids: list[str] = Field(default_factory=list)
    required_asset_ids: list[str] = Field(default_factory=list)
    allowed_claim_categories: list[str] = Field(default_factory=list)
    blocks: list[ContentBlockSpec] = Field(default_factory=list)


class SectionSpec(BaseModel):
    """Planning-time specification for a top-level section of a document.

    Captures all editorial intent: purpose, evidence requirements, asset
    requirements, claim constraints, and ordering.  The generator transforms
    these into ``CanonicalSection`` instances.
    """

    section_id: str = Field(default_factory=_new_id)
    title: str
    purpose: str = Field(
        default="",
        description="Why this section exists in the document.",
    )
    section_type: str = Field(
        default="body",
        description="One of: body | intro | conclusion | appendix | references | toc",
    )
    target_word_count: int = 500
    target_page_budget: float = 1.0
    variant_tags: list[str] = Field(default_factory=list)
    required_evidence_pmids: list[str] = Field(default_factory=list)
    required_asset_ids: list[str] = Field(default_factory=list)
    required_table_ids: list[str] = Field(default_factory=list)
    required_figure_ids: list[str] = Field(default_factory=list)
    allowed_claim_categories: list[str] = Field(default_factory=list)
    blocks: list[ContentBlockSpec] = Field(default_factory=list)
    subsections: list[SubsectionSpec] = Field(default_factory=list)
    ordering: int = 0
    generation_notes: str = Field(
        default="",
        description="Hints and constraints passed verbatim to the generator.",
    )


class DocumentBlueprint(BaseModel):
    """Top-level editorial plan for a long document.

    A blueprint is created before generation begins.  It encodes every
    structural and evidence requirement so that the generator can be
    deterministic and reproducible across runs.
    """

    blueprint_id: str = Field(default_factory=_new_id)
    condition_slug: str
    variant: SectionVariant
    document_type: str = Field(
        description="e.g. 'handbook', 'protocol', 'assessment'",
    )
    title: str
    subtitle: str = ""
    target_page_count: int = 50
    target_word_count: int = 25000
    sections: list[SectionSpec] = Field(default_factory=list)
    required_asset_ids: list[str] = Field(default_factory=list)
    evidence_profile_id: Optional[str] = None
    created_at: str = Field(default_factory=_now_iso)
    version: str = "1.0"
    build_notes: str = ""


# ===========================================================================
# SECTION 2 — Asset tracking
# ===========================================================================


class AssetRecord(BaseModel):
    """Tracks a single renderable asset (table, figure, chart, image, etc.)
    through its full lifecycle from registration to validated output.

    The ``source_data`` dict is passed directly to the renderer identified
    by ``renderer_type``.  ``numbering_label`` (e.g. "Table 3", "Figure 7")
    is resolved during the assembly phase.
    """

    asset_id: str = Field(default_factory=_new_id)
    asset_type: AssetType
    condition_slug: str
    section_target: str = Field(
        description="section_id of the section where this asset appears.",
    )
    variant_tags: list[str] = Field(default_factory=list)
    renderer_type: str = Field(
        description="e.g. 'table_builder', 'qeeg_topomap', 'chart_builder', 'montage_diagram'",
    )
    source_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Input data passed verbatim to the renderer.",
    )
    caption: Optional[str] = None
    caption_short: Optional[str] = None
    output_path: Optional[str] = None
    status: AssetStatus = "pending"
    error_message: Optional[str] = None
    provenance: dict[str, Any] = Field(
        default_factory=dict,
        description="Build metadata (renderer version, params, timestamps, etc.).",
    )
    numbering_slot: Optional[int] = Field(
        default=None,
        description="Resolved during assembly — position within its asset type sequence.",
    )
    numbering_label: Optional[str] = Field(
        default=None,
        description="Human-readable label resolved during assembly, e.g. 'Table 3'.",
    )
    checksum: Optional[str] = None
    created_at: str = Field(default_factory=_now_iso)
    updated_at: str = Field(default_factory=_now_iso)


# ===========================================================================
# SECTION 3 — Fully resolved (post-generation) block / section / document
# ===========================================================================


class CanonicalBlock(BaseModel):
    """A fully resolved content block produced by the generator.

    Unlike ``ContentBlockSpec`` (which describes *what* to generate),
    ``CanonicalBlock`` contains the *actual* generated content and a
    reference to any embedded asset.
    """

    block_id: str = Field(default_factory=_new_id)
    block_type: BlockType = "text"
    heading: Optional[str] = None
    heading_level: int = 0
    content: Optional[str] = Field(
        default=None,
        description="Resolved text content for text/list/callout/heading blocks.",
    )
    asset_id: Optional[str] = None
    asset_record: Optional[AssetRecord] = Field(
        default=None,
        description="Embedded AssetRecord for convenience; avoids extra lookups.",
    )
    placeholder_resolved: bool = True
    page_break_before: bool = False
    landscape_hint: bool = False
    numbering_label: Optional[str] = None
    caption: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)


class CanonicalSection(BaseModel):
    """A fully generated document section, ready for assembly into a document.

    Sections are recursive: ``subsections`` holds child ``CanonicalSection``
    instances so arbitrarily deep document hierarchies are supported.
    ``word_count`` is populated by calling ``compute_word_count()``.
    """

    section_id: str = Field(default_factory=_new_id)
    title: str
    level: int = 1
    section_type: str = "body"
    blocks: list[CanonicalBlock] = Field(default_factory=list)
    subsections: list["CanonicalSection"] = Field(default_factory=list)
    ordering: int = 0
    variant_tags: list[str] = Field(default_factory=list)
    generation_metadata: dict[str, Any] = Field(default_factory=dict)
    validation_status: str = "pending"
    word_count: int = 0
    page_estimate: float = 0.0
    evidence_pmids: list[str] = Field(default_factory=list)

    def compute_word_count(self) -> int:
        """Count words in all text blocks in this section and its subsections.

        Counts words in the ``content`` field of every ``CanonicalBlock``
        whose ``block_type`` is ``"text"``, then recurses into each child
        ``CanonicalSection``.  The result is also stored in ``self.word_count``.

        Returns:
            Total integer word count for this section tree.
        """
        count = 0
        for block in self.blocks:
            if block.block_type == "text" and block.content:
                count += len(block.content.split())
        for subsection in self.subsections:
            count += subsection.compute_word_count()
        self.word_count = count
        return count


# ===========================================================================
# SECTION 4 — Standalone asset content models
# ===========================================================================


class CanonicalTable(BaseModel):
    """A structured tabular asset that can appear in a ``CanonicalBlock``.

    ``rows`` is a list of rows, each of which is a list of cell strings aligned
    positionally with ``headers``.  Can also be used directly as the
    ``source_data`` schema for an ``AssetRecord`` with
    ``renderer_type="table_builder"``.
    """

    table_id: str = Field(default_factory=_new_id)
    title: str
    headers: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)
    footer: Optional[str] = None
    landscape: bool = False
    source_data_ref: Optional[str] = Field(
        default=None,
        description="Optional reference to an upstream data source (e.g. a CSV path).",
    )
    evidence_pmids: list[str] = Field(default_factory=list)


class CanonicalFigure(BaseModel):
    """A figure asset — static image or programmatically rendered illustration.

    When ``renderer_type`` is set, the figure is generated by a renderer rather
    than loaded from ``image_path``.
    """

    figure_id: str = Field(default_factory=_new_id)
    title: str
    image_path: Optional[str] = None
    alt_text: str = ""
    source_data_ref: Optional[str] = None
    renderer_type: Optional[str] = None
    evidence_pmids: list[str] = Field(default_factory=list)


class CanonicalChart(BaseModel):
    """A data-driven chart asset.

    ``data`` is a free-form dict passed to the chart renderer; its exact
    structure depends on ``chart_type`` and the rendering library in use.
    """

    chart_id: str = Field(default_factory=_new_id)
    title: str
    chart_type: str = Field(
        description="One of: bar | line | scatter | heatmap | radar | pie",
    )
    data: dict[str, Any] = Field(default_factory=dict)
    x_label: str = ""
    y_label: str = ""
    output_path: Optional[str] = None


class CanonicalImage(BaseModel):
    """A raster or vector image asset referenced by path.

    ``width_hint`` and ``height_hint`` are optional layout hints in inches
    for the DOCX renderer.
    """

    image_id: str = Field(default_factory=_new_id)
    title: str
    source_path: str
    alt_text: str = ""
    width_hint: Optional[float] = Field(
        default=None,
        description="Hint for rendered width in inches.",
    )
    height_hint: Optional[float] = Field(
        default=None,
        description="Hint for rendered height in inches.",
    )


# ===========================================================================
# SECTION 5 — Bibliography / citations
# ===========================================================================


class CanonicalCitation(BaseModel):
    """A single bibliographic citation used in the document.

    ``reference_number`` is assigned during assembly when the citation list
    is finalised and numbered.  Either ``pmid`` or ``doi`` (or both) should
    be provided to ensure traceability.
    """

    citation_id: str = Field(default_factory=_new_id)
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors_short: str = Field(
        description="Short author string, e.g. 'Smith et al.'",
    )
    year: Optional[int] = None
    journal: Optional[str] = None
    reference_number: Optional[int] = Field(
        default=None,
        description="Assigned during assembly when citations are numbered.",
    )


# ===========================================================================
# SECTION 6 — QA models
# ===========================================================================


class QAValidationIssue(BaseModel):
    """A single validation finding from one validator pass.

    ``severity`` controls pipeline behaviour: ``"block"`` prevents export,
    ``"warning"`` allows export with a flag, ``"info"`` is informational only.
    ``auto_fixable`` signals that the issue can be remediated programmatically
    without human review.
    """

    issue_id: str = Field(default_factory=_new_id)
    validator_id: str
    severity: ValidationSeverity
    category: str
    message: str
    location: str = Field(
        default="",
        description="section_id or asset_id identifying where the issue was found.",
    )
    context: dict[str, Any] = Field(default_factory=dict)
    auto_fixable: bool = False


class QAValidationResult(BaseModel):
    """The aggregated result from a single named validator.

    One ``QAValidationResult`` is produced per validator per document run.
    ``passed`` is ``True`` only when there are no ``"block"``-severity issues.
    """

    result_id: str = Field(default_factory=_new_id)
    validator_id: str
    document_id: str
    condition_slug: str
    passed: bool
    issues: list[QAValidationIssue] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now_iso)
    duration_seconds: float = 0.0


class DocumentQAReport(BaseModel):
    """Aggregated QA report across all validators for one document.

    ``overall_passed`` is ``True`` only when every constituent
    ``QAValidationResult`` has ``passed=True``.  Use ``compute_counts()``
    after all validator results have been attached to refresh the
    ``block_count``, ``warning_count``, and ``info_count`` fields.
    """

    report_id: str = Field(default_factory=_new_id)
    document_id: str
    condition_slug: str
    variant: str
    validator_results: list[QAValidationResult] = Field(default_factory=list)
    overall_passed: bool = False
    block_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    created_at: str = Field(default_factory=_now_iso)

    def compute_counts(self) -> None:
        """Recompute ``block_count``, ``warning_count``, and ``info_count``
        from all issues across every ``QAValidationResult``, and update
        ``overall_passed`` accordingly.

        Call this method whenever a new ``QAValidationResult`` is appended
        so the report totals stay in sync.
        """
        blocks = 0
        warnings = 0
        infos = 0
        for result in self.validator_results:
            for issue in result.issues:
                if issue.severity == "block":
                    blocks += 1
                elif issue.severity == "warning":
                    warnings += 1
                elif issue.severity == "info":
                    infos += 1
        self.block_count = blocks
        self.warning_count = warnings
        self.info_count = infos
        self.overall_passed = (
            all(r.passed for r in self.validator_results)
            if self.validator_results
            else False
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialise the report to a plain Python dict for JSON output.

        Returns:
            A ``dict`` produced by ``model_dump()``, safe for
            ``json.dumps()``.
        """
        return self.model_dump()


# ===========================================================================
# SECTION 7 — Assembly provenance
# ===========================================================================


class AssemblyProvenance(BaseModel):
    """Full audit trail for one document assembly run.

    Every stage of the pipeline (section generation, asset generation,
    assembly, QA) appends structured log entries to the corresponding
    ``_log`` lists.  This allows post-hoc debugging and reproducibility
    analysis without requiring access to the original inputs.
    """

    provenance_id: str = Field(default_factory=_new_id)
    document_id: str
    blueprint_id: Optional[str] = None
    condition_slug: str
    variant: str
    created_at: str = Field(default_factory=_now_iso)
    section_generation_log: list[dict[str, Any]] = Field(default_factory=list)
    asset_generation_log: list[dict[str, Any]] = Field(default_factory=list)
    assembly_log: list[dict[str, Any]] = Field(default_factory=list)
    qa_results: dict[str, Any] = Field(default_factory=dict)
    output_paths: dict[str, Any] = Field(default_factory=dict)
    build_duration_seconds: float = 0.0
    errors: list[str] = Field(default_factory=list)


# ===========================================================================
# SECTION 8 — Canonical document (root model)
# ===========================================================================


class CanonicalDocument(BaseModel):
    """Root model representing a fully assembled long document.

    This is the primary output of the pipeline.  It aggregates all sections,
    assets, citations, appendices, and QA metadata for a single document
    variant.  Helper methods support common queries during assembly and
    post-processing.
    """

    document_id: str = Field(default_factory=_new_id)
    condition_slug: str
    variant: SectionVariant
    document_type: str
    title: str
    subtitle: str = ""
    version: str = "1.0"
    sections: list[CanonicalSection] = Field(default_factory=list)
    assets: list[AssetRecord] = Field(default_factory=list)
    references: list[CanonicalCitation] = Field(default_factory=list)
    appendices: list[CanonicalSection] = Field(default_factory=list)
    toc_entries: list[dict[str, Any]] = Field(
        default_factory=list,
        description=(
            'Table of contents entries, each: '
            '{"title": str, "level": int, "section_id": str, "page_hint": int|None}'
        ),
    )
    qa_status: AssemblyStatus = "pending"
    assembly_provenance: Optional[AssemblyProvenance] = None
    created_at: str = Field(default_factory=_now_iso)
    qa_report: Optional[DocumentQAReport] = None

    # ------------------------------------------------------------------
    # Word-count
    # ------------------------------------------------------------------

    def total_word_count(self) -> int:
        """Return the sum of word counts across all top-level sections.

        Calls ``compute_word_count()`` on every section so the stored counts
        are always up to date before summing.

        Returns:
            Total word count as an integer.
        """
        total = 0
        for section in self.sections:
            total += section.compute_word_count()
        return total

    # ------------------------------------------------------------------
    # Section lookup
    # ------------------------------------------------------------------

    def get_section(self, section_id: str) -> Optional[CanonicalSection]:
        """Find a ``CanonicalSection`` by ``section_id`` with recursive search.

        Searches top-level sections, then recursively descends into
        ``subsections`` and ``appendices``.

        Args:
            section_id: The UUID string of the target section.

        Returns:
            The matching ``CanonicalSection``, or ``None`` if not found.
        """
        def _search(sections: list[CanonicalSection]) -> Optional[CanonicalSection]:
            for section in sections:
                if section.section_id == section_id:
                    return section
                found = _search(section.subsections)
                if found is not None:
                    return found
            return None

        result = _search(self.sections)
        if result is None:
            result = _search(self.appendices)
        return result

    # ------------------------------------------------------------------
    # Asset lookup
    # ------------------------------------------------------------------

    def get_asset(self, asset_id: str) -> Optional[AssetRecord]:
        """Find an ``AssetRecord`` by ``asset_id``.

        Args:
            asset_id: The UUID string of the target asset.

        Returns:
            The matching ``AssetRecord``, or ``None`` if not found.
        """
        for asset in self.assets:
            if asset.asset_id == asset_id:
                return asset
        return None

    # ------------------------------------------------------------------
    # Placeholder diagnostics
    # ------------------------------------------------------------------

    def unresolved_placeholders(self) -> list[str]:
        """Return ``block_id`` values for all blocks where ``placeholder_resolved=False``.

        Recursively walks all sections (including subsections and appendices).

        Returns:
            A list of ``block_id`` strings for unresolved placeholder blocks.
        """
        unresolved: list[str] = []

        def _collect(sections: list[CanonicalSection]) -> None:
            for section in sections:
                for block in section.blocks:
                    if not block.placeholder_resolved:
                        unresolved.append(block.block_id)
                _collect(section.subsections)

        _collect(self.sections)
        _collect(self.appendices)
        return unresolved

    # ------------------------------------------------------------------
    # Asset reference collection
    # ------------------------------------------------------------------

    def all_asset_ids(self) -> list[str]:
        """Collect all unique ``asset_id`` references from all blocks.

        Scans every block in the document (sections, subsections, appendices)
        and returns a deduplicated list of non-null ``asset_id`` values.

        Returns:
            A list of unique asset ID strings referenced by blocks.
        """
        seen: set[str] = set()
        result: list[str] = []

        def _collect(sections: list[CanonicalSection]) -> None:
            for section in sections:
                for block in section.blocks:
                    if block.asset_id and block.asset_id not in seen:
                        seen.add(block.asset_id)
                        result.append(block.asset_id)
                _collect(section.subsections)

        _collect(self.sections)
        _collect(self.appendices)
        return result

    # ------------------------------------------------------------------
    # TOC generation
    # ------------------------------------------------------------------

    def build_toc(self) -> list[dict[str, Any]]:
        """Generate ``toc_entries`` from the current section tree.

        Walks all top-level sections and their subsections in order,
        producing one TOC entry per section with ``title``, ``level``,
        ``section_id``, and ``page_hint`` (always ``None`` here — actual
        page numbers are resolved by the DOCX renderer after layout).

        The generated list is also stored in ``self.toc_entries``.

        Returns:
            The updated ``toc_entries`` list.
        """
        entries: list[dict[str, Any]] = []

        def _walk(sections: list[CanonicalSection]) -> None:
            for section in sorted(sections, key=lambda s: s.ordering):
                entries.append(
                    {
                        "title": section.title,
                        "level": section.level,
                        "section_id": section.section_id,
                        "page_hint": None,
                    }
                )
                _walk(section.subsections)

        _walk(self.sections)
        self.toc_entries = entries
        return entries


# ===========================================================================
# Forward-reference resolution
# ===========================================================================

CanonicalSection.model_rebuild()
CanonicalDocument.model_rebuild()
DocumentQAReport.model_rebuild()
AssemblyProvenance.model_rebuild()
DocumentBlueprint.model_rebuild()
