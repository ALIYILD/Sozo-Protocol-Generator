from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

from .models import PaperRaw

try:
    from semanticscholar import SemanticScholar
    from semanticscholar.SemanticScholarException import (
        ObjectNotFoundException,
    )
except ImportError as _s2_import_err:
    raise ImportError(
        "semanticscholar is required for SemanticScholarClient. "
        "Install it with: pip install semanticscholar"
    ) from _s2_import_err

logger = logging.getLogger(__name__)

# Fields requested from the Semantic Scholar API for every paper.
_S2_FIELDS: list[str] = [
    "title",
    "abstract",
    "authors",
    "year",
    "journal",
    "externalIds",
    "openAccessPdf",
    "tldr",
    "influentialCitationCount",
    "citationCount",
    "publicationTypes",
    "isOpenAccess",
]

# Mapping of S2 publicationType strings to study_design labels.
_S2_PUB_TYPE_MAP: dict[str, str] = {
    "ClinicalTrial": "RCT",
    "MetaAnalysis": "meta-analysis",
    "Review": "review",
}


class SemanticScholarClient:
    """Client for fetching academic papers from the Semantic Scholar API.

    Uses the ``semanticscholar`` Python library. An API key is optional but
    recommended for higher rate limits. Without a key the library still works
    at the public (lower) rate limit tier.

    Example usage::

        client = SemanticScholarClient(api_key="s2_xxxx")
        papers = client.search("deep brain stimulation Parkinson", max_results=40)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        """Initialise the Semantic Scholar client.

        Args:
            api_key: Optional Semantic Scholar API key.
            max_retries: Number of times to retry a failed request with
                exponential backoff (delays: 1 s, 2 s, 4 s, …).
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.s2 = SemanticScholar(api_key=api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        max_results: int = 40,
        min_year: int = 2000,
        condition_tags: list[str] = [],
        modality_tags: list[str] = [],
    ) -> list[PaperRaw]:
        """Search Semantic Scholar for papers matching *query*.

        Results are filtered client-side to publications from *min_year* onward.
        Papers with no title or no abstract are skipped.

        Args:
            query: Free-text search string.
            max_results: Maximum number of PaperRaw objects to return.
            min_year: Earliest publication year to include (inclusive).
            condition_tags: Tags to attach to every returned paper.
            modality_tags: Modality tags to attach to every returned paper.

        Returns:
            A list of PaperRaw objects, possibly empty on total failure.
        """
        logger.info(
            "S2 search | query=%r  max_results=%d  min_year=%d",
            query,
            max_results,
            min_year,
        )

        raw_results = None
        for attempt in range(self.max_retries):
            try:
                raw_results = self.s2.search_paper(
                    query,
                    limit=max_results,
                    fields=_S2_FIELDS,
                )
                break
            except (ConnectionError, TimeoutError) as exc:
                if attempt >= self.max_retries - 1:
                    logger.error(
                        "S2: search exhausted retries for query %r: %s", query, exc
                    )
                    return []
                wait = 2 ** attempt  # 1 s, 2 s, 4 s
                logger.warning(
                    "S2: transient error (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1,
                    self.max_retries,
                    wait,
                    exc,
                )
                time.sleep(wait)
            except Exception:
                logger.exception("S2: unexpected error during search for %r", query)
                return []

        if raw_results is None:
            return []

        papers: list[PaperRaw] = []
        try:
            for paper in raw_results:
                time.sleep(1.0)  # Polite delay between result iterations.

                # Year filter.
                paper_year = getattr(paper, "year", None)
                if paper_year is not None and paper_year < min_year:
                    continue

                # Skip papers with no title or no abstract.
                if not getattr(paper, "title", None):
                    continue
                if not getattr(paper, "abstract", None):
                    continue

                parsed = self._to_paper_raw(paper, condition_tags, modality_tags)
                if parsed is not None:
                    papers.append(parsed)

                if len(papers) >= max_results:
                    break
        except Exception:
            logger.exception(
                "S2: error iterating results for query %r (returning %d so far)",
                query,
                len(papers),
            )

        logger.info("S2 search | query=%r  fetched=%d papers", query, len(papers))
        return papers

    def fetch_by_doi(self, doi: str) -> Optional[PaperRaw]:
        """Fetch a single paper by its DOI.

        Args:
            doi: The DOI string, with or without the ``https://doi.org/`` prefix.

        Returns:
            A PaperRaw object, or None if not found or on error.
        """
        doi_clean = doi.replace("https://doi.org/", "").strip()
        paper_id = f"DOI:{doi_clean}"
        logger.debug("S2: fetch_by_doi paper_id=%s", paper_id)
        return self.fetch_by_paper_id(paper_id)

    def fetch_by_paper_id(self, paper_id: str) -> Optional[PaperRaw]:
        """Fetch a single paper by its Semantic Scholar paper ID (or prefixed ID).

        Accepts plain S2 paper IDs as well as prefixed forms such as
        ``DOI:10.xxxx/...`` or ``PMID:12345678``.

        Args:
            paper_id: Semantic Scholar paper identifier.

        Returns:
            A PaperRaw object, or None if not found or on error.
        """
        for attempt in range(self.max_retries):
            try:
                paper = self.s2.get_paper(paper_id, fields=_S2_FIELDS)
                time.sleep(1.0)
                if paper is None:
                    logger.warning("S2: no result for paper_id=%s", paper_id)
                    return None
                return self._to_paper_raw(paper, [], [])
            except ObjectNotFoundException:
                logger.warning("S2: paper not found: %s", paper_id)
                return None
            except (ConnectionError, TimeoutError) as exc:
                if attempt >= self.max_retries - 1:
                    logger.error(
                        "S2: fetch_by_paper_id exhausted retries for %s: %s",
                        paper_id,
                        exc,
                    )
                    return None
                wait = 2 ** attempt
                logger.warning(
                    "S2: transient error fetching %s (attempt %d/%d), retrying in %ds",
                    paper_id,
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                time.sleep(wait)
            except Exception:
                logger.exception(
                    "S2: unexpected error fetching paper_id=%s", paper_id
                )
                return None

        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_paper_raw(
        self,
        paper,  # semanticscholar.Paper.Paper — not typed to avoid hard dependency
        condition_tags: list[str],
        modality_tags: list[str],
    ) -> Optional[PaperRaw]:
        """Convert a semanticscholar Paper object to a PaperRaw instance.

        Returns None if the paper has no title or if an unexpected error occurs.
        Individual field extraction errors are caught and logged without raising.

        Args:
            paper: A Paper object from the semanticscholar library.
            condition_tags: Tags to attach to the paper.
            modality_tags: Modality tags to attach to the paper.

        Returns:
            A PaperRaw object or None.
        """
        try:
            title: Optional[str] = getattr(paper, "title", None)
            if not title:
                return None

            source_id: str = getattr(paper, "paperId", "") or ""

            external_ids: dict = getattr(paper, "externalIds", None) or {}
            doi: Optional[str] = external_ids.get("DOI") or None
            pmid: Optional[str] = external_ids.get("PubMed") or None

            # Authors — first 6 only.
            raw_authors = getattr(paper, "authors", None) or []
            authors: list[str] = []
            for a in raw_authors[:6]:
                name = getattr(a, "name", None)
                if name:
                    authors.append(name)

            year: Optional[int] = getattr(paper, "year", None)

            # Journal name.
            journal_obj = getattr(paper, "journal", None)
            journal: Optional[str] = (
                getattr(journal_obj, "name", None) if journal_obj else None
            )

            abstract: Optional[str] = getattr(paper, "abstract", None) or None

            open_access: bool = bool(getattr(paper, "isOpenAccess", False))
            oa_pdf = getattr(paper, "openAccessPdf", None)
            oa_url: Optional[str] = (
                getattr(oa_pdf, "url", None) if oa_pdf else None
            )

            tldr_obj = getattr(paper, "tldr", None)
            s2_tldr: Optional[str] = (
                getattr(tldr_obj, "text", None) if tldr_obj else None
            )

            s2_influential_citations: int = (
                getattr(paper, "influentialCitationCount", None) or 0
            )
            s2_citation_count: int = getattr(paper, "citationCount", None) or 0

            # Study design from publicationTypes.
            pub_types: Optional[list[str]] = getattr(paper, "publicationTypes", None) or []
            study_design = self._map_pub_types_to_study_design(
                pub_types, title, abstract or ""
            )

            logger.debug(
                "S2: parsed paper title=%r influential_citations=%d",
                title,
                s2_influential_citations,
            )

            return PaperRaw(
                source="semantic_scholar",
                source_id=source_id,
                doi=doi,
                pmid=pmid,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                open_access=open_access,
                oa_url=oa_url,
                s2_tldr=s2_tldr,
                s2_influential_citations=s2_influential_citations,
                s2_citation_count=s2_citation_count,
                study_design=study_design,
                condition_tags=list(condition_tags),
                modality_tags=list(modality_tags),
                fetched_at=datetime.now(timezone.utc).isoformat(),
            )

        except Exception:
            paper_id_hint = getattr(paper, "paperId", "<unknown>")
            logger.warning(
                "S2: failed to parse paper id=%s — skipping",
                paper_id_hint,
                exc_info=True,
            )
            return None

    def _map_pub_types_to_study_design(
        self,
        pub_types: list[str],
        title: str,
        abstract: str,
    ) -> Optional[str]:
        """Derive a study_design label from S2 publicationTypes.

        Checks pub_types in priority order. For ``JournalArticle`` falls back
        to heuristic text analysis via :meth:`_detect_study_design`.

        Args:
            pub_types: List of S2 publication type strings.
            title: Paper title (used for heuristic fallback).
            abstract: Paper abstract (used for heuristic fallback).

        Returns:
            A study_design label string or None.
        """
        if not pub_types:
            return self._detect_study_design(title, abstract)

        # Priority: more specific types first.
        priority_order = ["ClinicalTrial", "MetaAnalysis", "Review"]
        for pt in priority_order:
            if pt in pub_types:
                return _S2_PUB_TYPE_MAP[pt]

        if "JournalArticle" in pub_types:
            return self._detect_study_design(title, abstract)

        return None

    def _detect_study_design(self, title: str, abstract: str) -> Optional[str]:
        """Heuristic study-design classifier based on title and abstract text.

        Applies a ranked series of regex checks. The first match wins.

        Args:
            title: Paper title.
            abstract: Paper abstract (may be empty).

        Returns:
            A short study-design label string, or None if unclassifiable.
        """
        text = f"{title} {abstract}".lower()

        if re.search(r"\brandomized\b|\brandomised\b|\brct\b|\bclinical trial\b", text):
            return "RCT"
        if re.search(r"\bmeta[-\s]?analysis\b", text):
            return "meta-analysis"
        if re.search(r"\bsystematic review\b", text):
            return "systematic_review"
        if re.search(r"\bcohort\b", text):
            return "cohort"
        if re.search(r"\bpilot\b", text):
            return "pilot"
        if re.search(r"\bcase report\b|\bcase series\b", text):
            return "case_series"
        if re.search(r"\breview\b", text):
            return "review"

        return None
