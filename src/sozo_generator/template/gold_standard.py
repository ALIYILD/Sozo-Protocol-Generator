"""
Gold standard template manifest — defines the expected structure of all 15 document types.
Used for template conformity checking and document generation scaffolding.
"""
from ..core.enums import DocumentType, Tier


DOCUMENT_MANIFEST = {
    DocumentType.CLINICAL_EXAM: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "patient_info",
            "motor_examination",
            "standard_neurological_examination",
            "cognitive_screening",
            "mood_behavioral_screening",
            "phenotype_identification",
            "clinical_summary",
        ],
        "partners_sections": [
            "document_control",
            "patient_info",
            "fnon_network_assessment",
            "motor_examination",
            "standard_neurological_examination",
            "cognitive_screening",
            "mood_behavioral_screening",
            "phenotype_identification",
            "network_hypothesis",
            "clinical_summary",
        ],
        "required_tables": True,
        "required_figures": False,
    },
    DocumentType.PHENOTYPE_CLASSIFICATION: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "phenotype_algorithm",
            "step1_phenotype_determination",
            "step2_target_selection",
            "step3_tdcs_montage",
            "step4_tps_protocol",
            "step5_combination_strategy",
            "step6_sequencing",
            "step7_response_evaluation",
            "step8_maintenance",
        ],
        "partners_sections": [
            "document_control",
            "fnon_core_principle",
            "step1_phenotype_determination",
            "step2_network_prioritization",
            "step3_tdcs_montage",
            "step4_tps_protocol",
            "step5_combination_strategy",
            "step6_sozo_sequencing",
        ],
        "required_tables": True,
        "required_figures": False,
    },
    DocumentType.RESPONDER_TRACKING: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "operational_response_definition",
            "responder_profiles",
            "response_classification",
            "non_responder_pathway",
            "levodopa_scheduling",
            "documentation",
        ],
        "partners_sections": [
            "document_control",
            "fnon_responder_profiling",
            "response_classification",
            "fnon_non_responder_pathway",
            "levodopa_scheduling",
            "responder_signature",
        ],
        "required_tables": True,
        "required_figures": False,
    },
    DocumentType.PSYCH_INTAKE: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "patient_info",
            "structured_clinical_interview",
            "chief_complaints",
            "psychiatric_history",
            "functional_limitations",
            "treatment_history",
            "sozo_prs_baseline",
            "motor_domain",
            "nonmotor_domain",
            "clinical_summary",
        ],
        "partners_sections": [
            "document_control",
            "patient_info",
            "structured_clinical_interview",
            "sozo_prs_baseline",
            "network_clinical_impression",
            "baseline_summary",
        ],
        "required_tables": True,
        "required_figures": False,
    },
    DocumentType.NETWORK_ASSESSMENT: {
        "both_tiers": False,
        "partners_only": True,
        "sections": [
            "document_control",
            "patient_info",
            "dmn_assessment",
            "cen_assessment",
            "sn_assessment",
            "smn_assessment",
            "limbic_assessment",
            "attention_assessment",
            "total_score",
            "network_hypothesis",
        ],
        "required_tables": True,
        "required_figures": True,
    },
    DocumentType.HANDBOOK: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "introduction",
            "available_modalities",
            "roles_responsibilities",
            "stage_1",
            "stage_2",
            "stage_3",
            "stage_4",
            "stage_5",
            "stage_6",
            "stage_7",
            "stage_8",
            "governance_rules",
            "references",
        ],
        "partners_sections": [
            "document_control",
            "fnon_framework",
            "introduction",
            "available_modalities",
            "stage_1",
            "stage_2",
            "stage_3",
            "stage_4",
            "stage_5",
            "stage_6",
            "stage_7",
            "stage_8",
            "fnon_five_level_pathway",
            "governance_rules",
            "references",
        ],
        "required_tables": True,
        "required_figures": False,
    },
    DocumentType.ALL_IN_ONE_PROTOCOL: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "classic_tps_protocols",
            "newronika_tdcs_protocols",
            "platoscience_tdcs_protocols",
            "multimodal_combinations",
        ],
        "partners_sections": [
            "document_control",
            "classic_tps_protocols",
            "fnon_tps_protocols",
            "newronika_tdcs_protocols",
            "platoscience_tdcs_protocols",
            "tavns_protocols",
            "ces_protocols",
            "multimodal_combinations",
        ],
        "required_tables": True,
        "required_figures": False,
    },
    DocumentType.EVIDENCE_BASED_PROTOCOL: {
        "both_tiers": False,
        "fellow_sections": [
            "document_control",
            "inclusion_exclusion",
            "clinical_overview",
            "pathophysiology",
            "key_brain_structures",
            "clinical_phenotypes",
            "symptom_brain_mapping",
            "tdcs_protocols",
            "tps_protocols",
            "tavns_ces_protocols",
            "combination_protocols",
            "side_effects_monitoring",
            "followup_decision_making",
        ],
        "partners_sections": [
            "document_control",
            "inclusion_exclusion",
            "clinical_overview",
            "pathophysiology",
            "key_brain_structures_networks",
            "clinical_phenotypes_networks",
            "symptom_network_modality_mapping",
            "fnon_application",
            "tdcs_protocols",
            "tps_protocols",
            "tavns_ces_protocols",
            "combination_protocols",
            "side_effects_monitoring",
            "followup_decision_making",
        ],
        "required_tables": True,
        "required_figures": True,
    },
}


def get_required_sections(doc_type: DocumentType, tier: Tier) -> list[str]:
    """Return the required sections for a document type and tier."""
    manifest = DOCUMENT_MANIFEST.get(doc_type, {})
    if tier == Tier.PARTNERS:
        return manifest.get("partners_sections", manifest.get("sections", []))
    return manifest.get("fellow_sections", manifest.get("sections", []))


def get_all_section_ids(doc_type: DocumentType) -> list[str]:
    """Return union of all section IDs across both tiers for a document type."""
    manifest = DOCUMENT_MANIFEST.get(doc_type, {})
    fellow = set(manifest.get("fellow_sections", []))
    partners = set(manifest.get("partners_sections", manifest.get("sections", [])))
    return sorted(fellow | partners)


def requires_tables(doc_type: DocumentType) -> bool:
    """Return whether a document type requires table generation."""
    return DOCUMENT_MANIFEST.get(doc_type, {}).get("required_tables", False)


def requires_figures(doc_type: DocumentType) -> bool:
    """Return whether a document type requires figure generation."""
    return DOCUMENT_MANIFEST.get(doc_type, {}).get("required_figures", False)


def is_partners_only(doc_type: DocumentType) -> bool:
    """Return whether a document type is Partners tier only."""
    return DOCUMENT_MANIFEST.get(doc_type, {}).get("partners_only", False)
