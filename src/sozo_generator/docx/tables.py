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
    header_color: str = "E8F4F5",
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

    # Detect protocol Parameter/Value tables — use special styling
    is_protocol_table = (
        n_cols == 2
        and len(headers) == 2
        and headers[0].strip().lower() == "parameter"
        and headers[1].strip().lower() == "value"
    )

    table = doc.add_table(rows=n_rows, cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = "Table Grid"

    if header_text_color is None:
        header_text_color = RGBColor(0x1B, 0x47, 0x4D)

    if is_protocol_table:
        # Protocol table: no colored header row — Parameter/Value is just labels
        # Left column: #F5F5F5 gray bg + bold text; Right column: white + regular text
        hdr_row = table.rows[0]
        for j, hdr_text in enumerate(headers):
            cell = hdr_row.cells[j]
            fill = "F5F5F5" if j == 0 else "FFFFFF"
            set_cell_background(cell, fill)
            p = cell.paragraphs[0]
            p.clear()
            run = p.add_run(str(hdr_text))
            run.bold = True
            run.font.name = FONT_HEADING
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(0x1B, 0x47, 0x4D)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)

        for i, row_data in enumerate(rows):
            table_row = table.rows[i + 1]
            for j, cell_text in enumerate(row_data):
                if j >= n_cols:
                    break
                cell = table_row.cells[j]
                fill = "F5F5F5" if j == 0 else "FFFFFF"
                set_cell_background(cell, fill)
                p = cell.paragraphs[0]
                p.clear()
                cell_str = str(cell_text) if cell_text is not None else ""
                run = p.add_run(cell_str)
                run.font.name = FONT_BODY
                run.font.size = Pt(12)
                if j == 0:
                    run.font.bold = True
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
    else:
        # Standard table: teal header, white data rows
        header_row = table.rows[0]
        for j, header_text in enumerate(headers):
            cell = header_row.cells[j]
            set_cell_background(cell, header_color)
            p = cell.paragraphs[0]
            p.clear()
            run = p.add_run(str(header_text))
            run.bold = True
            run.font.name = FONT_HEADING
            run.font.size = Pt(12)
            run.font.color.rgb = header_text_color
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            cell.vertical_alignment = 1  # WD_ALIGN_VERTICAL.CENTER

        # Data rows
        for i, row_data in enumerate(rows):
            table_row = table.rows[i + 1]
            row_bg = "FFFFFF"  # v3 design: no zebra stripes, all rows white

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
                run.font.size = Pt(12)
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
        "warning": ("FFF3CD", "8B6914", "\u26a0 WARNING:"),
        "critical": ("FFF0F0", "CC0000", "\U0001f534 CRITICAL:"),
        "info": ("E8F4F5", "1B474D", "\u2139 INFO:"),
        "tip": ("F5F5F5", "333333", "CLINICAL TIP:"),
        "governance": ("FFF0F0", "CC0000", "\U0001f534 GOVERNANCE:"),
        "offlabel": ("FFF3CD", "8B6914", "\u26a0 OFF-LABEL:"),
    }
    bg_color, text_color_hex, prefix = colors.get(kind, colors["warning"])
    text_rgb = RGBColor(
        int(text_color_hex[0:2], 16),
        int(text_color_hex[2:4], 16),
        int(text_color_hex[4:6], 16),
    )

    # Render as single-cell borderless table (matches v3 reference doc)
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell = tbl.rows[0].cells[0]
    set_cell_background(cell, bg_color)

    p = cell.paragraphs[0]
    p.clear()

    run_prefix = p.add_run(f"{prefix} ")
    run_prefix.bold = True
    run_prefix.font.size = Pt(10)
    run_prefix.font.name = FONT_BODY
    run_prefix.font.color.rgb = text_rgb

    run_text = p.add_run(text)
    run_text.font.size = Pt(10)
    run_text.font.name = FONT_BODY
    run_text.font.color.rgb = text_rgb

    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)

    # Remove all borders for clean callout look
    tbl_element = tbl._tbl
    tblPr = tbl_element.tblPr if tbl_element.tblPr is not None else OxmlElement("w:tblPr")
    borders = OxmlElement("w:tblBorders")
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "none")
        border.set(qn("w:sz"), "0")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "auto")
        borders.append(border)
    tblPr.append(borders)


def add_image_param_table(
    doc: Document,
    image_path: str,
    headers: list,
    rows: list,
    caption: Optional[str] = None,
) -> None:
    """Add a 1×2 table with image in left cell and parameter table in right cell.
    Matches the reference document format for protocol blocks."""
    from pathlib import Path

    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Set column widths (40% image, 60% params)
    for cell in table.columns[0].cells:
        cell.width = Cm(7)
    for cell in table.columns[1].cells:
        cell.width = Cm(10)

    # Left cell: image
    left_cell = table.rows[0].cells[0]
    left_cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_path = Path(image_path)
    if img_path.exists():
        try:
            run = left_cell.paragraphs[0].add_run()
            run.add_picture(str(img_path), width=Cm(6.5))
        except Exception as e:
            left_cell.paragraphs[0].add_run(f"[Image: {img_path.name}]").font.italic = True
    else:
        left_cell.paragraphs[0].add_run(f"[Image: {img_path.name}]").font.italic = True

    # Right cell: parameter table as formatted text
    right_cell = table.rows[0].cells[1]
    # Clear default paragraph
    right_cell.paragraphs[0].text = ""

    for row_data in rows:
        if len(row_data) >= 2:
            p = right_cell.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            # Bold label
            run_label = p.add_run(f"{row_data[0]}: ")
            run_label.bold = True
            run_label.font.size = Pt(9)
            run_label.font.name = FONT_BODY
            run_label.font.color.rgb = RGBColor(0x1B, 0x47, 0x4D)  # dark teal
            # Value
            run_val = p.add_run(str(row_data[1]))
            run_val.font.size = Pt(9)
            run_val.font.name = FONT_BODY

    # Remove borders for clean look
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    borders = OxmlElement("w:tblBorders")
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "none")
        border.set(qn("w:sz"), "0")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "auto")
        borders.append(border)
    tblPr.append(borders)

    # Caption
    if caption:
        cap = doc.add_paragraph()
        run = cap.add_run(f"Table: {caption}")
        run.italic = True
        run.font.size = Pt(8)
        run.font.name = FONT_BODY
        run.font.color.rgb = COLOR_MEDIUM_GRAY
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(6)

    doc.add_paragraph()  # spacing


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
        header_color="E8F4F5",
        alternate_rows=True,
    )
