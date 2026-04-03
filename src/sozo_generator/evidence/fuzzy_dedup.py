"""
Fuzzy deduplication — extends PMID-only dedup with DOI matching and
title similarity for cross-source deduplication.

Uses trigram similarity (SequenceMatcher) for title comparison,
avoiding the need for database extensions.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Optional

from ..schemas.evidence import ArticleMetadata
from .pipeline_tracker import PipelineTracker, PipelineStage, PipelineDecision

logger = logging.getLogger(__name__)

# Minimum similarity threshold for title-based dedup
TITLE_SIMILARITY_THRESHOLD = 0.85


@dataclass
class FuzzyDedupResult:
    """Result of fuzzy deduplication."""

    unique_articles: list[ArticleMetadata] = field(default_factory=list)
    duplicates_removed: int = 0
    merge_log: list[str] = field(default_factory=list)
    method_counts: dict[str, int] = field(default_factory=dict)


def normalize_title(title: str) -> str:
    """Normalize title for comparison: lowercase, strip punctuation/whitespace."""
    title = title.lower().strip()
    title = re.sub(r"[^\w\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title


def title_similarity(title_a: str, title_b: str) -> float:
    """Compute similarity between two titles using SequenceMatcher."""
    norm_a = normalize_title(title_a)
    norm_b = normalize_title(title_b)
    if not norm_a or not norm_b:
        return 0.0
    return SequenceMatcher(None, norm_a, norm_b).ratio()


def fuzzy_deduplicate(
    articles: list[ArticleMetadata],
    similarity_threshold: float = TITLE_SIMILARITY_THRESHOLD,
    tracker: Optional[PipelineTracker] = None,
) -> FuzzyDedupResult:
    """Deduplicate articles using PMID, DOI, and title similarity.

    Priority order for keeping records:
    1. Records with PMIDs are preferred over records without
    2. Higher evidence scores are preferred
    3. Records with abstracts are preferred

    Args:
        articles: List of articles to deduplicate
        similarity_threshold: Minimum title similarity to consider as duplicate
        tracker: Optional pipeline tracker for PRISMA audit trail
    """
    result = FuzzyDedupResult()
    method_counts = {"pmid": 0, "doi": 0, "title": 0}

    # Phase 1: Index by PMID and DOI
    seen_pmids: dict[str, int] = {}  # pmid → index in unique list
    seen_dois: dict[str, int] = {}   # normalized doi → index in unique list
    unique: list[ArticleMetadata] = []

    # Sort: prefer articles with PMIDs, then higher score, then with abstracts
    sorted_articles = sorted(
        articles,
        key=lambda a: (
            1 if a.pmid else 0,
            a.score,
            1 if a.abstract else 0,
        ),
        reverse=True,
    )

    for article in sorted_articles:
        identifier = article.pmid or article.doi or article.title[:50]

        # Check PMID exact match
        if article.pmid and article.pmid in seen_pmids:
            idx = seen_pmids[article.pmid]
            _merge_metadata(unique[idx], article)
            result.merge_log.append(
                f"PMID {article.pmid}: merged duplicate"
            )
            method_counts["pmid"] += 1
            if tracker:
                tracker.log_dedup(identifier, merged_into=article.pmid)
            continue

        # Check DOI exact match
        if article.doi:
            doi_norm = article.doi.lower().strip()
            if doi_norm in seen_dois:
                idx = seen_dois[doi_norm]
                _merge_metadata(unique[idx], article)
                result.merge_log.append(
                    f"DOI {article.doi}: merged duplicate"
                )
                method_counts["doi"] += 1
                if tracker:
                    tracker.log_dedup(identifier, merged_into=article.doi)
                continue

        # Phase 2: Title similarity check (only against existing unique list)
        is_dup = False
        for i, existing in enumerate(unique):
            sim = title_similarity(article.title, existing.title)
            if sim >= similarity_threshold:
                _merge_metadata(existing, article)
                result.merge_log.append(
                    f"Title match ({sim:.2f}): "
                    f"'{article.title[:40]}...' ≈ '{existing.title[:40]}...'"
                )
                method_counts["title"] += 1
                is_dup = True
                if tracker:
                    tracker.log_dedup(
                        identifier,
                        merged_into=existing.pmid or existing.doi or existing.title[:30],
                    )
                break

        if is_dup:
            continue

        # Not a duplicate — add to unique list
        idx = len(unique)
        unique.append(article)

        if article.pmid:
            seen_pmids[article.pmid] = idx
        if article.doi:
            seen_dois[article.doi.lower().strip()] = idx

        if tracker:
            tracker.log_dedup(identifier, is_duplicate=False)

    result.unique_articles = unique
    result.duplicates_removed = len(articles) - len(unique)
    result.method_counts = method_counts

    logger.info(
        "Fuzzy dedup: %d → %d unique (%d removed: %d PMID, %d DOI, %d title)",
        len(articles),
        len(unique),
        result.duplicates_removed,
        method_counts["pmid"],
        method_counts["doi"],
        method_counts["title"],
    )

    return result


def _merge_metadata(primary: ArticleMetadata, secondary: ArticleMetadata) -> None:
    """Merge metadata from secondary into primary, filling gaps."""
    # Fill missing identifiers
    if not primary.pmid and secondary.pmid:
        primary.pmid = secondary.pmid
    if not primary.doi and secondary.doi:
        primary.doi = secondary.doi

    # Fill missing abstract
    if not primary.abstract and secondary.abstract:
        primary.abstract = secondary.abstract

    # Fill missing journal
    if not primary.journal and secondary.journal:
        primary.journal = secondary.journal

    # Fill missing year
    if not primary.year and secondary.year:
        primary.year = secondary.year

    # Merge authors if primary has fewer
    if len(secondary.authors) > len(primary.authors):
        primary.authors = secondary.authors

    # Take higher score
    if secondary.score > primary.score:
        primary.score = secondary.score
        primary.evidence_type = secondary.evidence_type
        primary.evidence_level = secondary.evidence_level

    # Merge key findings
    for finding in secondary.key_findings:
        if finding not in primary.key_findings:
            primary.key_findings.append(finding)

    # Merge source notes
    if secondary.notes and secondary.notes not in (primary.notes or ""):
        primary.notes = f"{primary.notes or ''} {secondary.notes}".strip()
