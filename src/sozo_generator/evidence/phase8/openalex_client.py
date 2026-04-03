from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

from .models import PaperRaw

try:
    import pyalex
    from pyalex import Works
except ImportError as _oa_import_err:
    raise ImportError(
        "pyalex is required for OpenAlexClient. "
        "Install it with: pip install pyalex"
    ) from _oa_import_err

logger = logging.getLogger(__name__)


def inverted_index_to_abstract(index: dict) -> str:
    """Convert OpenAlex abstract_inverted_index to plain text.

    OpenAlex stores abstracts as an inverted index mapping each word to the
    list of positions it appears at. This function reconstructs the original
    sentence by placing each token at its correct position and joining them
    with spaces.

    Args:
        index: A dict of {word: [position, ...]} as returned by the OpenAlex API.

    Returns:
        The reconstructed abstract as a plain-text string. Returns an empty
        string if the index is empty or None.
    """
    if not index:
        return ""

    # Build a position → word mapping, then sort by position.
    position_word: dict[int, str] = {}
    for word, positions in index.items():
        for pos in positions:
            position_word[pos] = word

    if not position_word:
        return ""

    max_pos = max(position_word.keys())
    tokens = [position_word.get(i, "") for i in range(max_pos + 1)]
    return " ".join(t for t in tokens if t)


