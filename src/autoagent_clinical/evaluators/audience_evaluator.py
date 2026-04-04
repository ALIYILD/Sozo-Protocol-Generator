"""Audience appropriateness — fellow vs partner heuristics."""
from __future__ import annotations

import re
from typing import Any

from ..schemas import DimensionScore

_FELLOW_MARKERS = (
    r"\bpathophysiology\b",
    r"\bmechanistic\b|\bmechanism\b",
    r"\blearning objectives\b",
    r"\bfoundational\b",
    r"\bintroductory\b",
)
_PARTNER_MARKERS = (
    r"\bfnon\b",
    r"\bclinic workflow\b",
    r"\bscheduling\b",
    r"\bimplementation\b",
    r"\boperator\b",
    r"\bhandoff\b",
    r"\bbilling\b",
    r"\bthroughput\b",
)


def _count_patterns(patterns: tuple[str, ...], low: str) -> int:
    n = 0
    for pat in patterns:
        if re.search(pat, low, re.IGNORECASE):
            n += 1
    return n


def evaluate_audience(
    text: str,
    case_inputs: dict[str, Any],
) -> DimensionScore:
    audience = str(case_inputs.get("audience") or "").lower()
    low = text.lower()
    reasons: list[str] = []
    if not audience:
        return DimensionScore(
            name="audience_appropriateness",
            score=1.0,
            passed=True,
            reasons=["No audience constraint specified for this case."],
        )

    f = _count_patterns(_FELLOW_MARKERS, low)
    p = _count_patterns(_PARTNER_MARKERS, low)

    if audience in ("fellow", "fellows"):
        if p > f + 1:
            reasons.append(
                "Partner-oriented workflow terms dominate; fellow drafts usually "
                "foreground foundational framing."
            )
        score = 1.0 if f >= 1 or p == 0 else 0.55
        if f >= 2:
            score = min(1.0, score + 0.15)
        passed = score >= 0.65
        if not reasons:
            reasons.append("Fellow-style explanatory markers present or neutral.")
        return DimensionScore(
            name="audience_appropriateness",
            score=round(score, 3),
            passed=passed,
            reasons=reasons,
        )

    if audience in ("partner", "partners"):
        if f > p + 2 and p == 0:
            reasons.append(
                "Mostly foundational language; partner drafts often reference "
                "implementation / clinic workflow constructs."
            )
            score = 0.5
        else:
            score = 0.75 if p >= 1 else 0.6
            if not reasons:
                reasons.append("Partner-oriented markers detected or mixed audience prose.")
        passed = score >= 0.6
        return DimensionScore(
            name="audience_appropriateness",
            score=round(score, 3),
            passed=passed,
            reasons=reasons,
        )

    return DimensionScore(
        name="audience_appropriateness",
        score=0.8,
        passed=True,
        reasons=[f"Audience {audience!r} not scored with specialized rubric."],
    )
