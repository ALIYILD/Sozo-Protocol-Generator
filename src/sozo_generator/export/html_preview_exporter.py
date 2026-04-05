"""
HTML preview exporter for the SOZO long-document production pipeline.

Renders a CanonicalDocument to self-contained HTML for browser preview,
review, or PDF conversion via headless browser.
"""
from __future__ import annotations

import html
import logging
import os
from datetime import datetime
from typing import Any, Optional

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
)

logger = logging.getLogger(__name__)


class HTMLPreviewExporter:
    """
    Renders a CanonicalDocument to HTML for preview/review purposes.

    Generates clean, self-contained HTML with inline CSS.
    Suitable for browser preview, email, or PDF conversion via browser.
    No external resources are required — all CSS is inlined.
    """

    def __init__(self, output_dir: str = "outputs/documents"):
        self.output_dir = output_dir

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def export(
        self,
        document: CanonicalDocument,
        output_path: Optional[str] = None,
        include_qa: bool = True,
    ) -> str:
        """
        Render CanonicalDocument to HTML.

        Args:
            document: The CanonicalDocument to render.
            output_path: Destination path. Auto-generated if None.
            include_qa: Whether to include QA badge in footer.

        Returns:
            Path to the generated HTML file.
        """
        if output_path is None:
            output_path = self._build_output_path(document)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        content = self._render_html(document, include_qa=include_qa)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        logger.info("Saved canonical HTML: %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    # Output path
    # ------------------------------------------------------------------

    def _build_output_path(self, document: CanonicalDocument) -> str:
        """outputs/documents/{condition}/{variant}/canonical/{document_type}_{variant}.html"""
        parts = [
            self.output_dir,
            document.condition_slug,
            document.variant,
            "canonical",
        ]
        filename = f"{document.document_type}_{document.variant}.html"
        return os.path.join(*parts, filename)

    # ------------------------------------------------------------------
    # Full HTML render
    # ------------------------------------------------------------------

    def _render_html(self, document: CanonicalDocument, include_qa: bool) -> str:
        """Return full HTML string."""
        title_esc = html.escape(document.title)
        subtitle_esc = html.escape(document.subtitle or "")

        toc_html = self._render_toc(document)

        # Main sections
        sections_html_parts = []
        for section in sorted(document.sections, key=lambda s: s.ordering):
            sections_html_parts.append(self._render_section(section, level=1))
        sections_html = "\n".join(sections_html_parts)

        # References
        references_html = ""
        if document.references:
            references_html = self._render_references(document)

        # Appendices
        appendices_html = ""
        if document.appendices:
            appendices_html = "<section class='appendices'>\n<h2>Appendices</h2>\n"
            for appendix in sorted(document.appendices, key=lambda s: s.ordering):
                appendices_html += self._render_section(appendix, level=2)
            appendices_html += "</section>\n"

        # QA badge
        qa_html = ""
        if include_qa:
            qa_html = self._render_qa_badge(document)

        # Generation metadata
        gen_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title_esc}</title>
  <style>
{self._css()}
  </style>
</head>
<body>

<header class="doc-header">
  <div class="doc-header-inner">
    <div class="doc-brand">SOZO Brain Center</div>
    <h1 class="doc-title">{title_esc}</h1>
    {f'<p class="doc-subtitle">{subtitle_esc}</p>' if subtitle_esc else ''}
    <div class="doc-meta">
      <span><strong>Condition:</strong> {html.escape(document.condition_slug.replace('_', ' ').title())}</span>
      <span><strong>Variant:</strong> {html.escape(document.variant.capitalize())}</span>
      <span><strong>Type:</strong> {html.escape(document.document_type.replace('_', ' ').title())}</span>
      <span><strong>Version:</strong> {html.escape(document.version)}</span>
      <span><strong>Generated:</strong> {gen_date}</span>
    </div>
  </div>
</header>

<div class="doc-body">

  <nav id="toc">
    <h2 class="toc-heading">Table of Contents</h2>
    {toc_html}
  </nav>

  <main>
    {sections_html}
    {references_html}
    {appendices_html}
  </main>

</div>

