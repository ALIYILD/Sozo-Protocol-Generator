"""
SOZO Safety Module — Medication interaction checking and patient safety evaluation.

Provides:
- DrugInteraction database for neuromodulation-relevant medications
- InteractionChecker for screening medications against target modalities
- ContraindicationEngine for full patient safety evaluation
"""

from sozo_generator.safety.drug_interactions import (
    DrugInteraction,
    DRUG_INTERACTIONS,
    get_interactions_for_drug_class,
    get_interactions_for_modality,
)
from sozo_generator.safety.interaction_checker import (
    InteractionAlert,
    InteractionCheckResult,
    check_interactions,
)
from sozo_generator.safety.contraindication_engine import (
    PatientSafetyProfile,
    evaluate_patient_safety,
)

__all__ = [
    "DrugInteraction",
    "DRUG_INTERACTIONS",
    "get_interactions_for_drug_class",
    "get_interactions_for_modality",
    "InteractionAlert",
    "InteractionCheckResult",
    "check_interactions",
    "PatientSafetyProfile",
    "evaluate_patient_safety",
]
