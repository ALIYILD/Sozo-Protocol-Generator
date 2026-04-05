"""Shared helpers, constants, and cached loaders used across UI modules."""
import io
import zipfile
from pathlib import Path

import streamlit as st

# ── Document / tier label maps ──────────────────────────────────────────────
DOC_TYPE_LABELS: dict[str, str] = {
    "clinical_exam":            "Clinical Examination Checklist",
    "phenotype_classification": "Phenotype Classification",
    "responder_tracking":       "Responder Tracking",
    "psych_intake":             "Psychological Intake & PRS Baseline",
    "network_assessment":       "6-Network Bedside Assessment (Partners only)",
    "handbook":                 "Clinical Handbook",
    "all_in_one_protocol":      "All-in-One Protocol",
    "evidence_based_protocol":  "Evidence-Based Protocol",
}

TIER_LABELS: dict[str, str] = {
    "fellow":   "Fellow",
    "partners": "Partners",
    "both":     "Both (Fellow + Partners)",
}


# ── Cached loaders ───────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_registry():
    from sozo_generator.conditions.registry import get_registry
    return get_registry()


@st.cache_data(show_spinner=False)
def condition_options() -> list[tuple[str, str]]:
    """Return sorted list of (slug, display_name) tuples from the registry."""
    registry = load_registry()
    options = []
    for slug in registry.list_slugs():
        try:
            meta = registry.get_meta(slug)
            display = meta.get("display_name", slug.replace("_", " ").title())
        except Exception:
            display = slug.replace("_", " ").title()
        options.append((slug, display))
    return sorted(options, key=lambda x: x[1])


# ── Utility ──────────────────────────────────────────────────────────────────
def zip_files(paths: dict) -> bytes:
    """Zip a dict of {label: Path} into bytes."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for label, path in paths.items():
            if path and Path(path).exists():
                zf.write(path, arcname=Path(path).name)
    return buf.getvalue()
