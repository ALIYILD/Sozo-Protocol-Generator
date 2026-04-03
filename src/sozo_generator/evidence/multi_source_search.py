"""
Multi-source search coordinator — unified interface to PubMed, Crossref,
and Semantic Scholar. Provides merged, deduplicated results.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..schemas.evidence import ArticleMetadata
from .pubmed_client import PubMedClient
from .crossref_client import CrossrefClient
from .semantic_scholar_client import SemanticScholarClient

logger = logging.getLogger(__name__)


@dataclass
class MultiSourceResult:
    """Result of a multi-source search."""

    query: str = ""
    articles: list[ArticleMetadata] = field(default_factory=list)
    source_counts: dict[str, int] = field(default_factory=dict)
    duplicates_removed: int = 0
    errors: list[str] = field(default_factory=list)


class MultiSourceSearch:
    """Coordinates searches across PubMed, Crossref, and Semantic Scholar.

    Deduplicates results across sources using DOI and PMID matching,
    preferring PubMed records (they have PMIDs and structured metadata).
    """

    def __init__(
        self,
        use_pubmed: bool = True,
        use_crossref: bool = True,
        use_semantic_scholar: bool = True,
        cache_dir: Optional[Path] = None,
        force_refresh: bool = False,
    ):
        self.use_pubmed = use_pubmed
        self.use_crossref = use_crossref
        self.use_semantic_scholar = use_semantic_scholar
        self._cache_dir = cache_dir
        self._force_refresh = force_refresh

        # Lazy-init clients
        self._pubmed: Optional[PubMedClient] = None
        self._crossref: Optional[CrossrefClient] = None
        self._s2: Optional[SemanticScholarClient] = None

    @property
    def pubmed(self) -> PubMedClient:
        if self._pubmed is None:
            self._pubmed = PubMedClient(
                cache_dir=self._cache_dir, force_refresh=self._force_refresh,
            )
        return self._pubmed

    @property
    def crossref(self) -> CrossrefClient:
        if self._crossref is None:
            self._crossref = CrossrefClient(
                cache_dir=self._cache_dir, force_refresh=self._force_refresh,
            )
        return self._crossref

    @property
    def s2(self) -> SemanticScholarClient:
        if self._s2 is None:
            self._s2 = SemanticScholarClient(
                cache_dir=self._cache_dir, force_refresh=self._force_refresh,
            )
        return self._s2

    def search(
        self,
        query: str,
        max_results_per_source: int = 20,
        years_back: int = 10,
    ) -> MultiSourceResult:
        """Search all enabled sources and return merged, deduplicated results."""
        result = MultiSourceResult(query=query)
        all_articles: list[ArticleMetadata] = []

        # PubMed — primary source (has PMIDs, structured metadata)
        if self.use_pubmed:
            try:
                pubmed_articles = self.pubmed.search(
                    query, max_results=max_results_per_source, years_back=years_back,
                )
                for a in pubmed_articles:
                    a.notes = (a.notes or "") + " [source:pubmed]"
                all_articles.extend(pubmed_articles)
                result.source_counts["pubmed"] = len(pubmed_articles)
            except Exception as e:
                result.errors.append(f"PubMed: {e}")
                result.source_counts["pubmed"] = 0

        # Crossref
        if self.use_crossref:
            try:
                crossref_articles = self.crossref.search(
                    query, max_results=max_results_per_source, years_back=years_back,
                )
                for a in crossref_articles:
                    a.notes = (a.notes or "") + " [source:crossref]"
                all_articles.extend(crossref_articles)
                result.source_counts["crossref"] = len(crossref_articles)
            except Exception as e:
                result.errors.append(f"Crossref: {e}")
                result.source_counts["crossref"] = 0

        # Semantic Scholar
        if self.use_semantic_scholar:
            try:
                s2_articles = self.s2.search(
                    query, max_results=max_results_per_source, years_back=years_back,
                )
                for a in s2_articles:
                    a.notes = (a.notes or "") + " [source:semantic_scholar]"
                all_articles.extend(s2_articles)
                result.source_counts["semantic_scholar"] = len(s2_articles)
            except Exception as e:
                result.errors.append(f"Semantic Scholar: {e}")
                result.source_counts["semantic_scholar"] = 0

        # Cross-source deduplication
        total_before = len(all_articles)
        result.articles = self._deduplicate_cross_source(all_articles)
        result.duplicates_removed = total_before - len(result.articles)

        logger.info(
            "Multi-source search '%s': %d total → %d unique (%d dupes) from %s",
            query[:50],
            total_before,
            len(result.articles),
            result.duplicates_removed,
            result.source_counts,
        )
        return result

    @staticmethod
    def _deduplicate_cross_source(
        articles: list[ArticleMetadata],
    ) -> list[ArticleMetadata]:
        """Deduplicate across sources. Prefer records with PMIDs (PubMed)."""
        seen_pmids: set[str] = set()
        seen_dois: set[str] = set()
        unique: list[ArticleMetadata] = []

        # Sort: PubMed first (has PMIDs), then by score desc
        articles.sort(
            key=lambda a: (
                1 if a.pmid else 0,
                a.score,
            ),
            reverse=True,
        )

        for article in articles:
            # Check PMID
            if article.pmid:
                if article.pmid in seen_pmids:
                    continue
                seen_pmids.add(article.pmid)

            # Check DOI
            if article.doi:
                doi_norm = article.doi.lower().strip()
                if doi_norm in seen_dois:
                    continue
                seen_dois.add(doi_norm)

            unique.append(article)

        return unique
