"""SOZO Protocol Generator — Streamlit UI entry point (thin orchestrator)."""
import os
import sys
from pathlib import Path

import streamlit as st

# ── Project root: always resolve relative paths from here ────────────────────
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
os.chdir(ROOT)  # ensures data/, configs/ relative paths work on cloud
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# ── Matplotlib non-interactive backend (required on server) ──────────────────
import matplotlib
matplotlib.use("Agg")

# ── Output / review / log directories ───────────────────────────────────────
_IS_CLOUD = not (ROOT / "outputs").exists() or os.environ.get("STREAMLIT_SHARING_MODE")
DEFAULT_OUTPUT_DIR = "/tmp/sozo_outputs" if _IS_CLOUD else str(ROOT / "outputs" / "documents")
REVIEWS_DIR = Path("/tmp/sozo_reviews") if _IS_CLOUD else ROOT / "reviews"
PILOT_LOGS_DIR = Path("/tmp/sozo_pilot_logs") if _IS_CLOUD else ROOT / "pilot_logs"
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
PILOT_LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ── Page config (must be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="SOZO Protocol Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth gate ────────────────────────────────────────────────────────────────
from ui.auth import check_password
check_password()

# ── Sidebar (returns selected page name) ────────────────────────────────────
from ui.sidebar import render_sidebar
page = render_sidebar(REVIEWS_DIR)

# ── Page routing ─────────────────────────────────────────────────────────────
if page == "Chat":
    from ui.page_chat import render
    render(DEFAULT_OUTPUT_DIR, REVIEWS_DIR, PILOT_LOGS_DIR)

elif page == "Studio":
    from ui.page_studio import render
    render(ROOT, DEFAULT_OUTPUT_DIR, REVIEWS_DIR, bool(_IS_CLOUD))

elif page == "Protocol Graph":
    from ui.page_protocol_graph import render
    render(DEFAULT_OUTPUT_DIR)

elif page == "Template Studio":
    from ui.page_template_studio import render
    render()

elif page == "Generate from Template":
    from ui.page_generate_from_template import render
    render(DEFAULT_OUTPUT_DIR)

elif page == "Generate Documents":
    from ui.page_generate_documents import render
    render(DEFAULT_OUTPUT_DIR)

elif page == "Visual Preview":
    from ui.page_visual_preview import render
    render()

elif page == "Operator Cockpit":
    from ui.page_operator_cockpit import render
    render()

elif page == "Review Queue":
    from ui.page_review_queue import render
    render(REVIEWS_DIR, DEFAULT_OUTPUT_DIR, PILOT_LOGS_DIR)

elif page == "Conditions Overview":
    from ui.page_conditions_overview import render
    render()

elif page == "QA Report":
    from ui.page_qa_report import render
    render(DEFAULT_OUTPUT_DIR)

elif page == "Evidence Ingest":
    from ui.page_evidence_ingest import render
    render(ROOT)