class OpenAlexClient:
    """Client for fetching academic papers from the OpenAlex API via pyalex.

    As of February 2026 OpenAlex requires a free API key to access the polite
    pool (higher rate limits). Pass your registered e-mail and optional API key
    to the constructor.

    Example usage::

        client = OpenAlexClient(email="you@example.com", api_key="oa_xxxx")
        papers = client.search("transcranial magnetic stimulation depression", max_results=40)
    """

    def __init__(
        self,
        email: str,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        per_page: int = 25,
    ) -> None:
        """Initialise the OpenAlex client.

        Args:
            email: Registered e-mail for the OpenAlex polite pool.
            api_key: Optional OpenAlex API key (recommended from Feb 2026).
            max_retries: Number of times to retry a failed request.
            per_page: Number of results to request per API page (max 200).
        """
        self.email = email
        self.api_key = api_key
        self.max_retries = max_retries
        self.per_page = min(per_page, 200)

        # Configure pyalex globally.
        pyalex.config.email = email
        if api_key:
            pyalex.config.api_key = api_key

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
        """Search OpenAlex for papers matching *query*.

        Results are sorted by cited_by_count descending and filtered to
        publications from *min_year* onward.

        Args:
            query: Free-text search string.
            max_results: Maximum number of PaperRaw objects to return.
            min_year: Earliest publication year to include (inclusive).
            condition_tags: Tags to attach to every returned paper.
            modality_tags: Modality tags to attach to every returned paper.

        Returns:
            A list of PaperRaw objects, possibly empty on total failure.
        """
        papers: list[PaperRaw] = []
        collected = 0
        page = 1

        logger.info(
            "OpenAlex search | query=%r  max_results=%d  min_year=%d",
            query,
            max_results,
            min_year,
        )

        try:
            pager = (
                Works()
                .search(query)
                .filter(publication_year=f">{min_year - 1}")
                .sort(cited_by_count="desc")
            )
        except Exception:
            logger.exception("OpenAlex: failed to build query for %r", query)
            return []

        while collected < max_results:
            batch_size = min(self.per_page, max_results - collected)

            attempt = 0
            works = None
            while attempt < self.max_retries:
                try:
                    works = pager.get(per_page=batch_size, page=page)
                    break
                except Exception:
                    attempt += 1
                    if attempt >= self.max_retries:
                        logger.error(
                            "OpenAlex: exhausted retries for query %r page %d",
                            query,
                            page,
                        )
                        return papers
                    wait = 2 ** attempt
                    logger.warning(
                        "OpenAlex: request error (attempt %d/%d), retrying in %ds",
                        attempt,
                        self.max_retries,
                        wait,
                    )
                    time.sleep(wait)

            if works is None or len(works) == 0:
                # No more results.
                break

            for work in works:
                if collected >= max_results:
                    break
                paper = self._to_paper_raw(work, condition_tags, modality_tags)
                if paper is not None:
                    papers.append(paper)
                    collected += 1

            if len(works) < batch_size:
                # Last page reached.
                break

            page += 1
            time.sleep(0.1)  # Polite pool courtesy delay.

        logger.info(
            "OpenAlex search | query=%r  fetched=%d papers", query, len(papers)
        )
        return papers

    def fetch_by_doi(self, doi: str) -> Optional[PaperRaw]:
        """Fetch a single paper by its DOI.

        Args:
            doi: The DOI string, with or without the ``https://doi.org/`` prefix.

        Returns:
            A PaperRaw object, or None if not found or on error.
        """
        doi_clean = doi.replace("https://doi.org/", "").strip()
        logger.debug("OpenAlex: fetch_by_doi doi=%s", doi_clean)

        for attempt in range(self.max_retries):
            try:
                works = Works().filter(doi=doi_clean).get(per_page=1)
                if not works:
                    logger.warning("OpenAlex: no result for DOI %s", doi_clean)
                    return None
                return self._to_paper_raw(works[0], [], [])
            except Exception:
                if attempt >= self.max_retries - 1:
                    logger.exception(
                        "OpenAlex: fetch_by_doi failed for doi=%s", doi_clean
                    )
                    return None
                time.sleep(2 ** (attempt + 1))

        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_paper_raw(
        self,
        work: dict,
        condition_tags: list[str],
        modality_tags: list[str],
    ) -> Optional[PaperRaw]:
        """Convert a raw OpenAlex work dict to a PaperRaw instance.

        Returns None if the work has no title or if an unexpected error occurs.

        Args:
            work: A raw work dict as returned by pyalex.
            condition_tags: Tags to attach to the paper.
            modality_tags: Modality tags to attach to the paper.

        Returns:
            A PaperRaw object or None.
        """
        try:
            title: Optional[str] = work.get("display_name") or work.get("title")
            if not title:
                return None

            # source_id: strip the OpenAlex URL prefix.
            raw_id: str = work.get("id", "")
            source_id = raw_id.replace("https://openalex.org/", "").strip() or raw_id

            # DOI: strip URL prefix.
            raw_doi: Optional[str] = work.get("doi")
            doi: Optional[str] = None
            if raw_doi:
                doi = raw_doi.replace("https://doi.org/", "").strip() or None

            # Authors — first 6 only.
            authorships: list[dict] = work.get("authorships") or []
            authors: list[str] = []
            for authorship in authorships[:6]:
                author_obj = authorship.get("author") or {}
                name = author_obj.get("display_name")
                if name:
                    authors.append(name)

            year: Optional[int] = work.get("publication_year")

            # Journal name from primary_location.
            journal: Optional[str] = None
            primary_location = work.get("primary_location") or {}
            source_obj = primary_location.get("source") or {}
            journal = source_obj.get("display_name") or None

            # Abstract from inverted index.
            inverted_index: Optional[dict] = work.get("abstract_inverted_index")
            abstract: Optional[str] = None
            if inverted_index:
                reconstructed = inverted_index_to_abstract(inverted_index)
                abstract = reconstructed if reconstructed else None

            # Open access.
            oa_info: dict = work.get("open_access") or {}
            open_access: bool = bool(oa_info.get("is_oa", False))
            oa_url: Optional[str] = oa_info.get("oa_url") or None

            # Study design via heuristic.
            study_design = self._detect_study_design(title or "", abstract or "")

            logger.debug(
                "OpenAlex: parsed paper title=%r doi=%s", title, doi
            )

            return PaperRaw(
                source="openalex",
                source_id=source_id,
                doi=doi,
                pmid=None,
                title=title,
                authors=authors,
                year=year,
                journal=journal,
                abstract=abstract,
                open_access=open_access,
                oa_url=oa_url,
                s2_tldr=None,
                s2_influential_citations=0,
                s2_citation_count=0,
                study_design=study_design,
                condition_tags=list(condition_tags),
                modality_tags=list(modality_tags),
                fetched_at=datetime.now(timezone.utc).isoformat(),
            )

        except Exception:
            logger.warning(
                "OpenAlex: failed to parse work id=%s — skipping",
                work.get("id", "<unknown>"),
                exc_info=True,
            )
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
