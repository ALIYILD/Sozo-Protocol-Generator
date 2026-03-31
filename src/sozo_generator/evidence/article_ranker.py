import logging
from ..core.enums import EvidenceLevel, EvidenceType
from ..schemas.evidence import ArticleMetadata

logger = logging.getLogger(__name__)

EVIDENCE_WEIGHTS = {
    EvidenceLevel.HIGHEST: 5,
    EvidenceLevel.HIGH: 4,
    EvidenceLevel.MEDIUM: 3,
    EvidenceLevel.LOW: 2,
    EvidenceLevel.VERY_LOW: 1,
}

RECENCY_BONUS = {  # bonus points for recent publications
    0: 2,   # current year
    1: 1.5,
    2: 1,
    3: 0.5,
}


def rank_articles(
    articles: list[ArticleMetadata],
    current_year: int = 2026,
    top_n: int = 20,
) -> list[ArticleMetadata]:
    """Rank articles by evidence level, recency, and abstract presence."""
    def compute_score(article: ArticleMetadata) -> float:
        base = EVIDENCE_WEIGHTS.get(article.evidence_level, 3)
        recency = 0.0
        if article.year:
            age = current_year - article.year
            recency = RECENCY_BONUS.get(min(age, 3), 0.0)
        abstract_bonus = 0.5 if article.abstract and len(article.abstract) > 100 else 0.0
        return base + recency + abstract_bonus

    scored = [(a, compute_score(a)) for a in articles]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [a for a, _ in scored[:top_n]]


def deduplicate_articles(articles: list[ArticleMetadata]) -> list[ArticleMetadata]:
    """Remove duplicate articles by PMID."""
    seen_pmids: set[str] = set()
    unique = []
    for a in articles:
        if a.pmid and a.pmid in seen_pmids:
            continue
        if a.pmid:
            seen_pmids.add(a.pmid)
        unique.append(a)
    return unique


def filter_by_min_score(
    articles: list[ArticleMetadata],
    min_score: int = 2,
) -> list[ArticleMetadata]:
    """Filter articles below a minimum evidence score."""
    return [a for a in articles if a.score >= min_score]
