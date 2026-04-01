"""
Contradiction detector — identifies conflicting evidence within bundles.

Uses keyword heuristics on key_finding text to flag pairs of items where
one reports positive outcomes and the other reports null/negative outcomes
for the same claim category.
"""
from __future__ import annotations

import logging
from itertools import combinations
from typing import Optional

from pydantic import BaseModel, Field

from ..core.enums import ClaimCategory, EvidenceRelation
from ..schemas.contracts import EvidenceBundle, EvidenceItem

logger = logging.getLogger(__name__)

# ── Direction keywords ───────────────────────────────────────────────

_POSITIVE_KEYWORDS: list[str] = [
    "effective",
    "improved",
    "improvement",
    "beneficial",
    "significant reduction",
    "significant improvement",
    "superior",
    "positive outcome",
    "therapeutic benefit",
    "clinically meaningful",
    "well-tolerated",
    "safe and effective",
    "enhances",
    "supports the use of",
]

_NEGATIVE_KEYWORDS: list[str] = [
    "no effect",
    "ineffective",
    "no significant",
    "no improvement",
    "no benefit",
    "not effective",
    "failed to demonstrate",
    "no difference",
    "inconclusive",
    "inferior",
    "not superior",
    "no therapeutic",
    "null result",
    "did not improve",
    "no evidence of benefit",
]


# ── Models ───────────────────────────────────────────────────────────


class ContradictionPair(BaseModel):
    """A pair of evidence items with conflicting findings."""

    item_a_pmid: str = ""
    item_b_pmid: str = ""
    category: ClaimCategory = ClaimCategory.PATHOPHYSIOLOGY
    description: str = ""


class ContradictionResult(BaseModel):
    """Result of contradiction detection for a single bundle."""

    bundle_id: str
    has_contradictions: bool = False
    contradictions: list[ContradictionPair] = Field(default_factory=list)

    @property
    def contradiction_count(self) -> int:
        return len(self.contradictions)


# ── Public API ───────────────────────────────────────────────────────


def detect_contradictions(bundle: EvidenceBundle) -> ContradictionResult:
    """Detect contradictory evidence within a single bundle.

    Checks for:
    1. Items with opposite EvidenceRelation values (SUPPORTS vs CONTRADICTS)
    2. Items whose key_finding text suggests opposite directional conclusions
    """
    contradictions: list[ContradictionPair] = []

    # Check relation-based contradictions
    contradictions.extend(_check_relation_conflict(bundle.items, bundle.category))

    # Check keyword-based direction conflicts
    contradictions.extend(_check_direction_conflict(bundle.items, bundle.category))

    # Deduplicate by PMID pair
    contradictions = _deduplicate_pairs(contradictions)

    has_contradictions = len(contradictions) > 0

    if has_contradictions:
        logger.info(
            "Bundle %s: %d contradictions detected",
            bundle.bundle_id,
            len(contradictions),
        )

    return ContradictionResult(
        bundle_id=bundle.bundle_id,
        has_contradictions=has_contradictions,
        contradictions=contradictions,
    )


def scan_all_bundles(
    bundles: list[EvidenceBundle],
) -> list[ContradictionResult]:
    """Scan all bundles for contradictions. Returns results for every bundle."""
    results: list[ContradictionResult] = []
    total_contradictions = 0

    for bundle in bundles:
        result = detect_contradictions(bundle)
        results.append(result)
        total_contradictions += result.contradiction_count

    logger.info(
        "Scanned %d bundles: %d total contradictions found",
        len(bundles),
        total_contradictions,
    )
    return results


# ── Internal helpers ─────────────────────────────────────────────────


def _check_relation_conflict(
    items: list[EvidenceItem],
    category: ClaimCategory,
) -> list[ContradictionPair]:
    """Find pairs where one item SUPPORTS and another CONTRADICTS."""
    supporting = [i for i in items if i.relation == EvidenceRelation.SUPPORTS]
    contradicting = [i for i in items if i.relation == EvidenceRelation.CONTRADICTS]

    pairs: list[ContradictionPair] = []
    for sup in supporting:
        for con in contradicting:
            pairs.append(ContradictionPair(
                item_a_pmid=sup.pmid or "unknown",
                item_b_pmid=con.pmid or "unknown",
                category=category,
                description=(
                    f"Relation conflict: '{_truncate(sup.title, 60)}' (supports) "
                    f"vs '{_truncate(con.title, 60)}' (contradicts)"
                ),
            ))

    return pairs


def _check_direction_conflict(
    items: list[EvidenceItem],
    category: ClaimCategory,
) -> list[ContradictionPair]:
    """Find pairs where key_finding keywords suggest opposite directions.

    One item uses positive keywords (effective, improved, beneficial) while
    another uses negative keywords (no effect, ineffective, no significant).
    """
    positive_items: list[EvidenceItem] = []
    negative_items: list[EvidenceItem] = []

    for item in items:
        finding = item.key_finding.lower()
        if not finding:
            continue

        is_positive = any(kw in finding for kw in _POSITIVE_KEYWORDS)
        is_negative = any(kw in finding for kw in _NEGATIVE_KEYWORDS)

        # Only classify if unambiguous
        if is_positive and not is_negative:
            positive_items.append(item)
        elif is_negative and not is_positive:
            negative_items.append(item)

    pairs: list[ContradictionPair] = []
    for pos in positive_items:
        for neg in negative_items:
            # Skip if same PMID
            if pos.pmid and neg.pmid and pos.pmid == neg.pmid:
                continue

            pairs.append(ContradictionPair(
                item_a_pmid=pos.pmid or "unknown",
                item_b_pmid=neg.pmid or "unknown",
                category=category,
                description=(
                    f"Direction conflict: '{_truncate(pos.key_finding, 60)}' "
                    f"vs '{_truncate(neg.key_finding, 60)}'"
                ),
            ))

    return pairs


def _deduplicate_pairs(pairs: list[ContradictionPair]) -> list[ContradictionPair]:
    """Remove duplicate contradiction pairs (same PMIDs, either order)."""
    seen: set[tuple[str, str]] = set()
    unique: list[ContradictionPair] = []

    for pair in pairs:
        key = tuple(sorted([pair.item_a_pmid, pair.item_b_pmid]))
        if key in seen:
            continue
        seen.add(key)
        unique.append(pair)

    return unique


def _truncate(text: str, max_len: int) -> str:
    """Truncate text to max_len, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."
