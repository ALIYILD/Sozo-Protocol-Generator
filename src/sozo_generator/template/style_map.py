"""
Style map — defines the Word document styles used in SOZO document generation.
Maps semantic content types to python-docx paragraph/character styles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StyleDefinition:
    """Defines a Word paragraph or character style."""
    style_name: str          # python-docx style name (must match template)
    font_name: str = "Calibri"
    font_size_pt: float = 11.0
    bold: bool = False
    italic: bool = False
    color_hex: Optional[str] = None       # e.g. "2E4057"
    space_before_pt: float = 0.0
    space_after_pt: float = 6.0
    left_indent_cm: float = 0.0
    keep_with_next: bool = False
    page_break_before: bool = False
    alignment: str = "left"   # left | center | right | justify


# ---- Document Title ----
STYLE_DOCUMENT_TITLE = StyleDefinition(
    style_name="SOZO Title",
    font_name="Calibri",
    font_size_pt=18.0,
    bold=True,
    color_hex="1F3864",
    space_before_pt=0.0,
    space_after_pt=12.0,
    alignment="center",
)

# ---- Document Subtitle ----
STYLE_SUBTITLE = StyleDefinition(
    style_name="SOZO Subtitle",
    font_name="Calibri",
    font_size_pt=13.0,
    bold=False,
    italic=True,
    color_hex="2E4057",
    space_after_pt=18.0,
    alignment="center",
)

# ---- Section Heading 1 (major section) ----
STYLE_HEADING_1 = StyleDefinition(
    style_name="SOZO Heading 1",
    font_name="Calibri",
    font_size_pt=14.0,
    bold=True,
    color_hex="1F3864",
    space_before_pt=18.0,
    space_after_pt=6.0,
    keep_with_next=True,
    page_break_before=False,
)

# ---- Section Heading 2 (subsection) ----
STYLE_HEADING_2 = StyleDefinition(
    style_name="SOZO Heading 2",
    font_name="Calibri",
    font_size_pt=12.0,
    bold=True,
    color_hex="2E4057",
    space_before_pt=12.0,
    space_after_pt=4.0,
    keep_with_next=True,
)

# ---- Section Heading 3 (sub-subsection) ----
STYLE_HEADING_3 = StyleDefinition(
    style_name="SOZO Heading 3",
    font_name="Calibri",
    font_size_pt=11.0,
    bold=True,
    italic=True,
    color_hex="404040",
    space_before_pt=8.0,
    space_after_pt=4.0,
    keep_with_next=True,
)

# ---- Body Text ----
STYLE_BODY = StyleDefinition(
    style_name="SOZO Body",
    font_name="Calibri",
    font_size_pt=10.5,
    bold=False,
    space_after_pt=6.0,
    alignment="justify",
)

# ---- Bullet list item ----
STYLE_BULLET = StyleDefinition(
    style_name="SOZO Bullet",
    font_name="Calibri",
    font_size_pt=10.5,
    left_indent_cm=0.75,
    space_after_pt=3.0,
)

# ---- Numbered list item ----
STYLE_NUMBERED = StyleDefinition(
    style_name="SOZO Numbered",
    font_name="Calibri",
    font_size_pt=10.5,
    left_indent_cm=0.75,
    space_after_pt=3.0,
)

# ---- Table header row ----
STYLE_TABLE_HEADER = StyleDefinition(
    style_name="SOZO Table Header",
    font_name="Calibri",
    font_size_pt=10.0,
    bold=True,
    color_hex="FFFFFF",  # white text
    alignment="center",
)

# ---- Table body cell ----
STYLE_TABLE_BODY = StyleDefinition(
    style_name="SOZO Table Body",
    font_name="Calibri",
    font_size_pt=9.5,
    bold=False,
    space_after_pt=2.0,
)

# ---- Table caption ----
STYLE_TABLE_CAPTION = StyleDefinition(
    style_name="SOZO Table Caption",
    font_name="Calibri",
    font_size_pt=9.0,
    bold=False,
    italic=True,
    color_hex="606060",
    space_before_pt=4.0,
    space_after_pt=8.0,
)

# ---- Review / Warning flag ----
STYLE_REVIEW_FLAG = StyleDefinition(
    style_name="SOZO Review Flag",
    font_name="Calibri",
    font_size_pt=10.5,
    bold=True,
    color_hex="C00000",  # red
    space_after_pt=4.0,
)

# ---- Clinical tip ----
STYLE_CLINICAL_TIP = StyleDefinition(
    style_name="SOZO Clinical Tip",
    font_name="Calibri",
    font_size_pt=10.0,
    bold=False,
    italic=True,
    color_hex="215732",  # dark green
    left_indent_cm=0.5,
    space_after_pt=4.0,
)

# ---- Governance rule ----
STYLE_GOVERNANCE = StyleDefinition(
    style_name="SOZO Governance",
    font_name="Calibri",
    font_size_pt=10.0,
    bold=True,
    color_hex="7B3F00",  # dark amber
    space_after_pt=4.0,
)

# ---- Footer / Document control ----
STYLE_FOOTER = StyleDefinition(
    style_name="SOZO Footer",
    font_name="Calibri",
    font_size_pt=8.0,
    color_hex="808080",
    alignment="center",
)

# ---- Reference list ----
STYLE_REFERENCE = StyleDefinition(
    style_name="SOZO Reference",
    font_name="Calibri",
    font_size_pt=9.5,
    left_indent_cm=1.0,
    space_after_pt=4.0,
)

# ---- OFF-LABEL warning box ----
STYLE_OFF_LABEL_WARNING = StyleDefinition(
    style_name="SOZO Off-Label Warning",
    font_name="Calibri",
    font_size_pt=10.5,
    bold=True,
    italic=False,
    color_hex="9C2500",  # burnt orange / warning
    space_before_pt=6.0,
    space_after_pt=6.0,
)


# ---- Style registry ----
STYLE_REGISTRY: dict[str, StyleDefinition] = {
    "document_title": STYLE_DOCUMENT_TITLE,
    "subtitle": STYLE_SUBTITLE,
    "heading_1": STYLE_HEADING_1,
    "heading_2": STYLE_HEADING_2,
    "heading_3": STYLE_HEADING_3,
    "body": STYLE_BODY,
    "bullet": STYLE_BULLET,
    "numbered": STYLE_NUMBERED,
    "table_header": STYLE_TABLE_HEADER,
    "table_body": STYLE_TABLE_BODY,
    "table_caption": STYLE_TABLE_CAPTION,
    "review_flag": STYLE_REVIEW_FLAG,
    "clinical_tip": STYLE_CLINICAL_TIP,
    "governance": STYLE_GOVERNANCE,
    "footer": STYLE_FOOTER,
    "reference": STYLE_REFERENCE,
    "off_label_warning": STYLE_OFF_LABEL_WARNING,
}


# ---- Table header background colors ----
TABLE_HEADER_COLORS = {
    "default": "1F3864",       # dark navy — standard
    "motor": "1F5C8B",         # blue — motor protocols
    "cognitive": "2D6A4F",     # dark green — cognitive protocols
    "mood": "6B2D8B",          # purple — mood/limbic protocols
    "safety": "C00000",        # red — safety sections
    "assessment": "7B3F00",    # amber — assessment sections
    "network": "14532D",       # forest green — FNON sections
}


def get_table_header_color(section_type: str) -> str:
    """Get the hex color for a table header by section type."""
    return TABLE_HEADER_COLORS.get(section_type, TABLE_HEADER_COLORS["default"])


def get_style(style_key: str) -> StyleDefinition:
    """Get a style definition by key. Falls back to body style."""
    return STYLE_REGISTRY.get(style_key, STYLE_BODY)
