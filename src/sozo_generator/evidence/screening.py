"""
Evidence screening service — auto-classifies papers as
include/exclude/uncertain for neuromodulation protocol relevance.

Uses keyword heuristics (fast, no API calls) with optional LLM
enhancement when an API key is configured.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from ..schemas.evidence import ArticleMetadata
from .pipeline_tracker import PipelineTracker, PipelineStage, PipelineDecision

logger = logging.getLogger(__name__)


# ── Inclusion/exclusion criteria ───────────────────────────────────────

# Keywords that strongly suggest neuromodulation protocol relevance
_INCLUSION_KEYWORDS = [
    "transcranial direct current stimulation", "tdcs",
    "transcranial magnetic stimulation", "tms", "rtms",
    "theta burst stimulation", "itbs", "ctbs",
    "transcranial alternating current", "tacs",
    "transcranial pulse stimulation", "tps",
    "transcutaneous vagus nerve", "tavns",
    "cranial electrotherapy stimulation", "ces",
    "transcranial focused ultrasound", "tfus",
    "deep brain stimulation", "dbs",
    "transcranial random noise", "trns",
    "neuromodulation protocol",
    "brain stimulation",
    "non-invasive brain stimulation", "nibs",
    "electrode montage", "stimulation parameters",
    "stimulation target",
]

# Keywords suggesting protocol parameters are present
_PROTOCOL_KEYWORDS = [
    "intensity", "ma", "milliamp",
    "duration", "session", "treatment protocol",
    "montage", "electrode placement",
    "motor threshold",
    "sham", "active stimulation",
    "dosage", "pulse",
]

# Keywords that trigger exclusion
_EXCLUSION_KEYWORDS = [
    "animal model", "rat model", "mouse model", "rodent",
    "in vitro", "cell culture",
    "computational model only",
    "spinal cord stimulation",  # different modality family
    "peripheral nerve stimulation",
    "editorial", "erratum", "corrigendum", "retraction",
    "protocol registration",  # just a registration, not results
]

# Condition-irrelevance markers
_CONDITION_EXCLUSION = [
    "veterinary",
    "agricultural",
    "plant electrostimulation",
]


@dataclass
class ScreeningResult:
    """Result of screening a single article."""

    article_identifier: str = ""
    decision: str = ""  # include, exclude, uncertain
    reason: str = ""
    confidence: float = 0.0
    inclusion_signals: list[str] = field(default_factory=list)
    exclusion_signals: list[str] = field(default_factory=list)
    protocol_signals: list[str] = field(default_factory=list)


@dataclass
class BatchScreeningResult:
    """Result of screening a batch of articles."""

    total: int = 0
    included: int = 0
    excluded: int = 0
    uncertain: int = 0
    results: list[ScreeningResult] = field(default_factory=list)


class ScreeningService:
    """Screens articles for neuromodulation protocol relevance.

    Two-pass approach:
    1. Keyword heuristics (fast, deterministic) — default
    2. LLM classification (optional, higher accuracy) — when API key present
    """

    def __init__(
        self,
        min_confidence_for_auto_decision: float = 0.7,
        target_condition: Optional[str] = None,
        target_modality: Optional[str] = None,
    ):
        self.min_confidence = min_confidence_for_auto_decision
        self.target_condition = target_condition
        self.target_modality = target_modality

    def screen(
        self,
        article: ArticleMetadata,
        tracker: Optional[PipelineTracker] = None,
    ) -> ScreeningResult:
        """Screen a single article using keyword heuristics."""
        identifier = article.pmid or article.doi or article.title[:50]
        result = ScreeningResult(article_identifier=identifier)

        text = f"{article.title} {article.abstract or ''}".lower()

        if len(text.strip()) < 20:
            result.decision = "uncertain"
            result.reason = "Insufficient text for screening"
            result.confidence = 0.0
            if tracker:
                tracker.log_screening(
                    identifier,
                    PipelineDecision.UNCERTAIN,
                    result.reason,
                    confidence=0.0,
                    decided_by="system:keyword_screener",
                )
            return result

        # Check exclusion signals first
        for kw in _EXCLUSION_KEYWORDS:
            if kw in text:
                result.exclusion_signals.append(kw)

        for kw in _CONDITION_EXCLUSION:
            if kw in text:
                result.exclusion_signals.append(kw)

        # Check inclusion signals
        for kw in _INCLUSION_KEYWORDS:
            if kw in text:
                result.inclusion_signals.append(kw)

        # Check protocol detail signals
        for kw in _PROTOCOL_KEYWORDS:
            if kw in text:
                result.protocol_signals.append(kw)

        # Check target condition relevance if specified
        condition_match = False
        if self.target_condition:
            condition_lower = self.target_condition.lower().replace("_", " ")
            if condition_lower in text:
                condition_match = True
                result.inclusion_signals.append(f"condition:{self.target_condition}")

        # Check target modality if specified
        if self.target_modality:
            mod_lower = self.target_modality.lower()
            if mod_lower in text:
                result.inclusion_signals.append(f"modality:{self.target_modality}")

        # Decision logic
        n_include = len(result.inclusion_signals)
        n_exclude = len(result.exclusion_signals)
        n_protocol = len(result.protocol_signals)

        if n_exclude > 0 and n_include == 0:
            result.decision = "exclude"
            result.reason = f"Exclusion signals: {', '.join(result.exclusion_signals[:3])}"
            result.confidence = min(0.95, 0.6 + n_exclude * 0.1)

        elif n_include >= 2 and n_protocol >= 1:
            result.decision = "include"
            result.reason = (
                f"Neuromodulation content ({n_include} signals) "
                f"with protocol details ({n_protocol} signals)"
            )
            result.confidence = min(0.95, 0.5 + n_include * 0.1 + n_protocol * 0.05)

        elif n_include >= 1:
            if n_exclude > 0:
                result.decision = "uncertain"
                result.reason = "Mixed signals: both inclusion and exclusion keywords"
                result.confidence = 0.3
            elif n_protocol >= 2:
                result.decision = "include"
                result.reason = f"Neuromodulation reference with protocol detail"
                result.confidence = 0.7
            else:
                result.decision = "uncertain"
                result.reason = "Neuromodulation reference but limited protocol detail"
                result.confidence = 0.4

        else:
            result.decision = "exclude"
            result.reason = "No neuromodulation content detected"
            result.confidence = 0.6

        # Boost confidence if condition matches
        if condition_match and result.decision == "include":
            result.confidence = min(0.95, result.confidence + 0.1)

        # Apply minimum confidence threshold
        if result.decision in ("include", "exclude") and result.confidence < self.min_confidence:
            result.decision = "uncertain"
            result.reason += f" (below confidence threshold {self.min_confidence})"

        # Log to tracker
        if tracker:
            decision_map = {
                "include": PipelineDecision.INCLUDE,
                "exclude": PipelineDecision.EXCLUDE,
                "uncertain": PipelineDecision.UNCERTAIN,
            }
            tracker.log_screening(
                identifier,
                decision_map[result.decision],
                result.reason,
                confidence=result.confidence,
                decided_by="system:keyword_screener",
            )

        return result

    def screen_batch(
        self,
        articles: list[ArticleMetadata],
        tracker: Optional[PipelineTracker] = None,
    ) -> BatchScreeningResult:
        """Screen a batch of articles."""
        batch_result = BatchScreeningResult(total=len(articles))

        for article in articles:
            result = self.screen(article, tracker=tracker)
            batch_result.results.append(result)

            if result.decision == "include":
                batch_result.included += 1
            elif result.decision == "exclude":
                batch_result.excluded += 1
            else:
                batch_result.uncertain += 1

        logger.info(
            "Screening: %d total → %d include, %d exclude, %d uncertain",
            batch_result.total,
            batch_result.included,
            batch_result.excluded,
            batch_result.uncertain,
        )
        return batch_result

    def get_included(
        self,
        articles: list[ArticleMetadata],
        tracker: Optional[PipelineTracker] = None,
    ) -> list[ArticleMetadata]:
        """Screen and return only included articles (include + uncertain)."""
        batch = self.screen_batch(articles, tracker=tracker)
        included_ids = {
            r.article_identifier
            for r in batch.results
            if r.decision in ("include", "uncertain")
        }
        return [
            a for a in articles
            if (a.pmid or a.doi or a.title[:50]) in included_ids
        ]
