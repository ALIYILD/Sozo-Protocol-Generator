"""Section-level generator for the SOZO long-document production pipeline.

Transforms SectionSpec and SubsectionSpec planning objects into fully populated
CanonicalSection instances. Works section-by-section; each section independently
generates its blocks via BlockGenerator.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from ..schemas.canonical import CanonicalBlock, CanonicalSection, ContentBlockSpec, SectionSpec, SubsectionSpec
from ..schemas.condition import ConditionSchema
from .block_generator import BlockGenerator

logger = logging.getLogger(__name__)


class SectionGenerator:
    """Generates a CanonicalSection from a SectionSpec.

    Works section-by-section, not whole-document-at-once.
    Each section independently generates its blocks.
    """

    def __init__(self, asset_registry: Optional[Any] = None) -> None:
        self.block_generator = BlockGenerator()
        self.asset_registry = asset_registry

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_section(
        self,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalSection:
        """Generate a top-level CanonicalSection from a SectionSpec.

        Steps:
        1. Generate all blocks listed in spec.blocks
        2. Generate all subsections recursively
        3. Compute word count
        4. Collect evidence PMIDs from condition.references
        5. Return populated CanonicalSection
        """
        # 1. Generate blocks
        blocks = self._generate_blocks(spec.blocks, condition, variant)

        # 2. Generate subsections
        subsections: list[CanonicalSection] = []
        for i, sub_spec in enumerate(spec.subsections):
            sub_section = self.generate_subsection(sub_spec, condition, variant)
            sub_section.ordering = i
            subsections.append(sub_section)

        # 3. Assemble section
        section = CanonicalSection(
            section_id=spec.section_id,
            title=spec.title,
            level=1,
            section_type=spec.section_type,
            blocks=blocks,
            subsections=subsections,
            ordering=spec.ordering,
            variant_tags=list(spec.variant_tags),
            generation_metadata={
                "spec_id": spec.section_id,
                "variant": variant,
                "condition_slug": condition.slug,
                "purpose": spec.purpose,
            },
            validation_status="pending",
        )

        # 4. Compute word count
        section.compute_word_count()

        # 5. Collect PMIDs
        section.evidence_pmids = self._extract_pmids_from_condition(
            condition,
            max_pmids=max(5, len(spec.required_evidence_pmids)),
        )

        logger.debug(
            "SectionGenerator: generated section '%s' — %d blocks, %d subsections, %d words.",
            spec.title,
            len(blocks),
            len(subsections),
            section.word_count,
        )
        return section

    def generate_subsection(
        self,
        spec: SubsectionSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalSection:
        """Generate a subsection (level 2+) from a SubsectionSpec."""
        blocks = self._generate_blocks(spec.blocks, condition, variant)

        sub = CanonicalSection(
            section_id=spec.subsection_id,
            title=spec.title,
            level=2,
            section_type="body",
            blocks=blocks,
            subsections=[],
            variant_tags=list(spec.variant_tags),
            generation_metadata={
                "spec_id": spec.subsection_id,
                "variant": variant,
                "condition_slug": condition.slug,
                "purpose": spec.purpose,
            },
            validation_status="pending",
        )

        sub.compute_word_count()
        sub.evidence_pmids = self._extract_pmids_from_condition(condition, max_pmids=3)

        logger.debug(
            "SectionGenerator: generated subsection '%s' — %d blocks, %d words.",
            spec.title,
            len(blocks),
            sub.word_count,
        )
        return sub

    def repair_section(
        self,
        section: CanonicalSection,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
        issues: Optional[list] = None,
    ) -> CanonicalSection:
        """Repair / regenerate a section that failed QA.

        If issues is provided, focuses repair on those issues.
        Currently re-generates from spec. Future: targeted repairs.
        """
        logger.info(
            "SectionGenerator.repair_section: re-generating section '%s' (issues: %s).",
            section.title,
            [getattr(i, "category", str(i)) for i in (issues or [])],
        )
        repaired = self.generate_section(spec, condition, variant)
        # Preserve original section_id so upstream references remain valid
        repaired.section_id = section.section_id
        repaired.generation_metadata["repaired"] = True
        repaired.generation_metadata["repair_issues"] = [
            getattr(i, "category", str(i)) for i in (issues or [])
        ]
        return repaired

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _generate_blocks(
        self,
        block_specs: list[ContentBlockSpec],
        condition: ConditionSchema,
        variant: str,
    ) -> list[CanonicalBlock]:
        """Generate all blocks from a list of ContentBlockSpec objects."""
        blocks: list[CanonicalBlock] = []
        for bspec in block_specs:
            # Skip blocks that are tagged for a different variant
            if bspec.variant_tags and variant not in bspec.variant_tags:
                logger.debug(
                    "SectionGenerator: skipping block '%s' (variant_tags=%s, current=%s).",
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
                    "SectionGenerator: block generation failed for '%s': %s",
                    bspec.block_id,
                    exc,
                    exc_info=True,
                )
                # Emit a safe fallback placeholder so the section is still usable
                blocks.append(
                    CanonicalBlock(
                        block_id=bspec.block_id,
                        block_type="text",
                        heading=bspec.heading,
                        content=f"[Generation error: {exc}]",
                        placeholder_resolved=False,
                        generation_metadata={"error": str(exc), "content_hint": bspec.content_hint},
                    )
                )
        return blocks

    def _extract_pmids_from_condition(
        self,
        condition: ConditionSchema,
        max_pmids: int = 5,
    ) -> list[str]:
        """Extract relevant PMIDs from condition.references."""
        pmids: list[str] = []
        for ref in condition.references:
            pmid = ref.get("pmid", "")
            if pmid and pmid not in pmids:
                pmids.append(str(pmid))
            if len(pmids) >= max_pmids:
                break
        return pmids
