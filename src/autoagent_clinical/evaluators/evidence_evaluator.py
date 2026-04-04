"""Evidence-related dimensions."""
from __future__ import annotations

from ..schemas import (
    DimensionScore,
    FailureTaxonomy,
    Severity,
    ValidatorReport,
)


def _penalty_from_reports(
    reports: list[ValidatorReport],
    validator_ids: set[str],
    codes: set[str],
    *,
    high_weight: float = 0.45,
) -> tuple[float, list[str]]:
    reasons: list[str] = []
    weight = 0.0
    for rep in reports:
        if rep.validator_id not in validator_ids:
            continue
        for f in rep.findings:
            if f.code not in codes:
                continue
            reasons.append(f"{rep.validator_id}: {f.message}")
            if f.severity == Severity.BLOCK:
                weight += 0.6
            elif f.severity == Severity.HIGH:
                weight += high_weight
            elif f.severity == Severity.MEDIUM:
                weight += 0.2
            else:
                weight += 0.08
    return min(1.0, weight), reasons


def evaluate_evidence_dimensions(
    reports: list[ValidatorReport],
) -> list[DimensionScore]:
    ev_codes = {
        FailureTaxonomy.MISSING_CITATION.value,
        FailureTaxonomy.EVIDENCE_GAP.value,
        FailureTaxonomy.CITATION_WEAK_OR_MISMATCHED.value,
        FailureTaxonomy.UNSUPPORTED_CLAIM.value,
        FailureTaxonomy.REGULATORY_OVERCLAIM.value,
    }
    w, rs = _penalty_from_reports(
        reports,
        {
            "evidence_validator",
            "citation_completeness_checker",
        },
        ev_codes,
    )
    evidence_score = max(0.0, 1.0 - w)
    ev_dim = DimensionScore(
        name="evidence_completeness",
        score=round(evidence_score, 3),
        passed=evidence_score >= 0.86,
        reasons=rs or ["No evidence or citation gaps flagged."],
    )

    uc_w, uc_r = _penalty_from_reports(
        reports,
        {"evidence_validator", "citation_completeness_checker"},
        {
            FailureTaxonomy.UNSUPPORTED_CLAIM.value,
            FailureTaxonomy.REGULATORY_OVERCLAIM.value,
        },
        high_weight=0.5,
    )
    unsupported_rate = min(1.0, uc_w)
    uc_score = round(max(0.0, 1.0 - unsupported_rate), 3)
    uc_dim = DimensionScore(
        name="unsupported_claim_rate",
        score=uc_score,
        passed=uc_score >= 0.85,
        reasons=uc_r
        or ["No unsupported or overclaim language flagged by heuristics."],
    )
    return [ev_dim, uc_dim]
