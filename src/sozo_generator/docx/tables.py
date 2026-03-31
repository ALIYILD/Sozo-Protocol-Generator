"""
DOCX table builder — handles all table types used in SOZO clinical documents.
"""
import logging
from typing import Optional
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from .styles import (
    COLOR_DARK_BLUE, COLOR_PRIMARY_BLUE, COLOR_LIGHT_GRAY,
    COLOR_WHITE, COLOR_ACCENT_RED, COLOR_MEDIUM_GRAY,
    FONT_BODY, FONT_HEADING,
    set_cell_background, shade_cell, set_table_borders, set_cell_text,
)

logger = logging.getLogger(__name__)


def set_cell_background_para(paragraph, hex_color: str) -> None:
    """Apply background shading to a paragraph (for callout boxes)."""
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color.lstrip("#"))
    pPr.append(shd)


def add_clinical_table(
    doc: Document,
    headers: list,
    rows: list,
    caption: Optional[str] = None,
    header_color: str = "1B3A5C",
    header_text_color: RGBColor = None,
    alternate_rows: bool = True,
    col_widths: Optional[list] = None,
) -> None:
    """
    Add a branded clinical table to the document.

    Args:
        doc: The Document object
        headers: Column header labels
        rows: List of row data (each row is a list of strings)
        caption: Optional caption below the table
        header_color: Hex color for header row background
        header_text_color: Font color for header text
        alternate_rows: Whether to alternate row shading
        col_widths: Optional column widths in inches (float) or cm (float)
    """
    if not headers:
        return

    n_cols = len(headers)
    n_rows = len(rows) + 1  # +1 for header row

    table = doc.add_table(rows=n_rows, cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = "Table Grid"

    if header_text_color is None:
        header_text_color = RGBColor(0xFF, 0xFF, 0xFF)

    # Header row
    header_row = table.rows[0]
    for j, header_text in enumerate(headers):
        cell = header_row.cells[j]
        set_cell_background(cell, header_color)
        p = cell.paragraphs[0]
        p.clear()
        run = p.add_run(str(header_text))
        run.bold = True
        run.font.name = FONT_HEADING
        run.font.size = Pt(10)
        run.font.color.rgb = header_text_color
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        cell.vertical_alignment = 1  # WD_ALIGN_VERTICAL.CENTER

    # Data rows
    for i, row_data in enumerate(rows):
        table_row = table.rows[i + 1]
        row_bg = "F2F2F2" if (alternate_rows and i % 2 == 0) else "FFFFFF"

        for j, cell_text in enumerate(row_data):
            if j >= n_cols:
                break
            cell = table_row.cells[j]
            set_cell_background(cell, row_bg)
            p = cell.paragraphs[0]
            p.clear()

            cell_str = str(cell_text) if cell_text is not None else ""

            # Handle warning markers
            if cell_str.startswith("\u26a0") or "OFF-LABEL" in cell_str:
                run = p.add_run(cell_str)
                run.font.color.rgb = COLOR_ACCENT_RED
                run.font.bold = True
            else:
                run = p.add_run(cell_str)

            run.font.name = FONT_BODY
            run.font.size = Pt(10)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)

    # Set column widths if provided
    if col_widths and len(col_widths) == n_cols:
        for row in table.rows:
            for j, cell in enumerate(row.cells):
                if j < len(col_widths):
                    # Accept inches (float < 10 is treated as inches)
                    w = col_widths[j]
                    cell.width = Inches(w) if w < 10 else Cm(w)

    # Add caption
    if caption:
        cap_para = doc.add_paragraph()
        cap_run = cap_para.add_run(f"Table: {caption}")
        cap_run.font.size = Pt(8)
        cap_run.font.italic = True
        cap_run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
        cap_para.paragraph_format.space_before = Pt(2)
        cap_para.paragraph_format.space_after = Pt(8)

    doc.add_paragraph()  # spacing after table


def add_warning_box(doc: Document, text: str, box_type: str = "warning", severity: str = None) -> None:
    """
    Add a colored callout/warning box.
    box_type / severity: 'warning' | 'info' | 'critical' | 'tip' | 'governance' | 'offlabel'
    """
    # Support both 'box_type' and 'severity' parameter names
    kind = severity or box_type

    colors = {
        "warning": ("FF8C00", "\u26a0 WARNING:"),
        "critical": ("CC0000", "\u26a0 CRITICAL:"),
        "info": ("2E75B6", "\u2139 INFO:"),
        "tip": ("996600", "CLINICAL TIP:"),
        "governance": ("1B3A5C", "GOVERNANCE RULE:"),
        "offlabel": ("CC0000", "\u26a0 OFF-LABEL:"),
    }
    bg_color, prefix = colors.get(kind, colors["warning"])

    p = doc.add_paragraph()
    set_cell_background_para(p, bg_color)

    run_prefix = p.add_run(f"{prefix} ")
    run_prefix.bold = True
    run_prefix.font.size = Pt(10)
    run_prefix.font.name = FONT_BODY
    run_prefix.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    run_text = p.add_run(text)
    run_text.font.size = Pt(10)
    run_text.font.name = FONT_BODY
    run_text.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)


def add_scoring_table(
    doc: Document,
    items: list,
    title: str = "Assessment Scoring",
) -> None:
    """Add a scoring/rating table for clinical assessments.
    items: list of tuples (label, score_field, notes_field)
    """
    headers = ["Assessment Item", "Score", "Notes"]
    rows = [[item[0], item[1] if len(item) > 1 else "", item[2] if len(item) > 2 else ""] for item in items]
    add_clinical_table(
        doc, headers, rows,
        caption=title,
        header_color="2E75B6",
        alternate_rows=True,
    )
