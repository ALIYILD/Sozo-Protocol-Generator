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


# SOZO brand colors — matching Fellow Protocol Handbook v3
COLOR_DARK_TEAL = hex_to_rgb("#1B474D")      # heading 1, table header text
COLOR_TEAL = hex_to_rgb("#01696F")            # heading 2
COLOR_DARK_GRAY = hex_to_rgb("#333333")       # heading 3 color
COLOR_MEDIUM_GRAY = hex_to_rgb("#999999")     # unchanged
COLOR_LIGHT_GRAY = hex_to_rgb("#F5F5F5")      # protocol table label column
COLOR_TABLE_HEADER_BG = hex_to_rgb("#E8F4F5") # light teal for table headers
COLOR_WHITE = hex_to_rgb("#FFFFFF")
COLOR_BLACK = hex_to_rgb("#000000")
COLOR_RED = hex_to_rgb("#CC0000")             # unchanged
COLOR_ACCENT_RED = COLOR_RED
COLOR_WARNING_AMBER = hex_to_rgb("#8B6914")   # warning text color
COLOR_WARNING_BG = hex_to_rgb("#FFF3CD")      # amber warning background
COLOR_CRITICAL_BG = hex_to_rgb("#FFF0F0")     # red critical background

# Keep backward-compatible aliases
COLOR_DARK_BLUE = COLOR_DARK_TEAL
COLOR_PRIMARY_BLUE = COLOR_TEAL
COLOR_WARNING = COLOR_WARNING_AMBER
COLOR_WARNING_ORANGE = COLOR_WARNING_AMBER
COLOR_GRAY = COLOR_DARK_GRAY
COLOR_BROWN = hex_to_rgb("#996600")
COLOR_PRIMARY_BROWN = COLOR_BROWN
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


def set_cell_border(cell, border_type: str = "all", size: int = 4, color: str = "auto") -> None:
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
        border.set(qn("w:color"), "auto")
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
    sizes = {1: 12, 2: 13, 3: 11, 4: 11}
    colors = {1: COLOR_DARK_TEAL, 2: COLOR_TEAL, 3: COLOR_DARK_GRAY, 4: COLOR_MEDIUM_GRAY}
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    run.font.size = Pt(sizes.get(level, 11))
    run.font.color.rgb = color or colors.get(level, COLOR_DARK_TEAL)
    run.font.bold = True
    run.font.name = FONT_HEADING
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_before = Pt(12 if level == 1 else 6)
    paragraph.paragraph_format.space_after = Pt(6)


def apply_body_style(paragraph, bold: bool = False, italic: bool = False, size: int = 12) -> None:
    """Apply SOZO body text style."""
    for run in paragraph.runs:
        run.font.name = FONT_BODY
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
    paragraph.paragraph_format.space_after = Pt(4)


def add_horizontal_rule(doc: Document, color: str = "1B474D") -> None:
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
