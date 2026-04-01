"""
Controlled live evidence refresh.
Attempts live PubMed fetch if Biopython is available, falls back to cached data.
Clearly labels evidence provenance: CACHED, REFRESHED, STALE, UNAVAILABLE.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from ..schemas.evidence import ArticleMetadata
from ..schemas.contracts import EvidenceItem, EvidenceRelation
from ..core.enums import EvidenceLevel, EvidenceType
from ..evidence.cache import EvidenceCache

logger = logging.getLogger(__name__)

class EvidenceProvenance:
    CACHED = "cached"
    REFRESHED = "refreshed"
    STALE = "stale"
    UNAVAILABLE = "unavailable"

@dataclass
class RefreshResult:
    condition_slug: str = ""
    query: str = ""
    provenance: str = EvidenceProvenance.UNAVAILABLE
    articles: list[ArticleMetadata] = field(default_factory=list)
    cached_count: int = 0
    refreshed_count: int = 0
    cache_age_days: Optional[int] = None
    error: str = ""

class LiveEvidenceRefresher:
    """Attempts live PubMed refresh with safe fallback to cache."""

    def __init__(self, cache_dir=None, recency_years: int = 5):
        from ..core.settings import get_settings
        settings = get_settings()
        self.cache = EvidenceCache(cache_dir or settings.cache_dir)
        self.recency_years = recency_years
        self._has_pubmed = self._check_pubmed_available()

    def _check_pubmed_available(self) -> bool:
        try:
            from ..evidence.pubmed_client import PubMedClient, _Entrez
            return _Entrez is not None
        except Exception:
            return False

    def refresh(self, query: str, condition_slug: str = "",
                max_results: int = 20, force: bool = False) -> RefreshResult:
        """Attempt live refresh, fall back to cache."""
        result = RefreshResult(condition_slug=condition_slug, query=query)
        cache_key = f"search|{query}|{max_results}|{self.recency_years}"

        # Check cache first
        cached = self.cache.get(cache_key)
        if cached and not force:
            result.articles = [ArticleMetadata(**a) for a in cached]
            result.cached_count = len(result.articles)
            result.provenance = EvidenceProvenance.CACHED
            logger.info("Using cached evidence for '%s': %d articles", query[:50], len(result.articles))
            return result

        # Attempt live refresh
        if self._has_pubmed and force:
            try:
                from ..evidence.pubmed_client import PubMedClient
                client = PubMedClient(force_refresh=True)
                articles = client.search(query, max_results=max_results, years_back=self.recency_years)
                result.articles = articles
                result.refreshed_count = len(articles)
                result.provenance = EvidenceProvenance.REFRESHED
                logger.info("Live refresh for '%s': %d articles", query[:50], len(articles))
                return result
            except Exception as e:
                result.error = str(e)
                logger.warning("Live refresh failed, falling back to cache: %s", e)

        # Fall back to stale cache or empty
        if cached:
            result.articles = [ArticleMetadata(**a) for a in cached]
            result.cached_count = len(result.articles)
            result.provenance = EvidenceProvenance.STALE
            logger.info("Using stale cache for '%s': %d articles", query[:50], len(result.articles))
        else:
            result.provenance = EvidenceProvenance.UNAVAILABLE
            logger.warning("No evidence available for '%s'", query[:50])

        return result

    @property
    def is_live_available(self) -> bool:
        return self._has_pubmed
