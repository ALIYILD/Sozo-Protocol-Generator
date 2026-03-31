"""SOZO branded Word document styles."""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import logging

logger = logging.getLogger(__name__)


def hex_to_rgb(hex_color: str) -> RGBColor:
    """Convert hex color string to RGBColor."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return RGBColor(r, g, b)


# SOZO brand colors
COLOR_DARK_BLUE = hex_to_rgb("#1B3A5C")
COLOR_PRIMARY_BLUE = hex_to_rgb("#2E75B6")
COLOR_BROWN = hex_to_rgb("#996600")
COLOR_PRIMARY_BROWN = COLOR_BROWN  # alias
COLOR_RED = hex_to_rgb("#CC0000")
COLOR_ACCENT_RED = COLOR_RED  # alias
COLOR_GRAY = hex_to_rgb("#666666")
COLOR_DARK_GRAY = COLOR_GRAY  # alias
COLOR_MEDIUM_GRAY = hex_to_rgb("#999999")
COLOR_LIGHT_GRAY = hex_to_rgb("#F2F2F2")
COLOR_WHITE = hex_to_rgb("#FFFFFF")
COLOR_BLACK = hex_to_rgb("#000000")
COLOR_WARNING = hex_to_rgb("#FF8C00")
COLOR_WARNING_ORANGE = COLOR_WARNING  # alias
COLOR_HIGHLIGHT_YELLOW = hex_to_rgb("#FFFF99")

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"


def set_cell_background(cell, hex_color: str) -> None:
    """Set table cell background color using XML manipulation."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    tcPr.append(shd)


# Alias used by new API
def shade_cell(cell, fill_hex: str) -> None:
    """Apply background shading to a table cell."""
    set_cell_background(cell, fill_hex)


def set_cell_border(cell, border_type: str = "all", size: int = 4, color: str = "2E75B6") -> None:
    """Set cell borders."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ["top", "left", "bottom", "right"]:
        if border_type in ("all", edge):
            border = OxmlElement(f"w:{edge}")
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), str(size))
            border.set(qn("w:space"), "0")
            border.set(qn("w:color"), color)
            tcBorders.append(border)
    tcPr.append(tcBorders)


def set_table_borders(table) -> None:
    """Apply visible borders to all table cells."""
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    tblBorders = OxmlElement("w:tblBorders")
    for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{border_name}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "1B3A5C")
        tblBorders.append(border)
    tblPr.append(tblBorders)
    if tbl.tblPr is None:
        tbl.append(tblPr)


def set_cell_text(cell, text: str, bold: bool = False, color: RGBColor = None, size: int = 10) -> None:
    """Set cell text with formatting."""
    cell.text = ""
    para = cell.paragraphs[0]
    run = para.add_run(text)
    run.font.name = FONT_BODY
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    para.paragraph_format.space_before = Pt(2)
    para.paragraph_format.space_after = Pt(2)


def apply_heading_style(paragraph, level: int = 1, color: RGBColor = None) -> None:
    """Apply SOZO heading style to a paragraph."""
    sizes = {1: 16, 2: 14, 3: 12, 4: 11}
    colors = {1: COLOR_DARK_BLUE, 2: COLOR_PRIMARY_BLUE, 3: COLOR_BROWN, 4: COLOR_GRAY}
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    run.font.size = Pt(sizes.get(level, 11))
    run.font.color.rgb = color or colors.get(level, COLOR_DARK_BLUE)
    run.font.bold = True
    run.font.name = FONT_HEADING
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_before = Pt(12 if level == 1 else 6)
    paragraph.paragraph_format.space_after = Pt(6)


def apply_body_style(paragraph, bold: bool = False, italic: bool = False, size: int = 11) -> None:
    """Apply SOZO body text style."""
    for run in paragraph.runs:
        run.font.name = FONT_BODY
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
    paragraph.paragraph_format.space_after = Pt(4)


def add_horizontal_rule(doc: Document, color: str = "2E75B6") -> None:
    """Add a horizontal rule paragraph."""
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)
    p.paragraph_format.space_after = Pt(6)
