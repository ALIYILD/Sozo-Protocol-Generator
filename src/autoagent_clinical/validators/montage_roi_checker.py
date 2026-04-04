"""Montage / ROI coherence — laterality and montage vs target consistency."""
from __future__ import annotations

import re
from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport

_LEFT_MARKERS = ("left dlpfc", "left m1", "contralateral to left", "left hemisphere")
_RIGHT_MARKERS = ("right dlpfc", "right m1", "right hemisphere", "ipsilateral right")
_MONTAGE_LEFT_ANODE = re.compile(
    r"anode[^\n]{0,80}\b(f3|left|dlpfc)\b",
    re.IGNORECASE,
)
_MONTAGE_RIGHT_ANODE = re.compile(
    r"anode[^\n]{0,80}\b(f4|right)\b",
    re.IGNORECASE,
)


def run_montage_roi_check(
    text: str,
    *,
    case_inputs: dict[str, Any],
) -> ValidatorReport:
    findings: list[ValidationFinding] = []
    low = text.lower()

    if "cathode" in low and "anode" not in low:
        findings.append(
            ValidationFinding(
                code=FailureTaxonomy.MONTAGE_CONTRADICTION.value,
                severity=Severity.MEDIUM,
                message="Cathode mentioned without paired anode description.",
                reasons=["Montage descriptions should remain internally complete."],
            )
        )

    left_hits = sum(1 for m in _LEFT_MARKERS if m in low)
    right_hits = sum(1 for m in _RIGHT_MARKERS if m in low)
    if left_hits and right_hits and "bilateral" not in low:
        if "left" in low and "right dlpfc" in low and "left dlpfc" in low:
            if _MONTAGE_LEFT_ANODE.search(text) and _MONTAGE_RIGHT_ANODE.search(text):
                findings.append(
                    ValidationFinding(
                        code=FailureTaxonomy.MONTAGE_CONTRADICTION.value,
                        severity=Severity.HIGH,
                        message="Conflicting anode laterality cues in montage language.",
                        reasons=[
                            "Draft implies competing anode placements; flag for review."
                        ],
                    )
                )

    if "tps" in low or "pulse" in low:
        if "anode" in low and "cathode" in low and "electrode pair" in low:
            if "tps target" not in low and "acoustic" not in low:
                findings.append(
                    ValidationFinding(
                        code=FailureTaxonomy.WRONG_MODALITY.value,
                        severity=Severity.MEDIUM,
                        message="TPS context coexists with classic tDCS electrode-pair language.",
                        reasons=[
                            "Check for modality contamination between tDCS montage prose "
                            "and TPS delivery descriptions."
                        ],
                    )
                )

    if case_inputs.get("montage_must_match_targets"):
        targets = str(case_inputs.get("expected_targets", "")).lower()
        montage = low
        if "dlpfc" in targets and "dlpfc" not in montage and "f3" not in montage and "f4" not in montage:
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.MONTAGE_CONTRADICTION.value,
                    severity=Severity.MEDIUM,
                    message="Stated brain targets do not appear reflected in montage section.",
                    reasons=["Align montage descriptors with stated ROI / targets."],
                )
            )

    return ValidatorReport(validator_id="montage_roi_checker", findings=findings)
