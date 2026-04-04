"""Scoring dimension for DocumentSpec attachment quality."""
from __future__ import annotations

from ..schemas import (
    DimensionScore,
    FailureTaxonomy,
    Severity,
    ValidatorReport,
)


def evaluate_structured_spec(reports: list[ValidatorReport]) -> DimensionScore:
    reasons: list[str] = []
    weight = 0.0
    for rep in reports:
        if rep.validator_id != "structured_spec_validator":
            continue
        if not rep.findings:
            continue
        for f in rep.findings:
            if f.code != FailureTaxonomy.MALFORMED_STRUCTURED_OUTPUT.value:
                continue
            reasons.append(f.message)
            if f.severity in (Severity.BLOCK, Severity.HIGH):
                weight += 0.45
            elif f.severity == Severity.MEDIUM:
                weight += 0.25
            else:
                weight += 0.1

    if not reasons:
        return DimensionScore(
            name="structured_spec_quality",
            score=1.0,
            passed=True,
            reasons=[
                "No Pydantic / coarse DocumentSpec issues from structured_spec_validator "
                "(schema). See document_spec_invariants for blueprint-native checks."
            ],
        )

    score = max(0.0, 1.0 - min(1.0, weight))
    return DimensionScore(
        name="structured_spec_quality",
        score=round(score, 3),
        passed=score >= 0.72,
        reasons=reasons,
    )