<footer class="doc-footer">
  <div class="footer-inner">
    {qa_html}
    <p class="footer-meta">
      Generated by SOZO Protocol Generator &mdash;
      {html.escape(document.condition_slug)} / {html.escape(document.variant)} /
      v{html.escape(document.version)} &mdash; {gen_date}
    </p>
    <p class="footer-disclaimer">
      <strong>Clinical Decision Support Disclaimer:</strong>
      This document is intended to assist qualified healthcare professionals.
      It does NOT constitute medical advice or autonomous prescribing.
      All recommendations must be independently reviewed by a qualified clinician.
    </p>
  </div>
</footer>

</body>
</html>
"""

    # ------------------------------------------------------------------
    # CSS
    # ------------------------------------------------------------------

    def _css(self) -> str:
        """Return inline CSS string. SOZO purple theme (#6B4FA0)."""
        return """
    :root {
      --sozo-purple: #6B4FA0;
      --sozo-purple-dark: #523C78;
      --sozo-purple-light: #E8E0F5;
      --sozo-purple-mid: #9B7EC8;
      --text-primary: #1a1a2e;
      --text-secondary: #444;
      --text-muted: #777;
      --bg-page: #f8f7fc;
      --bg-white: #ffffff;
      --border-light: #ddd8ed;
      --font-heading: 'Segoe UI', Calibri, Arial, sans-serif;
      --font-body: 'Segoe UI', Calibri, Arial, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--font-body);
      font-size: 11pt;
      line-height: 1.6;
      color: var(--text-primary);
      background: var(--bg-page);
    }

    /* Header */
    .doc-header {
      background: linear-gradient(135deg, var(--sozo-purple) 0%, var(--sozo-purple-dark) 100%);
      color: white;
      padding: 2.5rem 3rem 2rem;
    }
    .doc-header-inner { max-width: 960px; margin: 0 auto; }
    .doc-brand {
      font-size: 0.8rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      opacity: 0.8;
      margin-bottom: 0.75rem;
    }
    .doc-title {
      font-family: var(--font-heading);
      font-size: 2rem;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 0.5rem;
    }
    .doc-subtitle {
      font-size: 1.1rem;
      opacity: 0.85;
      font-style: italic;
      margin-bottom: 1.25rem;
    }
    .doc-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem 1.5rem;
      font-size: 0.85rem;
      opacity: 0.9;
    }
    .doc-meta span { white-space: nowrap; }

    /* Layout */
    .doc-body {
      max-width: 1100px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 240px 1fr;
      gap: 2rem;
      padding: 2rem 1.5rem;
      align-items: start;
    }

    /* TOC */
    #toc {
      position: sticky;
      top: 1.5rem;
      background: var(--bg-white);
      border: 1px solid var(--border-light);
      border-radius: 6px;
      padding: 1.25rem;
      font-size: 0.85rem;
      max-height: calc(100vh - 3rem);
      overflow-y: auto;
    }
    .toc-heading {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--sozo-purple);
      margin-bottom: 0.75rem;
      font-weight: 700;
    }
    #toc ul { list-style: none; padding-left: 0; }
    #toc li { margin: 0.2rem 0; }
    #toc ul ul { padding-left: 1rem; }
    #toc ul ul li { font-size: 0.82rem; }
    #toc a {
      color: var(--text-secondary);
      text-decoration: none;
      display: block;
      padding: 0.1rem 0.25rem;
      border-radius: 3px;
      transition: background 0.15s, color 0.15s;
    }
    #toc a:hover {
      background: var(--sozo-purple-light);
      color: var(--sozo-purple);
    }

    /* Main content */
    main { min-width: 0; }

    /* Sections */
    .doc-section {
      background: var(--bg-white);
      border: 1px solid var(--border-light);
      border-radius: 6px;
      padding: 1.75rem 2rem;
      margin-bottom: 1.5rem;
    }

    h1, h2, h3, h4 {
      font-family: var(--font-heading);
      color: var(--sozo-purple);
      line-height: 1.3;
    }
    h1 { font-size: 1.6rem; margin-bottom: 1rem; padding-bottom: 0.5rem;
         border-bottom: 2px solid var(--sozo-purple-light); }
    h2 { font-size: 1.3rem; margin-top: 1.5rem; margin-bottom: 0.75rem;
         color: var(--sozo-purple-dark); }
    h3 { font-size: 1.1rem; margin-top: 1.25rem; margin-bottom: 0.5rem;
         color: #3D2E5A; }
    h4 { font-size: 1rem; margin-top: 1rem; margin-bottom: 0.4rem;
         color: #33264A; }

    /* Body text */
    p { margin-bottom: 0.75rem; color: var(--text-secondary); }

    /* Lists */
    ul.content-list, ol.content-list {
      padding-left: 1.75rem;
      margin-bottom: 0.75rem;
      color: var(--text-secondary);
    }
    ul.content-list li, ol.content-list li { margin: 0.25rem 0; }

    /* Callout */
    .callout {
      background: var(--sozo-purple-light);
      border-left: 4px solid var(--sozo-purple);
      border-radius: 0 4px 4px 0;
      padding: 0.75rem 1rem;
      margin: 0.75rem 0;
      font-weight: 500;
      color: var(--sozo-purple-dark);
    }

    /* Divider */
    hr.section-divider {
      border: none;
      border-top: 1px solid var(--border-light);
      margin: 1.25rem 0;
    }

    /* Page break hint */
    .pagebreak { display: block; height: 1px; margin: 1rem 0; }
    @media print { .pagebreak { page-break-after: always; } }

    /* Tables */
    .table-wrapper { overflow-x: auto; margin: 1rem 0; }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
    }
    th {
      background: var(--sozo-purple);
      color: white;
      text-align: left;
      padding: 0.6rem 0.75rem;
      font-weight: 600;
    }
    td {
      padding: 0.5rem 0.75rem;
      border-bottom: 1px solid var(--border-light);
      color: var(--text-secondary);
    }
    tr:nth-child(even) td { background: #F3F0F8; }
    tr:hover td { background: var(--sozo-purple-light); }
    .table-footer {
      font-size: 0.8rem;
      color: var(--text-muted);
      font-style: italic;
      margin-top: 0.35rem;
    }

    /* Figures */
    figure {
      text-align: center;
      margin: 1.25rem 0;
    }
    figure img {
      max-width: 100%;
      max-height: 480px;
      border: 1px solid var(--border-light);
      border-radius: 4px;
    }
    figcaption {
      font-size: 0.85rem;
      color: var(--text-muted);
      font-style: italic;
      margin-top: 0.4rem;
    }
    .figure-placeholder {
      background: var(--sozo-purple-light);
      border: 2px dashed var(--sozo-purple-mid);
      border-radius: 4px;
      padding: 2rem;
      color: var(--sozo-purple-dark);
      font-style: italic;
      text-align: center;
    }

    /* Caption */
    .caption {
      font-size: 0.85rem;
      color: var(--text-muted);
      font-style: italic;
      text-align: center;
      margin-top: 0.35rem;
    }

    /* References */
    .references ol { padding-left: 1.5rem; }
    .references li {
      font-size: 0.88rem;
      margin-bottom: 0.4rem;
      color: var(--text-secondary);
    }

    /* QA Badge */
    .qa-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.4rem 0.85rem;
      border-radius: 4px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
    }
    .qa-badge.passed { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .qa-badge.failed { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .qa-badge.pending { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }

    /* Footer */
    .doc-footer {
      background: var(--sozo-purple-dark);
      color: rgba(255,255,255,0.8);
      padding: 1.5rem 3rem;
      margin-top: 2rem;
    }
    .footer-inner { max-width: 960px; margin: 0 auto; }
    .footer-meta {
      font-size: 0.8rem;
      margin-bottom: 0.5rem;
      color: rgba(255,255,255,0.7);
    }
    .footer-disclaimer {
      font-size: 0.78rem;
      color: rgba(255,255,255,0.55);
      max-width: 800px;
      line-height: 1.5;
    }
    .footer-disclaimer strong { color: rgba(255,255,255,0.75); }

    @media (max-width: 768px) {
      .doc-body { grid-template-columns: 1fr; }
      #toc { position: static; max-height: none; }
      .doc-header { padding: 1.5rem; }
    }
    """

    # ------------------------------------------------------------------
    # TOC
    # ------------------------------------------------------------------

    def _render_toc(self, document: CanonicalDocument) -> str:
        """Render TOC as nested <ul> from document.toc_entries or sections."""
        entries = document.toc_entries
        if not entries:
            # Build on the fly from sections
            entries = []
            def _walk(sections, level=1):
                for s in sorted(sections, key=lambda x: x.ordering):
                    entries.append({
                        "title": s.title,
                        "level": level,
                        "section_id": s.section_id,
                    })
                    _walk(s.subsections, level + 1)
            _walk(document.sections)

        if not entries:
            return "<p><em>No sections</em></p>"

        lines = ["<ul>"]
        prev_level = 1
        for entry in entries:
            level = entry.get("level", 1)
            title = html.escape(entry.get("title", ""))
            section_id = html.escape(entry.get("section_id", ""))

            if level > prev_level:
                for _ in range(level - prev_level):
                    lines.append("<ul>")
            elif level < prev_level:
                for _ in range(prev_level - level):
                    lines.append("</ul></li>")

            lines.append(f'<li><a href="#{section_id}">{title}</a>')
            prev_level = level

        # Close all open lists
        for _ in range(prev_level):
            lines.append("</li></ul>")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Section
    # ------------------------------------------------------------------

    def _render_section(self, section: Any, level: int = 1) -> str:
        """Render a CanonicalSection to HTML. Recursive for subsections."""
        section_id = html.escape(section.section_id)
        title = html.escape(section.title)
        htag = f"h{min(level, 4)}"

        blocks_html = "\n".join(self._render_block(block) for block in section.blocks)

        subsections_html = "\n".join(
            self._render_section(sub, level=level + 1)
            for sub in sorted(section.subsections, key=lambda s: s.ordering)
        )

        return (
            f'<section class="doc-section" id="{section_id}">\n'
            f'  <{htag}>{title}</{htag}>\n'
            f'  {blocks_html}\n'
            f'  {subsections_html}\n'
            f'</section>\n'
        )

    # ------------------------------------------------------------------
    # Block
    # ------------------------------------------------------------------

    def _render_block(self, block: Any) -> str:
        """Render a CanonicalBlock to an HTML fragment."""
        bt = block.block_type

        if bt == "pagebreak":
            return '<div class="pagebreak"></div>'

        if bt == "divider":
            return '<hr class="section-divider">'

        if bt == "heading":
            lvl = min(max(block.heading_level or 2, 1), 4)
            text = html.escape(block.heading or block.content or "")
            return f'<h{lvl}>{text}</h{lvl}>'

        if bt == "text":
            content = block.content or ""
            if not content.strip():
                return ""
            return f'<p>{html.escape(content)}</p>'

        if bt == "list":
            content = block.content or ""
            lines = [ln.lstrip("-*• ").strip() for ln in content.splitlines() if ln.strip()]
            if not lines:
                return ""
            items = "".join(f"<li>{html.escape(ln)}</li>" for ln in lines)
            return f'<ul class="content-list">{items}</ul>'

        if bt == "callout":
            content = html.escape(block.content or "")
            return f'<div class="callout">{content}</div>'

        if bt == "table":
            return self._render_table_html(block)

        if bt in ("figure", "chart", "image"):
            return self._render_figure_html(block)

        if bt == "appendix_entry":
            content = html.escape(block.content or block.heading or "")
            return f'<p>{content}</p>' if content else ""

        if bt == "toc_entry":
            return ""

        # Fallback
        content = block.content or ""
        if content.strip():
            return f'<p class="unknown-block">{html.escape(content)}</p>'
        return ""

    # ------------------------------------------------------------------
    # Table HTML
    # ------------------------------------------------------------------

    def _render_table_html(self, block: Any) -> str:
        """Render a table from asset_record.source_data as HTML <table>."""
        asset: Optional[AssetRecord] = getattr(block, "asset_record", None)
        source_data: dict = {}

        if asset is not None:
            source_data = asset.source_data or {}
        if not source_data:
            source_data = block.metadata or {}

        if not source_data:
            label = html.escape(
                block.caption or block.numbering_label or "Table"
            )
            return f'<p class="figure-placeholder">[Table: {label} — no source data]</p>'

        headers = source_data.get("headers", [])
        rows = source_data.get("rows", [])
        title = source_data.get("title", "")
        footer = source_data.get("footer", "")
        landscape = source_data.get("landscape", False)

        caption_text = (
            block.caption
            or (asset.caption if asset else None)
            or block.numbering_label
            or title
        )

        if not headers and not rows:
            return f'<p class="figure-placeholder">[Table: {html.escape(title or "Untitled")} — no data]</p>'

        # Build HTML
        parts = ['<div class="table-wrapper"><table>']

        if headers:
            parts.append("<thead><tr>")
            for h in headers:
                parts.append(f"<th>{html.escape(str(h))}</th>")
            parts.append("</tr></thead>")

        if rows:
            parts.append("<tbody>")
            for row in rows:
                parts.append("<tr>")
                col_count = max(len(headers), len(row)) if headers else len(row)
                for ci in range(col_count):
                    cell_val = str(row[ci]) if ci < len(row) else ""
                    parts.append(f"<td>{html.escape(cell_val)}</td>")
                parts.append("</tr>")
            parts.append("</tbody>")

        parts.append("</table>")

        if footer:
            parts.append(f'<p class="table-footer">{html.escape(footer)}</p>')

        if landscape:
            parts.append('<p class="table-footer"><em>(Wide table — consider landscape print view)</em></p>')

        parts.append("</div>")

        if caption_text:
            parts.append(f'<p class="caption">{html.escape(caption_text)}</p>')

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Figure HTML
    # ------------------------------------------------------------------

    def _render_figure_html(self, block: Any) -> str:
        """Render figure/chart/image block as HTML <figure>."""
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
        caption_html = f"<figcaption>{html.escape(caption_text)}</figcaption>" if caption_text else ""

        if output_path and os.path.isfile(output_path):
            src = html.escape(output_path.replace("\\", "/"))
            alt = html.escape(caption_text or "")
            return (
                f'<figure>\n'
                f'  <img src="{src}" alt="{alt}">\n'
                f'  {caption_html}\n'
                f'</figure>'
            )
        else:
            title = (
                (asset.source_data.get("title", "") if asset and asset.source_data else "")
                or caption_text
            )
            return (
                f'<figure>\n'
                f'  <div class="figure-placeholder">[Figure: {html.escape(title)} — not generated]</div>\n'
                f'  {caption_html}\n'
                f'</figure>'
            )

    # ------------------------------------------------------------------
    # References
    # ------------------------------------------------------------------

    def _render_references(self, document: CanonicalDocument) -> str:
        """Render references section as HTML."""
        if not document.references:
            return ""

        parts = ['<section class="doc-section references" id="references">']
        parts.append("<h2>References &amp; Evidence Sources</h2>")
        parts.append("<ol>")

        for citation in document.references:
            authors = getattr(citation, "authors_short", "") or ""
            year = getattr(citation, "year", "n.d.") or "n.d."
            title = getattr(citation, "title", "[No title]") or "[No title]"
            journal = getattr(citation, "journal", "") or ""
            pmid = getattr(citation, "pmid", "") or ""
            doi = getattr(citation, "doi", "") or ""

            text = f"{html.escape(authors)} ({year}). {html.escape(title)}."
            if journal:
                text += f" <em>{html.escape(journal)}</em>."
            if pmid:
                text += f' PMID: <a href="https://pubmed.ncbi.nlm.nih.gov/{html.escape(str(pmid))}" target="_blank">{html.escape(str(pmid))}</a>.'
            if doi:
                text += f' DOI: <a href="https://doi.org/{html.escape(str(doi))}" target="_blank">{html.escape(str(doi))}</a>.'

            parts.append(f"<li>{text}</li>")

        parts.append("</ol></section>")
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # QA badge
    # ------------------------------------------------------------------

    def _render_qa_badge(self, document: CanonicalDocument) -> str:
        """Render QA status badge (passed/failed/pending)."""
        qa_status = document.qa_status or "pending"
        report = document.qa_report

        if report is not None:
            if report.overall_passed:
                badge_class = "passed"
                label = "QA PASSED"
                detail = f"{report.block_count} blocking, {report.warning_count} warnings, {report.info_count} info"
            else:
                badge_class = "failed"
                label = "QA FAILED"
                detail = f"{report.block_count} blocking issue(s) — export blocked"
        else:
            status_map = {
                "complete": ("passed", "QA Complete"),
                "in_progress": ("pending", "QA In Progress"),
                "failed": ("failed", "QA Failed"),
                "pending": ("pending", "QA Pending"),
            }
            badge_class, label = status_map.get(qa_status, ("pending", f"QA: {qa_status}"))
            detail = ""

        detail_html = f" &mdash; {html.escape(detail)}" if detail else ""
        return f'<div class="qa-badge {badge_class}">{html.escape(label)}{detail_html}</div>'
