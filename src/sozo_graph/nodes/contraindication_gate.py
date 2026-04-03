"""
contraindication_gate — hard stop if blocking contraindications are present.

Type: Deterministic
Safety gate: hard block — no override without clinician interrupt.
"""
from __future__ import annotations

from ..audit.logger import audited_node
from ..state import SozoGraphState


@audited_node("contraindication_gate")
def contraindication_gate(state: SozoGraphState) -> dict:
    """Gate check: block if safety_cleared is false."""
    safety = state.get("safety", {})
    cleared = safety.get("safety_cleared", False)
    blocking = safety.get("blocking_contraindications", [])
    decisions = []

    if cleared:
        decisions.append("Contraindication gate PASSED")
        return {"_decisions": decisions}

    decisions.append(f"Contraindication gate BLOCKED: {blocking}")
    return {
        "status": "error",
        "_decisions": decisions,
    }
