"""Higher-level LLM section pipeline for the SOZO long-document production pipeline.

Generates all sections in a DocumentBlueprint using LLM block generation,
with progress tracking, per-section error isolation, and optional disk caching
to avoid regenerating already-completed sections.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Callable, Optional

from ..schemas.canonical import CanonicalSection, DocumentBlueprint, SectionSpec
from ..schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)


class LLMSectionPipeline:
    """
    Generates all sections in a DocumentBlueprint using LLM block generation.

    Features:
    - Progress callback for Streamlit UI
    - Per-section error isolation (one section failure never aborts the pipeline)
    - Section caching (avoid regenerating already-done sections between runs)
    - Batch status reporting via generate_all return value
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-haiku-4-5-20251001",
        cache_dir: Optional[str] = None,
    ) -> None:
        from .section_generator import SectionGenerator
        from .llm_block_generator import LLMBlockGenerator

        self.llm_gen = LLMBlockGenerator(api_key=api_key, model=model)
        self.section_generator = SectionGenerator(llm_block_generator=self.llm_gen)
        self.cache_dir = cache_dir
        self._model = model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_all(
        self,
        blueprint: DocumentBlueprint,
        condition: ConditionSchema,
        variant: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> list[CanonicalSection]:
        """
        Generate all sections in the blueprint.

        Args:
            blueprint: The DocumentBlueprint containing SectionSpec objects.
            condition: Verified ConditionSchema — all clinical data sourced from here.
            variant: "fellow" or "partners".
            progress_callback: Optional callable(section_num, total, section_title)
                called after each section is generated.  Intended for Streamlit
                progress bars or similar UI feedback.

        Returns:
            A list of CanonicalSection objects (one per blueprint section).
            Sections that fail are replaced by a minimal placeholder section so
            the pipeline always returns a complete list.
        """
        sections: list[CanonicalSection] = []
        total = len(blueprint.sections)

        for i, spec in enumerate(blueprint.sections, start=1):
            try:
                section = self.generate_section(spec, condition, variant)
            except Exception as exc:
                logger.error(
                    "LLMSectionPipeline: section '%s' failed unexpectedly: %s",
                    spec.title,
                    exc,
                    exc_info=True,
                )
                # Emit a safe placeholder section so the document is still assembl-able
                section = CanonicalSection(
                    section_id=spec.section_id,
                    title=spec.title,
                    level=1,
                    section_type=spec.section_type,
                    blocks=[],
                    subsections=[],
                    ordering=spec.ordering,
                    variant_tags=list(spec.variant_tags),
                    generation_metadata={
                        "error": str(exc),
                        "variant": variant,
                        "condition_slug": condition.slug,
                        "llm_pipeline_error": True,
                    },
                    validation_status="failed",
                )

            sections.append(section)

            if progress_callback is not None:
                try:
                    progress_callback(i, total, spec.title)
                except Exception:
                    pass  # Never let UI callback break the pipeline

        logger.info(
            "LLMSectionPipeline: generated %d/%d sections for '%s' [%s].",
            len(sections),
            total,
            condition.display_name,
            variant,
        )
        return sections

    def generate_section(
        self,
        spec: SectionSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalSection:
        """
        Generate a single section, using cache when available.

        Cache is keyed on (spec.section_id, condition.slug, variant, model).
        If a cached version exists on disk it is returned immediately.
        On successful generation the result is written to cache.
        """
        if self.cache_dir:
            key = self._cache_key(spec, condition.slug, variant)
            cached = self._load_cached(key)
            if cached is not None:
                logger.debug(
                    "LLMSectionPipeline: cache hit for section '%s'.", spec.title
                )
                return cached

        section = self.section_generator.generate_section(spec, condition, variant)

        if self.cache_dir:
            try:
                self._save_cached(key, section)  # type: ignore[possibly-undefined]
            except Exception as exc:
                logger.warning(
                    "LLMSectionPipeline: failed to cache section '%s': %s",
                    spec.title,
                    exc,
                )

        return section

    # ------------------------------------------------------------------
    # Caching helpers
    # ------------------------------------------------------------------

    def _cache_key(self, spec: SectionSpec, condition_slug: str, variant: str) -> str:
        """Build a deterministic cache key from section identity and model."""
        raw = f"{spec.section_id}:{condition_slug}:{variant}:{self._model}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _load_cached(self, key: str) -> Optional[CanonicalSection]:
        """Load a cached CanonicalSection from disk, or None if absent/invalid."""
        if not self.cache_dir:
            return None
        path = os.path.join(self.cache_dir, f"{key}.json")
        if not os.path.isfile(path):
            return None
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            return CanonicalSection.model_validate(data)
        except Exception as exc:
            logger.warning(
                "LLMSectionPipeline: cache load failed for key '%s': %s", key, exc
            )
            return None

    def _save_cached(self, key: str, section: CanonicalSection) -> None:
        """Persist a CanonicalSection to disk cache."""
        if not self.cache_dir:
            return
        os.makedirs(self.cache_dir, exist_ok=True)
        path = os.path.join(self.cache_dir, f"{key}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(section.model_dump(mode="json"), fh, indent=2, ensure_ascii=False)
        logger.debug("LLMSectionPipeline: cached section to '%s'.", path)
