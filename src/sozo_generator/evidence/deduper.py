"""
Evidence deduplication — PMID-based dedup with metadata merging.

Handles both EvidenceItem (contract-level) and ArticleMetadata (schema-level)
deduplication, keeping the version with the higher relevance/evidence score.
"""
from __future__ import annotations

import logging
from typing import Optional

from pydantic import BaseModel, Field

from ..schemas.contracts import EvidenceItem
from ..schemas.evidence import ArticleMetadata
from .article_ranker import deduplicate_articles  # re-export existing

logger = logging.getLogger(__name__)

__all__ = [
    "DeduplicationResult",
    "deduplicate_evidence_items",
    "deduplicate_articles",
    "merge_duplicate_metadata",
]


class DeduplicationResult(BaseModel):
    """Result of deduplicating a list of EvidenceItems."""

    unique_items: list[EvidenceItem] = Field(default_factory=list)
    duplicates_removed: int = 0
    merge_log: list[str] = Field(default_factory=list)


def deduplicate_evidence_items(
    items: list[EvidenceItem],
) -> DeduplicationResult:
    """Deduplicate EvidenceItems by PMID, merging metadata from duplicates.

    Items without a PMID are always kept (no dedup key).
    When duplicates are found, the one with the higher relevance_score is kept,
    and any missing fields are filled from the duplicate.
    """
    seen: dict[str, EvidenceItem] = {}
    no_pmid: list[EvidenceItem] = []
    merge_log: list[str] = []
    duplicates_removed = 0

    for item in items:
        if not item.pmid:
            no_pmid.append(item)
            continue

        if item.pmid not in seen:
            seen[item.pmid] = item
        else:
            existing = seen[item.pmid]
            merged = merge_duplicate_metadata(existing, item)
            seen[item.pmid] = merged
            duplicates_removed += 1
            merge_log.append(
                f"Merged PMID {item.pmid}: kept relevance_score="
                f"{merged.relevance_score:.2f} (was {existing.relevance_score:.2f} "
                f"vs {item.relevance_score:.2f})"
            )

    unique = list(seen.values()) + no_pmid

    if duplicates_removed > 0:
        logger.info(
            "Deduplication: %d items -> %d unique (%d duplicates merged)",
            len(items),
            len(unique),
            duplicates_removed,
        )

    return DeduplicationResult(
        unique_items=unique,
        duplicates_removed=duplicates_removed,
        merge_log=merge_log,
    )


def merge_duplicate_metadata(
    existing: EvidenceItem,
    new: EvidenceItem,
) -> EvidenceItem:
    """Merge two EvidenceItems with the same PMID.

    Keeps the item with the higher relevance_score as the base, then fills
    in any missing fields from the other.
    """
    if new.relevance_score > existing.relevance_score:
        primary, secondary = new, existing
    else:
        primary, secondary = existing, new

    # Build merged item from primary, filling gaps from secondary
    merged_data = primary.model_dump()

    # Fill empty string fields from secondary
    for field_name in ("title", "authors_short", "key_finding"):
        if not getattr(primary, field_name) and getattr(secondary, field_name):
            merged_data[field_name] = getattr(secondary, field_name)

    # Fill None fields from secondary
    for field_name in ("doi", "journal", "year", "condition_slug"):
        if getattr(primary, field_name) is None and getattr(secondary, field_name) is not None:
            merged_data[field_name] = getattr(secondary, field_name)

    # Merge modalities (union)
    primary_mods = set(primary.modalities)
    secondary_mods = set(secondary.modalities)
    merged_data["modalities"] = list(primary_mods | secondary_mods)

    return EvidenceItem(**merged_data)
