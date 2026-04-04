"""
SOZO Conditions x Modality Evidence Matrix.
Values = approximate published paper counts (PubMed/Scholar).
Source: SOZO_Master_Neuromodulation_Protocols_v2.xlsx (April 2026).
Importable by condition generators, agents, and document builders.
"""
from __future__ import annotations


# ===========================================================================
# MODALITIES — canonical ordered list
# ===========================================================================

MODALITIES: list[str] = [
    "TPS", "TMS", "tDCS", "taVNS", "CES", "tACS", "PBM", "PEMF", "LIFU", "tRNS", "DBS",
]


# ===========================================================================
# EVIDENCE_MATRIX
# dict: condition_name -> dict: modality -> paper_count (int or None)
# None = no significant published literature identified.
# ===========================================================================

EVIDENCE_MATRIX: dict[str, dict[str, int | None]] = {
    "Depression (MDD)": {
        "TPS": 14,
        "TMS": 500,
        "tDCS": 200,
        "taVNS": 80,
        "CES": 30,
        "tACS": 20,
        "PBM": 10,
        "PEMF": 15,
        "LIFU": 12,
        "tRNS": 3,
        "DBS": 30,
    },
    "Alzheimer's/Dementia": {
        "TPS": 31,
        "TMS": 30,
        "tDCS": 20,
        "taVNS": 5,
        "CES": None,
        "tACS": 15,
        "PBM": 20,
        "PEMF": 5,
        "LIFU": 10,
        "tRNS": None,
        "DBS": 5,
    },
    "Parkinson's Disease": {
        "TPS": 9,
        "TMS": 80,
        "tDCS": 15,
        "taVNS": 10,
        "CES": None,
        "tACS": 10,
        "PBM": 10,
        "PEMF": 5,
        "LIFU": None,
        "tRNS": 3,
        "DBS": 1000,
    },
    "Chronic Pain": {
        "TPS": 5,
        "TMS": 60,
        "tDCS": 150,
        "taVNS": 40,
        "CES": 35,
        "tACS": 10,
        "PBM": 10,
        "PEMF": 15,
        "LIFU": 15,
        "tRNS": 5,
        "DBS": 10,
    },
    "OCD": {
        "TPS": None,
        "TMS": 100,
        "tDCS": 10,
        "taVNS": 5,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": 3,
        "tRNS": None,
        "DBS": 50,
    },
    "Anxiety/GAD": {
        "TPS": None,
        "TMS": 20,
        "tDCS": 15,
        "taVNS": 10,
        "CES": 40,
        "tACS": 5,
        "PBM": 5,
        "PEMF": 5,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "PTSD": {
        "TPS": None,
        "TMS": 30,
        "tDCS": 10,
        "taVNS": 5,
        "CES": 10,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Insomnia": {
        "TPS": None,
        "TMS": 5,
        "tDCS": 5,
        "taVNS": 10,
        "CES": 25,
        "tACS": 15,
        "PBM": None,
        "PEMF": 5,
        "LIFU": None,
        "tRNS": 2,
        "DBS": None,
    },
    "Epilepsy": {
        "TPS": None,
        "TMS": 20,
        "tDCS": 15,
        "taVNS": 50,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": 20,
        "LIFU": 5,
        "tRNS": None,
        "DBS": 30,
    },
    "Stroke Rehabilitation": {
        "TPS": None,
        "TMS": 100,
        "tDCS": 100,
        "taVNS": 25,
        "CES": None,
        "tACS": None,
        "PBM": 10,
        "PEMF": 20,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Mild Cognitive Impairment": {
        "TPS": 3,
        "TMS": 15,
        "tDCS": 15,
        "taVNS": None,
        "CES": None,
        "tACS": 10,
        "PBM": 5,
        "PEMF": 5,
        "LIFU": None,
        "tRNS": 2,
        "DBS": None,
    },
    "Tinnitus": {
        "TPS": None,
        "TMS": 40,
        "tDCS": 40,
        "taVNS": 15,
        "CES": None,
        "tACS": 8,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": 15,
        "DBS": None,
    },
    "Schizophrenia": {
        "TPS": None,
        "TMS": 50,
        "tDCS": 30,
        "taVNS": None,
        "CES": None,
        "tACS": 10,
        "PBM": None,
        "PEMF": None,
        "LIFU": 3,
        "tRNS": 3,
        "DBS": None,
    },
    "TBI/Concussion": {
        "TPS": None,
        "TMS": 10,
        "tDCS": 10,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": 25,
        "PEMF": 10,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Addiction": {
        "TPS": None,
        "TMS": 30,
        "tDCS": 30,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": 3,
        "LIFU": 3,
        "tRNS": None,
        "DBS": 5,
    },
    "ADHD": {
        "TPS": 2,
        "TMS": 15,
        "tDCS": 20,
        "taVNS": None,
        "CES": None,
        "tACS": 5,
        "PBM": None,
        "PEMF": 5,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Essential Tremor": {
        "TPS": None,
        "TMS": 10,
        "tDCS": None,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": 5,
        "tRNS": None,
        "DBS": 200,
    },
    "Dystonia": {
        "TPS": None,
        "TMS": 10,
        "tDCS": 5,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": 100,
    },
    "Multiple Sclerosis": {
        "TPS": None,
        "TMS": 15,
        "tDCS": 10,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": 10,
        "LIFU": None,
        "tRNS": 5,
        "DBS": None,
    },
    "Fibromyalgia": {
        "TPS": None,
        "TMS": 15,
        "tDCS": 25,
        "taVNS": 5,
        "CES": 5,
        "tACS": None,
        "PBM": None,
        "PEMF": 5,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Autism Spectrum Disorder": {
        "TPS": 2,
        "TMS": 5,
        "tDCS": 5,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Disorders of Consciousness": {
        "TPS": 2,
        "TMS": 5,
        "tDCS": 10,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
}


# ===========================================================================
# BEST_MODALITIES
# dict: condition_name -> "best modality" string
# ===========================================================================

BEST_MODALITIES: dict[str, str] = {
    "Depression (MDD)": "TMS (rTMS/iTBS), tDCS",
    "Alzheimer's/Dementia": "TPS, TMS + Cognitive Training",
    "Parkinson's Disease": "DBS (STN/GPi), TMS",
    "Chronic Pain": "tDCS (M1), TMS (M1)",
    "OCD": "TMS (Deep/H7), DBS (VC/VS)",
    "Anxiety/GAD": "CES (Alpha-Stim), taVNS",
    "PTSD": "TMS, CES",
    "Insomnia": "CES, tACS (Nexalin)",
    "Epilepsy": "taVNS, DBS (ANT)",
    "Stroke Rehabilitation": "TMS, tDCS",
    "Mild Cognitive Impairment": "TPS, TMS, tDCS",
    "Tinnitus": "TMS (1 Hz), tDCS, tRNS",
    "Schizophrenia": "TMS (1 Hz L-TPJ), tDCS",
    "TBI/Concussion": "PBM (810 nm), tDCS",
    "Addiction": "TMS, tDCS",
    "ADHD": "tDCS (DLPFC), TMS",
    "Essential Tremor": "DBS (VIM), LIFU (MRgFUS)",
    "Dystonia": "DBS (GPi)",
    "Multiple Sclerosis": "PEMF, tRNS",
    "Fibromyalgia": "tDCS (M1), TMS",
    "Autism Spectrum Disorder": "TMS, TPS (emerging)",
    "Disorders of Consciousness": "TMS, tDCS",
}


# ===========================================================================
# EVIDENCE LEVEL LOOKUP
# Evidence level strings sourced from the protocols data, keyed by
# (condition_normalized, modality).  Used to enrich the evidence table.
# Only the most-evidence or most-cited level per condition × modality is stored.
# ===========================================================================

# Abbreviated evidence level descriptions for the table
_EVIDENCE_LEVELS: dict[str, dict[str, str]] = {
    "Depression (MDD)": {
        "TPS": "Pilot RCT + Multiple RCTs (2025)",
        "TMS": "RCT, Meta-analysis",
        "tDCS": "RCT, Meta-analysis",
        "taVNS": "RCT, Meta-analysis",
        "CES": "RCT, Meta-analysis",
        "tACS": "RCT, Open-label",
        "PBM": "Open-label, Pilot RCT",
        "PEMF": "RCT, Open-label",
        "LIFU": "Open-label, Pilot RCT",
        "tRNS": "Open-label, Pilot",
        "DBS": "Open-label, Case series",
    },
    "Alzheimer's/Dementia": {
        "TPS": "RCT, Meta-analysis, Systematic Review",
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": "Open-label, Pilot",
        "CES": None,
        "tACS": "RCT, Open-label",
        "PBM": "RCT, Open-label",
        "PEMF": "Open-label",
        "LIFU": "Open-label, Pilot",
        "tRNS": None,
        "DBS": "Open-label, Phase 2 trial",
    },
    "Parkinson's Disease": {
        "TPS": "Open-label, Pilot RCT (2025)",
        "TMS": "RCT, Meta-analysis",
        "tDCS": "RCT, Open-label",
        "taVNS": "Pilot, Case series",
        "CES": None,
        "tACS": "Open-label, Pilot RCT",
        "PBM": "Open-label, Pilot",
        "PEMF": "Open-label, Pilot",
        "LIFU": None,
        "tRNS": "Open-label, Pilot",
        "DBS": "RCT, Meta-analysis",
    },
    "Chronic Pain": {
        "TPS": "Case series, SA Perspective",
        "TMS": "RCT, Meta-analysis",
        "tDCS": "RCT, Meta-analysis",
        "taVNS": "RCT, Open-label",
        "CES": "RCT, Open-label",
        "tACS": "Open-label, Small RCT",
        "PBM": "Open-label, Small RCT",
        "PEMF": "RCT, Open-label",
        "LIFU": "Open-label, Case series",
        "tRNS": "Open-label, Pilot",
        "DBS": "Open-label",
    },
    "OCD": {
        "TPS": None,
        "TMS": "RCT, Meta-analysis",
        "tDCS": "Open-label",
        "taVNS": "Open-label, Pilot",
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": "Pilot, Case series",
        "tRNS": None,
        "DBS": "Open-label, Case series",
    },
    "Anxiety/GAD": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": "RCT, Open-label",
        "CES": "RCT, Meta-analysis",
        "tACS": "Open-label",
        "PBM": "Open-label, Pilot",
        "PEMF": "Open-label",
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "PTSD": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "Open-label",
        "taVNS": "Open-label, Pilot",
        "CES": "Open-label, Military cohort studies",
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Insomnia": {
        "TPS": None,
        "TMS": "Open-label, Pilot",
        "tDCS": "Open-label, Pilot",
        "taVNS": "Open-label, Pilot",
        "CES": "RCT, Meta-analysis",
        "tACS": "RCT, High quality",
        "PBM": None,
        "PEMF": "Open-label, Pilot",
        "LIFU": None,
        "tRNS": "Open-label, Pilot",
        "DBS": None,
    },
    "Epilepsy": {
        "TPS": None,
        "TMS": "RCT, Case series",
        "tDCS": "RCT, Case series",
        "taVNS": "RCT, Open-label",
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": "Open-label, Case series",
        "LIFU": "Open-label, Pilot",
        "tRNS": None,
        "DBS": "RCT",
    },
    "Stroke Rehabilitation": {
        "TPS": None,
        "TMS": "RCT, Meta-analysis",
        "tDCS": "RCT, Meta-analysis",
        "taVNS": "RCT, Open-label",
        "CES": None,
        "tACS": None,
        "PBM": "RCT (conflicting results)",
        "PEMF": "RCT, Open-label",
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Mild Cognitive Impairment": {
        "TPS": "Open-label, Observational, 24-wk trial",
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": "RCT, Open-label",
        "PBM": "RCT, Open-label",
        "PEMF": "Open-label",
        "LIFU": None,
        "tRNS": "Open-label, Pilot",
        "DBS": None,
    },
    "Tinnitus": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": "Open-label, Pilot RCT",
        "CES": None,
        "tACS": "Open-label, Pilot",
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": "RCT, Open-label",
        "DBS": None,
    },
    "Schizophrenia": {
        "TPS": None,
        "TMS": "RCT, Meta-analysis",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": "Open-label, Pilot RCT",
        "PBM": None,
        "PEMF": None,
        "LIFU": "Pilot, Case series",
        "tRNS": "Open-label, Pilot",
        "DBS": None,
    },
    "TBI/Concussion": {
        "TPS": None,
        "TMS": "Open-label, Pilot",
        "tDCS": "Open-label, Pilot",
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": "Open-label, RCT",
        "PEMF": "Open-label, Case series",
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Addiction": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": "Open-label, Pilot",
        "LIFU": "Open-label, Pilot",
        "tRNS": None,
        "DBS": "Case series, Open-label",
    },
    "ADHD": {
        "TPS": "Double-blind, Sham-controlled RCT",
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": "Open-label, Pilot",
        "PBM": None,
        "PEMF": "Open-label, Pilot",
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Essential Tremor": {
        "TPS": None,
        "TMS": "RCT, Case series",
        "tDCS": None,
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": "Open-label, Pilot",
        "tRNS": None,
        "DBS": "RCT, Case series",
    },
    "Dystonia": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": "Open-label, Case series",
    },
    "Multiple Sclerosis": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": "RCT, Open-label",
        "LIFU": None,
        "tRNS": "Open-label, Pilot",
        "DBS": None,
    },
    "Fibromyalgia": {
        "TPS": None,
        "TMS": "RCT, Open-label",
        "tDCS": "RCT",
        "taVNS": "Open-label",
        "CES": "Open-label, Pilot",
        "tACS": None,
        "PBM": None,
        "PEMF": "Open-label",
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Autism Spectrum Disorder": {
        "TPS": "Double-blind, Sham-controlled RCT",
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
    "Disorders of Consciousness": {
        "TPS": "Case series",
        "TMS": "RCT, Open-label",
        "tDCS": "RCT, Open-label",
        "taVNS": None,
        "CES": None,
        "tACS": None,
        "PBM": None,
        "PEMF": None,
        "LIFU": None,
        "tRNS": None,
        "DBS": None,
    },
}


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def get_evidence_table(condition: str) -> list[list]:
    """Return a table (list of lists) suitable for DOCX: [[Modality, Papers, Evidence Level], ...].

    Performs a case-insensitive exact match first; then falls back to a
    partial (substring) match.  Only rows where paper count is not None
    are included, sorted descending by paper count.

    Returns an empty list if no data is found.
    """
    # Exact match
    row_data = EVIDENCE_MATRIX.get(condition)
    level_data = _EVIDENCE_LEVELS.get(condition, {})

    # Fallback: case-insensitive partial match
    if row_data is None:
        query = condition.lower()
        for key, val in EVIDENCE_MATRIX.items():
            if query in key.lower():
                row_data = val
                level_data = _EVIDENCE_LEVELS.get(key, {})
                break

    if row_data is None:
        return []

    rows: list[list] = []
    for modality in MODALITIES:
        count = row_data.get(modality)
        if count is not None:
            level = level_data.get(modality) or "—"
            rows.append([modality, count, level])

    # Sort descending by paper count
    rows.sort(key=lambda r: r[1], reverse=True)

    # Prepend header row
    return [["Modality", "Published Papers (approx.)", "Evidence Level"]] + rows


def get_best_modality(condition: str) -> str:
    """Return the best modality string for a condition.

    Performs exact match first, then case-insensitive partial match.
    Returns an empty string if not found.
    """
    # Exact match
    result = BEST_MODALITIES.get(condition)
    if result is not None:
        return result

    # Partial match
    query = condition.lower()
    for key, val in BEST_MODALITIES.items():
        if query in key.lower():
            return val

    return ""


def get_ranked_modalities(condition: str) -> list[tuple[str, int]]:
    """Return a list of (modality, paper_count) tuples sorted by paper count descending.

    Only modalities with a non-None paper count are included.
    """
    row_data = EVIDENCE_MATRIX.get(condition)
    if row_data is None:
        query = condition.lower()
        for key, val in EVIDENCE_MATRIX.items():
            if query in key.lower():
                row_data = val
                break

    if row_data is None:
        return []

    ranked = [(mod, cnt) for mod, cnt in row_data.items() if cnt is not None]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


def list_conditions() -> list[str]:
    """Return the list of conditions in the evidence matrix."""
    return list(EVIDENCE_MATRIX.keys())
