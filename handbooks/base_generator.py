"""
SOZO Clinical Handbook Generator — clones PD template and applies condition-specific replacements.
Usage: from handbooks.base_generator import build_handbook
       build_handbook(cdata)  # cdata = one condition dict from condition_data.py
"""
from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.shared import RGBColor, Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEMPLATE = Path(r"C:/Users/yildi/OneDrive/Desktop/Parkinson D/Fellow/Handbook/SOZO_PD_Clinical_Handbook_Fellow.docx")
OUTPUT_ROOT = Path("outputs/documents")

C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK = RGBColor(0x00, 0x00, 0x00)


# ─── low-level helpers ────────────────────────────────────────────────────────

def _para_replace(para, old: str, new: str):
    """Replace old→new inside a paragraph; merges runs first to avoid split-token issues."""
    full = "".join(r.text for r in para.runs)
    if old not in full:
        return
    replaced = full.replace(old, new)
    # Store formatting of first run
    fr = para.runs[0] if para.runs else None
    bold  = fr.font.bold  if fr else None
    size  = fr.font.size  if fr else None
    try:
        color = fr.font.color.rgb if (fr and fr.font.color.type) else None
    except Exception:
        color = None
    # Clear all runs
    for r in para.runs:
        r.text = ""
    if fr:
        fr.text = replaced
        fr.font.bold = bold
        if size:  fr.font.size = size
        if color: fr.font.color.rgb = color
    else:
        para.add_run(replaced)


def _para_set(para, new_text: str):
    """Overwrite ALL text in paragraph (merge-then-set), preserving first-run formatting."""
    _para_replace(para, "".join(r.text for r in para.runs), new_text)


def _cell_write(cell, text: str, bold: bool = False, white: bool = False):
    """Clear cell and write text; background shading XML is preserved automatically."""
    for p in cell.paragraphs:
        for r in p.runs:
            r.text = ""
    para = cell.paragraphs[0]
    run  = para.runs[0] if para.runs else para.add_run()
    run.text = text
    run.font.bold = bold
    if white:
        run.font.color.rgb = C_WHITE
    else:
        # Reset to inherited black
        if run.font.color.type:
            run.font.color.rgb = C_BLACK


def _replace_table(table, rows: list):
    """
    Replace table content row-by-row.
    rows[0] = header row (white bold text, navy bg preserved from template).
    rows[1:] = body rows (black text, alternating bg preserved from template).
    If len(rows) differs from table row count, we pad / truncate.
    """
    n_template_rows = len(table.rows)
    n_new_rows = len(rows)
    for ri in range(n_template_rows):
        row = table.rows[ri]
        if ri >= n_new_rows:
            # blank out extra template rows
            for cell in row.cells:
                _cell_write(cell, "")
            continue
        is_hdr = (ri == 0)
        new_row = rows[ri]
        for ci, cell in enumerate(row.cells):
            text = str(new_row[ci]) if ci < len(new_row) else ""
            _cell_write(cell, text, bold=is_hdr, white=is_hdr)


# ─── global text replacements ────────────────────────────────────────────────

