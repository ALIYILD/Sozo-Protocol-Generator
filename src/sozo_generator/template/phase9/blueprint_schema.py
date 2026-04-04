"""
blueprint_schema.py — DocumentBlueprint: machine-readable structural DNA of a DOCX file.

Captures page layout, named styles, color palette, table schemas, section order, and
header/footer templates.  Does NOT store content — only structure and design.

Phase 9, pipeline_version: phase9_v1
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, computed_field, model_validator

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PageLayout
# ---------------------------------------------------------------------------


class PageLayout(BaseModel):
    """Physical page dimensions, margins, and column layout for a DOCX document."""

    size: Literal["A4", "Letter", "A3", "Legal"] = "A4"
    orientation: Literal["portrait", "landscape"] = "portrait"
    margin_top_cm: float = 2.54
    margin_bottom_cm: float = 2.54
    margin_left_cm: float = 2.54
    margin_right_cm: float = 2.54
    columns: int = 1
    header_distance_cm: float = 1.25
    footer_distance_cm: float = 1.25

    def to_emu_dict(self) -> dict[str, int]:
        """Return all margin and distance values converted to English Metric Units.

        1 cm = 360 000 EMU  (derived from: 914 400 EMU/inch ÷ 2.54 cm/inch).
        """
        factor = 360_000
        return {
            "margin_top": int(self.margin_top_cm * factor),
            "margin_bottom": int(self.margin_bottom_cm * factor),
            "margin_left": int(self.margin_left_cm * factor),
            "margin_right": int(self.margin_right_cm * factor),
            "header_distance": int(self.header_distance_cm * factor),
            "footer_distance": int(self.footer_distance_cm * factor),
        }


# ---------------------------------------------------------------------------
# StyleSpec
# ---------------------------------------------------------------------------


class StyleSpec(BaseModel):
    """Full specification for a Word paragraph, character, table, or numbering style."""

    name: str
    """Word style name, e.g. 'SOZO Heading 1'."""

    style_type: Literal["paragraph", "character", "table", "numbering"] = "paragraph"

    font_name: Optional[str] = None
    font_size_pt: Optional[float] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    underline: Optional[bool] = None

    color_hex: Optional[str] = None
    """6-char hex string without '#', e.g. '1F3864'."""

    highlight_color: Optional[str] = None

    space_before_pt: Optional[float] = None
    space_after_pt: Optional[float] = None

    line_spacing_rule: Optional[str] = None
    """One of: 'single', 'one_point_five', 'double', 'exact', 'multiple'."""

    line_spacing_value: Optional[float] = None
    """Point value used when line_spacing_rule is 'exact' or 'multiple'."""

    alignment: Optional[Literal["left", "center", "right", "justify"]] = None

    left_indent_cm: Optional[float] = None
    right_indent_cm: Optional[float] = None
    first_line_indent_cm: Optional[float] = None

    keep_with_next: bool = False
    page_break_before: bool = False

    is_heading: bool = False
    heading_level: Optional[int] = None
    """Heading hierarchy level 1–6; only meaningful when is_heading=True."""

    base_style: Optional[str] = None
    """Parent/base style name this style inherits from."""

    def apply_to_paragraph(self, para: Any) -> None:
        """Apply this StyleSpec to a python-docx Paragraph object.

        Imports python-docx lazily to avoid a hard dependency at module import time.
        Sets the paragraph style by name then overrides font properties directly on
        each run (or the paragraph's default run format) as needed.

        Args:
            para: A ``docx.text.paragraph.Paragraph`` instance.
        """
        try:
            from docx.shared import Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            logger.error("python-docx is not installed; cannot apply style: %s", exc)
            return

        # Apply named style if the document recognises it.
        try:
            para.style = self.name
        except Exception:  # noqa: BLE001
            logger.debug("Style '%s' not found in document; skipping named assignment.", self.name)

        # Override paragraph-level font properties.
        fmt = para.paragraph_format
        if self.space_before_pt is not None:
            fmt.space_before = Pt(self.space_before_pt)
        if self.space_after_pt is not None:
            fmt.space_after = Pt(self.space_after_pt)
        if self.keep_with_next:
            fmt.keep_with_next = True
        if self.page_break_before:
            fmt.page_break_before = True

        # Alignment mapping.
        if self.alignment:
            from docx.enum.text import WD_ALIGN_PARAGRAPH

            _align_map = {
                "left": WD_ALIGN_PARAGRAPH.LEFT,
                "center": WD_ALIGN_PARAGRAPH.CENTER,
                "right": WD_ALIGN_PARAGRAPH.RIGHT,
                "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
            }
            fmt.alignment = _align_map.get(self.alignment)

        # Font properties applied to the run-level default.
        run_font = para.runs[0].font if para.runs else None
        if run_font is None:
            # Create a temporary run to carry the font overrides.
            run_font = para.add_run().font

        if self.font_name is not None:
            run_font.name = self.font_name
        if self.font_size_pt is not None:
            run_font.size = Pt(self.font_size_pt)
        if self.bold is not None:
            run_font.bold = self.bold
        if self.italic is not None:
            run_font.italic = self.italic
        if self.underline is not None:
            run_font.underline = self.underline
        if self.color_hex is not None:
            try:
                r = int(self.color_hex[0:2], 16)
                g = int(self.color_hex[2:4], 16)
                b = int(self.color_hex[4:6], 16)
                run_font.color.rgb = RGBColor(r, g, b)
            except (ValueError, IndexError) as exc:
                logger.warning("Invalid color_hex '%s' in style '%s': %s", self.color_hex, self.name, exc)


# ---------------------------------------------------------------------------
# ColorPaletteEntry
# ---------------------------------------------------------------------------


class ColorPaletteEntry(BaseModel):
    """A single entry in the document's color palette, identified by semantic role."""

    role: str
    """Semantic role such as 'primary', 'secondary', 'accent', 'heading_1',
    'heading_2', 'body', 'table_header', 'table_stripe_light',
    'table_stripe_dark', 'callout_bg', 'callout_border', or 'muted'."""

    hex: str
    """6-character hex color string without a leading '#', e.g. '1F3864'."""

    @model_validator(mode="before")
    @classmethod
    def _normalise_hex(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Strip leading '#', uppercase, and validate exactly 6 hex characters."""
        hex_val = values.get("hex", "")
        if isinstance(hex_val, str):
            hex_val = hex_val.lstrip("#").upper()
            if len(hex_val) != 6:
                raise ValueError(
                    f"ColorPaletteEntry.hex must be exactly 6 hex characters (got '{hex_val}')."
                )
            # Validate all characters are valid hex digits.
            try:
                int(hex_val, 16)
            except ValueError:
                raise ValueError(
                    f"ColorPaletteEntry.hex contains non-hex characters: '{hex_val}'."
                )
            values["hex"] = hex_val
        return values


# ---------------------------------------------------------------------------
# TableSchemaBlueprint
# ---------------------------------------------------------------------------


class TableSchemaBlueprint(BaseModel):
    """Structural and visual schema for a repeating table pattern in the document."""

    schema_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    """Short unique identifier for this table schema."""

    style_name: Optional[str] = None
    """Word table style name, if any."""

    header_bg_hex: Optional[str] = None
    """Background hex color for the header row (no '#')."""

    header_font_color: Optional[str] = None
    """Font hex color for header row text (no '#')."""

    header_bold: bool = True

    row_alt_bg_hex: Optional[str] = None
    """Background hex color for alternating (zebra-striped) rows (no '#')."""

    border_color: Optional[str] = None
    """Hex color for table borders (no '#')."""

    border_width_pt: float = 0.5
    cell_padding_pt: float = 4.0
    col_count: int = 2

    typical_col_widths_pct: list[float] = Field(default_factory=list)
    """Proportional column widths as percentages; values should sum to approximately 100."""

    first_row_is_header: bool = True


# ---------------------------------------------------------------------------
# HeaderFooterBlueprint
# ---------------------------------------------------------------------------


class HeaderFooterBlueprint(BaseModel):
    """Layout and content template for a document header or footer."""

    left_text: Optional[str] = None
    center_text: Optional[str] = None
    right_text: Optional[str] = None

    has_logo: bool = False
    logo_position: Optional[Literal["left", "center", "right"]] = None

    font_name: Optional[str] = None
    font_size_pt: Optional[float] = None
    color_hex: Optional[str] = None
    """Font color hex string without '#'."""

    separator_line: bool = True
    """Whether a horizontal rule separates the header/footer from the document body."""


# ---------------------------------------------------------------------------
# ImageConstraints
# ---------------------------------------------------------------------------


class ImageConstraints(BaseModel):
    """Constraints and preferences for an image placeholder within a layout region."""

    min_width_px: int = 400
    min_height_px: int = 200

    aspect_ratio: Optional[str] = None
    """Preferred aspect ratio expressed as a string, e.g. '16:9', '1:1', '4:3'."""

    preferred_format: Literal["PNG", "SVG", "JPEG"] = "PNG"
    dpi: int = 300


# ---------------------------------------------------------------------------
# LayoutRegion
# ---------------------------------------------------------------------------


class LayoutRegion(BaseModel):
    """A single content slot within a section, describing its visual role and constraints."""

    region_id: str
    region_type: Literal[
        "text_block",
        "table",
        "image_placeholder",
        "callout_box",
        "citation_block",
        "figure_slot",
        "caption_slot",
        "two_column_layout",
        "device_card",
        "evidence_badge",
        "section_divider",
        "specification_table",
        "horizontal_rule",
        "spacer",
    ]

    content_key: str
    """Slot identifier used for content injection at generation time."""

    style_name: Optional[str] = None
    """Maps to a StyleSpec.name defined in the blueprint."""

    width_pct: float = 100.0
    """Width as a percentage of the text-area width."""

    position: Literal["inline", "float_left", "float_right", "full_width", "sidebar"] = "inline"

    required: bool = True

    order: int = 0
    """Sort order of this region within its parent section."""

    image_constraints: Optional[ImageConstraints] = None
    """Only meaningful when region_type is 'image_placeholder' or 'figure_slot'."""


# ---------------------------------------------------------------------------
# SectionBlueprint
# ---------------------------------------------------------------------------


class SectionBlueprint(BaseModel):
    """Blueprint for a logical document section, including its heading and layout regions."""

    section_id: str
    section_type: Literal[
        "cover",
        "toc",
        "overview",
        "condition_background",
        "protocol_parameters",
        "session_plan",
        "evidence_summary",
        "device_specs",
        "eeg_brain_map",
        "contraindications",
        "assessment_tools",
        "scoring_guide",
        "handbook_guidance",
        "figure_explanation",
        "reference_list",
        "appendix",
        "custom",
    ]

    heading_text: str
    """Static heading label displayed in the rendered document."""

    heading_style: Optional[str] = None
    """Maps to a StyleSpec.name; controls heading typography."""

    heading_level: int = 1
    """Heading hierarchy level (1 = top-level)."""

    order: int
    """Absolute position of this section in the document (0-based, sorted ascending)."""

    layout_regions: list[LayoutRegion] = Field(default_factory=list)

    is_conditional: bool = False
    condition_expression: Optional[str] = None
    """Python-like expression evaluated at generation time, e.g. \"doc_type == 'protocol'\"."""

    required: bool = True
    page_break_before: bool = False


# ---------------------------------------------------------------------------
# DocumentBlueprint — top-level model
# ---------------------------------------------------------------------------


class DocumentBlueprint(BaseModel):
    """Machine-readable structural and visual DNA extracted from an uploaded DOCX file.

    Stores page layout, named styles, the color palette, table schemas, section order,
    and header/footer templates.  Content is intentionally excluded — this model
    describes *design* only.
    """

    blueprint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_filename: str
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    pipeline_version: str = "phase9_v1"

    # -- Page -------------------------------------------------------------------
    page_layout: PageLayout = Field(default_factory=PageLayout)

    # -- Style system -----------------------------------------------------------
    styles: list[StyleSpec] = Field(default_factory=list)
    color_palette: list[ColorPaletteEntry] = Field(default_factory=list)
    table_schemas: list[TableSchemaBlueprint] = Field(default_factory=list)

    # -- Structure --------------------------------------------------------------
    sections: list[SectionBlueprint] = Field(default_factory=list)
    header: Optional[HeaderFooterBlueprint] = None
    footer: Optional[HeaderFooterBlueprint] = None

    # -- Metadata ---------------------------------------------------------------
    total_styles_extracted: int = 0
    total_sections_detected: int = 0
    document_type_guess: Optional[Literal["protocol", "assessment", "handbook", "unknown"]] = None
    has_cover_page: bool = False
    has_toc: bool = False
    has_header: bool = False
    has_footer: bool = False
    extraction_warnings: list[str] = Field(default_factory=list)

    # -- Style lookup -----------------------------------------------------------

    def get_style(self, name: str) -> Optional[StyleSpec]:
        """Return the StyleSpec whose name matches *name* (case-insensitive), or None.

        Args:
            name: The Word style name to look up.

        Returns:
            Matching :class:`StyleSpec`, or ``None`` if not found.
        """
        name_lower = name.lower()
        for style in self.styles:
            if style.name.lower() == name_lower:
                return style
        return None

    def has_style(self, name: str) -> bool:
        """Return True if a style with *name* exists in the blueprint (case-insensitive).

        Args:
            name: The Word style name to check.
        """
        return self.get_style(name) is not None

    def style_names(self) -> list[str]:
        """Return the names of all extracted styles in their original casing."""
        return [s.name for s in self.styles]

    # -- Heading helpers --------------------------------------------------------

    def heading_styles(self) -> list[StyleSpec]:
        """Return all styles where ``is_heading=True``, sorted ascending by heading_level.

        Styles with no heading_level set are sorted after those that have one.
        """
        heading = [s for s in self.styles if s.is_heading]
        return sorted(heading, key=lambda s: (s.heading_level is None, s.heading_level or 0))

    # -- Color helpers ----------------------------------------------------------

    def primary_color(self) -> Optional[str]:
        """Return the hex value of the first ColorPaletteEntry with role='primary', or None."""
        for entry in self.color_palette:
            if entry.role == "primary":
                return entry.hex
        return None

    # -- Section helpers --------------------------------------------------------

    def ordered_sections(self) -> list[SectionBlueprint]:
        """Return all sections sorted ascending by their ``order`` field."""
        return sorted(self.sections, key=lambda s: s.order)

    # -- Jinja2 / docxtpl integration ------------------------------------------

    def to_jinja2_context(self) -> dict[str, Any]:
        """Return a flat dict of key design values for use in docxtpl templates.

        Keys are prefixed with ``bp_`` to avoid collisions with content variables.

        Returns:
            dict with keys:
            - ``bp_primary_color`` — 6-char hex or SOZO default '1F3864'
            - ``bp_heading_font`` — font name of the first heading style or 'Calibri'
            - ``bp_body_font`` — font name of the 'Normal' style or 'Calibri'
            - ``bp_page_size`` — page size literal, e.g. 'A4'
            - ``bp_section_count`` — total number of sections
        """
        headings = self.heading_styles()
        normal_style = self.get_style("Normal")

        return {
            "bp_primary_color": self.primary_color() or "1F3864",
            "bp_heading_font": headings[0].font_name if headings else "Calibri",
            "bp_body_font": normal_style.font_name if normal_style else "Calibri",
            "bp_page_size": self.page_layout.size,
            "bp_section_count": len(self.sections),
        }


# ---------------------------------------------------------------------------
# Module-level helper
# ---------------------------------------------------------------------------


def empty_blueprint(source_filename: str = "unknown.docx") -> DocumentBlueprint:
    """Return a minimal valid DocumentBlueprint populated with SOZO defaults.

    Useful as a starting point when no source DOCX is available or when the
    extraction pipeline has not yet been run.

    Args:
        source_filename: The filename to record in the blueprint metadata.

    Returns:
        A :class:`DocumentBlueprint` with default page layout, three core styles,
        and a two-entry color palette.
    """
    logger.debug("Creating empty DocumentBlueprint for '%s'.", source_filename)
    return DocumentBlueprint(
        source_filename=source_filename,
        page_layout=PageLayout(),
        styles=[
            StyleSpec(name="Normal", font_name="Calibri", font_size_pt=11.0),
            StyleSpec(
                name="Heading 1",
                font_name="Calibri",
                font_size_pt=16.0,
                bold=True,
                is_heading=True,
                heading_level=1,
            ),
            StyleSpec(
                name="Heading 2",
                font_name="Calibri",
                font_size_pt=13.0,
                bold=True,
                is_heading=True,
                heading_level=2,
            ),
        ],
        color_palette=[
            ColorPaletteEntry(role="primary", hex="1F3864"),
            ColorPaletteEntry(role="body", hex="333333"),
        ],
    )
