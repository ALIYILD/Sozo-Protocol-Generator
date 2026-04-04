"""
sozo_generator.template.phase9
================================
Phase 9 — Template DNA System.

Extract the visual identity (blueprint) from an uploaded DOCX and use it
to ensure all generated Sozo documents are visually consistent.

Quick start
-----------
    from sozo_generator.template.phase9 import extract_blueprint, render_document
    from sozo_generator.schemas.documents import DocumentSpec

    blueprint = extract_blueprint("my_template.docx")   # extract visual DNA
    doc = render_document(blueprint, my_spec)            # render with that DNA
    doc.save("output.docx")
"""
from .blueprint_schema import (
    DocumentBlueprint, PageLayout, StyleSpec, ColorPaletteEntry,
    TableSchemaBlueprint, HeaderFooterBlueprint, SectionBlueprint,
    LayoutRegion, ImageConstraints, empty_blueprint,
)
from .blueprint_extractor import BlueprintExtractor, extract_blueprint
from .style_cloner import StyleCloner, clone_styles_from_blueprint
from .blueprint_renderer import BlueprintRenderer, render_document

__all__ = [
    "DocumentBlueprint", "PageLayout", "StyleSpec", "ColorPaletteEntry",
    "TableSchemaBlueprint", "HeaderFooterBlueprint", "SectionBlueprint",
    "LayoutRegion", "ImageConstraints", "empty_blueprint",
    "BlueprintExtractor", "extract_blueprint",
    "StyleCloner", "clone_styles_from_blueprint",
    "BlueprintRenderer", "render_document",
]
