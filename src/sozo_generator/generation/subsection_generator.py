"""Standalone subsection generator for the SOZO long-document production pipeline.

SubsectionGenerator can be called independently for partial regeneration of a
document, without needing a full SectionSpec context.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from ..schemas.canonical import CanonicalBlock, CanonicalSection, ContentBlockSpec, SubsectionSpec
from ..schemas.condition import ConditionSchema
from .block_generator import BlockGenerator

logger = logging.getLogger(__name__)


class SubsectionGenerator:
    """Generates subsections independently.

    Can be called standalone for partial regeneration without requiring a
    full SectionSpec. Delegates block generation to BlockGenerator.
    """

    def __init__(self, asset_registry: Optional[Any] = None) -> None:
        self.block_generator = BlockGenerator()
        self.asset_registry = asset_registry

    def generate(
        self,
        spec: SubsectionSpec,
        condition: ConditionSchema,
        variant: str,
        level: int = 2,
    ) -> CanonicalSection:
        """Generate a CanonicalSection (level >= 2) from a SubsectionSpec.

        Args:
            spec: The SubsectionSpec that describes what to generate.
            condition: The ConditionSchema providing source content.
            variant: Audience variant — "fellow" or "partners".
            level: Heading level for this subsection (default 2).

        Returns:
            A populated CanonicalSection with blocks, word count, and PMIDs.
        """
        blocks: list[CanonicalBlock] = []

        for bspec in spec.blocks:
            # Honour variant_tags filtering
            if bspec.variant_tags and variant not in bspec.variant_tags:
                logger.debug(
                    "SubsectionGenerator: skipping block '%s' (variant_tags=%s, current=%s).",
                    bspec.block_id,
                    bspec.variant_tags,
                    variant,
                )
                continue

            try:
                block = self.block_generator.generate(
                    spec=bspec,
                    condition=condition,
                    variant=variant,
                    asset_registry=self.asset_registry,
                )
                blocks.append(block)
            except Exception as exc:
                logger.warning(
                    "SubsectionGenerator: block generation failed for '%s': %s",
                    bspec.block_id,
                    exc,
                    exc_info=True,
                )
                blocks.append(
                    CanonicalBlock(
                        block_id=bspec.block_id,
                        block_type="text",
                        heading=bspec.heading,
                        content=f"[Generation error: {exc}]",
                        placeholder_resolved=False,
                        generation_metadata={
                            "error": str(exc),
                            "content_hint": bspec.content_hint,
                        },
                    )
                )

        section = CanonicalSection(
            section_id=spec.subsection_id,
            title=spec.title,
            level=level,
            section_type="body",
            blocks=blocks,
            subsections=[],
            variant_tags=list(spec.variant_tags),
            generation_metadata={
                "spec_id": spec.subsection_id,
                "variant": variant,
                "condition_slug": condition.slug,
                "purpose": spec.purpose,
                "generated_by": "SubsectionGenerator",
            },
            validation_status="pending",
        )

        section.compute_word_count()
        section.evidence_pmids = self._extract_pmids_from_condition(condition, max_pmids=3)

        logger.debug(
            "SubsectionGenerator: generated subsection '%s' — %d blocks, %d words.",
            spec.title,
            len(blocks),
            section.word_count,
        )
        return section

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_pmids_from_condition(
        self,
        condition: ConditionSchema,
        max_pmids: int = 3,
    ) -> list[str]:
        """Extract up to max_pmids PMIDs from condition.references."""
        pmids: list[str] = []
        for ref in condition.references:
            pmid = ref.get("pmid", "")
            if pmid and pmid not in pmids:
                pmids.append(str(pmid))
            if len(pmids) >= max_pmids:
                break
        return pmids
