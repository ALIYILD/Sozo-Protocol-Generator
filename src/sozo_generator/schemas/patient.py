"""Patient and Assessment Pydantic v2 models for SOZO V2 personalization.

Defines the core data structures for patient profiling, symptom tracking,
treatment history, medication records, and validated assessment scales
used across neuromodulation protocols.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ── Enums ────────────────────────────────────────────────────────────────


class BiologicalSex(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Handedness(str, Enum):
    RIGHT = "right"
    LEFT = "left"
    AMBIDEXTROUS = "ambidextrous"


class TreatmentOutcome(str, Enum):
    RESPONDER = "responder"
    PARTIAL_RESPONDER = "partial_responder"
    NON_RESPONDER = "non_responder"
    NOT_ASSESSED = "not_assessed"


class DrugClass(str, Enum):
    SSRI = "SSRI"
    SNRI = "SNRI"
    TCA = "TCA"
    MAOI = "MAOI"
    BENZODIAZEPINE = "benzodiazepine"
    ANTICONVULSANT = "anticonvulsant"
    ANTIPSYCHOTIC = "antipsychotic"
    STIMULANT = "stimulant"
    OTHER = "other"


class ScoringDirection(str, Enum):
    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class AssessmentTiming(str, Enum):
    PRE = "pre"
    POST = "post"
    EACH_SESSION = "each_session"


# ── Score range helper ───────────────────────────────────────────────────


class ScoreRange(BaseModel):
    """Inclusive min/max range for an assessment scale."""
    min: float = 0
    max: float

    @model_validator(mode="after")
    def _min_le_max(self) -> ScoreRange:
        if self.min > self.max:
            raise ValueError(
                f"Score range min ({self.min}) must be <= max ({self.max})"
            )
        return self


# ── Patient models ───────────────────────────────────────────────────────


class Demographics(BaseModel):
    """Basic patient demographics relevant to neuromodulation protocols."""
    age: int = Field(..., ge=0, le=120, description="Patient age in years")
    sex: BiologicalSex
    handedness: Handedness = Handedness.RIGHT

    @field_validator("age", mode="after")
    @classmethod
    def _age_clinical_range(cls, v: int) -> int:
        if v < 18:
            # Not an error — paediatric patients exist — but flag it
            pass
        return v


class SymptomAssessment(BaseModel):
    """A single scored assessment for a patient at a point in time.

    Captures the total score, optional subscale breakdown, severity band,
    and metadata about when/how the assessment was administered.
    """
    scale_name: str = Field(
        ..., min_length=1, description="Key matching an AssessmentScale abbreviation"
    )
    abbreviation: str = Field(
        ..., min_length=1, description="Short form, e.g. 'PHQ-9'"
    )
    total_score: float = Field(..., description="Overall score on the scale")
    subscale_scores: dict[str, float] = Field(
        default_factory=dict,
        description="Optional subscale name -> score mapping",
    )
    severity_band: str = Field(
        ..., min_length=1,
        description="Severity label, e.g. 'moderate', 'severe'",
    )
    assessed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the assessment",
    )
    session_number: Optional[int] = Field(
        None, ge=0,
        description="Session number at which assessment was taken (0 = baseline)",
    )
    percentile: Optional[float] = Field(
        None, ge=0.0, le=100.0,
        description="Population percentile, if available",
    )
    clinician_interpretation: Optional[str] = Field(
        None,
        description="Free-text clinician note on the result",
    )


class TreatmentRecord(BaseModel):
    """Record of a past or ongoing neuromodulation treatment course."""
    modality: str = Field(
        ..., min_length=1,
        description="Treatment modality, e.g. 'tdcs', 'tps', 'tavns'",
    )
    condition_slug: str = Field(
        ..., min_length=1,
        description="Slug of the target condition, e.g. 'depression'",
    )
    target: str = Field(
        ..., min_length=1,
        description="Stimulation target, e.g. 'L-DLPFC'",
    )
    parameters: dict[str, str | int | float | list] = Field(
        default_factory=dict,
        description="Protocol parameters (current_mA, duration_min, etc.)",
    )
    sessions_completed: int = Field(0, ge=0)
    outcome: TreatmentOutcome = TreatmentOutcome.NOT_ASSESSED
    outcome_measures: dict[str, float] = Field(
        default_factory=dict,
        description="Scale abbreviation -> post-treatment score",
    )
    adverse_events: list[str] = Field(
        default_factory=list,
        description="Documented adverse events, e.g. 'scalp tingling', 'headache'",
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    @model_validator(mode="after")
    def _dates_consistent(self) -> TreatmentRecord:
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot precede start_date")
        return self


class MedicationRecord(BaseModel):
    """Current or past medication record with interaction flags."""
    name: str = Field(..., min_length=1, description="Drug name (generic preferred)")
    drug_class: DrugClass
    dose: str = Field(
        ..., min_length=1,
        description="Dose with units, e.g. '20 mg/day'",
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    interaction_flags: list[str] = Field(
        default_factory=list,
        description=(
            "Clinically relevant interaction flags, e.g. "
            "'lowers_seizure_threshold', 'increases_bleeding_risk'"
        ),
    )

    @model_validator(mode="after")
    def _dates_consistent(self) -> MedicationRecord:
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot precede start_date")
        return self

    @property
    def is_active(self) -> bool:
        """True if the medication has no end_date (still being taken)."""
        return self.end_date is None


class PatientProfile(BaseModel):
    """Complete patient profile for V2 protocol personalization.

    Aggregates demographics, active conditions, symptom assessments,
    treatment history, medications, and patient-specific contraindications.
    """
    patient_id: str = Field(
        ..., min_length=1,
        description="Unique patient identifier",
    )
    demographics: Demographics
    conditions: list[str] = Field(
        default_factory=list,
        description="Active condition slugs, e.g. ['depression', 'chronic_pain']",
    )
    symptoms: list[SymptomAssessment] = Field(
        default_factory=list,
        description="Ordered list of symptom assessments (most recent last)",
    )
    treatment_history: list[TreatmentRecord] = Field(default_factory=list)
    medications: list[MedicationRecord] = Field(default_factory=list)
    contraindications_patient: list[str] = Field(
        default_factory=list,
        description=(
            "Patient-specific contraindications beyond condition defaults, "
            "e.g. 'cochlear implant', 'skull plate right parietal'"
        ),
    )
    notes: Optional[str] = Field(
        None,
        description="Free-text clinical notes",
    )

    @property
    def active_medications(self) -> list[MedicationRecord]:
        """Return medications that have no end_date."""
        return [m for m in self.medications if m.is_active]

    @property
    def all_interaction_flags(self) -> set[str]:
        """Aggregate all interaction flags from active medications."""
        flags: set[str] = set()
        for m in self.active_medications:
            flags.update(m.interaction_flags)
        return flags

    def latest_assessment(self, scale_abbr: str) -> Optional[SymptomAssessment]:
        """Return the most recent assessment for a given scale abbreviation."""
        matches = [s for s in self.symptoms if s.abbreviation == scale_abbr]
        if not matches:
            return None
        return max(matches, key=lambda s: s.assessed_at)

    def has_contraindication(self, term: str) -> bool:
        """Check whether a term appears in patient-level contraindications."""
        term_lower = term.lower()
        return any(term_lower in c.lower() for c in self.contraindications_patient)


# ── Assessment models ────────────────────────────────────────────────────


class SeverityBandRange(BaseModel):
    """Score range for a single severity band."""
    min: float
    max: float

    @model_validator(mode="after")
    def _min_le_max(self) -> SeverityBandRange:
        if self.min > self.max:
            raise ValueError(
                f"Severity band min ({self.min}) must be <= max ({self.max})"
            )
        return self


class AssessmentScale(BaseModel):
    """Definition of a validated clinical assessment scale.

    Used to validate scores, map severity bands, and determine appropriate
    assessment batteries for conditions.
    """
    scale_name: str = Field(..., description="Machine-readable key, e.g. 'phq9'")
    abbreviation: str = Field(..., description="Display abbreviation, e.g. 'PHQ-9'")
    full_name: str = Field(..., description="Full scale name")
    domains: list[str] = Field(
        default_factory=list,
        description="Clinical domains measured, e.g. ['mood', 'sleep', 'appetite']",
    )
    score_range: ScoreRange
    severity_bands: dict[str, SeverityBandRange] = Field(
        default_factory=dict,
        description="Band label -> score range mapping",
    )
    scoring_direction: ScoringDirection = ScoringDirection.LOWER_IS_BETTER
    administration_time_minutes: Optional[int] = Field(
        None, ge=1,
        description="Typical time to administer in minutes",
    )
    validated_for: list[str] = Field(
        default_factory=list,
        description="Condition slugs this scale is validated for",
    )

    def classify_severity(self, score: float) -> Optional[str]:
        """Return the severity band label for a given score, or None."""
        for label, band in self.severity_bands.items():
            if band.min <= score <= band.max:
                return label
        return None

    def is_valid_score(self, score: float) -> bool:
        """Check whether a score falls within the scale's defined range."""
        return self.score_range.min <= score <= self.score_range.max


