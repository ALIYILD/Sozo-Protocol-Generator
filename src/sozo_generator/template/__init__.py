"""Template parsing, extraction, style mapping, and document structure."""
from .parser import TemplateParser, ParsedSection
from .extractor import TemplateExtractor, ContentBlock
from .style_map import STYLE_REGISTRY, get_style, get_table_header_color
from .doc_structure import build_document_spec, get_document_output_path
from .gold_standard import (
    DOCUMENT_MANIFEST,
    get_required_sections,
    get_all_section_ids,
    requires_tables,
    requires_figures,
    is_partners_only,
)

__all__ = [
    "TemplateParser",
    "ParsedSection",
    "TemplateExtractor",
    "ContentBlock",
    "STYLE_REGISTRY",
    "get_style",
    "get_table_header_color",
    "build_document_spec",
    "get_document_output_path",
    "DOCUMENT_MANIFEST",
    "get_required_sections",
    "get_all_section_ids",
    "requires_tables",
    "requires_figures",
    "is_partners_only",
]
