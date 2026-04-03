"""
eeg_feature_loader — loads and validates EEG/QEEG data, extracts band powers.

Type: Deterministic
Computes standard EEG features: band powers, asymmetry indices, ratios.
"""
from __future__ import annotations

import logging
import math
from typing import Optional

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)

# Standard frequency bands (Hz)
BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 50.0),
}


@audited_node("eeg_feature_loader")
def eeg_feature_loader(state: SozoGraphState) -> dict:
    """Load EEG data and extract quantitative features."""
    decisions = []
    eeg = state.get("eeg") or {}

    if not eeg.get("data_available"):
        decisions.append("No EEG data available — skipping feature extraction")
        return {
            "eeg": {**eeg, "data_available": False},
            "_decisions": decisions,
        }

    # Check if features are already provided (from external QEEG system)
    existing_features = eeg.get("features") or {}
    if existing_features:
        feature_count = len(existing_features)
        decisions.append(f"Using {feature_count} pre-computed EEG features from external source")

        quality = _assess_feature_quality(existing_features)
        return {
            "eeg": {
                **eeg,
                "features": existing_features,
                "quality_metrics": quality,
                "data_available": True,
            },
            "_decisions": decisions,
        }

    # If raw EEG data were uploaded, we'd process it here.
    # For MVP, we expect pre-computed features from a QEEG report.
    decisions.append("No pre-computed features and no raw EEG parser — requesting manual input")
    return {
        "eeg": {
            **eeg,
            "features": {},
            "quality_metrics": {"status": "no_data", "usable": False},
            "data_available": False,
        },
        "_decisions": decisions,
    }


def _assess_feature_quality(features: dict) -> dict:
    """Assess quality of provided EEG features."""
    quality = {
        "status": "ok",
        "usable": True,
        "warnings": [],
        "bands_present": [],
        "channels_with_data": 0,
    }

    # Check which bands are present
    for band in BANDS:
        band_keys = [k for k in features if band in k.lower()]
        if band_keys:
            quality["bands_present"].append(band)

    if len(quality["bands_present"]) < 3:
        quality["warnings"].append(
            f"Only {len(quality['bands_present'])} frequency bands present "
            f"(recommend at least delta, theta, alpha, beta)"
        )

    # Check for asymmetry indices
    asym_keys = [k for k in features if "asymmetry" in k.lower() or "asym" in k.lower()]
    if asym_keys:
        quality["has_asymmetry"] = True
    else:
        quality["has_asymmetry"] = False
        quality["warnings"].append("No asymmetry indices — laterality adjustments limited")

    # Check for NaN/invalid values
    invalid = [k for k, v in features.items() if v is None or (isinstance(v, float) and math.isnan(v))]
    if invalid:
        quality["warnings"].append(f"Invalid values in: {invalid[:5]}")
        quality["status"] = "degraded"

    quality["channels_with_data"] = len([k for k, v in features.items() if v is not None])

    return quality
