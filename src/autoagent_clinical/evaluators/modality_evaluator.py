"""Modality / montage consistency dimensions."""
from __future__ import annotations

from ..schemas import (
    DimensionScore,
    FailureTaxonomy,
    Severity,
    ValidatorReport,
)


def evaluate_modality(reports: list[ValidatorReport]) -> list[DimensionScore]:
    modality_codes = {
        FailureTaxonomy.WRONG_MODALITY.value,
        FailureTaxonomy.DEVICE_MISMATCH.value,
    }
    mont_codes = {FailureTaxonomy.MONTAGE_CONTRADICTION.value,
                  FailureTaxonomy.LATERALITY_INCONSISTENCY.value}

    def _dim(name: str, codes: set[str]) -> DimensionScore:
        weight = 0.0
        reasons: list[str] = []
        for rep in reports:
            for f in rep.findings:
                if f.code not in codes:
                    continue
                reasons.append(f"{rep.validator_id}: {f.message}")
                if f.severity in (Severity.BLOCK, Severity.HIGH):
                    weight += 0.35
                elif f.severity == Severity.MEDIUM:
                    weight += 0.2
                else:
                    weight += 0.08
        w = min(1.0, weight)
        sc = max(0.0, 1.0 - w)
        return DimensionScore(
            name=name,
            score=round(sc, 3),
            passed=sc >= 0.74,
            reasons=reasons or [f"No issues flagged for {name}."],
        )

    return [
        _dim("modality_consistency", modality_codes),
        _dim("montage_roi_consistency", mont_codes),
    ]
