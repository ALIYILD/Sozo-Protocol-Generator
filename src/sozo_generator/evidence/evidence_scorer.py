"""
Multi-dimensional evidence scorer — replaces simple level-based scoring
with a composite model considering study design, sample size, bias risk,
reporting completeness, and replication.

Produces both study-level quality scores and query-level relevance scores.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..core.enums import EvidenceLevel, EvidenceType
from ..schemas.evidence import ArticleMetadata
from .parameter_extractor import StimulationParameters

logger = logging.getLogger(__name__)


# ── Score constants ────────────────────────────────────────────────────

# Study design scores (0-100)
DESIGN_SCORES: dict[EvidenceType, int] = {
    EvidenceType.META_ANALYSIS: 95,
    EvidenceType.SYSTEMATIC_REVIEW: 90,
    EvidenceType.CLINICAL_PRACTICE_GUIDELINE: 90,
    EvidenceType.LARGE_RCT: 88,
    EvidenceType.RCT: 85,
    EvidenceType.CONTROLLED_TRIAL: 70,
    EvidenceType.COHORT_STUDY: 55,
    EvidenceType.PILOT_STUDY: 40,
    EvidenceType.FEASIBILITY_STUDY: 35,
    EvidenceType.CASE_SERIES: 30,
    EvidenceType.NARRATIVE_REVIEW: 50,
    EvidenceType.CONSENSUS_STATEMENT: 45,
    EvidenceType.CASE_REPORT: 20,
    EvidenceType.EXPERT_OPINION: 15,
    EvidenceType.INDIRECT_EVIDENCE: 25,
    EvidenceType.MANUAL_ENTRY: 10,
}

# Sample size thresholds by modality family
SAMPLE_SIZE_NORMS: dict[str, dict[str, int]] = {
    "tDCS": {"large": 100, "medium": 40, "small": 15},
    "rTMS": {"large": 100, "medium": 50, "small": 20},
    "TMS": {"large": 100, "medium": 50, "small": 20},
    "default": {"large": 80, "medium": 30, "small": 10},
}

# Weights for composite quality score
QUALITY_WEIGHTS = {
    "design": 0.30,
    "sample": 0.20,
    "bias_risk": 0.20,
    "reporting": 0.10,
    "replication": 0.20,
}

# Weights for composite relevance score
RELEVANCE_WEIGHTS = {
    "parameter_match": 0.40,
    "population_match": 0.25,
    "recency": 0.15,
    "parameter_completeness": 0.20,
}


@dataclass
class QualityScore:
    """Multi-dimensional quality score for a single study."""

    design_score: int = 0
    sample_score: int = 0
    bias_risk_score: int = 0
    reporting_score: int = 0
    replication_score: int = 0
    composite_score: int = 0
    evidence_grade: str = "D"  # A, B, C, D
    scoring_notes: list[str] = field(default_factory=list)


@dataclass
class RelevanceScore:
    """Query-specific relevance score for a study."""

    parameter_match: float = 0.0  # 0-1
    population_match: float = 0.0  # 0-1
    recency_score: float = 0.0  # 0-1
    parameter_completeness: float = 0.0  # 0-1
    composite_score: int = 0
    scoring_notes: list[str] = field(default_factory=list)


@dataclass
class EvidenceScore:
    """Combined quality + relevance score for a study."""

    study_identifier: str = ""
    quality: Optional[QualityScore] = None
    relevance: Optional[RelevanceScore] = None
    final_grade: str = "D"
    final_score: int = 0


class EvidenceScorer:
    """Scores evidence quality and relevance for protocol grounding."""

    def __init__(
        self,
        replication_index: Optional[dict[str, int]] = None,
    ):
        """
        Args:
            replication_index: Map of modality+target+condition → replication count.
                               Built from the study corpus. None uses defaults.
        """
        self._replication_index = replication_index or {}

    def score_quality(
        self,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters] = None,
    ) -> QualityScore:
        """Compute multi-dimensional quality score for a single study."""
        q = QualityScore()

        # 1. Study design
        q.design_score = DESIGN_SCORES.get(article.evidence_type, 30)
        q.scoring_notes.append(
            f"Design: {article.evidence_type.value} → {q.design_score}"
        )

        # 2. Sample size
        q.sample_score = self._score_sample_size(article, extraction)

        # 3. Bias risk (heuristic from abstract text)
        q.bias_risk_score = self._score_bias_risk(article)

        # 4. Reporting completeness (how many protocol params are stated)
        q.reporting_score = self._score_reporting(extraction)

        # 5. Replication (how many independent studies report similar findings)
        q.replication_score = self._score_replication(article, extraction)

        # Composite
        q.composite_score = round(
            q.design_score * QUALITY_WEIGHTS["design"]
            + q.sample_score * QUALITY_WEIGHTS["sample"]
            + q.bias_risk_score * QUALITY_WEIGHTS["bias_risk"]
            + q.reporting_score * QUALITY_WEIGHTS["reporting"]
            + q.replication_score * QUALITY_WEIGHTS["replication"]
        )

        # Grade
        q.evidence_grade = self._score_to_grade(q.composite_score)

        return q

    def score_relevance(
        self,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters] = None,
        target_modality: Optional[str] = None,
        target_condition: Optional[str] = None,
        target_brain_region: Optional[str] = None,
        target_params: Optional[dict] = None,
    ) -> RelevanceScore:
        """Compute query-specific relevance score."""
        r = RelevanceScore()

        # 1. Parameter match (modality + brain target + condition)
        r.parameter_match = self._score_parameter_match(
            article, extraction, target_modality, target_condition, target_brain_region,
        )

        # 2. Population match (condition slug match)
        r.population_match = 1.0 if (
            target_condition
            and article.condition_slug
            and article.condition_slug.lower() == target_condition.lower()
        ) else 0.5  # partial credit if no condition tagged

        # 3. Recency
        r.recency_score = self._score_recency(article)

        # 4. Parameter completeness (does this study provide the params we need?)
        r.parameter_completeness = self._score_param_completeness(
            extraction, target_params,
        )

        # Composite
        r.composite_score = round(
            r.parameter_match * RELEVANCE_WEIGHTS["parameter_match"] * 100
            + r.population_match * RELEVANCE_WEIGHTS["population_match"] * 100
            + r.recency_score * RELEVANCE_WEIGHTS["recency"] * 100
            + r.parameter_completeness * RELEVANCE_WEIGHTS["parameter_completeness"] * 100
        )

        return r

    def score_full(
        self,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters] = None,
        target_modality: Optional[str] = None,
        target_condition: Optional[str] = None,
        target_brain_region: Optional[str] = None,
        target_params: Optional[dict] = None,
    ) -> EvidenceScore:
        """Compute full quality + relevance score."""
        quality = self.score_quality(article, extraction)
        relevance = self.score_relevance(
            article, extraction,
            target_modality, target_condition, target_brain_region, target_params,
        )

        final_score = round((quality.composite_score + relevance.composite_score) / 2)

        return EvidenceScore(
            study_identifier=article.pmid or article.doi or article.title[:40],
            quality=quality,
            relevance=relevance,
            final_grade=self._combined_grade(quality.composite_score, relevance.composite_score),
            final_score=final_score,
        )

    # ── Private scoring helpers ────────────────────────────────────────

    def _score_sample_size(
        self,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters],
    ) -> int:
        """Score sample size relative to modality norms."""
        n = extraction.sample_size if extraction and extraction.sample_size else None

        if n is None:
            return 40  # unknown → neutral

        modality = extraction.modality if extraction else None
        norms = SAMPLE_SIZE_NORMS.get(modality or "", SAMPLE_SIZE_NORMS["default"])

        if n >= norms["large"]:
            return 90
        if n >= norms["medium"]:
            return 70
        if n >= norms["small"]:
            return 50
        return 30

    def _score_bias_risk(self, article: ArticleMetadata) -> int:
        """Heuristic bias risk score from abstract text."""
        text = f"{article.title} {article.abstract or ''}".lower()
        score = 70  # default moderate risk

        # Positive indicators
        if "double-blind" in text or "double blind" in text:
            score += 10
        if "randomized" in text or "randomised" in text:
            score += 10
        if "placebo" in text or "sham" in text:
            score += 5
        if "intention-to-treat" in text or "intent-to-treat" in text:
            score += 5

        # Negative indicators
        if "open-label" in text or "open label" in text:
            score -= 15
        if "retrospective" in text:
            score -= 10
        if "pilot" in text and "study" in text:
            score -= 5
        if "small sample" in text or "limited sample" in text:
            score -= 10

        return max(10, min(100, score))

    def _score_reporting(
        self, extraction: Optional[StimulationParameters],
    ) -> int:
        """Score reporting completeness based on extracted parameters."""
        if not extraction:
            return 20

        # Count explicitly reported protocol parameters
        key_fields = [
            extraction.modality,
            extraction.brain_target,
            extraction.intensity_ma or extraction.intensity_v_per_m,
            extraction.frequency_hz,
            extraction.duration_minutes,
            extraction.sessions_total,
            extraction.sessions_per_week,
            extraction.primary_outcome_measure,
        ]
        reported = sum(1 for f in key_fields if f is not None)
        total = len(key_fields)

        return round((reported / total) * 100)

    def _score_replication(
        self,
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters],
    ) -> int:
        """Score based on how many independent replications exist."""
        if not extraction or not extraction.modality:
            return 40  # unknown

        key = f"{extraction.modality}_{extraction.brain_target}_{article.condition_slug}"
        rep_count = self._replication_index.get(key, 0)

        if rep_count >= 3:
            return 90
        if rep_count >= 1:
            return 60
        return 30

    @staticmethod
    def _score_recency(article: ArticleMetadata) -> float:
        """Exponential decay: score = exp(-0.05 * years_since_publication)."""
        if not article.year:
            return 0.5  # unknown age → neutral

        current_year = datetime.now().year
        age = max(0, current_year - article.year)
        return math.exp(-0.05 * age)

    @staticmethod
    def _score_parameter_match(
        article: ArticleMetadata,
        extraction: Optional[StimulationParameters],
        target_modality: Optional[str],
        target_condition: Optional[str],
        target_brain_region: Optional[str],
    ) -> float:
        """Jaccard-style match of modality + brain_target + condition."""
        target_set: set[str] = set()
        article_set: set[str] = set()

        if target_modality:
            target_set.add(f"mod:{target_modality.lower()}")
        if target_condition:
            target_set.add(f"cond:{target_condition.lower()}")
        if target_brain_region:
            target_set.add(f"target:{target_brain_region.lower()}")

        if extraction and extraction.modality:
            article_set.add(f"mod:{extraction.modality.lower()}")
        elif article.modalities:
            for m in article.modalities:
                article_set.add(f"mod:{m.lower()}")

        if extraction and extraction.brain_target:
            article_set.add(f"target:{extraction.brain_target.lower()}")

        if article.condition_slug:
            article_set.add(f"cond:{article.condition_slug.lower()}")

        if not target_set:
            return 0.5  # no target specified
        if not article_set:
            return 0.3  # no article metadata

        intersection = len(target_set & article_set)
        union = len(target_set | article_set)
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _score_param_completeness(
        extraction: Optional[StimulationParameters],
        target_params: Optional[dict],
    ) -> float:
        """Does this study provide the specific parameters the protocol needs?"""
        if not target_params or not extraction:
            return 0.5  # no target defined

        matched = 0
        total = len(target_params)

        param_map = {
            "intensity": extraction.intensity_ma,
            "frequency": extraction.frequency_hz,
            "duration": extraction.duration_minutes,
            "sessions": extraction.sessions_total,
            "montage": extraction.electrode_montage,
            "brain_target": extraction.brain_target,
            "modality": extraction.modality,
        }

        for param_name in target_params:
            if param_name in param_map and param_map[param_name] is not None:
                matched += 1

        return matched / total if total > 0 else 0.5

    @staticmethod
    def _score_to_grade(score: int) -> str:
        """Convert composite score to letter grade."""
        if score >= 75:
            return "A"
        if score >= 55:
            return "B"
        if score >= 35:
            return "C"
        return "D"

    @staticmethod
    def _combined_grade(quality: int, relevance: int) -> str:
        """Grade based on both quality and relevance meeting thresholds."""
        if quality >= 70 and relevance >= 70:
            return "A"
        if quality >= 50 and relevance >= 50:
            return "B"
        if quality >= 35 and relevance >= 35:
            return "C"
        return "D"