class AssessmentBattery(BaseModel):
    """A named collection of assessment scales applied at a specific timing.

    Defines which scales to administer together for a given condition
    (e.g., pre-treatment depression battery).
    """
    name: str = Field(..., min_length=1)
    description: str = Field("", description="Purpose of this battery")
    scales: list[str] = Field(
        ..., min_length=1,
        description="List of AssessmentScale abbreviations included in the battery",
    )
    timing: AssessmentTiming
    condition_slug: str = Field(
        ..., min_length=1,
        description="Condition this battery is designed for",
    )


# ── Validated scales registry ────────────────────────────────────────────


def _band(lo: float, hi: float) -> SeverityBandRange:
    """Shorthand constructor for severity band ranges."""
    return SeverityBandRange(min=lo, max=hi)


VALIDATED_SCALES: dict[str, AssessmentScale] = {
    "PHQ-9": AssessmentScale(
        scale_name="phq9",
        abbreviation="PHQ-9",
        full_name="Patient Health Questionnaire-9",
        domains=["mood", "anhedonia", "sleep", "energy", "appetite",
                 "self-esteem", "concentration", "psychomotor", "suicidality"],
        score_range=ScoreRange(min=0, max=27),
        severity_bands={
            "minimal": _band(0, 4),
            "mild": _band(5, 9),
            "moderate": _band(10, 14),
            "moderately_severe": _band(15, 19),
            "severe": _band(20, 27),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=5,
        validated_for=["depression"],
    ),
    "GAD-7": AssessmentScale(
        scale_name="gad7",
        abbreviation="GAD-7",
        full_name="Generalised Anxiety Disorder-7",
        domains=["anxiety", "worry", "restlessness", "irritability"],
        score_range=ScoreRange(min=0, max=21),
        severity_bands={
            "minimal": _band(0, 4),
            "mild": _band(5, 9),
            "moderate": _band(10, 14),
            "severe": _band(15, 21),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=4,
        validated_for=["anxiety", "depression"],
    ),
    "MoCA": AssessmentScale(
        scale_name="moca",
        abbreviation="MoCA",
        full_name="Montreal Cognitive Assessment",
        domains=["visuospatial", "naming", "attention", "language",
                 "abstraction", "delayed_recall", "orientation"],
        score_range=ScoreRange(min=0, max=30),
        severity_bands={
            "normal": _band(26, 30),
            "mild_impairment": _band(18, 25),
            "moderate_impairment": _band(10, 17),
            "severe_impairment": _band(0, 9),
        },
        scoring_direction=ScoringDirection.HIGHER_IS_BETTER,
        administration_time_minutes=10,
        validated_for=["alzheimers", "parkinsons", "mild_cognitive_impairment",
                       "traumatic_brain_injury"],
    ),
    "UPDRS-III": AssessmentScale(
        scale_name="updrs_iii",
        abbreviation="UPDRS-III",
        full_name="Unified Parkinson's Disease Rating Scale — Part III (Motor Examination)",
        domains=["speech", "facial_expression", "rigidity", "finger_tapping",
                 "hand_movements", "pronation_supination", "leg_agility",
                 "arising_from_chair", "posture", "gait", "postural_stability",
                 "body_bradykinesia"],
        score_range=ScoreRange(min=0, max=132),
        severity_bands={
            "minimal": _band(0, 10),
            "mild": _band(11, 26),
            "moderate": _band(27, 45),
            "severe": _band(46, 132),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=20,
        validated_for=["parkinsons"],
    ),
    "BDI-II": AssessmentScale(
        scale_name="bdi_ii",
        abbreviation="BDI-II",
        full_name="Beck Depression Inventory-II",
        domains=["sadness", "pessimism", "past_failure", "loss_of_pleasure",
                 "guilty_feelings", "punishment_feelings", "self-dislike",
                 "self-criticalness", "suicidal_thoughts", "crying",
                 "agitation", "loss_of_interest", "indecisiveness",
                 "worthlessness", "loss_of_energy", "sleep_changes",
                 "irritability", "appetite_changes", "concentration",
                 "fatigue", "loss_of_libido"],
        score_range=ScoreRange(min=0, max=63),
        severity_bands={
            "minimal": _band(0, 13),
            "mild": _band(14, 19),
            "moderate": _band(20, 28),
            "severe": _band(29, 63),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=10,
        validated_for=["depression"],
    ),
    "MADRS": AssessmentScale(
        scale_name="madrs",
        abbreviation="MADRS",
        full_name="Montgomery-Asberg Depression Rating Scale",
        domains=["apparent_sadness", "reported_sadness", "inner_tension",
                 "reduced_sleep", "reduced_appetite", "concentration",
                 "lassitude", "inability_to_feel", "pessimistic_thoughts",
                 "suicidal_thoughts"],
        score_range=ScoreRange(min=0, max=60),
        severity_bands={
            "normal": _band(0, 6),
            "mild": _band(7, 19),
            "moderate": _band(20, 34),
            "severe": _band(35, 60),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=15,
        validated_for=["depression"],
    ),
    "Y-BOCS": AssessmentScale(
        scale_name="ybocs",
        abbreviation="Y-BOCS",
        full_name="Yale-Brown Obsessive Compulsive Scale",
        domains=["obsessions_time", "obsessions_interference",
                 "obsessions_distress", "obsessions_resistance",
                 "obsessions_control", "compulsions_time",
                 "compulsions_interference", "compulsions_distress",
                 "compulsions_resistance", "compulsions_control"],
        score_range=ScoreRange(min=0, max=40),
        severity_bands={
            "subclinical": _band(0, 7),
            "mild": _band(8, 15),
            "moderate": _band(16, 23),
            "severe": _band(24, 31),
            "extreme": _band(32, 40),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=15,
        validated_for=["ocd"],
    ),
    "PCL-5": AssessmentScale(
        scale_name="pcl5",
        abbreviation="PCL-5",
        full_name="PTSD Checklist for DSM-5",
        domains=["intrusion", "avoidance", "negative_cognitions_mood",
                 "arousal_reactivity"],
        score_range=ScoreRange(min=0, max=80),
        severity_bands={
            "below_threshold": _band(0, 30),
            "probable_ptsd": _band(31, 50),
            "severe": _band(51, 80),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=10,
        validated_for=["ptsd"],
    ),
    "ISI": AssessmentScale(
        scale_name="isi",
        abbreviation="ISI",
        full_name="Insomnia Severity Index",
        domains=["sleep_onset", "sleep_maintenance", "early_awakening",
                 "sleep_satisfaction", "daytime_functioning",
                 "noticeability", "distress"],
        score_range=ScoreRange(min=0, max=28),
        severity_bands={
            "no_insomnia": _band(0, 7),
            "subthreshold": _band(8, 14),
            "moderate": _band(15, 21),
            "severe": _band(22, 28),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=5,
        validated_for=["insomnia"],
    ),
    "THI": AssessmentScale(
        scale_name="thi",
        abbreviation="THI",
        full_name="Tinnitus Handicap Inventory",
        domains=["functional", "emotional", "catastrophic"],
        score_range=ScoreRange(min=0, max=100),
        severity_bands={
            "slight": _band(0, 16),
            "mild": _band(17, 36),
            "moderate": _band(37, 56),
            "severe": _band(57, 76),
            "catastrophic": _band(77, 100),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=10,
        validated_for=["tinnitus"],
    ),
    "EDSS": AssessmentScale(
        scale_name="edss",
        abbreviation="EDSS",
        full_name="Expanded Disability Status Scale",
        domains=["pyramidal", "cerebellar", "brainstem", "sensory",
                 "bowel_bladder", "visual", "cerebral", "ambulation"],
        score_range=ScoreRange(min=0, max=10),
        severity_bands={
            "normal_exam": _band(0, 0),
            "minimal_disability": _band(1.0, 3.5),
            "moderate_disability": _band(4.0, 5.5),
            "severe_disability": _band(6.0, 7.5),
            "very_severe": _band(8.0, 10.0),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=20,
        validated_for=["multiple_sclerosis"],
    ),
    "VAS-Pain": AssessmentScale(
        scale_name="vas_pain",
        abbreviation="VAS-Pain",
        full_name="Visual Analogue Scale for Pain",
        domains=["pain_intensity"],
        score_range=ScoreRange(min=0, max=100),
        severity_bands={
            "no_pain": _band(0, 0),
            "mild": _band(1, 30),
            "moderate": _band(31, 60),
            "severe": _band(61, 100),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=1,
        validated_for=["chronic_pain", "fibromyalgia", "neuropathic_pain"],
    ),
    "BRIEF-A": AssessmentScale(
        scale_name="brief_a",
        abbreviation="BRIEF-A",
        full_name="Behavior Rating Inventory of Executive Function — Adult Version",
        domains=["inhibit", "shift", "emotional_control", "self_monitor",
                 "initiate", "working_memory", "plan_organize",
                 "task_monitor", "organization_of_materials"],
        score_range=ScoreRange(min=75, max=225),
        severity_bands={
            "normal": _band(75, 119),
            "borderline": _band(120, 134),
            "mildly_elevated": _band(135, 149),
            "moderately_elevated": _band(150, 179),
            "severely_elevated": _band(180, 225),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=15,
        validated_for=["adhd", "traumatic_brain_injury",
                       "mild_cognitive_impairment"],
    ),
    "ASRS": AssessmentScale(
        scale_name="asrs",
        abbreviation="ASRS",
        full_name="Adult ADHD Self-Report Scale v1.1",
        domains=["inattention", "hyperactivity_impulsivity"],
        score_range=ScoreRange(min=0, max=72),
        severity_bands={
            "unlikely_adhd": _band(0, 16),
            "likely_adhd": _band(17, 23),
            "highly_likely_adhd": _band(24, 72),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=5,
        validated_for=["adhd"],
    ),
    "CGI-S": AssessmentScale(
        scale_name="cgi_s",
        abbreviation="CGI-S",
        full_name="Clinical Global Impression — Severity",
        domains=["global_severity"],
        score_range=ScoreRange(min=1, max=7),
        severity_bands={
            "normal": _band(1, 1),
            "borderline": _band(2, 2),
            "mildly_ill": _band(3, 3),
            "moderately_ill": _band(4, 4),
            "markedly_ill": _band(5, 5),
            "severely_ill": _band(6, 6),
            "extremely_ill": _band(7, 7),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=2,
        validated_for=[
            "depression", "anxiety", "ocd", "ptsd", "adhd", "parkinsons",
            "alzheimers", "chronic_pain", "tinnitus", "insomnia",
        ],
    ),
    "CGI-I": AssessmentScale(
        scale_name="cgi_i",
        abbreviation="CGI-I",
        full_name="Clinical Global Impression — Improvement",
        domains=["global_improvement"],
        score_range=ScoreRange(min=1, max=7),
        severity_bands={
            "very_much_improved": _band(1, 1),
            "much_improved": _band(2, 2),
            "minimally_improved": _band(3, 3),
            "no_change": _band(4, 4),
            "minimally_worse": _band(5, 5),
            "much_worse": _band(6, 6),
            "very_much_worse": _band(7, 7),
        },
        scoring_direction=ScoringDirection.LOWER_IS_BETTER,
        administration_time_minutes=2,
        validated_for=[
            "depression", "anxiety", "ocd", "ptsd", "adhd", "parkinsons",
            "alzheimers", "chronic_pain", "tinnitus", "insomnia",
        ],
    ),
}
"""Registry of validated clinical assessment scales commonly used in
neuromodulation research and practice. Keyed by display abbreviation."""


def get_scale(abbreviation: str) -> Optional[AssessmentScale]:
    """Look up a validated scale by its abbreviation. Returns None if not found."""
    return VALIDATED_SCALES.get(abbreviation)


def list_scales_for_condition(condition_slug: str) -> list[AssessmentScale]:
    """Return all validated scales that list the given condition slug."""
    return [
        s for s in VALIDATED_SCALES.values()
        if condition_slug in s.validated_for
    ]
