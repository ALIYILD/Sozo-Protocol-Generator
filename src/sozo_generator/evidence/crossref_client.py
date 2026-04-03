"""
Crossref search client — searches Crossref API for scholarly articles.

Provides the same ArticleMetadata output as PubMedClient for unified
downstream processing. Uses the public Crossref REST API (no key required,
but polite pool with email header).
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from ..core.settings import get_settings
from ..core.enums import EvidenceType, EvidenceLevel
from ..schemas.evidence import ArticleMetadata
from .cache import EvidenceCache
from ..core.utils import clean_abstract, current_date_str

logger = logging.getLogger(__name__)

# Lazy import — works even if requests is not installed
try:
    import requests as _requests
except ImportError:
    _requests = None

# Map Crossref type strings to internal enums
_CROSSREF_TYPE_MAP: dict[str, tuple[EvidenceType, EvidenceLevel]] = {
    "journal-article": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
    "proceedings-article": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
    "book-chapter": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.LOW),
    "posted-content": (EvidenceType.EXPERT_OPINION, EvidenceLevel.VERY_LOW),
}

_LEVEL_SCORES = {
    EvidenceLevel.HIGHEST: 5,
    EvidenceLevel.HIGH: 4,
    EvidenceLevel.MEDIUM: 3,
    EvidenceLevel.LOW: 2,
    EvidenceLevel.VERY_LOW: 1,
}

_API_BASE = "https://api.crossref.org/works"


class CrossrefClient:
    """Client for querying Crossref REST API."""

    def __init__(
        self,
        email: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        force_refresh: bool = False,
    ):
        settings = get_settings()
        self._has_requests = _requests is not None
        self._email = email or settings.ncbi_email  # reuse for polite pool
        self.cache = EvidenceCache(cache_dir or settings.cache_dir)
        self.force_refresh = force_refresh
        self._request_delay = 1.0  # Crossref polite rate

    def search(
        self,
        query: str,
        max_results: int = 20,
        years_back: int = 10,
    ) -> list[ArticleMetadata]:
        """Search Crossref and return ArticleMetadata records."""
        cache_key = f"crossref|{query}|{max_results}|{years_back}"
        if not self.force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug("Crossref cache hit: %s", query[:60])
                return [ArticleMetadata(**a) for a in cached]

        if not self._has_requests:
            logger.warning("requests not installed — Crossref search unavailable")
            return []

        logger.info("Crossref search: %s", query[:80])
        articles = self._query_api(query, max_results, years_back)

        self.cache.set(cache_key, [a.model_dump() for a in articles])
        return articles

    def _query_api(
        self, query: str, max_results: int, years_back: int,
    ) -> list[ArticleMetadata]:
        """Execute Crossref API query."""
        from datetime import datetime

        min_year = datetime.now().year - years_back

        params = {
            "query": query,
            "rows": min(max_results, 50),
            "sort": "relevance",
            "order": "desc",
            "filter": f"from-pub-date:{min_year}",
            "select": "DOI,title,author,container-title,published-print,"
                      "published-online,type,abstract,ISSN",
        }

        headers = {"User-Agent": f"Sozo/1.0 (mailto:{self._email})"}

        try:
            resp = _requests.get(
                _API_BASE, params=params, headers=headers, timeout=30,
            )
            resp.raise_for_status()
            time.sleep(self._request_delay)

            data = resp.json()
            items = data.get("message", {}).get("items", [])
            return [a for a in (self._parse_item(item) for item in items) if a]

        except Exception as e:
            logger.error("Crossref API error: %s", e)
            return []

    def _parse_item(self, item: dict) -> Optional[ArticleMetadata]:
        """Parse a Crossref work item into ArticleMetadata."""
        try:
            doi = item.get("DOI", "")
            title_parts = item.get("title", [])
            title = title_parts[0] if title_parts else ""
            if not title:
                return None

            # Authors
            authors = []
            for a in item.get("author", [])[:10]:
                family = a.get("family", "")
                given = a.get("given", "")
                if family:
                    initials = "".join(
                        n[0].upper() for n in given.split() if n
                    ) if given else ""
                    authors.append(f"{family} {initials}".strip())

            # Journal
            containers = item.get("container-title", [])
            journal = containers[0] if containers else None

            # Year
            pub_date = item.get("published-print") or item.get("published-online")
            year = None
            if pub_date and pub_date.get("date-parts"):
                parts = pub_date["date-parts"][0]
                if parts and parts[0]:
                    year = int(parts[0])

            # Abstract
            abstract = item.get("abstract", "")
            if abstract:
                abstract = clean_abstract(abstract)

            # Classify
            item_type = item.get("type", "journal-article")
            evidence_type, evidence_level = _CROSSREF_TYPE_MAP.get(
                item_type,
                (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
            )

            # Upgrade if title/abstract contains trial/review keywords
            evidence_type, evidence_level = self._refine_classification(
                title, abstract, evidence_type, evidence_level,
            )

            score = _LEVEL_SCORES.get(evidence_level, 3)

            return ArticleMetadata(
                pmid=None,  # Crossref doesn't provide PMIDs
                doi=doi or None,
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract if len(abstract) > 50 else None,
                evidence_type=evidence_type,
                evidence_level=evidence_level,
                score=score,
                cached_at=current_date_str(),
            )

        except Exception as e:
            logger.debug("Crossref parse error: %s", e)
            return None

    @staticmethod
    def _refine_classification(
        title: str,
        abstract: str,
        evidence_type: EvidenceType,
        evidence_level: EvidenceLevel,
    ) -> tuple[EvidenceType, EvidenceLevel]:
        """Refine evidence classification using title/abstract keywords."""
        text = f"{title} {abstract}".lower()

        if "systematic review" in text or "meta-analysis" in text:
            return EvidenceType.SYSTEMATIC_REVIEW, EvidenceLevel.HIGHEST
        if "randomized controlled trial" in text or "randomised controlled trial" in text:
            return EvidenceType.RCT, EvidenceLevel.HIGH
        if "clinical trial" in text or "controlled trial" in text:
            return EvidenceType.CONTROLLED_TRIAL, EvidenceLevel.HIGH
        if "practice guideline" in text or "clinical guideline" in text:
            return EvidenceType.CLINICAL_PRACTICE_GUIDELINE, EvidenceLevel.HIGHEST
        if "pilot study" in text:
            return EvidenceType.PILOT_STUDY, EvidenceLevel.LOW
        if "case report" in text:
            return EvidenceType.CASE_REPORT, EvidenceLevel.VERY_LOW

        return evidence_type, evidence_level
