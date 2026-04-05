"""
Canonical DOCX exporter for the SOZO long-document production pipeline.

Renders a CanonicalDocument to a .docx file via python-docx.
This is independent of the legacy DocumentRenderer / DocumentExporter.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Any, Optional

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
)

logger = logging.getLogger(__name__)


class CanonicalDocxExporter:
    """
    Renders a CanonicalDocument to a DOCX file using python-docx.

    Handles:
    - Title page
    - TOC placeholder (Word-updatable field)
    - Section headings (levels 1-4)
    - Body text paragraphs
    - Tables (from asset_record.source_data or inline table data)
    - Figures/images (from asset_record.output_path)
    - Captions
    - Numbered tables and figures
    - References section
    - Appendices
    - Page breaks
    - Header/footer with document info
    """

    SOZO_PURPLE = RGBColor(0x6B, 0x4F, 0xA0)
    SOZO_LIGHT_PURPLE = RGBColor(0xE8, 0xE0, 0xF5)
    FONT_HEADING = "Calibri"
    FONT_BODY = "Calibri"

    def __init__(self, output_dir: str = "outputs/documents"):
        self.output_dir = output_dir

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def export(
        self,
        document: CanonicalDocument,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Render CanonicalDocument to DOCX.

        Args:
            document: The CanonicalDocument to render.
            output_path: Where to save the file. If None, auto-generated from
                         condition/variant/document_type.

        Returns:
            Absolute path to the generated DOCX file.
        """
        if output_path is None:
            output_path = self._build_output_path(document)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        doc = Document()
        self._setup_document(doc)
        self._add_header_footer(doc, document)
        self._add_title_page(doc, document)
        doc.add_page_break()
        self._add_toc_placeholder(doc)
        doc.add_page_break()

        self._render_sections(doc, document.sections, document)

        if document.references:
            self._render_ref_list(doc, document.references)

        if document.appendices:
            doc.add_page_break()
            self._render_appendices(doc, document.appendices)

        doc.save(output_path)
        logger.info("Saved canonical DOCX: %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Output path
    # ------------------------------------------------------------------

    def _build_output_path(self, document: CanonicalDocument) -> str:
        """Build deterministic output path:
        outputs/documents/{condition_slug}/{variant}/canonical/{document_type}_{variant}.docx
        """
        parts = [
            self.output_dir,
            document.condition_slug,
            document.variant,
            "canonical",
        ]
        filename = f"{document.document_type}_{document.variant}.docx"
        return os.path.join(*parts, filename)

    # ------------------------------------------------------------------
    # Page layout
    # ------------------------------------------------------------------

    def _setup_document(self, doc: Document) -> None:
        """Configure page layout: A4, standard margins."""
        section = doc.sections[0]
        section.page_width = Cm(21.0)
        section.page_height = Cm(29.7)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)

    # ------------------------------------------------------------------
    # Title page
    # ------------------------------------------------------------------

    def _add_title_page(self, doc: Document, document: CanonicalDocument) -> None:
        """Add title, subtitle, condition name, variant, date, version."""
        # Spacer
        for _ in range(4):
            doc.add_paragraph()

        # Main title
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_title.add_run(document.title)
        run.font.name = self.FONT_HEADING
        run.font.size = Pt(28)
        run.font.bold = True
        run.font.color.rgb = self.SOZO_PURPLE
        p_title.paragraph_format.space_after = Pt(12)

        # Subtitle
        if document.subtitle:
            p_sub = doc.add_paragraph()
            p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p_sub.add_run(document.subtitle)
            run.font.name = self.FONT_HEADING
            run.font.size = Pt(16)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            p_sub.paragraph_format.space_after = Pt(24)

        # Horizontal rule
        self._add_thin_rule(doc)

        # Metadata block
        meta_lines = [
            ("Condition", document.condition_slug.replace("_", " ").title()),
            ("Variant", document.variant.capitalize()),
            ("Document Type", document.document_type.replace("_", " ").title()),
            ("Version", document.version),
            ("Date", datetime.utcnow().strftime("%B %Y")),
        ]
        for label, value in meta_lines:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_label = p.add_run(f"{label}: ")
            run_label.font.bold = True
            run_label.font.size = Pt(11)
            run_label.font.name = self.FONT_BODY
            run_value = p.add_run(value)
            run_value.font.size = Pt(11)
            run_value.font.name = self.FONT_BODY
            p.paragraph_format.space_after = Pt(4)

        self._add_thin_rule(doc)

        # SOZO branding line
        p_brand = doc.add_paragraph()
        p_brand.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_brand.add_run("SOZO Brain Center — Clinical Document Production System")
        run.font.name = self.FONT_HEADING
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # ------------------------------------------------------------------
    # TOC placeholder
    # ------------------------------------------------------------------

    def _add_toc_placeholder(self, doc: Document) -> None:
        """Add a Word-updatable TOC field placeholder."""
        p_heading = doc.add_heading("Table of Contents", level=1)
        self._apply_heading_style(p_heading, level=1)

        p_toc = doc.add_paragraph()
        run = p_toc.add_run()

        fldChar_begin = OxmlElement("w:fldChar")
        fldChar_begin.set(qn("w:fldCharType"), "begin")
        run._r.append(fldChar_begin)

        instrText = OxmlElement("w:instrText")
        instrText.set(qn("xml:space"), "preserve")
        instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
        run._r.append(instrText)

        fldChar_sep = OxmlElement("w:fldChar")
        fldChar_sep.set(qn("w:fldCharType"), "separate")
        run._r.append(fldChar_sep)

        run2 = p_toc.add_run(
            "[Right-click and select 'Update Field' to generate Table of Contents]"
        )
        run2.font.size = Pt(10)
        run2.font.italic = True
        run2.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

        run3 = p_toc.add_run()
        fldChar_end = OxmlElement("w:fldChar")
        fldChar_end.set(qn("w:fldCharType"), "end")
        run3._r.append(fldChar_end)

    # ------------------------------------------------------------------
    # Header / footer
    # ------------------------------------------------------------------

    def _add_header_footer(self, doc: Document, document: CanonicalDocument) -> None:
        """Add running header with document title; footer with page number."""
        section = doc.sections[0]
        section.different_first_page_header_footer = True

        # Header (non-first pages)
        header = section.header
        p_header = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p_header.clear()
        p_header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p_header.add_run(document.title)
        run.font.name = self.FONT_HEADING
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

        # Footer with page number
        footer = section.footer
        p_footer = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p_footer.clear()
        p_footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run_left = p_footer.add_run(
            f"SOZO Brain Center | {document.condition_slug.replace('_', ' ').title()} | "
            f"v{document.version}    Page "
        )
        run_left.font.name = self.FONT_BODY
        run_left.font.size = Pt(8)
        run_left.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

        # Page number field
        fldChar1 = OxmlElement("w:fldChar")
        fldChar1.set(qn("w:fldCharType"), "begin")
        instrText = OxmlElement("w:instrText")
        instrText.set(qn("xml:space"), "preserve")
        instrText.text = " PAGE "
        fldChar2 = OxmlElement("w:fldChar")
        fldChar2.set(qn("w:fldCharType"), "end")
        run_pg = p_footer.add_run()
        run_pg._r.append(fldChar1)
        run_pg._r.append(instrText)
        run_pg._r.append(fldChar2)
        run_pg.font.size = Pt(8)
        run_pg.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    # ------------------------------------------------------------------
    # Section rendering
    # ------------------------------------------------------------------

    def _render_sections(
        self, doc: Document, sections: list, document: CanonicalDocument
    ) -> None:
        """Render all canonical sections recursively."""
        for section in sorted(sections, key=lambda s: s.ordering):
            self._render_section(doc, section, document, level=section.level or 1)

    def _render_section(
        self,
        doc: Document,
        section: Any,
        document: Optional[CanonicalDocument],
        level: int = 1,
    ) -> None:
        """Render a single CanonicalSection including its blocks and subsections."""
        if section.page_break_before if hasattr(section, "page_break_before") else False:
            doc.add_page_break()

        # Section heading
        heading_level = min(level, 4)
        p = doc.add_heading(section.title, level=heading_level)
        self._apply_heading_style(p, level=heading_level)

        # Blocks
        for block in section.blocks:
            self._render_block(doc, block, document)

        # Subsections
        for subsection in sorted(section.subsections, key=lambda s: s.ordering):
            self._render_section(doc, subsection, document, level=level + 1)

    # ------------------------------------------------------------------
    # Block rendering
    # ------------------------------------------------------------------

    def _render_block(
        self, doc: Document, block: Any, document: Optional[CanonicalDocument] = None
    ) -> None:
        """
        Render a single CanonicalBlock based on block_type.

        Supported types:
        - "text"      -> paragraph
        - "heading"   -> heading at block.heading_level
        - "table"     -> table from asset_record.source_data
        - "figure"    -> embedded image from asset_record.output_path
        - "chart"     -> embedded image from asset_record.output_path
        - "image"     -> embedded image from asset_record.output_path
        - "list"      -> bulleted list
        - "callout"   -> highlighted paragraph with shading
        - "divider"   -> thin horizontal rule
        - "pagebreak" -> page break
        """
        bt = block.block_type

        if block.page_break_before:
            doc.add_page_break()

        if bt == "pagebreak":
            doc.add_page_break()

        elif bt == "divider":
            self._add_thin_rule(doc)

        elif bt == "heading":
            lvl = min(max(block.heading_level or 2, 1), 4)
            text = block.heading or block.content or ""
            p = doc.add_heading(text, level=lvl)
            self._apply_heading_style(p, level=lvl)

        elif bt == "text":
            content = block.content or ""
            if content.strip():
                p = doc.add_paragraph()
                run = p.add_run(content)
                run.font.name = self.FONT_BODY
                run.font.size = Pt(11)
                p.paragraph_format.space_after = Pt(6)

        elif bt == "list":
            content = block.content or ""
            lines = [ln.lstrip("-*• ").strip() for ln in content.splitlines() if ln.strip()]
            for line in lines:
                p = doc.add_paragraph(style="List Bullet")
                run = p.add_run(line)
                run.font.name = self.FONT_BODY
                run.font.size = Pt(11)

        elif bt == "callout":
            content = block.content or ""
            p = doc.add_paragraph()
            run = p.add_run(content)
            run.font.name = self.FONT_BODY
            run.font.size = Pt(11)
            run.font.bold = True
            # Light purple shading on the paragraph via XML
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "E8E0F5")
            pPr.append(shd)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.left_indent = Pt(18)
            p.paragraph_format.right_indent = Pt(18)

        elif bt in ("table",):
            self._render_table_asset(doc, block)

        elif bt in ("figure", "chart", "image"):
            self._render_figure_asset(doc, block)

        elif bt == "appendix_entry":
            content = block.content or block.heading or ""
            if content.strip():
                p = doc.add_paragraph()
                run = p.add_run(content)
                run.font.name = self.FONT_BODY
                run.font.size = Pt(11)

        elif bt == "toc_entry":
            pass  # TOC entries handled separately

        else:
            # Unknown block type — render as plain text if content present
            content = block.content or ""
            if content.strip():
                p = doc.add_paragraph()
                run = p.add_run(content)
                run.font.name = self.FONT_BODY
                run.font.size = Pt(11)
                run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # ------------------------------------------------------------------
    # Table rendering
    # ------------------------------------------------------------------

    def _render_table_asset(self, doc: Document, block: Any) -> None:
        """
        Render a table from asset_record.source_data.

        source_data format::

            {
                "headers": ["Col1", "Col2", ...],
                "rows": [["val", "val", ...], ...],
                "title": "Table title",
                "landscape": False,
                "footer": "Optional footnote",
            }

        If landscape=True, a note is added. Full landscape support requires
        a separate document section and is left as TODO.
        """
        asset: Optional[AssetRecord] = getattr(block, "asset_record", None)
        source_data: dict = {}

        if asset is not None:
            source_data = asset.source_data or {}
        # Fallback: block may carry inline metadata
        if not source_data:
            source_data = block.metadata or {}

        if not source_data:
            p = doc.add_paragraph()
            title = getattr(block, "caption", None) or (
                block.numbering_label or "Table"
            )
            run = p.add_run(f"[Table placeholder: {title} — no source data]")
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
            return

        headers: list = source_data.get("headers", [])
        rows: list = source_data.get("rows", [])
        title: str = source_data.get("title", "")
        landscape: bool = source_data.get("landscape", False)
        footer: str = source_data.get("footer", "")

        # Landscape note
        if landscape:
            p_note = doc.add_paragraph()
            run = p_note.add_run("(See landscape table — wide table, consider printing in landscape)")
            run.font.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x77, 0x77, 0x77)

        if not headers and not rows:
            p = doc.add_paragraph()
            run = p.add_run(f"[Table: {title or 'Untitled'} — no data rows]")
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
            return

        col_count = max(len(headers), max((len(r) for r in rows), default=0))
        if col_count == 0:
            return

        table = doc.add_table(rows=1 + len(rows), cols=col_count)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"

        # Header row
        hdr_row = table.rows[0]
        for ci, hdr_text in enumerate(headers):
            cell = hdr_row.cells[ci]
            cell.text = ""
            p_cell = cell.paragraphs[0]
            run = p_cell.add_run(str(hdr_text))
            run.font.name = self.FONT_BODY
            run.font.size = Pt(10)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            # Purple header background
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), "6B4FA0")
            tcPr.append(shd)

        # Data rows
        for ri, row_data in enumerate(rows):
            tbl_row = table.rows[ri + 1]
            fill_hex = "F3F0F8" if ri % 2 == 0 else "FFFFFF"
            for ci in range(col_count):
                cell = tbl_row.cells[ci]
                cell.text = ""
                p_cell = cell.paragraphs[0]
                cell_text = str(row_data[ci]) if ci < len(row_data) else ""
                run = p_cell.add_run(cell_text)
                run.font.name = self.FONT_BODY
                run.font.size = Pt(10)
                # Zebra stripe shading
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), fill_hex)
                tcPr.append(shd)

        # Footer row (footnote)
        if footer:
            p_footer = doc.add_paragraph()
            run = p_footer.add_run(footer)
            run.font.name = self.FONT_BODY
            run.font.size = Pt(8)
            run.font.italic = True
            p_footer.paragraph_format.space_before = Pt(2)
            p_footer.paragraph_format.space_after = Pt(4)

        # Caption
        caption_text = (
            block.caption
            or (asset.caption if asset else None)
            or (block.numbering_label or "")
        )
        if caption_text:
            self._add_caption(doc, caption_text)
        elif title:
            self._add_caption(doc, title)

        doc.add_paragraph()  # spacing after table

    # ------------------------------------------------------------------
    # Figure rendering
    # ------------------------------------------------------------------

    def _render_figure_asset(self, doc: Document, block: Any) -> None:
        """
        Embed an image from asset_record.output_path.

        If the file doesn't exist, adds a placeholder paragraph.
        """
        asset: Optional[AssetRecord] = getattr(block, "asset_record", None)
        output_path: Optional[str] = None

        if asset is not None:
            output_path = asset.output_path

        caption_text = (
            block.caption
            or (asset.caption if asset else None)
            or block.numbering_label
            or (asset.numbering_label if asset else None)
            or "Figure"
        )

        if output_path and os.path.isfile(output_path):
            try:
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p_img.add_run()
                run.add_picture(output_path, width=Inches(5.5))
            except Exception as exc:
                logger.warning("Could not embed image %s: %s", output_path, exc)
                p = doc.add_paragraph()
                run = p.add_run(
                    f"[Figure could not be embedded: {os.path.basename(output_path)} — {exc}]"
                )
                run.font.italic = True
                run.font.color.rgb = RGBColor(0xCC, 0x44, 0x44)
        else:
            # Placeholder
            title = (asset.source_data.get("title", "") if asset and asset.source_data else "") or caption_text
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f"[Figure: {title} — not generated]")
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

        if caption_text:
            self._add_caption(doc, caption_text)

        doc.add_paragraph()  # spacing after figure

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    def _render_references(self, doc: Document, sections: list) -> None:
        """Render the references section from document.references."""
        # This method receives sections for interface compatibility but we
        # need the document-level references. Called from export() with
        # document.references pre-checked.
        pass  # Actual rendering is driven from export() calling _render_ref_list()

    def _render_ref_list(self, doc: Document, references: list) -> None:
        """Internal: render citations list."""
        doc.add_page_break()
        p = doc.add_heading("References & Evidence Sources", level=1)
        self._apply_heading_style(p, level=1)

        for i, citation in enumerate(references, 1):
            p_ref = doc.add_paragraph()
            p_ref.paragraph_format.left_indent = Pt(24)
            p_ref.paragraph_format.first_line_indent = Pt(-18)

            authors = getattr(citation, "authors_short", "") or ""
            year = getattr(citation, "year", "n.d.") or "n.d."
            title = getattr(citation, "title", "[No title]") or "[No title]"
            journal = getattr(citation, "journal", "") or ""
            pmid = getattr(citation, "pmid", "") or ""
            doi = getattr(citation, "doi", "") or ""

            parts = [f"{i}. {authors} ({year}). {title}."]
            if journal:
                parts.append(f" {journal}.")
            if pmid:
                parts.append(f" PMID: {pmid}.")
            if doi:
                parts.append(f" DOI: {doi}.")

            run = p_ref.add_run("".join(parts))
            run.font.name = self.FONT_BODY
            run.font.size = Pt(9)

    # ------------------------------------------------------------------
    # Appendices
    # ------------------------------------------------------------------

    def _render_appendices(self, doc: Document, appendices: list) -> None:
        """Render appendix sections."""
        p = doc.add_heading("Appendices", level=1)
        self._apply_heading_style(p, level=1)
        for appendix in sorted(appendices, key=lambda s: s.ordering):
            self._render_section(doc, appendix, None, level=2)

    # ------------------------------------------------------------------
    # Caption
    # ------------------------------------------------------------------

    def _add_caption(self, doc: Document, caption: str) -> None:
        """Add a caption paragraph (italic, small, centered)."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(caption)
        run.font.name = self.FONT_BODY
        run.font.size = Pt(9)
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)

    # ------------------------------------------------------------------
    # Heading styles
    # ------------------------------------------------------------------

    def _apply_heading_style(self, para: Any, level: int) -> None:
        """Apply SOZO purple heading styles."""
        sizes = {1: 16, 2: 14, 3: 12, 4: 11}
        colors = {
            1: self.SOZO_PURPLE,
            2: RGBColor(0x52, 0x3C, 0x78),
            3: RGBColor(0x3D, 0x2E, 0x5A),
            4: RGBColor(0x33, 0x26, 0x4A),
        }
        size = sizes.get(level, 11)
        color = colors.get(level, self.SOZO_PURPLE)

        if para.runs:
            for run in para.runs:
                run.font.name = self.FONT_HEADING
                run.font.size = Pt(size)
                run.font.bold = True
                run.font.color.rgb = color
        else:
            # Paragraph has no run objects yet — add one
            run = para.add_run()
            run.font.name = self.FONT_HEADING
            run.font.size = Pt(size)
            run.font.bold = True
            run.font.color.rgb = color

        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        para.paragraph_format.space_before = Pt(12 if level == 1 else 8)
        para.paragraph_format.space_after = Pt(6)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _add_thin_rule(self, doc: Document) -> None:
        """Add a thin horizontal rule paragraph."""
        p = doc.add_paragraph()
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "4")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "6B4FA0")
        pBdr.append(bottom)
        pPr.append(pBdr)
        p.paragraph_format.space_after = Pt(8)
