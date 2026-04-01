#!/usr/bin/env python3
"""
Generate Responder Tracking & Classification (Partners Tier) for all 14 conditions.
Usage: python scripts/generate_responder_tracking_partners.py [slug]
       omit slug to generate all 14.
"""
import sys
from pathlib import Path
from docx import Document
from docx.shared import RGBColor

# ── add project root to path ─────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from responder_conditions_data import CONDITIONS
from responder_conditions_data_2 import CONDITIONS_2
CONDITIONS.update(CONDITIONS_2)

TEMPLATE = Path(r"C:/Users/yildi/OneDrive/Desktop/Parkinson D/Partners/Assessments/PD_Responder_Tracking_Partners.docx")
OUTPUT_ROOT = Path("outputs/documents")

C_WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
C_BLACK  = RGBColor(0x00, 0x00, 0x00)


# ── helpers ──────────────────────────────────────────────────────────────────

def _para_replace(para, old: str, new: str):
    full = "".join(r.text for r in para.runs)
    if old not in full:
        return
    replaced = full.replace(old, new)
    fr = para.runs[0] if para.runs else None
    bold  = fr.font.bold if fr else None
    size  = fr.font.size if fr else None
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
    _para_replace(para, "".join(r.text for r in para.runs), new_text)


def _cell_write(cell, text: str, bold: bool = False, white: bool = False):
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
        try:
            if run.font.color.type:
                run.font.color.rgb = C_BLACK
        except Exception:
            pass


def _replace_table(table, rows: list):
    """Replace table content; preserves header navy background from template."""
    n_template = len(table.rows)
    for ri in range(n_template):
        row = table.rows[ri]
        if ri >= len(rows):
            for cell in row.cells:
                _cell_write(cell, "")
            continue
        is_hdr = (ri == 0)
        for ci, cell in enumerate(row.cells):
            text = str(rows[ri][ci]) if ci < len(rows[ri]) else ""
            _cell_write(cell, text, bold=is_hdr, white=is_hdr)


# ── global text replacements ─────────────────────────────────────────────────

