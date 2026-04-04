"""Aggregate scoring and pass/fail."""
from __future__ import annotations

from ..schemas import CaseEvaluation, DimensionScore


def evaluate_overall(ev: CaseEvaluation) -> CaseEvaluation:
    dims = ev.dimensions
    if not dims:
        ev.overall_score = 0.0
        ev.passed = False
        return ev

    weights = {
        "structure_correctness": 0.16,
        "structured_spec_quality": 0.09,
        "document_spec_invariants": 0.09,
        "modality_consistency": 0.13,
        "montage_roi_consistency": 0.13,
        "evidence_completeness": 0.16,
        "unsupported_claim_rate": 0.12,
        "audience_appropriateness": 0.12,
    }
    total_w = 0.0
    acc = 0.0
    for d in dims:
        w = weights.get(d.name, 0.1)
        total_w += w
        acc += d.score * w
    ev.overall_score = round(acc / total_w, 3) if total_w else 0.0
    hard_fail = any(
        not d.passed
        for d in dims
        if d.name
        in (
            "structure_correctness",
            "modality_consistency",
            "montage_roi_consistency",
            "evidence_completeness",
            "unsupported_claim_rate",
            "audience_appropriateness",
            "structured_spec_quality",
            "document_spec_invariants",
        )
    )
    ev.passed = (ev.overall_score >= 0.65) and not hard_fail
    return ev
