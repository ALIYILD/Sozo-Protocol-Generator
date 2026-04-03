"""
Phase 8 Evidence Ingestion — Consensus API Client
===================================================
Wraps the Consensus API (https://consensus.app/api/) for structured
academic search.  Returns :class:`ConsensusFinding` objects ready for
downstream deduplication and PICO enrichment.

Authentication
--------------
Set the ``CONSENSUS_API_KEY`` environment variable (or pass ``api_key``
to the constructor).  Get a key at https://consensus.app/api/.

Rate limits
-----------
Default: 100 requests/minute on standard plans.  The client enforces a
configurable ``requests_per_minute`` ceiling with a token-bucket approach
and retries on 429 / 5xx with exponential back-off (max 3 attempts).

Endpoint assumptions
--------------------
Consensus REST API v1 (as documented at consensus.app/api/):
  POST /search/
  Content-Type: application/json
  Authorization: Bearer <api_key>

  Body: {
    "query": "<natural-language question>",
    "filters": {
      "study_types": ["RCT", "Meta-Analysis", "Systematic Review"],
      "human_only": true,
      "year_min": 2000
    },
    "page": 1,
    "per_page": 10   # max 10 per request on standard plan
  }

  Response: {
    "total_results": <int>,
    "papers": [
      {
        "id": "<consensus_paper_id>",
        "title": "<str>",
        "year": <int>,
        "journal": "<str>",
        "authors": ["<str>", ...],
        "doi": "<str>",
        "pmid": "<str|null>",
        "url": "<str>",
        "citation_count": <int>,
        "study_type": "<str>",
        "sample_size": <int|null>,
        "finding": "<claim sentence>",
        "outcome_direction": "positive|negative|null|mixed"
      },
      ...
    ]
  }
"""

from __future__ import annotations

import logging
import os
import time
from typing import Optional

import httpx
from pydantic import ValidationError

from .models import ConsensusFinding

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_BASE_URL: str = "https://consensus.app/api"
_SEARCH_ENDPOINT: str = f"{_BASE_URL}/search/"
_DEFAULT_PER_PAGE: int = 10       # Consensus standard plan max
_MAX_PAGES: int = 5               # ceiling: 50 results per query
_DEFAULT_RPM: int = 100           # requests per minute rate cap
_RETRY_ATTEMPTS: int = 3
_RETRY_BACKOFF_BASE: float = 2.0  # seconds; doubled each retry

# Consensus study type labels (as expected by the API filter)
STUDY_TYPES_RCT_META: list[str] = [
    "RCT",
    "Meta-Analysis",
    "Systematic Review",
    "Controlled Trial",
]

OUTCOME_DIRECTION_MAP: dict[str, str] = {
    "positive": "positive",
    "negative": "negative",
    "null": "null",
    "mixed": "mixed",
    # aliases the API might return
    "no effect": "null",
    "inconclusive": "mixed",
    "unclear": "mixed",
}


# ---------------------------------------------------------------------------
# ConsensusClient
# ---------------------------------------------------------------------------

