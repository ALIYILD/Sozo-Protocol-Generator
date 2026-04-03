"""Personalization confidence scoring for Sozo Protocol Generator.

Computes a composite confidence score for personalized protocol recommendations.
This score tells the clinician how much to trust the system's recommendation
and what level of review is appropriate.

Score Components:
  1. Evidence strength (40%) -- quality of literature supporting the recommendation
  2. Data completeness (30%) -- fraction of relevant patient data available
  3. Phenotype match quality (30%) -- how well patient profile matches phenotype criteria

Confidence Bands:
  >=0.7  High     -> Standard clinician review
  0.4-0.7 Moderate -> Enhanced review, clinician should verify key parameters
  <0.4  Low      -> Specialist review recommended, consider manual protocol design

Integration Points:
  - Evidence strength feeds from :mod:`sozo_generator.evidence.confidence` and
    :mod:`sozo_generator.evidence.evidence_scorer` (article-level and query-level scores).
  - Data completeness reflects what patient information the intake pipeline collected.
  - Phenotype match uses the phenotype classification output from the condition engine.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ConfidenceBand(str, Enum):
    """Confidence band that determines the recommended review pathway.

    Values
    ------
    HIGH
        Composite score >= 0.7.  Standard clinician review is sufficient.
    MODERATE
        Composite score in [0.4, 0.7).  Enhanced review recommended --
        clinician should manually verify key protocol parameters.
    LOW
        Composite score in (0, 0.4).  Specialist review recommended;
        consider manual protocol design instead of automated output.
    INSUFFICIENT
        Composite score is effectively zero -- not enough information
        to produce a personalized recommendation.
    """

    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INSUFFICIENT = "insufficient"


# ---------------------------------------------------------------------------
# Input data-classes
# ---------------------------------------------------------------------------

@dataclass
class EvidenceStrengthInput:
    """Input for evidence strength scoring.

    Attributes
    ----------
    overall_evidence_level : str
        Highest evidence level available for this recommendation.
        One of ``"highest"``, ``"high"``, ``"medium"``, ``"low"``,
        ``"very_low"``, ``"missing"``.  Maps to
        :class:`sozo_generator.core.enums.EvidenceLevel` values.
    num_supporting_articles : int
        Total number of articles supporting the recommendation.
    num_rcts : int
        Number of randomised controlled trials in the supporting corpus.
    num_meta_analyses : int
        Number of meta-analyses / systematic reviews.
    has_clinical_guideline : bool
        Whether a clinical practice guideline covers this recommendation.
    contradicting_evidence_count : int
        Number of articles that contradict the recommendation.
    evidence_recency_years : float
        Age (in years) of the newest key article.  A value of ``1.5``
        means the most recent article was published 1.5 years ago.
    """

    overall_evidence_level: str
    num_supporting_articles: int
    num_rcts: int
    num_meta_analyses: int
    has_clinical_guideline: bool
    contradicting_evidence_count: int
    evidence_recency_years: float


@dataclass
class DataCompletenessInput:
    """Input for data completeness scoring.

    Each boolean flag indicates whether the corresponding data domain
    was collected during the patient intake pipeline.

    Attributes
    ----------
    has_demographics : bool
        Age, sex, handedness, etc.
    has_symptom_scores : bool
        At least one validated symptom scale score is available.
    num_symptom_scales : int
        Number of distinct validated scales administered (e.g. PHQ-9,
        GAD-7, PCL-5).
    has_treatment_history : bool
        Prior neuromodulation or pharmacotherapy treatment history.
    has_medications : bool
        Current medication list.
    has_eeg : bool
        Resting-state EEG / QEEG recording available.
    has_brain_map : bool
        Full brain-map (V3 feature) available.
    has_prior_response : bool
        Documented response to a prior neuromodulation protocol.
    total_assessments : int
        Total number of assessment instruments administered.
    """

    has_demographics: bool
    has_symptom_scores: bool
    num_symptom_scales: int
    has_treatment_history: bool
    has_medications: bool
    has_eeg: bool
    has_brain_map: bool
    has_prior_response: bool
    total_assessments: int


@dataclass
class PhenotypeMatchInput:
    """Input for phenotype match quality scoring.

    Attributes
    ----------
    condition_slug : str
        Condition slug (e.g. ``"mdd"``, ``"gad"``, ``"ptsd"``).
    matched_phenotype : str | None
        Phenotype slug if the classification engine matched one, else
        ``None``.
    symptom_overlap_ratio : float
        Fraction (0--1) of expected phenotype symptoms that the patient
        actually exhibits.
    network_concordance : float
        Agreement (0--1) between the patient's EEG-derived network
        profile and the expected network dysfunction for the matched
        phenotype.
    treatment_history_consistent : bool
        Whether prior treatment responses are consistent with what is
        expected for the matched phenotype.
    """

    condition_slug: str
    matched_phenotype: Optional[str]
    symptom_overlap_ratio: float
    network_concordance: float
    treatment_history_consistent: bool


# ---------------------------------------------------------------------------
# Output data-class
# ---------------------------------------------------------------------------

@dataclass
class ConfidenceBreakdown:
    """Detailed breakdown of confidence score components.

    Attributes
    ----------
    evidence_strength : float
        Evidence strength sub-score (0--1).
    evidence_strength_details : dict
        Itemised breakdown of evidence scoring decisions.
    data_completeness : float
        Data completeness sub-score (0--1).
    data_completeness_details : dict
        Itemised breakdown of completeness scoring decisions.
    phenotype_match : float
        Phenotype match quality sub-score (0--1).
    phenotype_match_details : dict
        Itemised breakdown of phenotype scoring decisions.
    composite_score : float
        Weighted average of the three sub-scores (0--1).
    band : ConfidenceBand
        Classified confidence band.
    review_recommendation : str
        Human-readable review recommendation for clinicians.
    explanation : str
        Multi-sentence explanation suitable for clinical reporting.
    missing_data_impact : list[str]
        Actionable suggestions describing what additional data would
        improve the confidence score, with estimated impact.
    """

    evidence_strength: float
    evidence_strength_details: dict
    data_completeness: float
    data_completeness_details: dict
    phenotype_match: float
    phenotype_match_details: dict
    composite_score: float
    band: ConfidenceBand
    review_recommendation: str
    explanation: str
    missing_data_impact: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class ConfidenceScorer:
    """Compute confidence scores for personalized protocol recommendations.

    The scorer combines three orthogonal dimensions into a single composite
    confidence value:

    * **Evidence strength** (weight 0.40) -- derived from the quality and
      quantity of literature supporting the recommendation.
    * **Data completeness** (weight 0.30) -- fraction of clinically relevant
      patient data that was collected during intake.
    * **Phenotype match quality** (weight 0.30) -- how closely the patient's
      profile matches the phenotype criteria used for protocol selection.

    Usage::

        scorer = ConfidenceScorer()
        breakdown = scorer.score(evidence_input, data_input, phenotype_input)
        print(breakdown.band, breakdown.composite_score)

    The weights can be overridden at construction time for research or
    sensitivity analysis.
    """

    # Component weights (must sum to 1.0)
    W_EVIDENCE: float = 0.40
    W_DATA: float = 0.30
    W_PHENOTYPE: float = 0.30

    # Mapping from evidence level string to base score (0-1).
    # Aligned with :class:`sozo_generator.core.enums.EvidenceLevel` values.
    EVIDENCE_LEVEL_SCORES: dict[str, float] = {
        "highest": 1.0,
        "high": 0.85,
        "medium": 0.65,
        "low": 0.40,
        "very_low": 0.20,
        "missing": 0.0,
    }

    def __init__(
        self,
        *,
        w_evidence: float | None = None,
        w_data: float | None = None,
        w_phenotype: float | None = None,
    ) -> None:
        """Initialise the scorer, optionally overriding default weights.

        Parameters
        ----------
        w_evidence : float, optional
            Weight for evidence strength component.
        w_data : float, optional
            Weight for data completeness component.
        w_phenotype : float, optional
            Weight for phenotype match component.

        Raises
        ------
        ValueError
            If custom weights are provided but do not sum to 1.0 (within
            a tolerance of 0.001).
        """
        if w_evidence is not None:
            self.W_EVIDENCE = w_evidence
        if w_data is not None:
            self.W_DATA = w_data
        if w_phenotype is not None:
            self.W_PHENOTYPE = w_phenotype

        total = self.W_EVIDENCE + self.W_DATA + self.W_PHENOTYPE
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"Component weights must sum to 1.0, got {total:.4f} "
                f"(evidence={self.W_EVIDENCE}, data={self.W_DATA}, "
                f"phenotype={self.W_PHENOTYPE})"
            )

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def score(
        self,
        evidence: EvidenceStrengthInput,
        data: DataCompletenessInput,
        phenotype: PhenotypeMatchInput,
    ) -> ConfidenceBreakdown:
        """Compute the full confidence breakdown.

        Parameters
        ----------
        evidence : EvidenceStrengthInput
            Evidence strength inputs.
        data : DataCompletenessInput
            Patient data completeness inputs.
        phenotype : PhenotypeMatchInput
            Phenotype match quality inputs.

        Returns
        -------
        ConfidenceBreakdown
            Complete breakdown including composite score, confidence band,
            review recommendation, explanation, and improvement suggestions.
        """
        ev_score, ev_details = self._score_evidence(evidence)
        data_score, data_details = self._score_completeness(data)
        pheno_score, pheno_details = self._score_phenotype(phenotype)

        composite = (
            self.W_EVIDENCE * ev_score
            + self.W_DATA * data_score
            + self.W_PHENOTYPE * pheno_score
        )
        composite = round(composite, 3)

        band = self._classify_band(composite)
        review_rec = self._review_recommendation(band)
        explanation = self._generate_explanation(ev_score, data_score, pheno_score, band)
        missing_impact = self._identify_missing_data_impact(data, phenotype)

        logger.info(
            "Confidence scored: composite=%.3f band=%s (ev=%.3f data=%.3f pheno=%.3f)",
            composite, band.value, ev_score, data_score, pheno_score,
        )

        return ConfidenceBreakdown(
            evidence_strength=ev_score,
            evidence_strength_details=ev_details,
            data_completeness=data_score,
            data_completeness_details=data_details,
            phenotype_match=pheno_score,
            phenotype_match_details=pheno_details,
            composite_score=composite,
            band=band,
            review_recommendation=review_rec,
            explanation=explanation,
            missing_data_impact=missing_impact,
        )

    # ------------------------------------------------------------------ #
    # Evidence strength                                                   #
    # ------------------------------------------------------------------ #

    def _score_evidence(self, ev: EvidenceStrengthInput) -> tuple[float, dict]:
        """Score evidence strength on a 0--1 scale.

        Scoring logic:
        1. Start with a base score mapped from ``overall_evidence_level``.
        2. Apply additive bonuses (capped at 1.0):
           - +0.10 if a clinical guideline covers this recommendation.
           - +0.05 if >= 2 meta-analyses are available.
           - +0.05 if >= 3 RCTs are available.
        3. Apply multiplicative penalties:
           - For each contradicting article, reduce by 10% (floor at 50%
             of the post-bonus score).
           - If the newest key article is > 5 years old, apply a 10% penalty.

        Parameters
        ----------
        ev : EvidenceStrengthInput
            Raw evidence inputs.

        Returns
        -------
        tuple[float, dict]
            Rounded score and details dictionary.
        """
        base = self.EVIDENCE_LEVEL_SCORES.get(ev.overall_evidence_level, 0.0)

        # Additive bonuses (capped at 1.0)
        if ev.has_clinical_guideline:
            base = min(1.0, base + 0.10)
        if ev.num_meta_analyses >= 2:
            base = min(1.0, base + 0.05)
        if ev.num_rcts >= 3:
            base = min(1.0, base + 0.05)

        # Multiplicative penalties
        if ev.contradicting_evidence_count > 0:
            penalty_factor = max(0.5, 1.0 - 0.1 * ev.contradicting_evidence_count)
            base *= penalty_factor
        if ev.evidence_recency_years > 5:
            base *= 0.9  # slight staleness penalty

        details = {
            "base_level_score": self.EVIDENCE_LEVEL_SCORES.get(
                ev.overall_evidence_level, 0.0
            ),
            "guideline_bonus": ev.has_clinical_guideline,
            "rct_count": ev.num_rcts,
            "meta_analysis_count": ev.num_meta_analyses,
            "supporting_article_count": ev.num_supporting_articles,
            "contradictions": ev.contradicting_evidence_count,
            "recency_years": ev.evidence_recency_years,
            "final_score": round(base, 3),
        }
        return round(base, 3), details

    # ------------------------------------------------------------------ #
    # Data completeness                                                   #
    # ------------------------------------------------------------------ #

    def _score_completeness(self, data: DataCompletenessInput) -> tuple[float, dict]:
        """Score data completeness on a 0--1 scale.

        Each data domain carries a fixed weight reflecting its importance
        to personalization accuracy:

        ============== ======  ==============================
        Domain         Weight  Rationale
        ============== ======  ==============================
        symptom_scores  0.25   Primary driver of phenotyping
        treatment_hist  0.20   Exclusion of failed approaches
        demographics    0.15   Dosing/safety adjustments
        medications     0.15   Interaction checking
        eeg             0.15   Network-based targeting
        prior_response  0.10   Responder prediction
        ============== ======  ==============================

        A small bonus (+0.05, capped at 1.0) is applied when >= 3 distinct
        symptom scales are administered, reflecting richer phenotyping data.

        Parameters
        ----------
        data : DataCompletenessInput
            Patient data availability flags.

        Returns
        -------
        tuple[float, dict]
            Rounded score and details dictionary.
        """
        fields: dict[str, tuple[bool, float]] = {
            "demographics": (data.has_demographics, 0.15),
            "symptom_scores": (data.has_symptom_scores, 0.25),
            "treatment_history": (data.has_treatment_history, 0.20),
            "medications": (data.has_medications, 0.15),
            "eeg": (data.has_eeg, 0.15),
            "prior_response": (data.has_prior_response, 0.10),
        }

        score = sum(weight for present, weight in fields.values() if present)

        # Bonus for multiple symptom scales (richer phenotyping data)
        if data.num_symptom_scales >= 3:
            score = min(1.0, score + 0.05)

        details: dict = {
            field_name: {"present": present, "weight": weight}
            for field_name, (present, weight) in fields.items()
        }
        details["num_symptom_scales"] = data.num_symptom_scales
        details["has_brain_map"] = data.has_brain_map
        details["total_assessments"] = data.total_assessments
        details["final_score"] = round(score, 3)

        return round(score, 3), details

    # ------------------------------------------------------------------ #
    # Phenotype match quality                                             #
    # ------------------------------------------------------------------ #

    def _score_phenotype(self, pheno: PhenotypeMatchInput) -> tuple[float, dict]:
        """Score phenotype match quality on a 0--1 scale.

        When no phenotype is matched, a baseline score of 0.3 is returned
        (reflecting condition-level guidance only).  When a phenotype *is*
        matched, the score is composed of:

        * 0.30 base (phenotype identified)
        * up to 0.30 from symptom overlap ratio
        * up to 0.20 from EEG network concordance
        * 0.20 if treatment history is consistent

        Parameters
        ----------
        pheno : PhenotypeMatchInput
            Phenotype match inputs.

        Returns
        -------
        tuple[float, dict]
            Rounded score (capped at 1.0) and details dictionary.
        """
        if pheno.matched_phenotype is None:
            return 0.3, {
                "matched": False,
                "condition": pheno.condition_slug,
                "reason": "No phenotype matched -- using condition-level defaults.",
            }

        score = 0.3  # base for having a phenotype match
        score += 0.3 * pheno.symptom_overlap_ratio
        score += 0.2 * pheno.network_concordance
        if pheno.treatment_history_consistent:
            score += 0.2

        details = {
            "matched": True,
            "condition": pheno.condition_slug,
            "phenotype": pheno.matched_phenotype,
            "symptom_overlap": pheno.symptom_overlap_ratio,
            "network_concordance": pheno.network_concordance,
            "history_consistent": pheno.treatment_history_consistent,
            "final_score": round(min(1.0, score), 3),
        }
        return round(min(1.0, score), 3), details

    # ------------------------------------------------------------------ #
    # Band classification & recommendations                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _classify_band(score: float) -> ConfidenceBand:
        """Classify a composite score into a confidence band.

        Parameters
        ----------
        score : float
            Composite confidence score (0--1).

        Returns
        -------
        ConfidenceBand
        """
        if score >= 0.7:
            return ConfidenceBand.HIGH
        if score >= 0.4:
            return ConfidenceBand.MODERATE
        if score > 0:
            return ConfidenceBand.LOW
        return ConfidenceBand.INSUFFICIENT

    @staticmethod
    def _review_recommendation(band: ConfidenceBand) -> str:
        """Return a clinician-facing review recommendation for the band.

        Parameters
        ----------
        band : ConfidenceBand

        Returns
        -------
        str
            Plain-language recommendation.
        """
        recommendations = {
            ConfidenceBand.HIGH: (
                "Standard clinician review -- recommendation well-supported."
            ),
            ConfidenceBand.MODERATE: (
                "Enhanced review recommended -- verify key parameters manually."
            ),
            ConfidenceBand.LOW: (
                "Specialist review recommended -- consider manual protocol design."
            ),
            ConfidenceBand.INSUFFICIENT: (
                "Insufficient data for personalization -- use condition-based "
                "protocol."
            ),
        }
        return recommendations[band]

    # ------------------------------------------------------------------ #
    # Explanation generation                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _generate_explanation(
        ev: float,
        data: float,
        pheno: float,
        band: ConfidenceBand,
    ) -> str:
        """Generate a multi-sentence human-readable explanation.

        The explanation covers each sub-score dimension in plain clinical
        language, suitable for inclusion in a protocol cover sheet.

        Parameters
        ----------
        ev : float
            Evidence strength sub-score (0--1).
        data : float
            Data completeness sub-score (0--1).
        pheno : float
            Phenotype match sub-score (0--1).
        band : ConfidenceBand
            Overall confidence band.

        Returns
        -------
        str
            Multi-sentence explanation.
        """
        parts: list[str] = []

        # Evidence dimension
        if ev >= 0.7:
            parts.append("Strong evidence base supports this recommendation.")
        elif ev >= 0.4:
            parts.append("Moderate evidence base; some parameters extrapolated.")
        else:
            parts.append("Limited evidence for this specific configuration.")

        # Data dimension
        if data >= 0.7:
            parts.append("Patient data is comprehensive.")
        elif data >= 0.4:
            parts.append(
                "Some patient data is missing (see recommendations below)."
            )
        else:
            parts.append(
                "Significant patient data gaps limit personalization accuracy."
            )

        # Phenotype dimension
        if pheno >= 0.7:
            parts.append("Strong phenotype match detected.")
        elif pheno >= 0.4:
            parts.append("Partial phenotype match; review subtype classification.")
        else:
            parts.append("Phenotype match is uncertain.")

        return " ".join(parts)

    # ------------------------------------------------------------------ #
    # Missing data impact analysis                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _identify_missing_data_impact(
        data: DataCompletenessInput,
        pheno: PhenotypeMatchInput,
    ) -> list[str]:
        """Identify what additional data would most improve the score.

        Each suggestion includes the approximate completeness weight gain
        so clinicians can prioritise data collection.

        Parameters
        ----------
        data : DataCompletenessInput
            Current data availability.
        pheno : PhenotypeMatchInput
            Current phenotype match state.

        Returns
        -------
        list[str]
            Ordered list of actionable improvement suggestions.
        """
        impacts: list[str] = []

        if not data.has_symptom_scores:
            impacts.append(
                "Adding symptom scale scores would significantly improve "
                "personalization (+0.25 data completeness)."
            )
        if not data.has_treatment_history:
            impacts.append(
                "Treatment history would help exclude failed approaches "
                "(+0.20 data completeness)."
            )
        if not data.has_eeg:
            impacts.append(
                "EEG/QEEG data would enable target refinement and "
                "network-based personalization (+0.15 data completeness)."
            )
        if not data.has_medications:
            impacts.append(
                "Medication list needed for interaction safety checking "
                "(+0.15 data completeness)."
            )
        if not data.has_demographics:
            impacts.append(
                "Demographic data would improve dosing and safety "
                "adjustments (+0.15 data completeness)."
            )
        if not data.has_prior_response:
            impacts.append(
                "Prior neuromodulation response data would improve "
                "responder prediction (+0.10 data completeness)."
            )
        if pheno.matched_phenotype is None:
            impacts.append(
                "Phenotype classification would enable modality-specific "
                "optimization."
            )

        return impacts
