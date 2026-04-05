"""SOZO Generator — document blueprint builder.

Orchestrates the full planning pipeline:

1. Load condition from the ``ConditionRegistry`` (if available).
2. Plan the outline via :class:`~sozo_generator.planning.outline_planner.OutlinePlanner`.
3. Convert each outline entry to a ``SectionSpec`` via
   :class:`~sozo_generator.planning.section_planner.SectionPlanner`.
4. Collect all required asset IDs across all sections.
5. Assemble and return a :class:`~sozo_generator.schemas.canonical.DocumentBlueprint`.

No external API calls are made here; all work is deterministic and offline.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from sozo_generator.schemas.canonical import DocumentBlueprint, SectionSpec
from sozo_generator.schemas.condition import ConditionSchema
from sozo_generator.planning.outline_planner import OutlinePlanner
from sozo_generator.planning.section_planner import SectionPlanner

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Title-generation helpers
# ---------------------------------------------------------------------------

_DOCUMENT_TYPE_LABELS: dict[str, str] = {
    "handbook": "Clinical Handbook",
    "protocol": "Treatment Protocol",
    "assessment": "Assessment Guide",
    "all_in_one": "Comprehensive Clinical Reference",
    "partner_compendium": "Partner Clinical Compendium",
}

_VARIANT_LABELS: dict[str, str] = {
    "fellow": "Fellow Edition",
    "partners": "Partners Edition",
    "shared": "Shared Edition",
}


def _make_title(
    condition_slug: str,
    variant: str,
    document_type: str,
    condition: Optional[ConditionSchema] = None,
) -> str:
    """Derive a human-readable document title."""
    condition_name = (
        condition.display_name
        if condition is not None
        else condition_slug.replace("_", " ").title()
    )
    doc_label = _DOCUMENT_TYPE_LABELS.get(document_type, document_type.replace("_", " ").title())
    return f"{condition_name} — {doc_label}"


def _make_subtitle(variant: str) -> str:
    """Derive a variant subtitle."""
    return _VARIANT_LABELS.get(variant, variant.title())


def _estimate_total_words(sections: list[SectionSpec]) -> int:
    """Sum ``target_word_count`` across all sections."""
    return sum(s.target_word_count for s in sections)


def _collect_all_asset_ids(sections: list[SectionSpec]) -> list[str]:
    """Collect all unique asset IDs from all sections in document order."""
    seen: set[str] = set()
    result: list[str] = []
    for section in sections:
        for asset_id in section.required_asset_ids:
            if asset_id and asset_id not in seen:
                seen.add(asset_id)
                result.append(asset_id)
    return result


# ---------------------------------------------------------------------------
# DocumentBlueprintBuilder
# ---------------------------------------------------------------------------

class DocumentBlueprintBuilder:
    """Orchestrates the full blueprint-building pipeline.

    Typical usage::

        builder = DocumentBlueprintBuilder()
        blueprint = builder.build(
            condition_slug="parkinsons",
            variant="fellow",
            document_type="handbook",
            target_page_count=60,
        )
        path = builder.save(blueprint, output_dir="/tmp/blueprints")
    """

    def __init__(self) -> None:
        self.outline_planner = OutlinePlanner()
        self.section_planner = SectionPlanner()

    # ------------------------------------------------------------------
    # Primary build entry points
    # ------------------------------------------------------------------

    def build(
        self,
        condition_slug: str,
        variant: str,
        document_type: str,
        target_page_count: int = 60,
        evidence_profile_id: Optional[str] = None,
    ) -> DocumentBlueprint:
        """Build a ``DocumentBlueprint`` from a condition slug.

        Steps:

        1. Attempt to load the full ``ConditionSchema`` from the registry.
           On failure (missing condition or broken registry), continues with
           ``condition=None`` so the pipeline remains functional.
        2. Delegate to :meth:`build_from_condition`.

        Args:
            condition_slug: Registry slug for the condition (e.g. ``"parkinsons"``).
            variant: ``"fellow"`` or ``"partners"``.
            document_type: One of ``"handbook"``, ``"protocol"``, ``"assessment"``,
                ``"all_in_one"``, ``"partner_compendium"``.
            target_page_count: Soft page-count target passed to the outline planner.
            evidence_profile_id: Optional identifier for an evidence profile to
                attach to the blueprint (stored as metadata only in this layer).

        Returns:
            A fully assembled :class:`~sozo_generator.schemas.canonical.DocumentBlueprint`.
        """
        condition: Optional[ConditionSchema] = None
        try:
            from sozo_generator.conditions.registry import get_registry
            registry = get_registry()
            if registry.exists(condition_slug):
                condition = registry.get(condition_slug)
                logger.info("Loaded condition '%s' from registry.", condition_slug)
            else:
                logger.warning(
                    "Condition '%s' not found in registry; building blueprint without condition data.",
                    condition_slug,
                )
        except Exception as exc:
            logger.warning(
                "Registry lookup failed for '%s' (%s); continuing without condition data.",
                condition_slug,
                exc,
            )

        blueprint = self.build_from_condition(
            condition=condition,
            variant=variant,
            document_type=document_type,
            target_page_count=target_page_count,
            _condition_slug_override=condition_slug,
        )

        # Attach the evidence profile id if supplied
        if evidence_profile_id is not None:
            blueprint.evidence_profile_id = evidence_profile_id

        return blueprint

    def build_from_condition(
        self,
        condition: Optional[ConditionSchema],
        variant: str,
        document_type: str,
        target_page_count: int = 60,
        _condition_slug_override: Optional[str] = None,
    ) -> DocumentBlueprint:
        """Build a ``DocumentBlueprint`` from a ``ConditionSchema`` instance.

        Use this when you already have a ``ConditionSchema`` object and want to
        bypass the registry lookup.

        Args:
            condition: A ``ConditionSchema`` instance, or ``None`` to build a
                skeleton blueprint without condition-specific data.
            variant: ``"fellow"`` or ``"partners"``.
            document_type: Document type identifier string.
            target_page_count: Soft page-count target.
            _condition_slug_override: Used internally to preserve the original
                slug when ``condition`` is ``None``.

        Returns:
            A fully assembled ``DocumentBlueprint``.
        """
        # Resolve condition slug
        if condition is not None:
            condition_slug = condition.slug
        elif _condition_slug_override:
            condition_slug = _condition_slug_override
        else:
            condition_slug = "unknown"

        # Normalise variant
        normalised_variant = variant if variant in ("fellow", "partners", "shared") else "fellow"

        logger.info(
            "Building blueprint: slug=%s variant=%s doc_type=%s pages=%d",
            condition_slug,
            normalised_variant,
            document_type,
            target_page_count,
        )

        # Step 1 — Plan outline
        outline = self.outline_planner.plan(
            condition_slug=condition_slug,
            variant=normalised_variant,
            document_type=document_type,
            target_page_count=target_page_count,
        )
        logger.debug("Outline planned: %d sections.", len(outline))

        # Step 2 — Convert to SectionSpecs
        sections: list[SectionSpec] = self.section_planner.build_all_section_specs(
            outline=outline,
            condition_slug=condition_slug,
            variant=normalised_variant,
            condition=condition,
        )
        logger.debug("SectionSpecs built: %d.", len(sections))

        # Step 3 — Collect asset IDs
        all_asset_ids = _collect_all_asset_ids(sections)

        # Step 4 — Compute total word count
        total_word_count = _estimate_total_words(sections)

        # Step 5 — Derive title
        title = _make_title(condition_slug, normalised_variant, document_type, condition)
        subtitle = _make_subtitle(normalised_variant)

        # Step 6 — Assemble blueprint
        blueprint = DocumentBlueprint(
            condition_slug=condition_slug,
            variant=normalised_variant,  # type: ignore[arg-type]
            document_type=document_type,
            title=title,
            subtitle=subtitle,
            target_page_count=target_page_count,
            target_word_count=total_word_count,
            sections=sections,
            required_asset_ids=all_asset_ids,
            build_notes=(
                f"Generated by DocumentBlueprintBuilder. "
                f"Outline sections: {len(outline)}. "
                f"Total word target: {total_word_count:,}. "
                f"Required assets: {len(all_asset_ids)}."
            ),
        )

        logger.info(
            "Blueprint built: id=%s sections=%d words=%d assets=%d",
            blueprint.blueprint_id,
            len(sections),
            total_word_count,
            len(all_asset_ids),
        )

        return blueprint

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def save(self, blueprint: DocumentBlueprint, output_dir: str) -> str:
        """Save *blueprint* as a JSON file in *output_dir*.

        The file is named ``blueprint_{condition_slug}_{variant}_{document_type}_{id[:8]}.json``.

        Args:
            blueprint: The ``DocumentBlueprint`` to serialise.
            output_dir: Directory path where the JSON file will be written.
                Created if it does not exist.

        Returns:
            The absolute path string of the saved file.

        Raises:
            OSError: If the directory cannot be created or the file cannot be
                written.
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        filename = (
            f"blueprint"
            f"_{blueprint.condition_slug}"
            f"_{blueprint.variant}"
            f"_{blueprint.document_type}"
            f"_{blueprint.blueprint_id[:8]}"
            ".json"
        )
        file_path = out_path / filename

        json_data = blueprint.model_dump(mode="json")
        file_path.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info("Blueprint saved to: %s", file_path)
        return str(file_path)

    def load(self, path: str) -> DocumentBlueprint:
        """Load a ``DocumentBlueprint`` from a JSON file.

        Args:
            path: Absolute or relative path to the JSON file.

        Returns:
            A ``DocumentBlueprint`` instance reconstructed from the file.

        Raises:
            FileNotFoundError: If *path* does not exist.
            ValueError: If the file cannot be parsed as a valid blueprint.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Blueprint file not found: {path}")

        raw = file_path.read_text(encoding="utf-8")
        try:
            data: dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in blueprint file '{path}': {exc}") from exc

        try:
            blueprint = DocumentBlueprint.model_validate(data)
        except Exception as exc:
            raise ValueError(f"Cannot parse blueprint from '{path}': {exc}") from exc

        logger.info(
            "Blueprint loaded from '%s': id=%s sections=%d",
            path,
            blueprint.blueprint_id,
            len(blueprint.sections),
        )
        return blueprint
