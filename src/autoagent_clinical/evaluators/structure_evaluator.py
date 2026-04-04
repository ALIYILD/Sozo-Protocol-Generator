"""Structure dimension from protocol_structure_validator."""
from __future__ import annotations

from ..schemas import (
    DimensionScore,
    FailureTaxonomy,
    Severity,
    ValidatorReport,
)


def evaluate_structure(reports: list[ValidatorReport]) -> DimensionScore:
    reasons: list[str] = []
    block = 0
    med = 0
    for rep in reports:
        if rep.validator_id != "protocol_structure_validator":
            continue
        for f in rep.findings:
            if f.code == FailureTaxonomy.STRUCTURE_VIOLATION.value:
                reasons.append(f.message)
                if f.severity == Severity.BLOCK:
                    block += 1
                elif f.severity == Severity.HIGH:
                    block += 0.5
                else:
                    med += 1
    penalty = min(1.0, block * 0.55 + med * 0.22)
    score = max(0.0, 1.0 - penalty)
    passed = block == 0 and med == 0 and score >= 0.78
    if not reasons:
        reasons.append("No structure violations flagged by rule-based checks.")
    return DimensionScore(
        name="structure_correctness",
        score=round(score, 3),
        passed=passed,
        reasons=reasons,
    )
