"""Dimension for blueprint-aligned DocumentSpec invariants (structure-native)."""
from __future__ import annotations

from ..schemas import (
    DimensionScore,
    FailureTaxonomy,
    Severity,
    ValidatorReport,
)

_NATIVE_CODES = frozenset(
    {
        FailureTaxonomy.MISSING_REQUIRED_SECTION.value,
        FailureTaxonomy.INSUFFICIENT_REFERENCES.value,
        FailureTaxonomy.SPEC_IDENTITY_MISMATCH.value,
        FailureTaxonomy.PLACEHOLDER_OR_EMPTY_SECTION.value,
        FailureTaxonomy.SECTION_ORDER_OR_DEPTH_ANOMALY.value,
    }
)


def evaluate_document_spec_invariants(reports: list[ValidatorReport]) -> DimensionScore:
    reasons: list[str] = []
    weight = 0.0
    for rep in reports:
        if rep.validator_id != "document_spec_invariants":
            continue
        for f in rep.findings:
            if f.code not in _NATIVE_CODES:
                continue
            reasons.append(f"[{f.code}] {f.message}")
            if f.severity == Severity.BLOCK:
                weight += 0.55
            elif f.severity == Severity.HIGH:
                weight += 0.38
            elif f.severity == Severity.MEDIUM:
                weight += 0.22
            else:
                weight += 0.08

    if not reasons:
        return DimensionScore(
            name="document_spec_invariants",
            score=1.0,
            passed=True,
            reasons=[
                "No structure-native invariant violations, or no document_spec attached."
            ],
        )

    score = max(0.0, 1.0 - min(1.0, weight))
    return DimensionScore(
        name="document_spec_invariants",
        score=round(score, 3),
        passed=score >= 0.72,
        reasons=reasons,
    )
