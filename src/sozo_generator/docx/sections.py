"""Section renderer — converts SectionContent objects into docx paragraphs."""
import logging
import os
from pathlib import Path
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from ..schemas.documents import SectionContent
from .styles import (
    COLOR_DARK_BLUE, COLOR_PRIMARY_BLUE, COLOR_ACCENT_RED,
    COLOR_WARNING_ORANGE, COLOR_MEDIUM_GRAY, FONT_HEADING, FONT_BODY,
    add_horizontal_rule, apply_heading_style, apply_body_style,
)
from .tables import add_clinical_table, add_warning_box

logger = logging.getLogger(__name__)

PLACEHOLDER_MARKER = "[REVIEW REQUIRED"
REVIEW_FLAG_MARKER = "\u26a0"


def render_section(doc: Document, section: SectionContent, level: int = 1, depth: int = None, image_manifest=None) -> None:
    """Render a SectionContent object into the document.
    Accepts both 'level' and 'depth' parameter names for compatibility.
    If image_manifest is provided, inserts curated images after section content.
    """
    if depth is not None:
        level = depth

    # Section heading
    if section.title:
        _add_section_heading(doc, section.title, level)

    # Review flags / confidence label
    if section.review_flags:
        for flag in section.review_flags:
            add_warning_box(doc, flag, box_type="warning")

    # Placeholder indicator
    if section.is_placeholder:
        add_warning_box(
            doc,
            "[REVIEW REQUIRED] This section requires clinical review and content completion.",
            box_type="critical",
        )

    if section.confidence_label and section.confidence_label not in ("high_confidence",):
        _add_confidence_note(doc, section.confidence_label)

    # Main content
    if section.content:
        _render_content_text(doc, section.content, section.is_placeholder)

    # Tables
    for table_def in section.tables:
        if isinstance(table_def, dict):
            add_clinical_table(
                doc,
                headers=table_def.get("headers", []),
                rows=table_def.get("rows", []),
                caption=table_def.get("caption"),
            )

    # Figures (placeholders for now — actual figures inserted by images.py)
    for fig_path in section.figures:
        _add_figure_placeholder(doc, fig_path)

    # Curated images for this section (from web search / pre-curated library)
    if image_manifest is not None:
        _insert_curated_images(doc, section.section_id, image_manifest)

    # Subsections (recursive)
    for subsection in section.subsections:
        render_section(doc, subsection, level=min(level + 1, 4), image_manifest=image_manifest)

    # Spacing after section
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def _add_section_heading(doc: Document, title: str, level: int) -> None:
    """Add a styled section heading."""
    heading_colors = {
        1: COLOR_DARK_BLUE,
        2: COLOR_PRIMARY_BLUE,
        3: RGBColor(0x2E, 0x75, 0xB6),
        4: RGBColor(0x66, 0x66, 0x66),
    }
    heading_sizes = {1: 14, 2: 12, 3: 11, 4: 10}

    p = doc.add_paragraph()
    run = p.add_run(title)
    run.bold = True
    run.font.name = FONT_HEADING
    run.font.size = Pt(heading_sizes.get(level, 11))
    run.font.color.rgb = heading_colors.get(level, COLOR_PRIMARY_BLUE)
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(4)

    if level == 1:
        add_horizontal_rule(doc, "2E75B6")


def _render_content_text(doc: Document, content: str, is_placeholder: bool = False) -> None:
    """Render multi-line content text, handling bullet points and warnings."""
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)

        if line.startswith("\u2022 ") or line.startswith("- ") or line.startswith("* "):
            try:
                p.style = "List Bullet"
            except Exception:
                pass
            text = line[2:]
        elif line.startswith("\u2022") and len(line) > 1:
            try:
                p.style = "List Bullet"
            except Exception:
                pass
            text = line[1:].strip()
        elif len(line) > 2 and line[0].isdigit() and ". " in line[:4]:
            try:
                p.style = "List Number"
            except Exception:
                pass
            text = line[line.index(". ") + 2:]
        else:
            text = line

        # Determine text color
        if is_placeholder or PLACEHOLDER_MARKER in text:
            run = p.add_run(text)
            run.font.color.rgb = COLOR_ACCENT_RED
            run.font.bold = True
        elif text.startswith(REVIEW_FLAG_MARKER) or "REVIEW REQUIRED" in text:
            run = p.add_run(text)
            run.font.color.rgb = COLOR_WARNING_ORANGE
            run.font.bold = True
        elif text.startswith("CLINICAL TIP:"):
            run = p.add_run(text)
            run.font.color.rgb = COLOR_PRIMARY_BLUE
            run.font.italic = True
        elif text.startswith("GOVERNANCE RULE:") or text.startswith("MANDATORY:"):
            run = p.add_run(text)
            run.font.color.rgb = COLOR_DARK_BLUE
            run.font.bold = True
        else:
            run = p.add_run(text)
            run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)

        run.font.name = FONT_BODY
        run.font.size = Pt(11)


def _add_confidence_note(doc: Document, confidence_label: str) -> None:
    """Add a small confidence indicator note."""
    label_map = {
        "medium_confidence": ("Supported by emerging evidence", COLOR_PRIMARY_BLUE),
        "low_confidence": ("Consensus-informed \u2014 limited evidence", COLOR_WARNING_ORANGE),
        "insufficient": ("\u26a0 Evidence insufficient \u2014 clinician review required", COLOR_ACCENT_RED),
        "review_required": ("\u26a0 REVIEW REQUIRED", COLOR_ACCENT_RED),
    }
    label_text, color = label_map.get(confidence_label, ("Note", RGBColor(0x66, 0x66, 0x66)))
    p = doc.add_paragraph()
    run = p.add_run(f"[Evidence note: {label_text}]")
    run.italic = True
    run.font.size = Pt(9)
    run.font.name = FONT_BODY
    run.font.color.rgb = color
    p.paragraph_format.space_after = Pt(4)


def _add_figure_placeholder(doc: Document, fig_path: str) -> None:
    """Add a figure or figure placeholder."""
    if fig_path and Path(fig_path).exists():
        try:
            from .images import insert_image
            insert_image(doc, fig_path, width_cm=14.0)
            return
        except Exception as e:
            logger.warning(f"Could not insert figure {fig_path}: {e}")

    # Placeholder box
    p = doc.add_paragraph()
    run = p.add_run(f"[FIGURE: {os.path.basename(fig_path) if fig_path else 'diagram'}]")
    run.font.color.rgb = COLOR_PRIMARY_BLUE
    run.font.italic = True
    run.font.name = FONT_BODY
    run.font.size = Pt(10)


def _insert_curated_images(doc: Document, section_id: str, image_manifest) -> None:
    """Insert curated images for a section inline, with captions and attribution."""
    try:
        images = image_manifest.images_for_section(section_id)
    except Exception:
        return

    if not images:
        return

    for img in images:
        img_path = Path(str(img.local_path))
        if not img_path.exists():
            logger.debug(f"Curated image not found: {img_path}")
            continue

        try:
            from .images import insert_figure
            caption = img.caption
            if img.attribution and img.source != "precurated":
                caption += f" (Source: {img.attribution})"
            insert_figure(doc, str(img_path), caption=caption, width_inches=img.width_inches or 5.0)
        except Exception as e:
            logger.debug(f"Failed to insert curated image {img_path}: {e}")
