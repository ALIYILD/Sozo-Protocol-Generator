"""
SOZO Clinical Handbook Generator — Partners Tier
Clones PD Partners template and applies condition-specific replacements.
Usage: from handbooks_partners.base_generator import build_handbook
       build_handbook(cdata)

Template profile: 478 paragraphs, 16 tables, ~3,621 words
Key replaced tables: [1],[4],[7],[11],[12],[14]
Key replaced para ranges: [10],[37],[103],[131-148],[152],[287],[314],[367],[433-455]
"""
from pathlib import Path
from docx import Document
from docx.shared import RGBColor

TEMPLATE = Path(r"C:/Users/yildi/OneDrive/Desktop/Parkinson D/Partners/Handbook/SOZO_PD_Clinical_Handbook_Partners.docx")
OUTPUT_ROOT = Path("outputs/documents")

C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK = RGBColor(0x00, 0x00, 0x00)


# ─── low-level helpers ────────────────────────────────────────────────────────

def _para_replace(para, old: str, new: str):
    """Replace old→new inside a paragraph; merges runs first, restores first-run formatting."""
    full = "".join(r.text for r in para.runs)
    if old not in full:
        return
    replaced = full.replace(old, new)
    fr = para.runs[0] if para.runs else None
    bold  = fr.font.bold  if fr else None
    size  = fr.font.size  if fr else None
    try:
        color = fr.font.color.rgb if (fr and fr.font.color.type) else None
    except Exception:
        color = None
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
    """Overwrite ALL text in paragraph, preserving first-run formatting (including purple)."""
    _para_replace(para, "".join(r.text for r in para.runs), new_text)


def _cell_write(cell, text: str, bold: bool = False, white: bool = False):
    """Clear cell and write text; background shading XML preserved automatically."""
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
        if run.font.color.type:
            run.font.color.rgb = C_BLACK


def _replace_table(table, rows: list):
    """
    Replace table content row-by-row.
    rows[0] = header row (white bold text, navy bg preserved from template).
    rows[1:] = body rows.
    """
    n_template_rows = len(table.rows)
    n_new_rows = len(rows)
    for ri in range(n_template_rows):
        row = table.rows[ri]
        if ri >= n_new_rows:
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
    """Replace PD-specific phrases with condition-specific equivalents throughout."""
    reps = [
        # Name variants (longest first to avoid partial replacement)
        ("PARKINSON'S DISEASE",         c["cover_title"]),
        ("Parkinson's Disease (PD)",     c["name"]),
        ("Parkinson's disease (PD)",     c["name"]),
        ("Parkinson's Disease",          c["name"]),
        ("Parkinson's disease",          c["name"]),
        ("Parkinson's",                  c["short"]),
        # Abbreviation
        (" (PD)",                        f" ({c['abbr']})"),
        ("(PD) ",                        f"({c['abbr']}) "),
        (" PD ",                         f" {c['abbr']} "),
        (" PD.",                         f" {c['abbr']}."),
        (" PD,",                         f" {c['abbr']},"),
        (" PD)",                         f" {c['abbr']})"),
        (" PD:",                         f" {c['abbr']}:"),
        ("PD diagnosis",                 f"{c['abbr']} diagnosis"),
        (" PD is",                       f" {c['abbr']} is"),
        ("PD or",                        f"{c['abbr']} or"),
        ("for PD ",                      f"for {c['abbr']} "),
        ("for PD.",                      f"for {c['abbr']}."),
        ("for PD,",                      f"for {c['abbr']},"),
        # PD-specific clinical references in boilerplate
        ("Hoehn & Yahr stage",           "disease severity rating"),
        ("Hoehn and Yahr stage",         "disease severity rating"),
        ("Document levodopa timing specifically", "Document primary medication timing specifically"),
        ("levodopa",                     c.get("med_name", "primary medication")),
        # Cover subtitle (condition already handled above via name replacements)
        ("for Parkinson's Disease (PD) using", f"for {c['name']} using"),
    ]
    for para in doc.paragraphs:
        full = "".join(r.text for r in para.runs)
        if not any(old in full for old, _ in reps):
            continue
        for old, new in reps:
            _para_replace(para, old, new)

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
    """Replace full paragraph text at known indices."""
    paras = doc.paragraphs

    # [10] PARTNERS TIER callout (purple)
    _para_set(paras[10], c["partners_tier_body"])

    # [37] TPS off-label warning
    _para_set(paras[37], c["tps_offlabel_body"])

    # [103] MANDATORY consent warning
    _para_set(paras[103], c["mandatory_consent_body"])

    # [131] Primary symptoms domain header
    _para_set(paras[131], c["prs_primary_label"])

    # [132]–[139] Primary PRS items (8)
    for i, item in enumerate(c["prs_primary_items"][:8]):
        _para_set(paras[132 + i], item)

    # [140] Secondary symptoms domain header
    _para_set(paras[140], c["prs_secondary_label"])

    # [141]–[148] Secondary PRS items (8)
    for i, item in enumerate(c["prs_secondary_items"][:8]):
        _para_set(paras[141 + i], item)

    # [152] Preliminary phenotype assignment line
    _para_set(paras[152], c["phenotype_prelim"])

    # [287] Pre-session medication check
    _para_set(paras[287], c["pre_session_med_check"])

    # [314] Session medication documentation item
    _para_set(paras[314], c["session_med_doc"])

    # [367] False classification warning
    _para_set(paras[367], c["false_class_body"])

    # [433]–[438] Inclusion criteria items (6)
    for i, item in enumerate(c["inclusion_items"][:6]):
        _para_set(paras[433 + i], item)

    # [440]–[446] Absolute exclusion items (7)
    for i, item in enumerate(c["exclusion_items"][:7]):
        _para_set(paras[440 + i], item)

    # [448]–[455] Conditional criteria items (8)
    for i, item in enumerate(c["conditional_items"][:8]):
        _para_set(paras[448 + i], item)


# ─── table-level replacements ────────────────────────────────────────────────

def _apply_table_replacements(doc, c):
    tables = doc.tables

    # Table[1]: Available Modalities (5r × 4c)
    _replace_table(tables[1], c["modality_table"])

    # Table[4]: Off-Label Disclosure Summary (5r × 4c)
    _replace_table(tables[4], c["offlabel_table"])

    # Table[7]: Phenotype Identification (9r × 2c)
    _replace_table(tables[7], c["phenotype_table"])

    # Table[11]: In-Clinic Task Pairing (6r × 3c)
    _replace_table(tables[11], c["task_pairing_table"])

    # Table[12]: Response Domains (5r × 2c)
    _replace_table(tables[12], c["response_domains_table"])

    # Table[14]: Appendix B Phenotype-to-Montage (10r × 2c)
    _replace_table(tables[14], c["montage_table"])


# ─── main entry point ────────────────────────────────────────────────────────

def build_handbook(c: dict):
    """Build Partners handbook for one condition. c = condition data dict."""
    doc = Document(str(TEMPLATE))

    _apply_global_replacements(doc, c)
    _apply_para_replacements(doc, c)
    _apply_table_replacements(doc, c)

    slug = c["slug"]
    out_path = OUTPUT_ROOT / slug / "partners" / f"Clinical_Handbook_Partners_{slug}.docx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
    print(f"  [OK] {out_path}")
    return out_path
