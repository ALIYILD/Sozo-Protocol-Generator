from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from ..core.enums import NetworkKey, NetworkDysfunction, Modality, EvidenceLevel


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


class AssessmentTool(BaseModel):
    scale_key: str
    name: str
    abbreviation: str
    domains: list[str] = Field(default_factory=list)
    timing: str = "baseline"  # baseline | weekly | monthly | endpoint
    evidence_pmid: Optional[str] = None
    notes: Optional[str] = None


class SafetyNote(BaseModel):
    category: str  # contraindication | precaution | monitoring | stopping_rule
    description: str
    severity: str = "moderate"  # low | moderate | high | absolute
    source: Optional[str] = None


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
    contraindications: list[str] = Field(default_factory=list)
    safety_notes: list[SafetyNote] = Field(default_factory=list)

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