def _apply_global_replacements(doc, c):
    """Replace every PD-specific phrase with condition-specific equivalents."""
    reps = [
        # Cover / headings
        ("PARKINSON'S DISEASE",                c["cover_title"]),
        ("Parkinson's Disease (PD)",            c["name"]),
        ("Parkinson's disease (PD)",            c["name"]),
        ("Parkinson's Disease",                 c["name"]),
        ("Parkinson's disease",                 c["name"]),
        ("Parkinson's",                         c["short"]),
        (" (PD)",                               f" ({c['abbr']})"),
        ("(PD) ",                               f"({c['abbr']}) "),
        (" PD ",                                f" {c['abbr']} "),
        (" PD.",                                f" {c['abbr']}."),
        (" PD,",                                f" {c['abbr']},"),
        ("for PD ",                             f"for {c['abbr']} "),
        ("for PD.",                             f"for {c['abbr']}."),
        ("for PD,",                             f"for {c['abbr']},"),
        ("for PD\n",                            f"for {c['abbr']}\n"),
        # Medication timing
        ("last levodopa dose, ON/OFF state",    c["med_check_item"]),
        ("medication state (ON/OFF, timing of last dose)", c["session_med_doc"]),
        # Exam step heading (Heading 3)
        ("4.1 Motor Examination",               c["exam_step_heading"]),
        ("Motor examination completed",         c["exam_checklist_item"]),
        # PRS domain label
        ("Motor Symptoms Domain",               c["prs_domain_label"]),
        # About text (just the PD-specific part)
        ("for Parkinson's Disease (PD) using",  f"for {c['name']} using"),
    ]
    for para in doc.paragraphs:
        full = "".join(r.text for r in para.runs)
        if not any(old in full for old, _ in reps):
            continue
        for old, new in reps:
            _para_replace(para, old, new)

    # Also replace in table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    full = "".join(r.text for r in para.runs)
                    if not any(old in full for old, _ in reps):
                        continue
                    for old, new in reps:
                        _para_replace(para, old, new)


# ─── paragraph-level targeted replacements ───────────────────────────────────

def _apply_para_replacements(doc, c):
    """Replace full paragraph text for paragraphs identified by index or content."""
    paras = doc.paragraphs

    # [26] TPS off-label callout body
    _para_set(paras[26], c["tps_offlabel_body"])

    # [79] MANDATORY callout body
    _para_set(paras[79], c["mandatory_consent_body"])

    # [110] Motor symptoms domain header
    _para_set(paras[110], c["prs_domain_header_line"])

    # [132] Motor exam description
    _para_set(paras[132], c["exam_step_desc"])

    # [283] False classification callout body
    _para_set(paras[283], c["false_class_body"])


# ─── table-level replacements ────────────────────────────────────────────────

def _apply_table_replacements(doc, c):
    tables = doc.tables

    # Table 1: Available Modalities (5 rows, 4 cols)
    _replace_table(tables[1], c["modality_table"])

    # Table 7: Off-Label Disclosure Summary (5 rows, 4 cols)
    _replace_table(tables[7], c["offlabel_table"])

    # Table 9: SOZO PRS (9 rows, 2 cols)
    _replace_table(tables[9], c["prs_table"])

    # Table 11: Clinical Exam (7 rows, 3 cols)
    _replace_table(tables[11], c["exam_table"])

    # Table 13: Cognitive/Mood Screening (8 rows, 3 cols)
    _replace_table(tables[13], c["screening_table"])

    # Table 14: Phenotype Identification (8 rows, 2 cols)
    _replace_table(tables[14], c["phenotype_table"])

    # Table 23: Task Pairing (6 rows, 3 cols)
    _replace_table(tables[23], c["task_pairing_table"])

    # Table 24: Response Domains (5 rows, 2 cols)
    _replace_table(tables[24], c["response_domains_table"])

    # Table 28: Inclusion Criteria (7 rows, 2 cols)
    _replace_table(tables[28], c["inclusion_table"])

    # Table 29: Absolute Exclusion (8 rows, 2 cols)
    _replace_table(tables[29], c["exclusion_table"])

    # Table 30: Conditional Criteria (9 rows, 2 cols)
    _replace_table(tables[30], c["conditional_table"])

    # Table 31: Phenotype-to-Protocol (9 rows, 4 cols)
    _replace_table(tables[31], c["protocol_table"])


# ─── main entry point ────────────────────────────────────────────────────────

def build_handbook(c: dict):
    """Build handbook for one condition. c = condition data dict."""
    doc = Document(str(TEMPLATE))

    _apply_global_replacements(doc, c)
    _apply_para_replacements(doc, c)
    _apply_table_replacements(doc, c)

    slug = c["slug"]
    out_path = OUTPUT_ROOT / slug / "fellow" / f"SOZO_Clinical_Handbook_{slug}.docx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print(f"  [OK] {out_path}")
    return out_path