def _apply_global(doc, c):
    """Replace PD-specific terms throughout the document."""
    reps = [
        ("PD Responder Tracking & Classification", c["subtitle"]),
        ("SOZO Response Assessment, Levodopa-tDCS Documentation & FNON Non-Responder Pathway",
         c["sec2_subtitle"]),
        ("Levodopa-tDCS Scheduling & Documentation", c["sec7_title"].replace("7. ", "")),
        ("7. Levodopa-tDCS Scheduling & Documentation", c["sec7_title"]),
        ("7A. ON-State vs OFF-State Comparison", c["sec7a_title"]),
        ("7C. Levodopa + tDCS Pairing by PD Phenotype", c["sec7c_title"]),
        ("7D. Levodopa-tDCS Documentation Checklist", c["sec7d_title"]),
        ("tDCS effects are state-dependent. Dopamine influences NMDA-dependent plasticity.",
         c["sec7_intro"]),
        ("SOZO Standard Rule: Choose ONE medication state for a block and keep it CONSISTENT. Inconsistent ON/OFF timing is one of",
         c["scheduling_rule"][:120]),
        ("Use at Session 10 (or 8\u201310) and again at end of block:",
         f"Use at Session 10 (or 8\u201310) and again at end of block:"),
        # PD-specific terms
        ("Parkinson's Disease (PD)", c["name"]),
        ("Parkinson's disease (PD)", c["name"]),
        ("Parkinson's Disease", c["name"]),
        ("Parkinson's disease", c["name"]),
        ("Parkinson's", c["short"]),
        ("PD fluctuations", f"{c['short']} symptom fluctuation"),
        (" (PD)", f""),
        ("PD Phenotype", f"{c['short']} Phenotype"),
        ("H&Y Stage", "Symptom Severity"),
        ("levodopa", c["med_name"]),
        ("Levodopa", c["med_name"].capitalize()),
    ]
    for para in doc.paragraphs:
        full = "".join(r.text for r in para.runs)
        for old, new in reps:
            if old in full:
                _para_replace(para, old, new)
                full = "".join(r.text for r in para.runs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    full = "".join(r.text for r in para.runs)
                    for old, new in reps:
                        if old in full:
                            _para_replace(para, old, new)
                            full = "".join(r.text for r in para.runs)


# ── targeted para replacements ───────────────────────────────────────────────

def _apply_paras(doc, c):
    paras = doc.paragraphs
    # [1] subtitle
    _para_set(paras[1], c["subtitle"])
    # [2] section 2 subtitle
    _para_set(paras[2], c["sec2_subtitle"])
    # [8] false non-responder note
    _para_set(paras[8], c["false_nonresponder_note"])
    # [19] measurement confound warning
    _para_set(paras[19], c["measurement_confound_warning"])
    # [29] safety warning (keep generic)
    _para_set(paras[29], "DO NOT escalate intensity beyond safety limits. Always follow SOZO FNON Protocol safety parameters.")
    # [32] section 7 intro
    _para_set(paras[32], c["sec7_intro"])
    # [36] scheduling rule
    _para_set(paras[36], c["scheduling_rule"])


# ── table replacements ────────────────────────────────────────────────────────

def _apply_tables(doc, c):
    tables = doc.tables

    # Table[0]: Patient info — update phenotype row (row 3)
    _cell_write(tables[0].rows[3].cells[0], c["phenotype_row"][0], bold=False)
    _cell_write(tables[0].rows[3].cells[1], c["phenotype_row"][1], bold=False)
    # Clear H&Y Stage row (row 4) — replace label
    _cell_write(tables[0].rows[4].cells[0], "Symptom Severity / Stage", bold=False)

    # Table[1]: Response domains (5r x 4c)
    _replace_table(tables[1], c["response_domains"])

    # Table[2]: Responder profiles (7r x 4c)
    _replace_table(tables[2], c["responder_profiles"])

    # Table[3]: Clinical predictors (5r x 3c)
    _replace_table(tables[3], c["clinical_predictors"])

    # Table[4]: Protocol predictors (5r x 2c)
    _replace_table(tables[4], c["protocol_predictors"])

    # Table[5]: Response classification (4r x 3c)
    _replace_table(tables[5], c["response_classification"])

    # Table[6]: Non-responder profiles (5r x 3c)
    _replace_table(tables[6], c["non_responder_profiles"])

    # Table[8]: Medication state comparison (6r x 3c)
    _replace_table(tables[8], c["med_state_comparison"])

    # Table[9]: Medication documentation (8r x 2c)
    _replace_table(tables[9], c["med_documentation"])

    # Table[10]: Phenotype pairing (5r x 4c)
    _replace_table(tables[10], c["phenotype_pairing"])

    # Table[11]: Documentation checklist (10r x 3c)
    _replace_table(tables[11], c["doc_checklist"])

    # Table[13]: Language guide (4r x 2c)
    _replace_table(tables[13], c["language_guide"])


# ── build one condition ───────────────────────────────────────────────────────

def build(c: dict):
    slug = c["slug"]
    print(f"  Generating: {c['short']} ({slug})...")
    doc = Document(str(TEMPLATE))
    _apply_global(doc, c)
    _apply_paras(doc, c)
    _apply_tables(doc, c)

    out = OUTPUT_ROOT / slug / "partners" / f"Responder_Tracking_Partners_{slug}.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    print(f"  [OK] {out}")
    return out


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    if target:
        if target not in CONDITIONS:
            print(f"Unknown slug: {target}. Available: {list(CONDITIONS.keys())}")
            sys.exit(1)
        build(CONDITIONS[target])
    else:
        print(f"Generating Responder Tracking (Partners) for {len(CONDITIONS)} conditions...")
        ok, fail = [], []
        for slug, data in CONDITIONS.items():
            try:
                build(data)
                ok.append(slug)
            except Exception as e:
                print(f"  [FAIL] {slug}: {e}")
                fail.append(slug)
        print(f"\nDone: {len(ok)} OK, {len(fail)} failed.")
        if fail:
            print(f"Failed: {fail}")
