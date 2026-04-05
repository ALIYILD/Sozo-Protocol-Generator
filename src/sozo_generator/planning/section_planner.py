"""SOZO Generator — section planner.

Converts a list of outline-entry dicts produced by
:class:`~sozo_generator.planning.outline_planner.OutlinePlanner` into fully
populated :class:`~sozo_generator.schemas.canonical.SectionSpec` objects with
``ContentBlockSpec`` lists, ``SubsectionSpec`` lists, required evidence PMIDs,
and required asset IDs.

No external API calls are made here; all planning logic is deterministic.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from sozo_generator.schemas.canonical import (
    ContentBlockSpec,
    SectionSpec,
    SubsectionSpec,
)
from sozo_generator.schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Maximum number of PMIDs to attach to a single section from the condition's
# reference list.
_MAX_PMIDS_PER_SECTION: int = 5

# Claim categories that imply the section requires evidence PMIDs
_EVIDENCE_HUNGRY_CATEGORIES: frozenset[str] = frozenset(
    {
        "pathophysiology",
        "brain_regions",
        "network_involvement",
        "stimulation_targets",
        "stimulation_parameters",
        "modality_rationale",
        "assessment_tools",
        "safety",
        "contraindications",
        "responder_criteria",
    }
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_text_block(
    content_hint: str,
    target_word_count: int = 0,
    variant_tags: Optional[list[str]] = None,
) -> ContentBlockSpec:
    """Create a plain text ``ContentBlockSpec``."""
    return ContentBlockSpec(
        block_type="text",
        content_hint=content_hint,
        target_word_count=target_word_count,
        variant_tags=variant_tags or [],
        placeholder=False,
    )


def _make_table_block(
    condition_slug: str,
    table_name: str,
    variant_tags: Optional[list[str]] = None,
) -> ContentBlockSpec:
    """Create a table placeholder ``ContentBlockSpec``."""
    asset_id = f"asset_{condition_slug}_{table_name}"
    return ContentBlockSpec(
        block_type="table",
        asset_id=asset_id,
        content_hint=f"Build {table_name} table",
        placeholder=True,
        variant_tags=variant_tags or [],
    )


def _make_figure_block(
    condition_slug: str,
    figure_name: str,
    variant_tags: Optional[list[str]] = None,
) -> ContentBlockSpec:
    """Create a figure placeholder ``ContentBlockSpec``."""
    asset_id = f"asset_{condition_slug}_{figure_name}"
    return ContentBlockSpec(
        block_type="figure",
        asset_id=asset_id,
        content_hint=f"Render {figure_name}",
        placeholder=True,
        variant_tags=variant_tags or [],
    )


def _extract_pmids(
    condition: Optional[ConditionSchema],
    allowed_categories: list[str],
    max_pmids: int = _MAX_PMIDS_PER_SECTION,
) -> list[str]:
    """Pull up to *max_pmids* PMIDs from *condition.references*.

    Prefers references whose ``categories`` field overlaps with
    *allowed_categories*; falls back to any PMID in the reference list when
    there are fewer matches than requested.

    Returns an empty list when *condition* is ``None`` or has no references.
    """
    if condition is None or not condition.references:
        return []

    refs = condition.references
    pmids: list[str] = []

    # First pass: category-matched references
    for ref in refs:
        if len(pmids) >= max_pmids:
            break
        pmid = ref.get("pmid") or ref.get("PMID") or ref.get("id")
        if not pmid:
            continue
        pmid = str(pmid).strip()
        if not pmid:
            continue
        cats = ref.get("categories", []) or ref.get("category", [])
        if isinstance(cats, str):
            cats = [cats]
        if any(c in allowed_categories for c in cats):
            pmids.append(pmid)

    # Second pass: fill remaining slots from any reference
    if len(pmids) < max_pmids:
        for ref in refs:
            if len(pmids) >= max_pmids:
                break
            pmid = ref.get("pmid") or ref.get("PMID") or ref.get("id")
            if not pmid:
                continue
            pmid = str(pmid).strip()
            if pmid and pmid not in pmids:
                pmids.append(pmid)

    return pmids[:max_pmids]


def _build_subsection_specs(
    subsection_stubs: list[dict[str, Any]],
    condition_slug: str,
    variant: str,
    condition: Optional[ConditionSchema],
    variant_tags: list[str],
) -> list[SubsectionSpec]:
    """Convert subsection stub dicts into ``SubsectionSpec`` objects."""
    specs: list[SubsectionSpec] = []
    for stub in subsection_stubs:
        title = stub.get("title", "Untitled Subsection")
        purpose = stub.get("purpose", "")
        target_wc = stub.get("target_word_count", 300)

        # Attach a single text block to each subsection
        block = _make_text_block(
            content_hint=purpose or f"Write content for: {title}",
            target_word_count=target_wc,
            variant_tags=variant_tags,
        )

        spec = SubsectionSpec(
            title=title,
            purpose=purpose,
            target_word_count=target_wc,
            variant_tags=variant_tags,
            blocks=[block],
            required_evidence_pmids=[],
            allowed_claim_categories=[],
        )
        specs.append(spec)
    return specs


# ---------------------------------------------------------------------------
# SectionPlanner
# ---------------------------------------------------------------------------

class SectionPlanner:
    """Converts outline entries into full ``SectionSpec`` objects with blocks.

    This class is stateless; call :meth:`build_section_spec` or
    :meth:`build_all_section_specs` directly.
    """

    def build_section_spec(
        self,
        outline_entry: dict[str, Any],
        condition_slug: str,
        variant: str,
        condition: Optional[ConditionSchema] = None,
    ) -> SectionSpec:
        """Convert a single outline-entry dict into a ``SectionSpec``.

        The resulting spec includes:

        - One ``ContentBlockSpec`` of type ``"text"`` for the narrative prose,
          targeting the section's word count.
        - One ``ContentBlockSpec`` of type ``"table"`` for each entry in
          ``required_tables``.
        - One ``ContentBlockSpec`` of type ``"figure"`` for each entry in
          ``required_figures``.
        - ``SubsectionSpec`` objects derived from the ``subsections`` stubs.
        - Up to :data:`_MAX_PMIDS_PER_SECTION` evidence PMIDs pulled from
          *condition.references* when the section has evidence-hungry claim
          categories.
        - ``required_asset_ids`` populated from all table and figure blocks.

        Args:
            outline_entry: A single dict as returned by
                :class:`~sozo_generator.planning.outline_planner.OutlinePlanner`.
            condition_slug: Condition slug string (used to construct asset IDs).
            variant: ``"fellow"`` or ``"partners"``.
            condition: Optional :class:`~sozo_generator.schemas.condition.ConditionSchema`
                used to pull evidence PMIDs.  If ``None``, no PMIDs are attached.

        Returns:
            A fully populated :class:`~sozo_generator.schemas.canonical.SectionSpec`.
        """
        title = outline_entry.get("title", "Untitled Section")
        purpose = outline_entry.get("purpose", "")
        section_type = outline_entry.get("section_type", "body")
        target_wc = outline_entry.get("target_word_count", 0)
        target_page_budget = outline_entry.get("target_page_budget", 1.0)
        ordering = outline_entry.get("ordering", 0)
        variant_tags: list[str] = outline_entry.get("variant_tags", [])
        required_tables: list[str] = outline_entry.get("required_tables", [])
        required_figures: list[str] = outline_entry.get("required_figures", [])
        allowed_categories: list[str] = outline_entry.get("allowed_claim_categories", [])
        subsection_stubs: list[dict] = outline_entry.get("subsections", [])

        blocks: list[ContentBlockSpec] = []
        required_asset_ids: list[str] = []
        required_table_ids: list[str] = []
        required_figure_ids: list[str] = []

        # ---- Narrative text block (skip for structural sections) ----------
        if section_type in ("body", "intro") and target_wc > 0:
            blocks.append(
                _make_text_block(
                    content_hint=purpose or f"Write the '{title}' section.",
                    target_word_count=target_wc,
                    variant_tags=variant_tags,
                )
            )

        # ---- Table placeholder blocks ------------------------------------
        for table_name in required_tables:
            block = _make_table_block(condition_slug, table_name, variant_tags)
            blocks.append(block)
            if block.asset_id:
                required_asset_ids.append(block.asset_id)
                required_table_ids.append(block.asset_id)

        # ---- Figure placeholder blocks -----------------------------------
        for figure_name in required_figures:
            block = _make_figure_block(condition_slug, figure_name, variant_tags)
            blocks.append(block)
            if block.asset_id:
                required_asset_ids.append(block.asset_id)
                required_figure_ids.append(block.asset_id)

        # ---- Evidence PMIDs -----------------------------------------------
        evidence_pmids: list[str] = []
        needs_evidence = bool(
            set(allowed_categories) & _EVIDENCE_HUNGRY_CATEGORIES
        )
        if needs_evidence:
            evidence_pmids = _extract_pmids(condition, allowed_categories)

        # ---- Subsections --------------------------------------------------
        subsection_specs = _build_subsection_specs(
            subsection_stubs,
            condition_slug=condition_slug,
            variant=variant,
            condition=condition,
            variant_tags=variant_tags,
        )

        # ---- Build generation notes ------------------------------------
        generation_notes_parts: list[str] = []
        if variant == "fellow":
            generation_notes_parts.append(
                "Audience: fellows — use accessible clinical language, avoid advanced neuroscience jargon."
            )
        else:
            generation_notes_parts.append(
                "Audience: partners — include advanced FNON framework references and multimodal considerations."
            )
        if allowed_categories:
            generation_notes_parts.append(
                f"Allowed claim categories: {', '.join(allowed_categories)}."
            )
        if evidence_pmids:
            generation_notes_parts.append(
                f"Must cite PMIDs: {', '.join(evidence_pmids)}."
            )

        generation_notes = " ".join(generation_notes_parts)

        return SectionSpec(
            title=title,
            purpose=purpose,
            section_type=section_type,
            target_word_count=target_wc,
            target_page_budget=target_page_budget,
            ordering=ordering,
            variant_tags=variant_tags,
            blocks=blocks,
            subsections=subsection_specs,
            required_evidence_pmids=evidence_pmids,
            required_asset_ids=required_asset_ids,
            required_table_ids=required_table_ids,
            required_figure_ids=required_figure_ids,
            allowed_claim_categories=allowed_categories,
            generation_notes=generation_notes,
        )

    def build_all_section_specs(
        self,
        outline: list[dict[str, Any]],
        condition_slug: str,
        variant: str,
        condition: Optional[ConditionSchema] = None,
    ) -> list[SectionSpec]:
        """Build all ``SectionSpec`` objects from a complete outline.

        Args:
            outline: Full outline list as returned by
                :class:`~sozo_generator.planning.outline_planner.OutlinePlanner`.
            condition_slug: Condition slug string.
            variant: ``"fellow"`` or ``"partners"``.
            condition: Optional ``ConditionSchema`` for evidence PMID extraction.

        Returns:
            An ordered list of ``SectionSpec`` objects, one per outline entry.
        """
        specs: list[SectionSpec] = []
        for entry in outline:
            try:
                spec = self.build_section_spec(
                    outline_entry=entry,
                    condition_slug=condition_slug,
                    variant=variant,
                    condition=condition,
                )
                specs.append(spec)
            except Exception as exc:
                logger.warning(
                    "Failed to build SectionSpec for '%s': %s",
                    entry.get("title", "?"),
                    exc,
                )
        return specs

    def get_required_asset_ids(self, section_spec: SectionSpec) -> list[str]:
        """Collect all unique asset IDs needed by a section.

        Unions the ``required_asset_ids`` at the section level with any
        ``asset_id`` values found on individual ``ContentBlockSpec`` instances
        in ``blocks`` and across all ``SubsectionSpec`` instances.

        Args:
            section_spec: A ``SectionSpec`` previously built by
                :meth:`build_section_spec`.

        Returns:
            A deduplicated list of asset ID strings.
        """
        seen: set[str] = set()
        result: list[str] = []

        def _add(asset_id: Optional[str]) -> None:
            if asset_id and asset_id not in seen:
                seen.add(asset_id)
                result.append(asset_id)

        for asset_id in section_spec.required_asset_ids:
            _add(asset_id)

        for block in section_spec.blocks:
            _add(block.asset_id)

        for subsection in section_spec.subsections:
            for asset_id in subsection.required_asset_ids:
                _add(asset_id)
            for block in subsection.blocks:
                _add(block.asset_id)

        return result
