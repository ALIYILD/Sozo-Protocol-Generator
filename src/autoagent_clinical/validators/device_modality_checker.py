"""Device / modality consistency against declared task inputs."""
from __future__ import annotations

import re
from typing import Any

from ..schemas import FailureTaxonomy, Severity, ValidationFinding, ValidatorReport

_MODALITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "tdcs": ("tdcs", "transcranial direct current", " ma ", "anode", "cathode"),
    "tps": ("tps", "transcranial pulse", "acoustic", "pulse stimulation"),
    "tavns": ("tavns", "auricular", "tragus"),
    "ces": ("ces", "cranial electrotherapy", "microcurrent"),
}


def run_device_modality_check(
    text: str,
    *,
    case_inputs: dict[str, Any],
) -> ValidatorReport:
    findings: list[ValidationFinding] = []
    declared = str(case_inputs.get("modality") or "").lower().strip()
    device = str(case_inputs.get("device_name") or "").lower().strip()
    low = text.lower()

    if declared in _MODALITY_KEYWORDS:
        forbidden = []
        for other, kws in _MODALITY_KEYWORDS.items():
            if other == declared:
                continue
            if any(k in low for k in kws):
                forbidden.append(other)
        if declared == "tps" and "tdcs" in forbidden:
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.WRONG_MODALITY.value,
                    severity=Severity.HIGH,
                    message="Declared TPS modality coexists with strong tDCS-specific cues.",
                    reasons=[
                        "Internal QA: separate modality-specific instruction blocks "
                        "to avoid mixed-modality contamination.",
                    ],
                )
            )
        if declared == "tdcs" and "tps" in low and "tps" in forbidden:
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.DEVICE_MISMATCH.value,
                    severity=Severity.MEDIUM,
                    message="tDCS-declared draft contains TPS wording — verify intent.",
                    reasons=["May be intentional combination protocol; flag for review."],
                )
            )

    if device:
        dev_tokens = re.findall(r"\b[a-z0-9\-]{4,}\b", device)
        found = any(t in low for t in dev_tokens if len(t) > 4)
        if not found and case_inputs.get("device_must_appear", False):
            findings.append(
                ValidationFinding(
                    code=FailureTaxonomy.DEVICE_MISMATCH.value,
                    severity=Severity.LOW,
                    message=f"Expected device label {device!r} not prominent in text.",
                    reasons=["Ensure device-specific parameters match intended hardware."],
                )
            )

    return ValidatorReport(
        validator_id="device_modality_checker",
        findings=findings,
    )
