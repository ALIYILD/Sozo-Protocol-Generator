"""
Shared DOCX template manipulation helpers.

These utilities are used by legacy template-replacement generators to clone
a PD master template and apply condition-specific content. They handle
paragraph text replacement, cell writing, table content replacement, and
global find-replace across all paragraphs and table cells in a document.

Canonical location: all legacy generators should import from here rather
than defining their own copies of these functions.
"""
from __future__ import annotations

from docx.shared import RGBColor

C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK = RGBColor(0x00, 0x00, 0x00)


def para_replace(para, old: str, new: str) -> None:
    """Replace ``old`` with ``new`` inside a paragraph's merged run text.

    Preserves the bold/size/color formatting of the first run. All runs are
    collapsed into one to avoid split-token issues (Word splits text across
    multiple runs for tracking/spelling/etc.).
    """
    full = "".join(r.text for r in para.runs)
    if old not in full:
        return
    replaced = full.replace(old, new)
    fr = para.runs[0] if para.runs else None
    bold = fr.font.bold if fr else None
    size = fr.font.size if fr else None
    try:
        color = fr.font.color.rgb if (fr and fr.font.color.type) else None
    except Exception:
        color = None
    for r in para.runs:
        r.text = ""
    if fr:
        fr.text = replaced
        fr.font.bold = bold
        if size:
            fr.font.size = size
        if color:
            fr.font.color.rgb = color
    else:
        para.add_run(replaced)


def para_set(para, new_text: str) -> None:
    """Overwrite ALL text in a paragraph, preserving first-run formatting."""
    para_replace(para, "".join(r.text for r in para.runs), new_text)


def cell_write(
    cell, text: str, bold: bool = False, white: bool = False
) -> None:
    """Clear a table cell and write new text.

    Background shading XML is preserved automatically (it lives on the cell
    element, not the run element).
    """
    for p in cell.paragraphs:
        for r in p.runs:
            r.text = ""
    para = cell.paragraphs[0]
    run = para.runs[0] if para.runs else para.add_run()
    run.text = str(text)
    run.font.bold = bold
    if white:
        run.font.color.rgb = C_WHITE
    else:
        if run.font.color.type:
            run.font.color.rgb = C_BLACK


def replace_table(table, rows: list) -> None:
    """Replace table content row-by-row.

    ``rows[0]`` is the header row (white bold text, navy bg preserved from
    template). ``rows[1:]`` are body rows. If ``rows`` has fewer entries
    than the template table, extra template rows are blanked out.
    """
    n_template_rows = len(table.rows)
    for ri in range(n_template_rows):
        row = table.rows[ri]
        if ri >= len(rows):
            for cell in row.cells:
                cell_write(cell, "")
            continue
        is_hdr = ri == 0
        new_row = rows[ri]
        for ci, cell in enumerate(row.cells):
            text = str(new_row[ci]) if ci < len(new_row) else ""
            cell_write(cell, text, bold=is_hdr, white=is_hdr)


def global_replace(doc, old: str, new: str) -> None:
    """Replace ``old`` with ``new`` in every paragraph and table cell."""
    for para in doc.paragraphs:
        if old in "".join(r.text for r in para.runs):
            para_replace(para, old, new)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if old in "".join(r.text for r in para.runs):
                        para_replace(para, old, new)


def apply_global_replacements(doc, replacements: list[tuple[str, str]]) -> None:
    """Apply a list of (old, new) replacements across all paragraphs and table cells.

    This is more efficient than calling ``global_replace`` in a loop because it
    scans each paragraph only once to check if any replacement is needed.
    """
    for para in doc.paragraphs:
        full = "".join(r.text for r in para.runs)
        if not any(old in full for old, _ in replacements):
            continue
        for old, new in replacements:
            para_replace(para, old, new)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    full = "".join(r.text for r in para.runs)
                    if not any(old in full for old, _ in replacements):
                        continue
                    for old, new in replacements:
                        para_replace(para, old, new)
