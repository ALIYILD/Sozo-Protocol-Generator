from __future__ import annotations

import logging
from ..core.enums import EvidenceLevel, ConfidenceLabel, ReviewFlag
from ..schemas.evidence import ArticleMetadata, EvidenceClaim

logger = logging.getLogger(__name__)

LEVEL_TO_SCORE = {
    EvidenceLevel.HIGHEST: 5,
    EvidenceLevel.HIGH: 4,
    EvidenceLevel.MEDIUM: 3,
    EvidenceLevel.LOW: 2,
    EvidenceLevel.VERY_LOW: 1,
    EvidenceLevel.MISSING: 0,
}

CONFIDENCE_LANGUAGE = {
    ConfidenceLabel.HIGH: "Evidence-based:",
    ConfidenceLabel.MEDIUM: "Supported by emerging evidence:",
    ConfidenceLabel.LOW: "Consensus-informed (limited evidence):",
    ConfidenceLabel.INSUFFICIENT: "\u26a0 Requires clinical review \u2014 evidence insufficient:",
    ConfidenceLabel.REVIEW_REQUIRED: "\u26a0 REVIEW REQUIRED:",
}


def score_articles(articles: list[ArticleMetadata]) -> float:
    """Compute mean evidence score from a list of articles."""
    if not articles:
        return 0.0
    scores = [LEVEL_TO_SCORE.get(a.evidence_level, 3) for a in articles]
    return sum(scores) / len(scores)


def assign_confidence(articles: list[ArticleMetadata], min_sources: int = 2) -> ConfidenceLabel:
    """Assign confidence label based on available evidence."""
    if not articles:
        return ConfidenceLabel.INSUFFICIENT
    mean_score = score_articles(articles)
    n = len(articles)
    # Require minimum sources for higher confidence
    if mean_score >= 4.5 and n >= min_sources:
        return ConfidenceLabel.HIGH
    if mean_score >= 3.5 and n >= min_sources:
        return ConfidenceLabel.HIGH
    if mean_score >= 3.0:
        return ConfidenceLabel.MEDIUM
    if mean_score >= 2.0:
        return ConfidenceLabel.LOW
    return ConfidenceLabel.INSUFFICIENT


def get_clinical_language(confidence: ConfidenceLabel) -> str:
    """Return the appropriate clinical language prefix for a confidence level."""
    return CONFIDENCE_LANGUAGE.get(confidence, "Note:")


def detect_review_flags(articles: list[ArticleMetadata], category: str) -> list[str]:
    """Detect review flags based on evidence quality for a category."""
    flags = []
    if not articles:
        flags.append(ReviewFlag.MISSING_PRIMARY_SOURCE.value)
        return flags
    if all(a.evidence_level in [EvidenceLevel.LOW, EvidenceLevel.VERY_LOW] for a in articles):
        flags.append(ReviewFlag.PILOT_DATA_ONLY.value)
    if all(a.evidence_level == EvidenceLevel.VERY_LOW for a in articles):
        flags.append(ReviewFlag.INDIRECT_EVIDENCE_ONLY.value)
    return flags
