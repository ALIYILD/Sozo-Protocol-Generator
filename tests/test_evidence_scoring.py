"""Tests for evidence confidence scoring and classification."""
import pytest


def test_empty_articles_returns_zero_score():
    """score_articles([]) returns 0.0."""
    from sozo_generator.evidence.confidence import score_articles

    result = score_articles([])
    assert result == 0.0


def test_rct_scores_higher_than_case_report():
    """An article with HIGH evidence_level scores higher than VERY_LOW."""
    from sozo_generator.evidence.confidence import score_articles
    from sozo_generator.schemas.evidence import ArticleMetadata
    from sozo_generator.core.enums import EvidenceLevel

    high_article = ArticleMetadata(
        title="RCT study on tDCS",
        evidence_level=EvidenceLevel.HIGH,
    )
    very_low_article = ArticleMetadata(
        title="Case report on tDCS",
        evidence_level=EvidenceLevel.VERY_LOW,
    )

    high_score = score_articles([high_article])
    very_low_score = score_articles([very_low_article])

    assert high_score > very_low_score, (
        f"HIGH score ({high_score}) should exceed VERY_LOW score ({very_low_score})"
    )


def test_assign_confidence_with_empty_list():
    """assign_confidence([]) returns INSUFFICIENT."""
    from sozo_generator.evidence.confidence import assign_confidence
    from sozo_generator.core.enums import ConfidenceLabel

    result = assign_confidence([])
    assert result == ConfidenceLabel.INSUFFICIENT


def test_assign_confidence_with_high_quality_evidence():
    """Three HIGH-level articles yield HIGH or MEDIUM confidence."""
    from sozo_generator.evidence.confidence import assign_confidence
    from sozo_generator.schemas.evidence import ArticleMetadata
    from sozo_generator.core.enums import EvidenceLevel, ConfidenceLabel

    articles = [
        ArticleMetadata(title=f"RCT study {i}", evidence_level=EvidenceLevel.HIGH)
        for i in range(3)
    ]

    result = assign_confidence(articles)
    assert result in (ConfidenceLabel.HIGH, ConfidenceLabel.MEDIUM), (
        f"Expected HIGH or MEDIUM confidence with 3 HIGH articles, got {result}"
    )


def test_score_articles_highest_level():
    """HIGHEST evidence_level should produce the maximum score."""
    from sozo_generator.evidence.confidence import score_articles
    from sozo_generator.schemas.evidence import ArticleMetadata
    from sozo_generator.core.enums import EvidenceLevel

    article = ArticleMetadata(
        title="Systematic review",
        evidence_level=EvidenceLevel.HIGHEST,
    )
    score = score_articles([article])
    assert score == 5.0


def test_score_articles_missing_level():
    """MISSING evidence_level should produce score of 0."""
    from sozo_generator.evidence.confidence import score_articles
    from sozo_generator.schemas.evidence import ArticleMetadata
    from sozo_generator.core.enums import EvidenceLevel

    article = ArticleMetadata(
        title="No evidence article",
        evidence_level=EvidenceLevel.MISSING,
    )
    score = score_articles([article])
    assert score == 0.0
