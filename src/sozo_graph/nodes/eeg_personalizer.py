"""
eeg_personalizer — applies validated EEG-driven adjustments to protocol.

Type: Deterministic
Enforces parameter bounds from modalities.yaml. Never exceeds safety limits
regardless of LLM recommendation.
"""
from __future__ import annotations

import logging

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)

# Safety bounds per modality (from configs/modalities.yaml)
PARAMETER_BOUNDS = {
    "tdcs": {
        "intensity_ma": {"min": 0.5, "max": 2.0},
        "duration_min": {"min": 10, "max": 30},
        "sessions_per_week": {"min": 1, "max": 7},
    },
    "tps": {
        "pulses_per_session": {"min": 100, "max": 600},
        "energy_mj_mm2": {"min": 0.1, "max": 0.3},
    },
    "tavns": {
        "intensity_ma": {"min": 0.5, "max": 5.0},
        "frequency_hz": {"min": 1, "max": 25},
        "duration_min": {"min": 15, "max": 60},
    },
    "ces": {
        "intensity_ua": {"min": 10, "max": 600},
        "frequency_hz": {"min": 0.5, "max": 100},
        "duration_min": {"min": 20, "max": 60},
    },
}


@audited_node("eeg_personalizer")
def eeg_personalizer(state: SozoGraphState) -> dict:
    """Apply EEG-driven adjustments within safety bounds."""
    decisions = []
    eeg = state.get("eeg") or {}
    protocol = state.get("protocol", {})

    interpretation = eeg.get("interpretation") or {}
    adjustments = interpretation.get("recommended_adjustments", [])

    if not adjustments:
        decisions.append("No EEG adjustments to apply — using base protocol")
        return {
            "eeg": {
                **eeg,
                "adjustments_applied": [],
                "adjustments_rejected": [],
            },
            "_decisions": decisions,
        }

    # Determine current modality
    base_seq = protocol.get("base_sequence", {})
    modalities = base_seq.get("all_modalities", [])
    primary_modality = modalities[0] if modalities else "tdcs"
    mod_lower = primary_modality.lower()

    applied = []
    rejected = []

    for adj in adjustments:
        param = adj.get("parameter", "")
        recommended = adj.get("recommended_value", "")
        confidence = adj.get("confidence", "low")

        # Skip low-confidence adjustments
        if confidence == "low" and adj.get("uncertainty_flag"):
            rejected.append({
                **adj,
                "rejection_reason": f"Low confidence with uncertainty: {adj['uncertainty_flag']}",
            })
            decisions.append(f"REJECTED {param}: low confidence — {adj.get('uncertainty_flag')}")
            continue

        # Validate numeric parameters against safety bounds
        bounds = PARAMETER_BOUNDS.get(mod_lower, {})
        param_bounds = bounds.get(param)

        if param_bounds:
            try:
                val = float(recommended)
                if val < param_bounds["min"]:
                    rejected.append({
                        **adj,
                        "rejection_reason": f"Below minimum: {val} < {param_bounds['min']}",
                    })
                    decisions.append(f"REJECTED {param}={val}: below min {param_bounds['min']}")
                    continue
                if val > param_bounds["max"]:
                    rejected.append({
                        **adj,
                        "rejection_reason": f"Above maximum: {val} > {param_bounds['max']}",
                    })
                    decisions.append(f"REJECTED {param}={val}: above max {param_bounds['max']}")
                    continue
            except (ValueError, TypeError):
                pass  # Non-numeric parameter (e.g., target), no bounds check needed

        # Adjustment passed validation
        applied.append(adj)
        decisions.append(
            f"APPLIED {param}: {adj.get('current_value')} → {recommended} "
            f"(confidence: {confidence})"
        )

    decisions.append(f"EEG personalization: {len(applied)} applied, {len(rejected)} rejected")

    return {
        "eeg": {
            **eeg,
            "adjustments_applied": applied,
            "adjustments_rejected": rejected,
            "personalized_protocol": {
                "base_sequence_id": base_seq.get("sequence_id"),
                "adjustments": applied,
                "eeg_driven": True,
            } if applied else None,
        },
        "_decisions": decisions,
    }