class ConsensusClient:
    """
    Client for the Consensus academic search API.

    Parameters
    ----------
    api_key:
        Consensus API key.  Falls back to the ``CONSENSUS_API_KEY``
        environment variable if not supplied.
    requests_per_minute:
        Maximum number of API calls per 60-second window.
    timeout:
        Per-request HTTP timeout in seconds.
    dry_run:
        When True the client returns an empty result list without hitting
        the network.  Useful for offline testing.

    Example
    -------
    ::

        client = ConsensusClient()
        findings = client.search(
            query="Does tDCS improve depression symptoms?",
            study_types=["RCT", "Meta-Analysis"],
            human_only=True,
            max_results=30,
        )
        for f in findings:
            print(f.claim, f.outcome_direction)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        requests_per_minute: int = _DEFAULT_RPM,
        timeout: float = 30.0,
        dry_run: bool = False,
    ) -> None:
        self.api_key = api_key or os.environ.get("CONSENSUS_API_KEY", "")
        self.requests_per_minute = requests_per_minute
        self.timeout = timeout
        self.dry_run = dry_run

        if not self.api_key and not self.dry_run:
            logger.warning(
                "CONSENSUS_API_KEY not set.  Requests will fail with 401. "
                "Pass api_key= or set the environment variable."
            )

        # Token-bucket state: track timestamps of recent requests.
        self._request_times: list[float] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        study_types: Optional[list[str]] = None,
        human_only: bool = True,
        year_min: int = 2000,
        max_results: int = 50,
    ) -> list[ConsensusFinding]:
        """
        Search Consensus for papers matching *query*.

        Parameters
        ----------
        query:
            Natural-language research question (e.g. ``"Does tDCS improve
            depression symptoms?"``).
        study_types:
            List of Consensus study type labels to filter on.  Defaults to
            ``STUDY_TYPES_RCT_META`` (RCT + Meta-Analysis + Systematic Review).
        human_only:
            If True, restrict to studies on human participants.
        year_min:
            Earliest publication year to include.
        max_results:
            Maximum number of findings to return (capped at
            ``_DEFAULT_PER_PAGE × _MAX_PAGES``).

        Returns
        -------
        list[ConsensusFinding]
            Findings ordered as returned by the API (relevance-ranked).
        """
        if self.dry_run:
            logger.info("[dry_run] ConsensusClient.search(%r) — returning []", query)
            return []

        if study_types is None:
            study_types = STUDY_TYPES_RCT_META

        findings: list[ConsensusFinding] = []
        page = 1

        while len(findings) < max_results and page <= _MAX_PAGES:
            per_page = min(_DEFAULT_PER_PAGE, max_results - len(findings))
            batch = self._fetch_page(
                query=query,
                study_types=study_types,
                human_only=human_only,
                year_min=year_min,
                page=page,
                per_page=per_page,
            )
            if not batch:
                break
            findings.extend(batch)
            if len(batch) < per_page:
                break   # last page reached
            page += 1

        logger.info(
            "Consensus search(%r): retrieved %d findings across %d page(s)",
            query,
            len(findings),
            page,
        )
        return findings

    def multi_query_search(
        self,
        queries: list[str],
        study_types: Optional[list[str]] = None,
        human_only: bool = True,
        year_min: int = 2000,
        max_per_query: int = 30,
    ) -> list[ConsensusFinding]:
        """
        Run multiple queries and merge results, deduplicating by DOI.

        Parameters
        ----------
        queries:
            Ordered list of query strings.  Earlier queries are preferred
            when DOI collisions occur.
        max_per_query:
            Per-query result ceiling.

        Returns
        -------
        list[ConsensusFinding]
            Merged, DOI-deduplicated findings.
        """
        seen_dois: set[str] = set()
        all_findings: list[ConsensusFinding] = []

        for q in queries:
            batch = self.search(
                query=q,
                study_types=study_types,
                human_only=human_only,
                year_min=year_min,
                max_results=max_per_query,
            )
            for f in batch:
                key = (f.doi or "").lower().strip() or f.consensus_paper_id
                if key not in seen_dois:
                    seen_dois.add(key)
                    all_findings.append(f)

        logger.info(
            "multi_query_search: %d queries → %d deduplicated findings",
            len(queries),
            len(all_findings),
        )
        return all_findings

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_page(
        self,
        query: str,
        study_types: list[str],
        human_only: bool,
        year_min: int,
        page: int,
        per_page: int,
    ) -> list[ConsensusFinding]:
        """Fetch a single page from the Consensus search endpoint."""
        self._rate_limit()

        payload: dict = {
            "query": query,
            "filters": {
                "study_types": study_types,
                "human_only": human_only,
                "year_min": year_min,
            },
            "page": page,
            "per_page": per_page,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(1, _RETRY_ATTEMPTS + 1):
            try:
                response = httpx.post(
                    _SEARCH_ENDPOINT,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
                return self._parse_response(data, query)

            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                if status == 429 or status >= 500:
                    wait = _RETRY_BACKOFF_BASE ** attempt
                    logger.warning(
                        "Consensus API HTTP %d on attempt %d/%d — "
                        "retrying in %.1fs (query=%r)",
                        status,
                        attempt,
                        _RETRY_ATTEMPTS,
                        wait,
                        query,
                    )
                    time.sleep(wait)
                    continue
                logger.error(
                    "Consensus API HTTP %d (non-retryable) for query=%r: %s",
                    status,
                    query,
                    exc,
                )
                return []

            except (httpx.RequestError, ValueError) as exc:
                wait = _RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    "Consensus API request error on attempt %d/%d — "
                    "retrying in %.1fs: %s",
                    attempt,
                    _RETRY_ATTEMPTS,
                    wait,
                    exc,
                )
                time.sleep(wait)

        logger.error("Consensus API: all %d attempts failed for query=%r", _RETRY_ATTEMPTS, query)
        return []

    def _parse_response(self, data: dict, query: str) -> list[ConsensusFinding]:
        """Convert raw API JSON to a list of ConsensusFinding objects."""
        papers = data.get("papers", [])
        findings: list[ConsensusFinding] = []

        for raw in papers:
            try:
                outcome_raw = (raw.get("outcome_direction") or "").lower().strip()
                outcome = OUTCOME_DIRECTION_MAP.get(outcome_raw, "unknown") if outcome_raw else None

                doi = _normalise_doi(raw.get("doi") or "")
                pmid = str(raw["pmid"]) if raw.get("pmid") else None

                finding = ConsensusFinding(
                    consensus_paper_id=str(raw.get("id", "")),
                    query=query,
                    claim=raw.get("finding") or raw.get("excerpt") or raw.get("summary") or "",
                    outcome_direction=outcome,  # type: ignore[arg-type]
                    study_type=raw.get("study_type"),
                    sample_size=_safe_int(raw.get("sample_size")),
                    doi=doi or None,
                    pmid=pmid,
                    title=raw.get("title"),
                    authors=raw.get("authors") or [],
                    year=_safe_int(raw.get("year")),
                    journal=raw.get("journal"),
                    url=raw.get("url"),
                    citation_count=_safe_int(raw.get("citation_count")) or 0,
                )
                findings.append(finding)

            except (ValidationError, KeyError, TypeError) as exc:
                logger.warning(
                    "Skipping malformed Consensus paper record: %s — raw=%r",
                    exc,
                    raw,
                )

        return findings

    def _rate_limit(self) -> None:
        """Block until we are within the requests_per_minute budget."""
        now = time.monotonic()
        window_start = now - 60.0
        # Prune timestamps outside the rolling 60-second window.
        self._request_times = [t for t in self._request_times if t > window_start]

        if len(self._request_times) >= self.requests_per_minute:
            oldest = self._request_times[0]
            sleep_for = 60.0 - (now - oldest) + 0.05   # small buffer
            if sleep_for > 0:
                logger.debug("Rate limit: sleeping %.2fs", sleep_for)
                time.sleep(sleep_for)

        self._request_times.append(time.monotonic())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _normalise_doi(raw: str) -> str:
    """Strip URL prefixes from a DOI string."""
    raw = (raw or "").strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if raw.lower().startswith(prefix):
            return raw[len(prefix):]
    return raw


def _safe_int(value: object) -> Optional[int]:
    """Return int(value) or None if conversion fails."""
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
