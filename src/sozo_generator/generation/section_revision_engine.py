"""Section revision engine for the SOZO long-document production pipeline.

Handles targeted repair of individual sections based on QA feedback.
Supports full regeneration, block-level patching, block insertion, and
block removal, with full provenance tracking via generation_metadata.
"""
from __future__ import annotations

import copy
import logging
from typing import Any, Optional

from ..schemas.canonical import CanonicalBlock, CanonicalSection, SectionSpec
from ..schemas.condition import ConditionSchema
from .block_generator import BlockGenerator
from .section_generator import SectionGenerator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Issue category constants — used to dispatch repair strategies
# ---------------------------------------------------------------------------

_ISSUE_EMPTY_SECTION = "empty_section"
_ISSUE_WORD_COUNT_UNDERFLOW = "word_count_underflow"
_ISSUE_WORD_COUNT_OVERFLOW = "word_count_overflow"
_ISSUE_UNRESOLVED_PLACEHOLDER = "unresolved_placeholder"
_ISSUE_MISSING_ASSET = "missing_asset"


class SectionRevisionEngine:
    """Handles revision/repair of individual sections based on QA feedback.

    Supports:
    - Regenerate entire section
    - Patch specific blocks
    - Add missing content
    - Remove prohibited content
    """

    def __init__(self, section_generator: Optional[SectionGenerator] = None) -> None:
        self.section_generator = section_generator or SectionGenerator()

    # ------------------------------------------------------------------
    # Primary revision entry point
    # ------------------------------------------------------------------

    def revise(
        self,
        section: CanonicalSection,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
        qa_issues: list,  # list of QAValidationIssue dicts or objects
    ) -> CanonicalSection:
        """Apply revisions based on QA issues.

        Issue categories handled:
        - "empty_section"            → regenerate all blocks
        - "word_count_underflow"     → add more text blocks from spec
        - "word_count_overflow"      → trim longest text blocks
        - "unresolved_placeholder"   → re-generate the specific block
        - "missing_asset"            → mark block as needing asset
        - other / unrecognised       → re-generate entire section

        Returns revised CanonicalSection with generation_metadata tracking.
        """
        if not qa_issues:
            logger.debug("SectionRevisionEngine.revise: no issues, returning section unchanged.")
            return section

        categories = [_issue_category(issue) for issue in qa_issues]
        logger.info(
            "SectionRevisionEngine.revise: section '%s', issue categories: %s",
            section.title,
            categories,
        )

        # Work on a deep copy to avoid mutating the caller's object
        revised = _deep_copy_section(section)

        for issue in qa_issues:
            cat = _issue_category(issue)

            if cat == _ISSUE_EMPTY_SECTION:
                revised = self.section_generator.generate_section(spec, condition, variant)
                revised.section_id = section.section_id
                revised.generation_metadata["revision_reason"] = "empty_section"
                break  # Full regeneration supersedes other repairs

            elif cat == _ISSUE_WORD_COUNT_UNDERFLOW:
                revised = self._handle_underflow(revised, spec, condition, variant, issue)

            elif cat == _ISSUE_WORD_COUNT_OVERFLOW:
                revised = self._handle_overflow(revised, issue)

            elif cat == _ISSUE_UNRESOLVED_PLACEHOLDER:
                block_id = _issue_location(issue)
                if block_id:
                    revised = self._regenerate_block_in_section(
                        revised, block_id, spec, condition, variant
                    )
                else:
                    # No location info — regenerate all unresolved blocks
                    revised = self._regenerate_all_unresolved(revised, spec, condition, variant)

            elif cat == _ISSUE_MISSING_ASSET:
                block_id = _issue_location(issue)
                if block_id:
                    revised = self._mark_block_needs_asset(revised, block_id)

            else:
                # Unrecognised issue — full section regeneration as safe fallback
                logger.info(
                    "SectionRevisionEngine.revise: unrecognised issue category '%s', "
                    "regenerating full section.",
                    cat,
                )
                revised = self.section_generator.generate_section(spec, condition, variant)
                revised.section_id = section.section_id
                revised.generation_metadata["revision_reason"] = f"unrecognised_issue:{cat}"
                break

        # Recompute word count after all repairs
        revised.compute_word_count()

        # Append revision metadata
        existing = revised.generation_metadata.get("revisions", [])
        if isinstance(existing, list):
            existing.append({
                "issue_categories": categories,
                "variant": variant,
            })
        revised.generation_metadata["revisions"] = existing

        return revised

    # ------------------------------------------------------------------
    # Block-level operations (public, callable standalone)
    # ------------------------------------------------------------------

    def patch_block(
        self,
        section: CanonicalSection,
        block_id: str,
        new_content: str,
    ) -> CanonicalSection:
        """Replace the content of a specific block by block_id.

        Operates on a copy of the section. If block_id is not found in
        top-level blocks, searches subsections recursively.
        """
        revised = _deep_copy_section(section)
        patched = _patch_block_in_tree(revised, block_id, new_content)
        if not patched:
            logger.warning(
                "SectionRevisionEngine.patch_block: block '%s' not found in section '%s'.",
                block_id,
                section.section_id,
            )
        else:
            revised.compute_word_count()
        return revised

    def add_block(
        self,
        section: CanonicalSection,
        block: CanonicalBlock,
        position: int = -1,  # -1 = append
    ) -> CanonicalSection:
        """Insert a new block at position (-1 means append to end)."""
        revised = _deep_copy_section(section)
        if position == -1 or position >= len(revised.blocks):
            revised.blocks.append(block)
        else:
            revised.blocks.insert(position, block)
        revised.compute_word_count()
        revised.generation_metadata["block_added"] = block.block_id
        return revised

    def remove_block(
        self,
        section: CanonicalSection,
        block_id: str,
    ) -> CanonicalSection:
        """Remove a block by block_id (searches top-level blocks and subsections)."""
        revised = _deep_copy_section(section)
        removed = _remove_block_from_tree(revised, block_id)
        if not removed:
            logger.warning(
                "SectionRevisionEngine.remove_block: block '%s' not found in section '%s'.",
                block_id,
                section.section_id,
            )
        else:
            revised.compute_word_count()
            revised.generation_metadata["block_removed"] = block_id
        return revised

    # ------------------------------------------------------------------
    # Private repair strategies
    # ------------------------------------------------------------------

    def _handle_underflow(
        self,
        section: CanonicalSection,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
        issue: Any,
    ) -> CanonicalSection:
        """Add more text blocks to address word-count underflow.

        Regenerates the full section from spec so that all blocks are
        freshly populated. This is the most reliable way to address
        underflow without knowing which individual blocks were short.
        """
        logger.debug(
            "SectionRevisionEngine: handling word_count_underflow for '%s'.", section.title
        )
        regenerated = self.section_generator.generate_section(spec, condition, variant)
        regenerated.section_id = section.section_id
        regenerated.generation_metadata["revision_reason"] = "word_count_underflow"
        return regenerated

    def _handle_overflow(
        self,
        section: CanonicalSection,
        issue: Any,
    ) -> CanonicalSection:
        """Trim the longest text blocks to address word-count overflow.

        Trims greedily from the longest text block, removing trailing
        sentences until total word count is within a reasonable range
        relative to the section's word_count.
        """
        import re

        revised = _deep_copy_section(section)
        target = _issue_context_int(issue, "target_word_count", 0)
        if target <= 0:
            logger.debug(
                "SectionRevisionEngine: overflow issue has no target_word_count — skipping trim."
            )
            return revised

        def _trim_block(block: CanonicalBlock) -> None:
            if block.block_type != "text" or not block.content:
                return
            sentences = re.split(r"(?<=[.!?])\s+", block.content.strip())
            while len(sentences) > 2:
                wc = sum(len(s.split()) for s in sentences)
                if wc <= target:
                    break
                sentences.pop()
            block.content = " ".join(sentences)

        def _trim_tree(sec: CanonicalSection) -> None:
            for blk in sec.blocks:
                _trim_block(blk)
            for sub in sec.subsections:
                _trim_tree(sub)

        _trim_tree(revised)
        revised.compute_word_count()
        revised.generation_metadata["revision_reason"] = "word_count_overflow"
        return revised

    def _regenerate_block_in_section(
        self,
        section: CanonicalSection,
        block_id: str,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalSection:
        """Re-generate one block in the section by matching block_id against spec.blocks."""
        # Find the ContentBlockSpec for this block_id
        matching_spec = None
        for bspec in spec.blocks:
            if bspec.block_id == block_id:
                matching_spec = bspec
                break
        # Also search subsection specs
        if matching_spec is None:
            for sub_spec in spec.subsections:
                for bspec in sub_spec.blocks:
                    if bspec.block_id == block_id:
                        matching_spec = bspec
                        break
                if matching_spec is not None:
                    break

        if matching_spec is None:
            logger.warning(
                "SectionRevisionEngine: no spec found for block '%s', skipping re-generation.",
                block_id,
            )
            return section

        bg = self.section_generator.block_generator
        new_block = bg.generate(
            spec=matching_spec,
            condition=condition,
            variant=variant,
            asset_registry=self.section_generator.asset_registry,
        )
        section = self.patch_block(section, block_id, new_block.content or "")
        # Preserve all block metadata from the freshly generated block
        _replace_block_in_tree(section, block_id, new_block)
        return section

    def _regenerate_all_unresolved(
        self,
        section: CanonicalSection,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalSection:
        """Regenerate every block that has placeholder_resolved=False."""
        unresolved_ids = [
            b.block_id for b in section.blocks if not b.placeholder_resolved
        ]
        for block_id in unresolved_ids:
            section = self._regenerate_block_in_section(
                section, block_id, spec, condition, variant
            )
        return section

    def _mark_block_needs_asset(
        self,
        section: CanonicalSection,
        block_id: str,
    ) -> CanonicalSection:
        """Set placeholder_resolved=False on a block identified as missing an asset."""
        def _mark(sec: CanonicalSection) -> bool:
            for blk in sec.blocks:
                if blk.block_id == block_id:
                    blk.placeholder_resolved = False
                    blk.generation_metadata["missing_asset"] = True
                    return True
            for sub in sec.subsections:
                if _mark(sub):
                    return True
            return False

        revised = _deep_copy_section(section)
        found = _mark(revised)
        if not found:
            logger.warning(
                "SectionRevisionEngine._mark_block_needs_asset: block '%s' not found.",
                block_id,
            )
        return revised


# ---------------------------------------------------------------------------
# Module-level tree-manipulation helpers
# ---------------------------------------------------------------------------

def _deep_copy_section(section: CanonicalSection) -> CanonicalSection:
    """Return a deep copy of a CanonicalSection."""
    return section.model_copy(deep=True)


def _patch_block_in_tree(section: CanonicalSection, block_id: str, new_content: str) -> bool:
    """Replace block content in-place; returns True if found."""
    for blk in section.blocks:
        if blk.block_id == block_id:
            blk.content = new_content
            blk.placeholder_resolved = True
            return True
    for sub in section.subsections:
        if _patch_block_in_tree(sub, block_id, new_content):
            return True
    return False


def _replace_block_in_tree(
    section: CanonicalSection, block_id: str, new_block: CanonicalBlock
) -> bool:
    """Replace an entire CanonicalBlock in-place by block_id; returns True if found."""
    for i, blk in enumerate(section.blocks):
        if blk.block_id == block_id:
            section.blocks[i] = new_block
            return True
    for sub in section.subsections:
        if _replace_block_in_tree(sub, block_id, new_block):
            return True
    return False


def _remove_block_from_tree(section: CanonicalSection, block_id: str) -> bool:
    """Remove a block in-place by block_id; returns True if found."""
    for i, blk in enumerate(section.blocks):
        if blk.block_id == block_id:
            section.blocks.pop(i)
            return True
    for sub in section.subsections:
        if _remove_block_from_tree(sub, block_id):
            return True
    return False


# ---------------------------------------------------------------------------
# QA issue accessors
# ---------------------------------------------------------------------------

def _issue_category(issue: Any) -> str:
    """Extract category from a QAValidationIssue object or dict."""
    if isinstance(issue, dict):
        return issue.get("category", "")
    return getattr(issue, "category", "")


def _issue_location(issue: Any) -> str:
    """Extract location (block_id or section_id) from a QAValidationIssue."""
    if isinstance(issue, dict):
        return issue.get("location", "")
    return getattr(issue, "location", "")


def _issue_context_int(issue: Any, key: str, default: int) -> int:
    """Extract an integer value from the issue context dict."""
    if isinstance(issue, dict):
        ctx = issue.get("context", {})
    else:
        ctx = getattr(issue, "context", {}) or {}
    try:
        return int(ctx.get(key, default))
    except (TypeError, ValueError):
        return default
