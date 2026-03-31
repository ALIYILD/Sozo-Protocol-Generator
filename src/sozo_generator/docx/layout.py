"""Page layout and section configuration."""
from docx import Document
from docx.shared import Inches, Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from .styles import (
    COLOR_DARK_BLUE, COLOR_PRIMARY_BLUE, COLOR_BROWN, COLOR_GRAY,
    COLOR_ACCENT_RED, FONT_HEADING, FONT_BODY, add_horizontal_rule,
)
import logging

logger = logging.getLogger(__name__)

PAGE_MARGIN_CM = 2.54  # Standard 1 inch


def configure_page_layout(doc: Document) -> None:
    """Apply SOZO standard page layout: A4, standard margins."""
    for section in doc.sections:
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(PAGE_MARGIN_CM)
        section.right_margin = Cm(PAGE_MARGIN_CM)
        section.top_margin = Cm(3.0)
        section.bottom_margin = Cm(PAGE_MARGIN_CM)
        section.header_distance = Cm(1.27)
        section.footer_distance = Cm(1.27)


def add_title_block(
    doc: Document,
    title: str = "",
    subtitle: str = "",
    condition_name: str = "",
    tier_label: str = "",
    version: str = "Version 1.0",
    date_label: str = "",
    confidentiality: str = "CONFIDENTIAL",
    document_title: str = "",
    tier_description: str = "",
) -> None:
    """Add a formatted title block at the start of the document."""
    # Support both 'title' and legacy 'document_title' param
    doc_title = title or document_title

    # Organization name
    p_org = doc.add_paragraph()
    run_org = p_org.add_run("SOZO BRAIN CENTER")
    run_org.bold = True
    run_org.font.size = Pt(18)
    run_org.font.name = FONT_HEADING
    run_org.font.color.rgb = COLOR_DARK_BLUE
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_org.paragraph_format.space_before = Pt(0)
    p_org.paragraph_format.space_after = Pt(4)

    # Tagline
    p_tag = doc.add_paragraph()
    run_tag = p_tag.add_run("Evidence-Based Neuromodulation")
    run_tag.italic = True
    run_tag.font.size = Pt(11)
    run_tag.font.name = FONT_BODY
    run_tag.font.color.rgb = COLOR_PRIMARY_BLUE
    p_tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tag.paragraph_format.space_after = Pt(12)

    # Separator
    add_horizontal_rule(doc, "2E75B6")

    # Condition name
    if condition_name:
        p_cond = doc.add_paragraph()
        run_cond = p_cond.add_run(condition_name.upper())
        run_cond.bold = True
        run_cond.font.size = Pt(16)
        run_cond.font.name = FONT_HEADING
        run_cond.font.color.rgb = COLOR_DARK_BLUE
        p_cond.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cond.paragraph_format.space_before = Pt(12)
        p_cond.paragraph_format.space_after = Pt(4)

    # Document title
    if doc_title:
        p_title = doc.add_paragraph()
        run_title = p_title.add_run(doc_title)
        run_title.bold = True
        run_title.font.size = Pt(14)
        run_title.font.name = FONT_HEADING
        run_title.font.color.rgb = COLOR_PRIMARY_BLUE
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(8)

    # Subtitle
    if subtitle:
        p_sub = doc.add_paragraph()
        run_sub = p_sub.add_run(subtitle)
        run_sub.italic = True
        run_sub.font.size = Pt(11)
        run_sub.font.name = FONT_BODY
        run_sub.font.color.rgb = COLOR_PRIMARY_BLUE
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.paragraph_format.space_after = Pt(8)

    # Tier label
    if tier_label:
        p_tier = doc.add_paragraph()
        run_tier = p_tier.add_run(tier_label)
        run_tier.bold = True
        run_tier.font.size = Pt(11)
        run_tier.font.name = FONT_BODY
        run_tier.font.color.rgb = COLOR_ACCENT_RED
        p_tier.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Tier description (legacy)
    if tier_description:
        p_tier_desc = doc.add_paragraph()
        run_tier_desc = p_tier_desc.add_run(tier_description)
        run_tier_desc.italic = True
        run_tier_desc.font.size = Pt(10)
        run_tier_desc.font.name = FONT_BODY
        run_tier_desc.font.color.rgb = COLOR_PRIMARY_BLUE
        p_tier_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_tier_desc.paragraph_format.space_after = Pt(8)

    # Version / date
    p_meta = doc.add_paragraph()
    meta_text = version
    if date_label:
        meta_text += f"  |  {date_label}"
    run_meta = p_meta.add_run(meta_text)
    run_meta.font.size = Pt(9)
    run_meta.font.name = FONT_BODY
    run_meta.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Confidentiality
    p_conf = doc.add_paragraph()
    run_conf = p_conf.add_run(confidentiality)
    run_conf.bold = True
    run_conf.font.size = Pt(9)
    run_conf.font.name = FONT_BODY
    run_conf.font.color.rgb = COLOR_ACCENT_RED
    p_conf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_conf.paragraph_format.space_after = Pt(16)

    add_horizontal_rule(doc, "996600")
    doc.add_paragraph()
