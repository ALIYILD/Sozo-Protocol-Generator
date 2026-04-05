"""SOZO Generator — document planning layer.

Exports the three main planning classes used to build a DocumentBlueprint
from a condition slug, variant, and document type.

Typical usage::

    from sozo_generator.planning import DocumentBlueprintBuilder

    builder = DocumentBlueprintBuilder()
    blueprint = builder.build(
        condition_slug="parkinsons",
        variant="fellow",
        document_type="handbook",
        target_page_count=60,
    )
"""

from sozo_generator.planning.outline_planner import OutlinePlanner
from sozo_generator.planning.section_planner import SectionPlanner
from sozo_generator.planning.document_blueprint_builder import DocumentBlueprintBuilder

__all__ = [
    "OutlinePlanner",
    "SectionPlanner",
    "DocumentBlueprintBuilder",
]
