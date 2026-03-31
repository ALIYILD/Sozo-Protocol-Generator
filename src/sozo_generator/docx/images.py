"""Image insertion utilities for SOZO documents."""
import logging
from pathlib import Path
from docx import Document
from docx.shared import Inches, Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .styles import COLOR_GRAY, FONT_BODY

logger = logging.getLogger(__name__)


def insert_image(
    doc: Document,
    image_path,
    width_cm: float = 14.0,
    caption: str = None,
    center: bool = True,
) -> None:
    """Insert an image into the document with optional caption."""
    path = Path(image_path)
    if not path.exists():
        logger.warning(f"Image not found: {path}")
        insert_figure_placeholder(doc, str(path.name))
        return

    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))

    if caption:
        cap_p = doc.add_paragraph()
        cap_run = cap_p.add_run(f"Figure: {caption}")
        cap_run.italic = True
        cap_run.font.name = FONT_BODY
        cap_run.font.size = Pt(9)
        cap_run.font.color.rgb = COLOR_GRAY
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def insert_figure(
    doc: Document,
    image_path,
    caption: str = "",
    width_inches: float = 5.5,
    centered: bool = True,
) -> bool:
    """Insert a figure into the document with optional caption. Returns True if successful."""
    path = Path(image_path)
    if not path.exists():
        logger.warning(f"Figure not found: {path} — inserting placeholder")
        placeholder = doc.add_paragraph(f"[FIGURE: {caption or path.name} — image file not found]")
        placeholder.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in placeholder.runs:
            run.font.italic = True
            run.font.color.rgb = COLOR_GRAY
        return False

    try:
        img_para = doc.add_paragraph()
        if centered:
            img_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = img_para.add_run()
        run.add_picture(str(path), width=Inches(width_inches))
        img_para.paragraph_format.space_after = Pt(4)

        if caption:
            cap_para = doc.add_paragraph()
            cap_run = cap_para.add_run(f"Figure: {caption}")
            cap_run.font.name = FONT_BODY
            cap_run.font.size = Pt(9)
            cap_run.font.italic = True
            cap_run.font.color.rgb = COLOR_GRAY
            cap_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_para.paragraph_format.space_after = Pt(10)

        return True
    except Exception as e:
        logger.error(f"Failed to insert figure {path}: {e}")
        return False


def insert_figure_placeholder(doc: Document, label: str) -> None:
    """Insert a text placeholder where a figure will go."""
    para = doc.add_paragraph(f"[FIGURE PLACEHOLDER: {label}]")
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in para.runs:
        run.font.italic = True
        run.font.size = Pt(10)
        run.font.name = FONT_BODY
        run.font.color.rgb = COLOR_GRAY
    para.paragraph_format.space_before = Pt(8)
    para.paragraph_format.space_after = Pt(8)
