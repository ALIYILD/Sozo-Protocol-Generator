from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from ..core.enums import NetworkKey, NetworkDysfunction, Modality, EvidenceLevel
from .validators import validate_pmid


class PhenotypeSubtype(BaseModel):
    slug: str
    label: str
    description: str
    key_features: list[str] = Field(default_factory=list)
    primary_networks: list[NetworkKey] = Field(default_factory=list)
    secondary_networks: list[NetworkKey] = Field(default_factory=list)
    preferred_modalities: list[Modality] = Field(default_factory=list)
    tdcs_target: Optional[str] = None
    tps_target: Optional[str] = None
    tbs_target: Optional[str] = None


class NetworkProfile(BaseModel):
    network: NetworkKey
    dysfunction: NetworkDysfunction
    relevance: str  # description of how this network is implicated
    severity: str = "moderate"  # mild | moderate | severe
    primary: bool = False
    evidence_note: Optional[str] = None


class StimulationTarget(BaseModel):
    modality: Modality
    target_region: str
    target_abbreviation: str
    laterality: str = "bilateral"  # bilateral | left | right
    rationale: str
    protocol_label: Optional[str] = None
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM
    off_label: bool = True
    consent_required: bool = True
    eeg_canonical: Optional[list[str]] = None  # canonical EEG positions from brain_regions data
    eeg_10_20_positions: Optional[list[str]] = None  # All 10-20 positions this target maps to
    brain_region_description: Optional[str] = None
    neuromod_rationale: Optional[str] = None


class AssessmentTool(BaseModel):
    scale_key: str
    name: str
    abbreviation: str
    domains: list[str] = Field(default_factory=list)
    timing: str = "baseline"  # baseline | weekly | monthly | endpoint
    evidence_pmid: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("evidence_pmid", mode="before")
    @classmethod
    def _validate_pmid(cls, v: str | None) -> str | None:
        import re
        if v is None:
            return None
        stripped = str(v).strip()
        # Silently discard placeholder strings that are not valid PubMed IDs
        if not re.match(r"^\d{1,9}$", stripped):
            return None
        return stripped


class SafetyNote(BaseModel):
    category: str  # contraindication | precaution | monitoring | stopping_rule
    description: str
    severity: str = "moderate"  # low | moderate | high | absolute
    source: Optional[str] = None


class AdverseEventGrade(BaseModel):
    grade: int  # 1-4
    label: str  # "Mild", "Moderate", "Severe", "Life-threatening"
    description: str
    examples: list[str] = Field(default_factory=list)
    action: str = ""


class SideEffectEntry(BaseModel):
    effect: str
    frequency: str  # "Common (>30%)", "Uncommon (1-10%)", etc.
    modalities: list[Modality] = Field(default_factory=list)
    management: str
    severity: str = "mild"


class PlatoScienceVariant(BaseModel):
    variant_id: str
    protocol_id: str  # links to parent ProtocolEntry
    label: str
    parameters: dict[str, str | int | float] = Field(default_factory=dict)
    notes: str = ""


class MultimodalCombo(BaseModel):
    combo_id: str
    label: str
    phenotype_slugs: list[str] = Field(default_factory=list)
    tps_protocol_id: Optional[str] = None
    non_tps_protocol_ids: list[str] = Field(default_factory=list)
    sequencing_notes: str = ""
    rationale: str = ""


class HomeBasedProtocol(BaseModel):
    protocol_id: str
    label: str
    modality: Modality
    device: str
    parameters: dict[str, str | int | float] = Field(default_factory=dict)
    eligibility_criteria: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    monitoring_requirements: list[str] = Field(default_factory=list)


