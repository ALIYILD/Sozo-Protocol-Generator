"""Header and footer management for SOZO documents."""
import logging
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from .styles import (
    hex_to_rgb, COLOR_DARK_BLUE, COLOR_GRAY, COLOR_MEDIUM_GRAY,
    COLOR_ACCENT_RED, FONT_BODY, FONT_HEADING,
)

logger = logging.getLogger(__name__)


def add_header(
    doc: Document,
    condition_name: str,
    tier_label: str,
    version: str = "1.0",
    confidentiality: str = "CONFIDENTIAL",
    document_title: str = "",
) -> None:
    """Add branded header to all sections of the document."""
    section = doc.sections[0]
    section.header_distance = Pt(12)
    header = section.header
    header.is_linked_to_previous = False

    # Clear existing header content
    for para in header.paragraphs:
        para.clear()

    # Line 1: Organization + Condition
    p1 = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p1.clear()
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(2)

    run_org = p1.add_run("SOZO BRAIN CENTER")
    run_org.bold = True
    run_org.font.size = Pt(9)
    run_org.font.color.rgb = COLOR_DARK_BLUE
    run_org.font.name = FONT_BODY

    p1.add_run("  |  ").font.size = Pt(9)

    label = condition_name
    if document_title:
        label = f"{condition_name} \u2014 {document_title}"
    run_cond = p1.add_run(label)
    run_cond.font.size = Pt(9)
    run_cond.font.name = FONT_BODY
    run_cond.font.color.rgb = COLOR_DARK_BLUE

    p1.add_run("  |  ").font.size = Pt(9)

    run_tier = p1.add_run(tier_label)
    run_tier.bold = True
    run_tier.font.size = Pt(9)
    run_tier.font.name = FONT_BODY
    run_tier.font.color.rgb = COLOR_ACCENT_RED

    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Line 2: Version + Confidentiality
    p2 = header.add_paragraph()
    run2 = p2.add_run(f"{version}  |  {confidentiality}  |  \u00a9 2026 SOZO Brain Center. All rights reserved.")
    run2.font.name = FONT_BODY
    run2.font.size = Pt(8)
    run2.font.italic = True
    run2.font.color.rgb = COLOR_MEDIUM_GRAY
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Separator line
    add_border_to_paragraph(p2, bottom=True)


def add_footer(
    doc: Document,
    condition_name: str = "",
    organization: str = "SOZO Brain Center",
    copyright_year: int = 2026,
) -> None:
    """Add branded footer with page number and copyright."""
    section = doc.sections[0]
    footer = section.footer
    footer.is_linked_to_previous = False

    for para in footer.paragraphs:
        para.clear()

    p1 = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p1.clear()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run_left = p1.add_run(f"\u00a9 {copyright_year} {organization}. All rights reserved. CONFIDENTIAL.  |  Page ")
    run_left.font.name = FONT_BODY
    run_left.font.size = Pt(8)
    run_left.font.color.rgb = COLOR_MEDIUM_GRAY

    # Page number field
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    r = p1.add_run()
    r._r.append(fldChar1)
    r._r.append(instrText)
    r._r.append(fldChar2)
    r.font.size = Pt(8)
    r.font.color.rgb = COLOR_MEDIUM_GRAY

    add_border_to_paragraph(p1, top=True)


def add_border_to_paragraph(paragraph, top: bool = False, bottom: bool = False) -> None:
    """Add top or bottom border to paragraph."""
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    if top:
        top_bdr = OxmlElement("w:top")
        top_bdr.set(qn("w:val"), "single")
        top_bdr.set(qn("w:sz"), "4")
        top_bdr.set(qn("w:color"), "1B3A5C")
        pBdr.append(top_bdr)
    if bottom:
        bot_bdr = OxmlElement("w:bottom")
        bot_bdr.set(qn("w:val"), "single")
        bot_bdr.set(qn("w:sz"), "4")
        bot_bdr.set(qn("w:color"), "1B3A5C")
        pBdr.append(bot_bdr)
    pPr.append(pBdr)
