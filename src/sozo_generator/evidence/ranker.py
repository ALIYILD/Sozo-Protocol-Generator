"""
Extended evidence ranker — ranks EvidenceItem objects by evidence level,
recency, relevance, and category match.

Builds on the constants and patterns from article_ranker.py but operates
on the EvidenceItem contract type used across Phase 2.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from ..core.enums import ClaimCategory, EvidenceLevel, EvidenceRelation
from ..schemas.contracts import EvidenceItem

logger = logging.getLogger(__name__)

# ── Scoring constants (aligned with article_ranker) ──────────────────

EVIDENCE_WEIGHT: dict[EvidenceLevel, float] = {
    EvidenceLevel.HIGHEST: 5.0,
    EvidenceLevel.HIGH: 4.0,
    EvidenceLevel.MEDIUM: 3.0,
    EvidenceLevel.LOW: 2.0,
    EvidenceLevel.VERY_LOW: 1.0,
    EvidenceLevel.MISSING: 0.0,
}

RECENCY_BONUS: dict[int, float] = {
    0: 2.0,   # current year
    1: 1.5,
    2: 1.0,
    3: 0.5,
}

# Bonus for items that support (vs contradict/neutral)
_RELATION_BONUS: dict[EvidenceRelation, float] = {
    EvidenceRelation.SUPPORTS: 0.5,
    EvidenceRelation.CONTRADICTS: 0.3,  # still valuable
    EvidenceRelation.NEUTRAL: 0.0,
    EvidenceRelation.INDIRECT: 0.1,
}

# ── Category keyword map for relevance scoring ───────────────────────

_CATEGORY_KEYWORDS: dict[ClaimCategory, list[str]] = {
    ClaimCategory.PATHOPHYSIOLOGY: ["pathophysiology", "mechanism", "neurobiology", "etiology"],
    ClaimCategory.BRAIN_REGIONS: ["cortex", "region", "cortical", "subcortical", "prefrontal"],
    ClaimCategory.NETWORK_INVOLVEMENT: ["network", "connectivity", "resting state", "connectome"],
    ClaimCategory.CLINICAL_PHENOTYPES: ["phenotype", "subtype", "presentation", "classification"],
    ClaimCategory.ASSESSMENT_TOOLS: ["scale", "measure", "questionnaire", "assessment", "psychometric"],
    ClaimCategory.STIMULATION_TARGETS: ["target", "montage", "electrode", "stimulation site"],
    ClaimCategory.STIMULATION_PARAMETERS: ["dosage", "intensity", "duration", "parameter", "protocol"],
    ClaimCategory.MODALITY_RATIONALE: ["efficacy", "effectiveness", "rationale", "mechanism"],
    ClaimCategory.SAFETY: ["safety", "adverse", "side effect", "tolerability"],
    ClaimCategory.CONTRAINDICATIONS: ["contraindication", "precaution", "risk", "exclusion"],
    ClaimCategory.RESPONDER_CRITERIA: ["responder", "predictor", "biomarker", "treatment response"],
    ClaimCategory.INCLUSION_CRITERIA: ["inclusion", "eligibility", "selection"],
    ClaimCategory.EXCLUSION_CRITERIA: ["exclusion", "ineligible", "contraindication"],
}


def rank_evidence_items(
    items: list[EvidenceItem],
    top_n: int = 20,
    current_year: int | None = None,
) -> list[EvidenceItem]:
    """Rank evidence items by composite score, return top N.

    Scoring combines evidence level weight, recency bonus, relation bonus,
    key-finding richness, and the item's existing relevance_score.
    """
    if current_year is None:
        current_year = datetime.now(timezone.utc).year

    scored: list[tuple[EvidenceItem, float]] = []
    for item in items:
        score = _compute_composite_score(item, current_year)
        scored.append((item, score))

    scored.sort(key=lambda x: x[1], reverse=True)

    ranked = [item for item, _ in scored[:top_n]]
    logger.info(
        "Ranked %d evidence items -> top %d returned",
        len(items),
        len(ranked),
    )
    return ranked


def compute_relevance_score(
    item: EvidenceItem,
    condition_slug: str,
    target_category: ClaimCategory,
) -> float:
    """Compute a 0-10 relevance score for an item relative to a condition and category.

    Higher scores mean the item is more relevant to the target category for
    the given condition.
    """
    score = 0.0

    # Evidence level base (0-5)
    score += EVIDENCE_WEIGHT.get(item.evidence_level, 0.0)

    # Condition match bonus
    if item.condition_slug and item.condition_slug == condition_slug:
        score += 1.0

    # Category keyword match in key_finding
    keywords = _CATEGORY_KEYWORDS.get(target_category, [])
    finding_lower = item.key_finding.lower()
    title_lower = item.title.lower()
    combined_text = f"{finding_lower} {title_lower}"

    keyword_hits = sum(1 for kw in keywords if kw in combined_text)
    if keywords:
        score += min(keyword_hits / len(keywords) * 3.0, 3.0)

    # Relation bonus
    score += _RELATION_BONUS.get(item.relation, 0.0)

    # Key finding richness
    if item.key_finding and len(item.key_finding) > 50:
        score += 0.5

    return min(score, 10.0)


# ── Internal ─────────────────────────────────────────────────────────


def _compute_composite_score(item: EvidenceItem, current_year: int) -> float:
    """Compute composite ranking score for an EvidenceItem."""
    score = 0.0

    # Evidence level weight (0-5)
    score += EVIDENCE_WEIGHT.get(item.evidence_level, 0.0)

    # Recency bonus (0-2)
    if item.year:
        age = current_year - item.year
        score += RECENCY_BONUS.get(min(age, 3), 0.0)

    # Relation bonus (0-0.5)
    score += _RELATION_BONUS.get(item.relation, 0.0)

    # Existing relevance_score contribution (0-2)
    score += item.relevance_score * 0.2

    # Key finding richness bonus (0-0.5)
    if item.key_finding and len(item.key_finding) > 50:
        score += 0.5

    # Population match bonus
    if item.population_match:
        score += 0.3

    return score
