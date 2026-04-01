"""
Evidence clusterer — groups EvidenceItems into section-level EvidenceBundles.

Items are assigned to ClaimCategory buckets using keyword heuristics on their
titles, key_findings, and modality tags. Each bundle receives a computed
confidence label based on the evidence levels present.
"""
from __future__ import annotations

import logging
from collections import defaultdict

from ..core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    EvidenceLevel,
    EvidenceRelation,
    Modality,
)
from ..schemas.contracts import EvidenceBundle, EvidenceItem

logger = logging.getLogger(__name__)

# ── Category assignment heuristics ───────────────────────────────────

_CATEGORY_KEYWORDS: dict[ClaimCategory, list[str]] = {
    ClaimCategory.PATHOPHYSIOLOGY: [
        "pathophysiology", "mechanism", "neurobiology", "etiology",
        "neuroinflammation", "oxidative stress", "neurodegeneration",
    ],
    ClaimCategory.BRAIN_REGIONS: [
        "cortex", "cortical", "subcortical", "prefrontal", "dlpfc",
        "hippocampus", "amygdala", "temporal", "parietal", "brain region",
    ],
    ClaimCategory.NETWORK_INVOLVEMENT: [
        "network", "connectivity", "resting state", "connectome",
        "default mode", "salience", "central executive", "functional connectivity",
    ],
    ClaimCategory.CLINICAL_PHENOTYPES: [
        "phenotype", "subtype", "classification", "clinical presentation",
        "symptom cluster", "endophenotype",
    ],
    ClaimCategory.ASSESSMENT_TOOLS: [
        "scale", "questionnaire", "measure", "assessment", "psychometric",
        "outcome measure", "screening", "inventory",
    ],
    ClaimCategory.STIMULATION_TARGETS: [
        "target", "montage", "electrode placement", "stimulation site",
        "anode", "cathode", "f3", "f4",
    ],
    ClaimCategory.STIMULATION_PARAMETERS: [
        "dosage", "intensity", "duration", "frequency", "protocol",
        "milliamp", "session", "parameter", "sham",
    ],
    ClaimCategory.MODALITY_RATIONALE: [
        "rationale", "mechanism of action", "efficacy", "effectiveness",
        "therapeutic", "clinical trial", "treatment outcome",
    ],
    ClaimCategory.SAFETY: [
        "safety", "adverse", "side effect", "tolerability", "adverse event",
        "skin irritation", "headache",
    ],
    ClaimCategory.CONTRAINDICATIONS: [
        "contraindication", "precaution", "risk", "seizure risk",
        "implant", "pacemaker", "pregnancy",
    ],
    ClaimCategory.RESPONDER_CRITERIA: [
        "responder", "predictor", "biomarker", "treatment response",
        "non-responder", "prognostic",
    ],
    ClaimCategory.INCLUSION_CRITERIA: [
        "inclusion criteria", "eligibility", "patient selection",
        "eligible", "enrollment",
    ],
    ClaimCategory.EXCLUSION_CRITERIA: [
        "exclusion criteria", "ineligible", "excluded", "disqualified",
    ],
}

# Modality-related categories that get boosted when modality tags are present
_MODALITY_BOOST_CATEGORIES: set[ClaimCategory] = {
    ClaimCategory.STIMULATION_TARGETS,
    ClaimCategory.STIMULATION_PARAMETERS,
    ClaimCategory.MODALITY_RATIONALE,
    ClaimCategory.SAFETY,
    ClaimCategory.CONTRAINDICATIONS,
}

# ── Confidence level thresholds ──────────────────────────────────────

_LEVEL_WEIGHT: dict[EvidenceLevel, int] = {
    EvidenceLevel.HIGHEST: 5,
    EvidenceLevel.HIGH: 4,
    EvidenceLevel.MEDIUM: 3,
    EvidenceLevel.LOW: 2,
    EvidenceLevel.VERY_LOW: 1,
    EvidenceLevel.MISSING: 0,
}


def cluster_into_bundles(
    items: list[EvidenceItem],
    condition_slug: str,
) -> list[EvidenceBundle]:
    """Cluster evidence items into bundles grouped by ClaimCategory.

    Each item is assigned to exactly one category. A bundle is created for
    each category that has at least one item.
    """
    buckets: dict[ClaimCategory, list[EvidenceItem]] = defaultdict(list)

    for item in items:
        category = _assign_category(item)
        buckets[category].append(item)

    bundles: list[EvidenceBundle] = []
    for category in ClaimCategory:
        cat_items = buckets.get(category, [])
        if not cat_items:
            continue

        bundle_id = f"{condition_slug}_{category.value}"
        confidence = _compute_bundle_confidence(cat_items)
        has_contradictions = any(
            i.relation == EvidenceRelation.CONTRADICTS for i in cat_items
        )

        bundle = EvidenceBundle(
            bundle_id=bundle_id,
            condition_slug=condition_slug,
            category=category,
            items=cat_items,
            confidence=confidence,
            has_contradictions=has_contradictions,
        )
        bundles.append(bundle)

    logger.info(
        "Clustered %d items into %d bundles for %s",
        len(items),
        len(bundles),
        condition_slug,
    )

    return bundles


def _assign_category(item: EvidenceItem) -> ClaimCategory:
    """Assign a single ClaimCategory to an item using keyword heuristics.

    Checks title, key_finding, and modality tags. Returns the best-matching
    category, defaulting to PATHOPHYSIOLOGY if no clear match is found.
    """
    text = f"{item.title} {item.key_finding}".lower()

    scores: dict[ClaimCategory, float] = {}
    for category, keywords in _CATEGORY_KEYWORDS.items():
        score = sum(1.0 for kw in keywords if kw in text)
        # Boost modality-related categories when item has modality tags
        if item.modalities and category in _MODALITY_BOOST_CATEGORIES:
            score += 0.5
        scores[category] = score

    # Return best match, default to PATHOPHYSIOLOGY
    best = max(scores, key=lambda c: scores[c])
    if scores[best] == 0.0:
        return ClaimCategory.PATHOPHYSIOLOGY

    return best


def _compute_bundle_confidence(items: list[EvidenceItem]) -> ConfidenceLabel:
    """Compute a confidence label for a bundle based on its items.

    Rules:
    - HIGH: has 3+ items and max evidence level >= HIGH
    - MEDIUM: has 2+ items and max evidence level >= MEDIUM
    - LOW: has items but max level <= LOW
    - INSUFFICIENT: single item at VERY_LOW or no items
    """
    if not items:
        return ConfidenceLabel.INSUFFICIENT

    max_weight = max(_LEVEL_WEIGHT.get(i.evidence_level, 0) for i in items)
    count = len(items)

    # Check for contradictions requiring review
    supports = sum(1 for i in items if i.relation == EvidenceRelation.SUPPORTS)
    contradicts = sum(1 for i in items if i.relation == EvidenceRelation.CONTRADICTS)
    if contradicts > 0 and supports > 0 and contradicts >= supports:
        return ConfidenceLabel.REVIEW_REQUIRED

    if count >= 3 and max_weight >= _LEVEL_WEIGHT[EvidenceLevel.HIGH]:
        return ConfidenceLabel.HIGH
    if count >= 2 and max_weight >= _LEVEL_WEIGHT[EvidenceLevel.MEDIUM]:
        return ConfidenceLabel.MEDIUM
    if count >= 1 and max_weight >= _LEVEL_WEIGHT[EvidenceLevel.LOW]:
        return ConfidenceLabel.LOW

    return ConfidenceLabel.INSUFFICIENT
