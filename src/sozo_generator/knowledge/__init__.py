"""SOZO Clinical Knowledge System — structured clinical knowledge compiler."""

from .tps_knowledge import (
    TPS_DEVICE_SPECS,
    TPS_MECHANISM,
    TPS_PARAMETER_STANDARDS,
    TPS_PROTOCOL_BY_CONDITION,
    TPS_EVIDENCE_BY_CONDITION,
    TPS_SAFETY_PROFILE,
    TPS_REFERENCES,
    get_tps_protocol,
    get_tps_evidence,
    get_tps_references_for_condition,
    get_tps_parameter_table_rows,
    get_tps_evidence_summary_table,
)

from .multimodal_protocols import (
    PROTOCOLS,
    get_condition_protocols,
    list_modalities,
    get_modality_protocols,
)

from .brain_regions import (
    BRAIN_REGIONS,
    EEG_TO_REGION,
    get_region_for_condition,
    get_regions_for_modality,
    get_region,
    get_eeg_positions_for_region,
)

from .evidence_matrix import (
    MODALITIES,
    EVIDENCE_MATRIX,
    BEST_MODALITIES,
    get_evidence_table,
    get_best_modality,
    get_ranked_modalities,
    list_conditions,
)

__all__ = [
    # tps_knowledge
    "TPS_DEVICE_SPECS",
    "TPS_MECHANISM",
    "TPS_PARAMETER_STANDARDS",
    "TPS_PROTOCOL_BY_CONDITION",
    "TPS_EVIDENCE_BY_CONDITION",
    "TPS_SAFETY_PROFILE",
    "TPS_REFERENCES",
    "get_tps_protocol",
    "get_tps_evidence",
    "get_tps_references_for_condition",
    "get_tps_parameter_table_rows",
    "get_tps_evidence_summary_table",
    # multimodal_protocols
    "PROTOCOLS",
    "get_condition_protocols",
    "list_modalities",
    "get_modality_protocols",
    # brain_regions
    "BRAIN_REGIONS",
    "EEG_TO_REGION",
    "get_region_for_condition",
    "get_regions_for_modality",
    "get_region",
    "get_eeg_positions_for_region",
    # evidence_matrix
    "MODALITIES",
    "EVIDENCE_MATRIX",
    "BEST_MODALITIES",
    "get_evidence_table",
    "get_best_modality",
    "get_ranked_modalities",
    "list_conditions",
]
