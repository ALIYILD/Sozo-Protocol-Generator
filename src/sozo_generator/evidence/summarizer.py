from __future__ import annotations

import logging
from ..core.enums import EvidenceLevel, ClaimCategory, ConfidenceLabel
from ..schemas.evidence import ArticleMetadata, EvidenceClaim, EvidenceDossier
from ..core.utils import current_date_str, format_authors, truncate_text
from .confidence import assign_confidence, get_clinical_language, detect_review_flags
from .article_ranker import rank_articles, deduplicate_articles

logger = logging.getLogger(__name__)


class EvidenceSummarizer:
    """Builds structured evidence dossiers from article lists."""

    def build_dossier(
        self,
        condition_slug: str,
        condition_name: str,
        articles_by_category: dict[ClaimCategory, list[ArticleMetadata]],
        search_queries: list[str],
    ) -> EvidenceDossier:
        """Build a complete evidence dossier for a condition."""
        all_articles = deduplicate_articles(
            [a for arts in articles_by_category.values() for a in arts]
        )
        ranked = rank_articles(all_articles, top_n=50)

        # Evidence level distribution
        level_counts: dict[str, int] = {}
        for a in ranked:
            key = a.evidence_level.value
            level_counts[key] = level_counts.get(key, 0) + 1

        # Detect overall quality
        overall_quality = self._overall_quality(ranked)

        # Build claims per category
        claims = []
        evidence_gaps = []
        review_flags = []

        for category, cat_articles in articles_by_category.items():
            cat_ranked = rank_articles(deduplicate_articles(cat_articles), top_n=10)
            confidence = assign_confidence(cat_ranked)
            flags = detect_review_flags(cat_ranked, category.value)

            if confidence == ConfidenceLabel.INSUFFICIENT:
                evidence_gaps.append(
                    f"Insufficient evidence for {category.value.replace('_', ' ')}"
                )

            review_flags.extend(flags)

            claim = EvidenceClaim(
                claim_id=f"{condition_slug}_{category.value}",
                text=self._summary_text(category, cat_ranked),
                category=category,
                confidence=confidence,
                evidence_level=self._best_level(cat_ranked),
                supporting_pmids=[a.pmid for a in cat_ranked if a.pmid],
                supporting_sources=cat_ranked[:5],
                review_flags=flags,
                clinical_language=get_clinical_language(confidence),
                condition_slug=condition_slug,
                requires_review=(confidence in [ConfidenceLabel.INSUFFICIENT, ConfidenceLabel.REVIEW_REQUIRED]),
            )
            claims.append(claim)

        # Recommended scales — extracted from assessment tools articles
        recommended_scales = self._extract_scale_recommendations(
            articles_by_category.get(ClaimCategory.ASSESSMENT_TOOLS, [])
        )

        return EvidenceDossier(
            condition_slug=condition_slug,
            condition_name=condition_name,
            generated_at=current_date_str(),
            total_sources=len(ranked),
            sources_by_level=level_counts,
            articles=ranked[:30],
            claims=claims,
            evidence_gaps=list(set(evidence_gaps)),
            review_flags=list(set(review_flags)),
            overall_evidence_quality=overall_quality,
            recommended_scales=recommended_scales,
            search_queries_used=search_queries,
            pubmed_fetch_date=current_date_str(),
        )

    def _summary_text(self, category: ClaimCategory, articles: list[ArticleMetadata]) -> str:
        if not articles:
            return f"[REVIEW REQUIRED: No evidence sources found for {category.value}]"
        top = articles[0]
        authors = format_authors(top.authors)
        year = top.year or "n.d."
        return (
            f"Based on {len(articles)} source(s). "
            f"Primary: {truncate_text(top.title, 120)} "
            f"({authors}, {year})."
        )

    def _best_level(self, articles: list[ArticleMetadata]) -> EvidenceLevel:
        if not articles:
            return EvidenceLevel.MISSING
        level_order = [
            EvidenceLevel.HIGHEST, EvidenceLevel.HIGH,
            EvidenceLevel.MEDIUM, EvidenceLevel.LOW,
            EvidenceLevel.VERY_LOW, EvidenceLevel.MISSING,
        ]
        for level in level_order:
            if any(a.evidence_level == level for a in articles):
                return level
        return EvidenceLevel.MISSING

    def _overall_quality(self, articles: list[ArticleMetadata]) -> EvidenceLevel:
        if not articles:
            return EvidenceLevel.MISSING
        highest_count = sum(1 for a in articles if a.evidence_level == EvidenceLevel.HIGHEST)
        high_count = sum(1 for a in articles if a.evidence_level == EvidenceLevel.HIGH)
        if highest_count >= 3:
            return EvidenceLevel.HIGHEST
        if highest_count >= 1 or high_count >= 3:
            return EvidenceLevel.HIGH
        if high_count >= 1:
            return EvidenceLevel.MEDIUM
        return EvidenceLevel.LOW

    def _extract_scale_recommendations(self, articles: list[ArticleMetadata]) -> list[str]:
        scales = []
        for a in articles:
            for finding in a.key_findings:
                if any(kw in finding.upper() for kw in ["SCALE", "QUESTIONNAIRE", "INVENTORY", "RATING"]):
                    scales.append(finding[:100])
        return scales[:10]