class ProtocolEntry(BaseModel):
    protocol_id: str
    label: str
    modality: Modality
    target_region: str
    target_abbreviation: str
    phenotype_slugs: list[str] = Field(default_factory=list)
    network_targets: list[NetworkKey] = Field(default_factory=list)
    parameters: dict[str, str | int | float | list] = Field(default_factory=dict)
    rationale: str
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM
    off_label: bool = True
    session_count: Optional[int] = None
    notes: Optional[str] = None

    # Extended protocol fields matching SOZO Fellow Handbook format
    protocol_name: Optional[str] = None  # e.g. "TPS-ANX — TPS Protocol for Anxious TRD"
    clinical_objective: Optional[str] = None
    primary_targets: Optional[list[str]] = None  # e.g. ["Left DLPFC", "ACC (Fz)", "Amygdala region"]
    secondary_targets: Optional[list[str]] = None
    device_name: Optional[str] = None  # Specific device e.g. "NEUROLITH® TPS System (Storz Medical)"
    session_structure: Optional[str] = None  # e.g. "Neuronavigation setup → Holocranial priming (2,000 pulses) → ..."
    frequency: Optional[str] = None  # e.g. "3–5 sessions/week"
    duration: Optional[str] = None  # e.g. "30–45 min per session"
    intensity_dose: Optional[str] = None  # e.g. "0.20–0.25 mJ/mm²; 1–4 Hz"
    montage_roi: Optional[str] = None  # e.g. "Anode (+): F3 (L-DLPFC). Cathode (−): F4 (R-DLPFC)"
    laterality: Optional[str] = None  # e.g. "Left-dominant for DLPFC; bilateral for amygdala region"
    treatment_course: Optional[str] = None  # e.g. "10–12 sessions over 2–4 weeks; then maintenance 1–2/week"
    monitoring: Optional[str] = None  # e.g. "GAD-7 weekly; PHQ-9 biweekly; heart rate; tolerability log"
    expected_response: Optional[str] = None
    evidence_status: Optional[str] = None  # Narrative evidence text (vs evidence_level enum)
    cautions: Optional[str] = None
    when_to_escalate: Optional[str] = None
    when_to_stop_modify: Optional[str] = None
    clinical_notes_extended: Optional[str] = None  # Longer clinical notes
    key_citations: Optional[list[str]] = None  # e.g. ["Cheung et al., 2023", "Qin et al., 2025"]


class ConditionSchema(BaseModel):
    """Complete structured representation of one condition for document generation."""
    # Identity
    slug: str
    display_name: str
    icd10: str
    aliases: list[str] = Field(default_factory=list)
    version: str = "1.0"
    generated_at: str = ""

    # Clinical content
    overview: str = ""
    pathophysiology: str = ""
    core_symptoms: list[str] = Field(default_factory=list)
    non_motor_symptoms: list[str] = Field(default_factory=list)

    # Anatomy
    key_brain_regions: list[str] = Field(default_factory=list)
    brain_region_descriptions: dict[str, str] = Field(default_factory=dict)

    # Networks
    network_profiles: list[NetworkProfile] = Field(default_factory=list)
    primary_network: Optional[NetworkKey] = None
    fnon_rationale: str = ""

    # Clinical phenotypes
    phenotypes: list[PhenotypeSubtype] = Field(default_factory=list)

    # Assessment
    assessment_tools: list[AssessmentTool] = Field(default_factory=list)
    baseline_measures: list[str] = Field(default_factory=list)
    followup_measures: list[str] = Field(default_factory=list)

    # Inclusion / Exclusion
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    conditions_requiring_discussion: Optional[list[str]] = None
    contraindications: list[str] = Field(default_factory=list)
    safety_notes: list[SafetyNote] = Field(default_factory=list)

    # EEG reference
    eeg_reference_table: Optional[list[dict]] = None  # 10-20 EEG positions reference: [{"position": "F3", "brain_region": "Left DLPFC", "role": "...", "protocols_using": [...]}]

    # Treatment
    stimulation_targets: list[StimulationTarget] = Field(default_factory=list)
    protocols: list[ProtocolEntry] = Field(default_factory=list)
    symptom_network_mapping: dict[str, list[NetworkKey]] = Field(default_factory=dict)
    symptom_modality_mapping: dict[str, list[Modality]] = Field(default_factory=dict)

    # Responder logic
    responder_criteria: list[str] = Field(default_factory=list)
    non_responder_pathway: str = ""
    levodopa_note: Optional[str] = None  # None for non-PD conditions

    # Evidence
    evidence_summary: str = ""
    evidence_gaps: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    references: list[dict] = Field(default_factory=list)
    overall_evidence_quality: EvidenceLevel = EvidenceLevel.MEDIUM

    # Handbook logic
    patient_journey_notes: dict[str, str] = Field(default_factory=dict)
    decision_tree_notes: list[str] = Field(default_factory=list)
    clinical_tips: list[str] = Field(default_factory=list)
    governance_rules: list[str] = Field(default_factory=list)

    # Rich protocol data (optional — builders skip when empty)
    adverse_event_grades: list[AdverseEventGrade] = Field(default_factory=list)
    side_effects: list[SideEffectEntry] = Field(default_factory=list)
    platoscience_variants: list[PlatoScienceVariant] = Field(default_factory=list)
    multimodal_combos: list[MultimodalCombo] = Field(default_factory=list)
    home_based_protocols: list[HomeBasedProtocol] = Field(default_factory=list)
    sequencing_framework: dict[str, str] = Field(default_factory=dict)
    modality_specific_contraindications: dict[str, list[str]] = Field(default_factory=dict)
