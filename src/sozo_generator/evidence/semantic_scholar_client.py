"""
Semantic Scholar search client — uses the S2 Academic Graph API.

Returns ArticleMetadata compatible with the existing evidence pipeline.
Free tier: 100 requests per 5 minutes (no key required).
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

try:
    import requests as _requests
except ImportError:
    _requests = None

_API_BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

# S2 publication types → internal enums
_S2_TYPE_MAP: dict[str, tuple[EvidenceType, EvidenceLevel]] = {
    "Review": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
    "JournalArticle": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
    "Conference": (EvidenceType.NARRATIVE_REVIEW, EvidenceLevel.MEDIUM),
    "CaseReport": (EvidenceType.CASE_REPORT, EvidenceLevel.VERY_LOW),
    "Editorial": (EvidenceType.EXPERT_OPINION, EvidenceLevel.VERY_LOW),
    "LettersAndComments": (EvidenceType.EXPERT_OPINION, EvidenceLevel.VERY_LOW),
    "Study": (EvidenceType.COHORT_STUDY, EvidenceLevel.MEDIUM),
}

_LEVEL_SCORES = {
    EvidenceLevel.HIGHEST: 5,
    EvidenceLevel.HIGH: 4,
    EvidenceLevel.MEDIUM: 3,
    EvidenceLevel.LOW: 2,
    EvidenceLevel.VERY_LOW: 1,
}


class SemanticScholarClient:
    """Client for Semantic Scholar Academic Graph API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        force_refresh: bool = False,
    ):
        settings = get_settings()
        self._has_requests = _requests is not None
        self._api_key = api_key
        self.cache = EvidenceCache(cache_dir or settings.cache_dir)
        self.force_refresh = force_refresh
        self._request_delay = 3.1  # ~100 req per 5 min → ~3s between calls

    def search(
        self,
        query: str,
        max_results: int = 20,
        years_back: int = 10,
    ) -> list[ArticleMetadata]:
        """Search Semantic Scholar and return ArticleMetadata records."""
        cache_key = f"s2|{query}|{max_results}|{years_back}"
        if not self.force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug("S2 cache hit: %s", query[:60])
                return [ArticleMetadata(**a) for a in cached]

        if not self._has_requests:
            logger.warning("requests not installed — S2 search unavailable")
            return []

        logger.info("Semantic Scholar search: %s", query[:80])
        articles = self._query_api(query, max_results, years_back)

        self.cache.set(cache_key, [a.model_dump() for a in articles])
        return articles

    def _query_api(
        self, query: str, max_results: int, years_back: int,
    ) -> list[ArticleMetadata]:
        """Execute S2 API query."""
        from datetime import datetime

        min_year = datetime.now().year - years_back

        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": "paperId,externalIds,title,authors,year,abstract,"
                      "venue,publicationTypes,citationCount",
            "year": f"{min_year}-",
        }

        headers = {}
        if self._api_key:
            headers["x-api-key"] = self._api_key

        try:
            resp = _requests.get(
                _API_BASE, params=params, headers=headers, timeout=30,
            )
            resp.raise_for_status()
            time.sleep(self._request_delay)

            data = resp.json()
            papers = data.get("data", [])
            return [a for a in (self._parse_paper(p) for p in papers) if a]

        except Exception as e:
            logger.error("Semantic Scholar API error: %s", e)
            return []

    def _parse_paper(self, paper: dict) -> Optional[ArticleMetadata]:
        """Parse an S2 paper into ArticleMetadata."""
        try:
            title = paper.get("title", "")
            if not title:
                return None

            # External IDs
            ext_ids = paper.get("externalIds") or {}
            pmid = ext_ids.get("PubMed")
            doi = ext_ids.get("DOI")

            # Authors
            authors = []
            for a in (paper.get("authors") or [])[:10]:
                name = a.get("name", "")
                if name:
                    parts = name.rsplit(" ", 1)
                    if len(parts) == 2:
                        given, family = parts
                        initials = "".join(
                            n[0].upper() for n in given.split() if n
                        )
                        authors.append(f"{family} {initials}")
                    else:
                        authors.append(name)

            # Year
            year = paper.get("year")

            # Abstract
            abstract = paper.get("abstract", "") or ""
            if abstract:
                abstract = clean_abstract(abstract)

            # Venue/Journal
            journal = paper.get("venue") or None

            # Classification
            pub_types = paper.get("publicationTypes") or []
            evidence_type, evidence_level = self._classify(pub_types, title, abstract)

            score = _LEVEL_SCORES.get(evidence_level, 3)

            return ArticleMetadata(
                pmid=pmid,
                doi=doi,
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
            logger.debug("S2 parse error: %s", e)
            return None

    @staticmethod
    def _classify(
        pub_types: list[str],
        title: str,
        abstract: str,
    ) -> tuple[EvidenceType, EvidenceLevel]:
        """Classify evidence type from S2 publication types and text."""
        # Check pub types first
        for pt in pub_types:
            if pt in _S2_TYPE_MAP:
                etype, elevel = _S2_TYPE_MAP[pt]
                break
        else:
            etype = EvidenceType.NARRATIVE_REVIEW
            elevel = EvidenceLevel.MEDIUM

        # Refine with keywords
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

        return etype, elevel
