"""
Canonical definitions for document generation.

These models describe WHAT should be generated, not the generated content itself.
They are the "blueprints" that the generation pipeline reads to know which sections,
visuals, and checks to produce for each document type.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field

from ..core.enums import DocumentType, Tier, Modality, NetworkKey


# ─── Visual specifications ─────────────────────────────────────────────────


class VisualSpec(BaseModel):
    """Declares a single visual asset required by a document."""

    visual_type: str  # brain_map, network_diagram, montage_panel, symptom_flow, patient_journey, eeg_topomap
    caption_template: str = ""  # e.g. "{condition} — EEG 10-20 Montage for {protocol}"
    required: bool = True
    condition_dependent: bool = True  # False for shared legends
    description: str = ""


# ─── Section specification ──────────────────────────────────────────────────


class SectionSpec(BaseModel):
    """Declares a section required in a document type."""

    section_id: str  # e.g. "overview", "anatomy", "protocols_tps"
    title: str
    required: bool = True
    tier: Optional[Tier] = None  # None = both tiers; set to restrict
    description: str = ""
    requires_evidence: bool = False  # If True, claims in this section need PMID backing
    subsections: list["SectionSpec"] = Field(default_factory=list)


# ─── Document definition ────────────────────────────────────────────────────


class DocumentDefinition(BaseModel):
    """Blueprint for a document type — what sections and visuals it requires.

    This is NOT a generated document. It is the specification that the generation
    pipeline uses to assemble a document for a given condition and tier.
    """

    doc_type: DocumentType
    display_name: str
    description: str = ""
    applicable_tiers: list[Tier] = Field(default_factory=lambda: [Tier.FELLOW, Tier.PARTNERS])
    sections: list[SectionSpec] = Field(default_factory=list)
    visuals: list[VisualSpec] = Field(default_factory=list)
    requires_evidence_appendix: bool = False
    requires_safety_section: bool = True
    template_name: Optional[str] = None  # gold_standard template filename if applicable


# ─── Generation request ─────────────────────────────────────────────────────


class GenerationRequest(BaseModel):
    """A single request to generate one document.

    This is the canonical input to the GenerationService.
    """

    condition_slug: str
    tier: Tier
    doc_type: DocumentType
    output_dir: Optional[str] = None
    with_visuals: bool = True
    with_qa: bool = True
    with_evidence_refresh: bool = False
    force_regenerate: bool = False


# ─── Pre-built document definitions ────────────────────────────────────────


DOCUMENT_DEFINITIONS: dict[DocumentType, DocumentDefinition] = {
    DocumentType.EVIDENCE_BASED_PROTOCOL: DocumentDefinition(
        doc_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
        display_name="Evidence-Based Protocol",
        description="Comprehensive protocol with full evidence base for a single condition.",
        sections=[
            SectionSpec(section_id="overview", title="Clinical Overview", requires_evidence=True),
            SectionSpec(section_id="pathophysiology", title="Pathophysiology", requires_evidence=True),
            SectionSpec(section_id="anatomy", title="Neuroanatomy & Brain Regions", requires_evidence=True),
            SectionSpec(section_id="networks", title="FNON Network Profile", requires_evidence=True),
            SectionSpec(section_id="phenotypes", title="Phenotype Classification", requires_evidence=True),
            SectionSpec(section_id="assessments", title="Assessment Tools & Scales"),
            SectionSpec(section_id="protocols", title="Stimulation Protocols", requires_evidence=True),
            SectionSpec(section_id="safety", title="Safety & Contraindications", requires_evidence=True),
            SectionSpec(section_id="responder", title="Responder Criteria & Tracking"),
            SectionSpec(section_id="inclusion_exclusion", title="Inclusion / Exclusion Criteria"),
            SectionSpec(section_id="evidence_summary", title="Evidence Summary & Gaps"),
            SectionSpec(section_id="references", title="References"),
        ],
        visuals=[
            VisualSpec(visual_type="brain_map", caption_template="{condition} — Key Brain Regions"),
            VisualSpec(visual_type="network_diagram", caption_template="{condition} — FNON Network Profile"),
            VisualSpec(visual_type="symptom_flow", caption_template="{condition} — Symptom-Network Flow"),
            VisualSpec(visual_type="qeeg_topomap", caption_template="{condition} — 10-10 EEG Stimulation Map"),
            VisualSpec(visual_type="mri_target_view", caption_template="{condition} — Sagittal Stimulation Targets"),
            VisualSpec(visual_type="axial_brain_view", caption_template="{condition} — Axial Stimulation Targets"),
            VisualSpec(visual_type="coronal_brain_view", caption_template="{condition} — Coronal Stimulation Targets"),
            VisualSpec(visual_type="connectivity_map", caption_template="{condition} — Network Connectivity Profile"),
            VisualSpec(visual_type="spectral_topomap", caption_template="{condition} — EEG Spectral Band Profile"),
        ],
        requires_evidence_appendix=True,
        template_name="Evidence_Based_Protocol.docx",
    ),
    DocumentType.HANDBOOK: DocumentDefinition(
        doc_type=DocumentType.HANDBOOK,
        display_name="Clinical Handbook",
        description="8-stage patient journey handbook for clinicians.",
        sections=[
            SectionSpec(section_id="overview", title="Condition Overview"),
            SectionSpec(section_id="modalities", title="Available Modalities"),
            SectionSpec(section_id="offlabel_disclosure", title="Off-Label Disclosure"),
            SectionSpec(section_id="prs_baseline", title="SOZO PRS Baseline"),
            SectionSpec(section_id="clinical_exam", title="Clinical Examination"),
            SectionSpec(section_id="phenotype_id", title="Phenotype Identification"),
            SectionSpec(section_id="protocol_assignment", title="Protocol Assignment"),
            SectionSpec(section_id="session_workflow", title="Session Workflow"),
            SectionSpec(section_id="responder_tracking", title="Responder Tracking"),
            SectionSpec(section_id="inclusion_exclusion", title="Inclusion / Exclusion"),
            SectionSpec(section_id="safety", title="Safety & Contraindications"),
        ],
        visuals=[
            VisualSpec(visual_type="patient_journey", caption_template="{condition} — Patient Journey"),
            VisualSpec(visual_type="treatment_timeline", caption_template="{condition} — SOZO Session Timeline"),
            VisualSpec(visual_type="dose_response", caption_template="{condition} — Response Tracking Template"),
        ],
        template_name="Clinical_Handbook.docx",
    ),
    DocumentType.CLINICAL_EXAM: DocumentDefinition(
        doc_type=DocumentType.CLINICAL_EXAM,
        display_name="Clinical Examination Checklist",
        description="Structured neurological/psychiatric examination checklist.",
        sections=[
            SectionSpec(section_id="patient_info", title="Patient Information"),
            SectionSpec(section_id="medical_history", title="Medical History"),
            SectionSpec(section_id="exam_domains", title="Examination Domains"),
            SectionSpec(section_id="screening_scales", title="Screening Scales"),
            SectionSpec(section_id="phenotype_prelim", title="Preliminary Phenotype"),
            SectionSpec(section_id="safety_checklist", title="Safety Checklist"),
        ],
        template_name="Clinical_Examination_Checklist.docx",
    ),
    DocumentType.PHENOTYPE_CLASSIFICATION: DocumentDefinition(
        doc_type=DocumentType.PHENOTYPE_CLASSIFICATION,
        display_name="Phenotype Classification & Protocol Mapping",
        description="Maps clinical phenotypes to treatment protocols.",
        sections=[
            SectionSpec(section_id="phenotype_definitions", title="Phenotype Definitions"),
            SectionSpec(section_id="protocol_mapping", title="Phenotype-to-Protocol Mapping"),
            SectionSpec(section_id="network_assignment", title="Network Target Assignment"),
            SectionSpec(section_id="montage_reference", title="Montage Reference"),
        ],
        template_name="Phenotype_Classification.docx",
    ),
    DocumentType.RESPONDER_TRACKING: DocumentDefinition(
        doc_type=DocumentType.RESPONDER_TRACKING,
        display_name="Responder Tracking & Classification",
        description="Session-by-session outcome tracking with responder criteria.",
        sections=[
            SectionSpec(section_id="response_criteria", title="Response Criteria"),
            SectionSpec(section_id="tracking_form", title="Session Tracking Form"),
            SectionSpec(section_id="responder_classification", title="Responder Classification"),
            SectionSpec(section_id="non_responder_pathway", title="Non-Responder Pathway"),
        ],
        visuals=[
            VisualSpec(visual_type="dose_response", caption_template="{condition} — Response Tracking Template"),
        ],
        template_name="Responder_Tracking.docx",
    ),
    DocumentType.PSYCH_INTAKE: DocumentDefinition(
        doc_type=DocumentType.PSYCH_INTAKE,
        display_name="Psychological Intake & PRS Baseline",
        description="Standardized psychosocial intake and baseline measures.",
        sections=[
            SectionSpec(section_id="demographics", title="Patient Demographics"),
            SectionSpec(section_id="clinical_history", title="Clinical History"),
            SectionSpec(section_id="prs_baseline", title="PRS Baseline Measures"),
            SectionSpec(section_id="risk_assessment", title="Risk Assessment"),
        ],
        template_name="Psychological_Intake_PRS.docx",
    ),
    DocumentType.NETWORK_ASSESSMENT: DocumentDefinition(
        doc_type=DocumentType.NETWORK_ASSESSMENT,
        display_name="6-Network Bedside Assessment",
        description="Full FNON 6-network bedside assessment (Partners only).",
        applicable_tiers=[Tier.PARTNERS],
        sections=[
            SectionSpec(section_id="dmn_assessment", title="Default Mode Network (DMN)"),
            SectionSpec(section_id="cen_assessment", title="Central Executive Network (CEN)"),
            SectionSpec(section_id="sn_assessment", title="Salience Network (SN)"),
            SectionSpec(section_id="smn_assessment", title="Sensorimotor Network (SMN)"),
            SectionSpec(section_id="limbic_assessment", title="Limbic/Emotional Network"),
            SectionSpec(section_id="attention_assessment", title="Attention Networks"),
            SectionSpec(section_id="scoring_summary", title="Network Scoring Summary"),
        ],
        visuals=[
            VisualSpec(visual_type="network_diagram", caption_template="{condition} — 6-Network Assessment"),
        ],
        template_name="6Network_Bedside_Assessment.docx",
    ),
    DocumentType.ALL_IN_ONE_PROTOCOL: DocumentDefinition(
        doc_type=DocumentType.ALL_IN_ONE_PROTOCOL,
        display_name="All-in-One Protocol Compendium",
        description="Comprehensive protocol card with TPS, tDCS, PlatoScience, and multimodal sequences.",
        sections=[
            SectionSpec(section_id="tps_protocols", title="TPS Protocols (T1-T5)"),
            SectionSpec(section_id="tdcs_protocols", title="HDCkit tDCS Protocols (C1-C8)"),
            SectionSpec(section_id="plato_protocols", title="PlatoScience Protocols"),
            SectionSpec(section_id="multimodal", title="Multimodal SOZO Sequences (F1-F9)"),
            SectionSpec(section_id="safety_monitoring", title="Safety & Adverse Event Monitoring"),
        ],
        visuals=[
            VisualSpec(visual_type="eeg_topomap", caption_template="{condition} — QEEG 10-10 Montage"),
            VisualSpec(visual_type="montage_panel", caption_template="{condition} — Protocol Montage Panels"),
            VisualSpec(visual_type="mri_target_view", caption_template="{condition} — Sagittal Stimulation Targets"),
            VisualSpec(visual_type="axial_brain_view", caption_template="{condition} — Axial Stimulation Targets"),
            VisualSpec(visual_type="treatment_timeline", caption_template="{condition} — SOZO Session Timeline"),
            VisualSpec(visual_type="impedance_map", caption_template="{condition} — Electrode Impedance Check"),
        ],
        template_name="All_In_One_Protocol.docx",
    ),
}


def get_document_definition(doc_type: DocumentType) -> DocumentDefinition:
    """Get the canonical document definition for a document type."""
    if doc_type not in DOCUMENT_DEFINITIONS:
        raise ValueError(f"No document definition for {doc_type.value}")
    return DOCUMENT_DEFINITIONS[doc_type]


def get_all_document_definitions() -> dict[DocumentType, DocumentDefinition]:
    """Get all document definitions."""
    return DOCUMENT_DEFINITIONS.copy()
