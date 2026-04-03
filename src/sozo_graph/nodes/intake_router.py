"""
intake_router — classifies request as upload or prompt and routes accordingly.

Type: Deterministic
"""
from __future__ import annotations

from ..audit.logger import audited_node
from ..state import SozoGraphState


@audited_node("intake_router")
def intake_router(state: SozoGraphState) -> dict:
    """Classify the incoming request and set source_mode."""
    intake = state.get("intake", {})
    decisions = []

    has_upload = bool(intake.get("uploaded_file") or intake.get("uploaded_filename"))
    has_prompt = bool(intake.get("user_prompt"))

    if has_upload:
        source_mode = "upload"
        decisions.append("Upload detected — routing to template_parser")
    elif has_prompt:
        source_mode = "prompt"
        decisions.append("Prompt detected — routing to prompt_normalizer")
    else:
        source_mode = "prompt"  # default
        decisions.append("No input detected — defaulting to prompt mode (will require input)")

    return {
        "source_mode": source_mode,
        "status": "intake",
        "_decisions": decisions,
    }
