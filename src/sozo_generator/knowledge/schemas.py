"""
Core knowledge schemas for the SOZO Clinical Knowledge System.

These Pydantic models define the structure of all knowledge objects.
Each model corresponds to a YAML file under sozo_knowledge/knowledge/.

Design principles:
- Every clinical claim links to evidence (PMID or source)
- Cross-references use slug identifiers (validated by the linker)
- Regulatory and safety information is explicit, never assumed
- Models are designed for generation consumption, not storage optimization
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
from ..schemas.validators import validate_pmid


# ── Shared sub-models ──────────────────────────────────────────────────────


class Reference(BaseModel):
    """A literature reference with traceability."""
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str = ""
    authors: str = ""
    year: Optional[int] = None
    journal: str = ""
    evidence_level: str = "medium"  # highest, high, medium, low, very_low
    notes: str = ""

    @field_validator("pmid", mode="before")
    @classmethod
    def _validate_pmid(cls, v):
        return validate_pmid(v)


class NetworkInvolvement(BaseModel):
    """How a brain network is involved in a condition."""
    network: str  # dmn, cen, sn, smn, limbic, attention
    dysfunction: str = "normal"  # hypo, normal, hyper
    severity: str = "moderate"  # mild, moderate, severe
    primary: bool = False
    relevance: str = ""
    evidence_note: str = ""


class Phenotype(BaseModel):
    """A clinical subtype within a condition."""
    slug: str
    label: str
    description: str = ""
    key_features: list[str] = Field(default_factory=list)
    primary_networks: list[str] = Field(default_factory=list)
    secondary_networks: list[str] = Field(default_factory=list)
    preferred_modalities: list[str] = Field(default_factory=list)
    tdcs_target: str = ""
    tps_target: str = ""


class StimulationProtocol(BaseModel):
    """A specific stimulation protocol for a condition."""
    protocol_id: str
    label: str
    modality: str  # slug reference → Modality
    target_region: str
    target_abbreviation: str
    target_electrodes: list[str] = Field(default_factory=list)
    phenotype_slugs: list[str] = Field(default_factory=list)
    network_targets: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    evidence_level: str = "medium"
    off_label: bool = True
    session_count: Optional[int] = None
    notes: str = ""


class SafetyRule(BaseModel):
    """A safety note or contraindication."""
    category: str  # contraindication, precaution, monitoring, stopping_rule
    description: str
    severity: str = "moderate"  # low, moderate, high, absolute
    modalities: list[str] = Field(default_factory=list)  # which modalities this applies to
    source: str = ""


class AssessmentRef(BaseModel):
    """Reference to an assessment scale used for a condition."""
    scale_key: str  # slug reference → Assessment
    timing: str = "baseline"  # baseline, weekly, monthly, endpoint
    primary: bool = False
    notes: str = ""


# ── Core Knowledge Objects ─────────────────────────────────────────────────


class KnowledgeCondition(BaseModel):
    """Complete knowledge object for a clinical condition.

    This is the central knowledge type. It contains or references
    everything needed to generate any SOZO document for this condition.
    """
    # Identity
    slug: str
    display_name: str
    icd10: str
    aliases: list[str] = Field(default_factory=list)
    category: str = ""  # neurological, psychiatric, pain, neurodegenerative
    version: str = "1.0"

    # Clinical
    overview: str = ""
    pathophysiology: str = ""
    epidemiology: str = ""
    core_symptoms: list[str] = Field(default_factory=list)
    non_motor_symptoms: list[str] = Field(default_factory=list)

    # Anatomy
    brain_regions: list[str] = Field(default_factory=list)  # slug refs → BrainTarget
    brain_region_details: dict[str, str] = Field(default_factory=dict)

    # Networks (FNON)
    network_profiles: list[NetworkInvolvement] = Field(default_factory=list)
    primary_network: str = ""
    fnon_rationale: str = ""

    # Phenotypes
    phenotypes: list[Phenotype] = Field(default_factory=list)

    # Assessments (references)
    assessments: list[AssessmentRef] = Field(default_factory=list)

    # Modalities (references)
    applicable_modalities: list[str] = Field(default_factory=list)  # slug refs → Modality

    # Protocols
    protocols: list[StimulationProtocol] = Field(default_factory=list)

    # Safety
    safety_rules: list[SafetyRule] = Field(default_factory=list)
    contraindications: list[str] = Field(default_factory=list)
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)

    # Responder
    responder_criteria: list[str] = Field(default_factory=list)
    non_responder_pathway: str = ""

    # Evidence
    evidence_summary: str = ""
    evidence_quality: str = "medium"
    evidence_gaps: list[str] = Field(default_factory=list)
    references: list[Reference] = Field(default_factory=list)

    # Generation hints
    clinical_tips: list[str] = Field(default_factory=list)
    governance_rules: list[str] = Field(default_factory=list)
    patient_journey_notes: dict[str, str] = Field(default_factory=dict)


class KnowledgeModality(BaseModel):
    """Knowledge object for a neuromodulation modality."""
    slug: str
    name: str
    abbreviation: str
    description: str = ""

    # Technical
    mechanism: str = ""
    parameters: dict[str, Any] = Field(default_factory=dict)
    devices: list[dict[str, Any]] = Field(default_factory=list)

    # Regulatory
    regulatory_status: str = ""
    off_label_conditions: list[str] = Field(default_factory=list)
    on_label_conditions: list[str] = Field(default_factory=list)

    # Safety
    safety_principles: list[str] = Field(default_factory=list)
    contraindications: list[SafetyRule] = Field(default_factory=list)
    side_effects: list[dict[str, str]] = Field(default_factory=list)

    # Evidence
    evidence_level_by_condition: dict[str, str] = Field(default_factory=dict)
    key_references: list[Reference] = Field(default_factory=list)

    # Applicable conditions (back-references)
    applicable_conditions: list[str] = Field(default_factory=list)


class KnowledgeAssessment(BaseModel):
    """Knowledge object for a clinical assessment scale."""
    slug: str
    name: str
    abbreviation: str
    description: str = ""

    # Scale details
    scale_type: str = "clinician_administered"  # clinician_administered, self_report
    domains: list[str] = Field(default_factory=list)
    score_range: str = ""
    clinically_significant_threshold: str = ""
    minimal_detectable_change: str = ""

    # Applicability
    applicable_conditions: list[str] = Field(default_factory=list)
    recommended_timing: str = "baseline"  # baseline, weekly, monthly, endpoint

    # Evidence
    validation_pmid: Optional[str] = None
    notes: str = ""

    @field_validator("validation_pmid", mode="before")
    @classmethod
    def _validate_pmid(cls, v):
        return validate_pmid(v)


class KnowledgeBrainTarget(BaseModel):
    """Knowledge object for a brain stimulation target."""
    slug: str
    name: str
    abbreviation: str
    description: str = ""

    # Anatomy
    lobe: str = ""
    hemisphere: str = "bilateral"  # left, right, bilateral, midline
    brodmann_areas: list[str] = Field(default_factory=list)

    # EEG mapping
    eeg_10_20: list[str] = Field(default_factory=list)
    eeg_10_10: list[str] = Field(default_factory=list)

    # Network associations
    networks: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)

    # Modality access
    tdcs_accessible: bool = True
    tps_accessible: bool = True
    tdcs_montage_hint: str = ""
    tps_approach_hint: str = ""

    # Conditions where this target is relevant
    relevant_conditions: list[str] = Field(default_factory=list)
    relevant_symptoms: list[str] = Field(default_factory=list)


class KnowledgeEvidenceMap(BaseModel):
    """Links condition + modality to evidence."""
    condition_slug: str
    modality_slug: str
    evidence_level: str = "medium"
    evidence_quality: str = "medium"
    indication_status: str = "investigational"  # approved, investigational, off_label, experimental

    # Evidence details
    key_trials: list[Reference] = Field(default_factory=list)
    meta_analyses: list[Reference] = Field(default_factory=list)
    guidelines: list[Reference] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)

    # Clinical summary
    summary: str = ""
    recommended_protocols: list[str] = Field(default_factory=list)  # protocol_id refs


class KnowledgeContraindication(BaseModel):
    """A contraindication profile."""
    slug: str
    name: str
    description: str = ""
    severity: str = "absolute"  # absolute, relative
    modalities: list[str] = Field(default_factory=list)
    conditions_excluded: list[str] = Field(default_factory=list)
    regulatory_basis: str = ""
    source: str = ""


class SharedClinicalRule(BaseModel):
    """A cross-condition clinical rule or protocol."""
    slug: str
    name: str
    category: str = ""  # governance, safety, session_protocol, consent, monitoring
    description: str = ""
    applies_to: list[str] = Field(default_factory=list)  # "all" or list of condition/modality slugs
    rule_text: str = ""
    mandatory: bool = False
    source: str = ""
