"""Machine-readable protocol schema for Sozo Protocol Generator.

This is the canonical internal representation of a neuromodulation protocol.
Every generated, uploaded, or manually created protocol conforms to this schema.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from ..core.enums import EvidenceLevel, EvidenceType, Modality
from .validators import validate_pmid


# ---------------------------------------------------------------------------
# Protocol-specific enums
# ---------------------------------------------------------------------------


class ProtocolStatus(str, Enum):
    """Lifecycle states for a protocol document."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class GenerationMethod(str, Enum):
    """How a protocol was created."""

    CONDITION_BASED = "condition_based"
    TEMPLATE_EXTRACTED = "template_extracted"
    PROMPT_GENERATED = "prompt_generated"
    PERSONALIZED = "personalized"
    MANUAL = "manual"


class Hemisphere(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    BILATERAL = "bilateral"
    MIDLINE = "midline"


class StopSeverity(str, Enum):
    """Urgency level for a stopping criterion."""

    IMMEDIATE_STOP = "immediate_stop"
    PAUSE_AND_REVIEW = "pause_and_review"
    NOTE_AND_CONTINUE = "note_and_continue"


class ContraindicationSeverity(str, Enum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    PRECAUTION = "precaution"


class AssessmentTiming(str, Enum):
    PRE_TREATMENT = "pre_treatment"
    EACH_SESSION = "each_session"
    WEEKLY = "weekly"
    MID_TREATMENT = "mid_treatment"
    POST_TREATMENT = "post_treatment"
    FOLLOW_UP = "follow_up"


class ScoringDirection(str, Enum):
    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class ConditionInfo(BaseModel):
    """Minimal condition reference embedded in a protocol."""

    slug: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    display_name: str
    icd10: str = Field(pattern=r"^[A-Z][0-9]{2}(\.[0-9]{1,2})?$")
    subtype: Optional[str] = None
    phenotype_slug: Optional[str] = None
    indication: str = ""


class ModalityInfo(BaseModel):
    """Primary and optional secondary stimulation modalities."""

    primary: Modality
    secondary: Optional[list[Modality]] = None
    rationale: str = ""


class MNICoordinates(BaseModel):
    """Montreal Neurological Institute stereotaxic coordinates."""

    x: float
    y: float
    z: float


class StimulationTarget(BaseModel):
    """Brain target for stimulation delivery."""

    primary_site: str
    coordinates_10_20: Optional[str] = None
    mni_coordinates: Optional[MNICoordinates] = None
    brodmann_area: Optional[int] = None
    hemisphere: Hemisphere = Hemisphere.LEFT
    rationale: str = ""
    evidence_refs: list[str] = Field(default_factory=list)


class Montage(BaseModel):
    """Electrode montage configuration."""

    anode: Optional[str] = None
    cathode: Optional[str] = None
    reference: Optional[str] = None
    electrode_size_cm2: Optional[float] = None
    description: str = ""


class IntensityParams(BaseModel):
    """Stimulation intensity and ramp parameters."""

    value: float = Field(gt=0)
    unit: Literal["mA", "Hz", "pulses", "V", "mJ/mm2"]
    ramp_up_seconds: Optional[int] = None
    ramp_down_seconds: Optional[int] = None


class DeviceInfo(BaseModel):
    """Device metadata for regulatory traceability."""

    name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    regulatory_status: Optional[str] = None


class StimulationParameters(BaseModel):
    """Complete stimulation configuration for one session type."""

    target: StimulationTarget
    montage: Montage
    intensity: IntensityParams
    duration_minutes: float = Field(ge=1, le=120)
    frequency_hz: Optional[float] = None
    pulse_count: Optional[int] = None
    waveform: Optional[str] = None
    device: Optional[DeviceInfo] = None


class PhaseSchedule(BaseModel):
    """A named phase within the treatment schedule (e.g. induction, taper)."""

    phase_name: str
    sessions: int = Field(ge=1)
    frequency: str
    parameters_override: Optional[dict] = None
    notes: str = ""


class MaintenanceProtocol(BaseModel):
    """Ongoing maintenance after the acute treatment phase."""

    frequency: str
    duration: str
    reassessment_interval: str


class Schedule(BaseModel):
    """Treatment schedule and session plan."""

    total_sessions: int = Field(ge=1)
    frequency: str  # e.g. "3x/week"
    phase_schedule: list[PhaseSchedule] = Field(default_factory=list)
    estimated_duration_weeks: Optional[float] = None
    maintenance_protocol: Optional[MaintenanceProtocol] = None


class Eligibility(BaseModel):
    """Patient inclusion and exclusion criteria."""

    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)


class SafetyRule(BaseModel):
    """A single contraindication or precaution rule."""

    description: str
    category: str = ""
    severity: ContraindicationSeverity
    source: Optional[str] = None


class MonitoringRequirement(BaseModel):
    """A measure to monitor during treatment for safety."""

    measure: str
    timing: str
    threshold: Optional[str] = None
    action_if_breached: Optional[str] = None


class StoppingCriterion(BaseModel):
    """Condition under which treatment should be paused or stopped."""

    criterion: str
    severity: StopSeverity
    action: str


class Safety(BaseModel):
    """Complete safety profile for a protocol."""

    contraindications_absolute: list[SafetyRule] = Field(default_factory=list)
    contraindications_relative: list[SafetyRule] = Field(default_factory=list)
    precautions: list[str] = Field(default_factory=list)
    monitoring_requirements: list[MonitoringRequirement] = Field(
        default_factory=list,
    )
    stopping_criteria: list[StoppingCriterion] = Field(default_factory=list)
    adverse_event_protocol: Optional[str] = None


class BaselineAssessment(BaseModel):
    """An outcome measure used before, during, or after treatment."""

    scale_name: str
    abbreviation: str
    timing: AssessmentTiming
    domain: str = ""
    scoring_direction: ScoringDirection = ScoringDirection.LOWER_IS_BETTER
    required: bool = True


class TitrationRule(BaseModel):
    """Rule for adjusting stimulation parameters during treatment."""

    trigger: str
    action: str
    limit: Optional[str] = None


class ResponderCriteria(BaseModel):
    """Definition of treatment response and remission."""

    primary_measure: str
    response_threshold: str
    remission_threshold: Optional[str] = None
    timepoint: str


class ProgressionRules(BaseModel):
    """Rules governing dose titration and responder classification."""

    titration: list[TitrationRule] = Field(default_factory=list)
    responder_criteria: Optional[ResponderCriteria] = None
    non_responder_pathway: Optional[str] = None


class ExpectedOutcome(BaseModel):
    """Predicted clinical outcome with evidence grading."""

    outcome: str
    measure: str
    expected_effect_size: Optional[str] = None
    evidence_level: EvidenceLevel
    timeframe: str = ""


class EvidenceReference(BaseModel):
    """A literature reference linked to one or more protocol sections."""

    pmid: str = Field(pattern=r"^[0-9]{1,9}$")
    doi: Optional[str] = None
    title: str = ""
    authors: str = ""
    journal: Optional[str] = None
    year: int = Field(ge=1900, le=2100)
    evidence_type: EvidenceType
    evidence_level: EvidenceLevel
    relevance_score: float = Field(ge=0, le=5)
    linked_sections: list[str] = Field(default_factory=list)

    @field_validator("pmid", mode="before")
    @classmethod
    def _validate_pmid(cls, v: str) -> str:
        result = validate_pmid(v)
        if result is None:
            raise ValueError("PMID must be a non-empty numeric string")
        return result


class PersonalizationAdaptation(BaseModel):
    """A single patient-specific adaptation applied to the protocol."""

    field_path: str
    original_value: Optional[str] = None
    adapted_value: Optional[str] = None
    reason: str
    confidence: float = Field(ge=0, le=1)
    evidence_refs: list[str] = Field(default_factory=list)
    rule_id: Optional[str] = None


class Personalization(BaseModel):
    """V2: Patient-specific protocol adaptations."""

    patient_id: str
    phenotype_match: Optional[str] = None
    adaptations: list[PersonalizationAdaptation] = Field(default_factory=list)
    eeg_driven: bool = False
    eeg_features_used: Optional[dict] = None
    confidence_score: float = Field(ge=0, le=1, default=0.5)
    explanation: str = ""


class ClinicianNote(BaseModel):
    """Free-text annotation attached to a protocol by a clinician."""

    author: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    section: Optional[str] = None
    text: str


class Approval(BaseModel):
    """Record of clinical approval for a protocol."""

    approved_by: str
    approved_at: datetime
    approval_notes: Optional[str] = None
    digital_signature_hash: Optional[str] = None


class NodeHistoryEntry(BaseModel):
    """Trace of a single LangGraph node execution during generation."""

    node: str
    timestamp: datetime
    input_hash: str
    output_hash: str
    decision: Optional[str] = None
    duration_ms: Optional[int] = None


class AuditMetadata(BaseModel):
    """Provenance and build metadata for traceability."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    generation_method: GenerationMethod = GenerationMethod.CONDITION_BASED
    build_id: Optional[str] = None
    model_version: Optional[str] = None
    knowledge_version: Optional[str] = None
    node_history: list[NodeHistoryEntry] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Root Protocol Model
# ---------------------------------------------------------------------------


class SozoProtocol(BaseModel):
    """Root protocol object -- the canonical representation of a neuromodulation protocol.

    Every protocol generated, uploaded, or manually created in the Sozo
    Protocol Generator is validated against this schema.
    """

    # Identity
    protocol_id: UUID = Field(default_factory=uuid4)
    version: int = Field(ge=1, default=1)
    parent_version_id: Optional[UUID] = None
    status: ProtocolStatus = ProtocolStatus.DRAFT

    # Clinical
    condition: ConditionInfo
    modality: ModalityInfo
    stimulation_parameters: StimulationParameters
    schedule: Schedule
    eligibility: Eligibility = Field(default_factory=Eligibility)
    safety: Safety
    baseline_assessments: list[BaselineAssessment] = Field(default_factory=list)
    progression_rules: ProgressionRules = Field(default_factory=ProgressionRules)
    expected_outcomes: list[ExpectedOutcome] = Field(default_factory=list)

    # Evidence
    evidence_references: list[EvidenceReference] = Field(min_length=1)

    # Personalization (V2)
    personalization: Optional[Personalization] = None

    # Review
    clinician_notes: list[ClinicianNote] = Field(default_factory=list)
    approval: Optional[Approval] = None

    # Audit
    audit: AuditMetadata

    class Config:
        json_schema_extra = {
            "title": "SozoProtocol",
            "description": (
                "Canonical neuromodulation protocol representation "
                "for Sozo Protocol Generator"
            ),
        }


# ---------------------------------------------------------------------------
# JSON Schema export helper
# ---------------------------------------------------------------------------


def get_protocol_json_schema() -> dict:
    """Return the full JSON Schema for SozoProtocol (Pydantic v2 compatible)."""
    return SozoProtocol.model_json_schema()


if __name__ == "__main__":
    import json

    print(json.dumps(get_protocol_json_schema(), indent=2))
