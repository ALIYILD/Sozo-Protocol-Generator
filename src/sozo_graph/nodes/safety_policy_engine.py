"""
safety_policy_engine — applies contraindication rules, modality restrictions,
and regulatory constraints.

Type: Deterministic
Loads rules from sozo_knowledge YAML and modalities.yaml.
"""
from __future__ import annotations

import logging

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)

# Hard contraindications per modality family
_HARD_CONTRAINDICATIONS: dict[str, list[str]] = {
    "tdcs": [
        "metallic_cranial_implant",
        "open_wound_at_electrode_site",
        "unstable_epilepsy",
    ],
    "tps": [
        "metallic_cranial_implant",
        "cochlear_implant",
        "increased_intracranial_pressure",
        "active_bleeding_disorder",
    ],
    "tavns": [
        "active_ear_infection",
        "vagotomy_history",
        "cardiac_arrhythmia_uncontrolled",
    ],
    "ces": [
        "metallic_cranial_implant",
        "cardiac_pacemaker",
    ],
    "all": [
        "pregnancy_first_trimester",
        "active_psychosis",
        "severe_skin_disease_at_site",
    ],
}

# Modalities requiring doctor authorization
_DOCTOR_AUTH_REQUIRED = {"tps"}

# Modalities with specific off-label disclosures
_OFF_LABEL_DISCLOSURES: dict[str, str] = {
    "tps": "TPS is CE-marked ONLY for Alzheimer's disease. All other conditions are off-label.",
    "tdcs": "tDCS is CE-marked but off-label for most neuropsychiatric indications.",
    "tavns": "taVNS is CE-marked for epilepsy; off-label for neuropsychiatric conditions.",
}

# Conditions where TPS has CE-mark
_TPS_APPROVED_CONDITIONS = {"alzheimers"}


@audited_node("safety_policy_engine")
def safety_policy_engine(state: SozoGraphState) -> dict:
    """Apply safety rules and produce a SafetyAssessment."""
    decisions = []
    condition = state.get("condition", {})
    patient = state.get("patient_context") or {}

    # Determine target modalities from condition schema
    schema_dict = condition.get("schema_dict", {})
    stim_targets = schema_dict.get("stimulation_targets", [])
    target_modalities = list({
        t.get("modality", "tdcs") for t in stim_targets
    }) or ["tdcs"]

    patient_contraindications = set(
        c.lower().replace(" ", "_") for c in patient.get("contraindications", [])
    )

    blocking = []
    warnings = []
    consent_requirements = ["Informed consent for neuromodulation treatment"]
    off_label_flags = []
    modality_restrictions = []

    condition_slug = condition.get("slug", "")

    for modality in target_modalities:
        mod_lower = modality.lower()

        # Check hard contraindications
        hard = _HARD_CONTRAINDICATIONS.get(mod_lower, []) + _HARD_CONTRAINDICATIONS.get("all", [])
        for ci in hard:
            if ci in patient_contraindications:
                blocking.append(f"{mod_lower}: {ci}")
                decisions.append(f"BLOCKING contraindication: {ci} for {mod_lower}")

        # Doctor authorization
        if mod_lower in _DOCTOR_AUTH_REQUIRED:
            consent_requirements.append(f"Doctor authorization required for {mod_lower.upper()}")

        # Off-label disclosure
        if mod_lower in _OFF_LABEL_DISCLOSURES:
            # Check if condition is approved for this modality
            if mod_lower == "tps" and condition_slug not in _TPS_APPROVED_CONDITIONS:
                off_label_flags.append(_OFF_LABEL_DISCLOSURES[mod_lower])
                consent_requirements.append(f"Off-label consent required for {mod_lower.upper()}")
                decisions.append(f"Off-label: {mod_lower} for {condition_slug}")
            elif mod_lower != "tps":
                off_label_flags.append(_OFF_LABEL_DISCLOSURES[mod_lower])

    # Medication interactions (simplified check)
    medications = [m.lower() for m in patient.get("current_medications", [])]
    seizure_risk_meds = {"bupropion", "clozapine", "theophylline", "tramadol"}
    for med in medications:
        if med in seizure_risk_meds:
            warnings.append(f"Medication '{med}' may lower seizure threshold — monitor closely")
            decisions.append(f"Warning: seizure-risk medication '{med}'")

    safety_cleared = len(blocking) == 0

    if safety_cleared:
        decisions.append(f"Safety cleared for modalities: {target_modalities}")
    else:
        decisions.append(f"Safety BLOCKED: {blocking}")

    return {
        "safety": {
            "contraindications_found": [{"modality": b.split(":")[0], "contraindication": b.split(":")[-1].strip()} for b in blocking],
            "modality_restrictions": modality_restrictions,
            "consent_requirements": consent_requirements,
            "off_label_flags": off_label_flags,
            "safety_cleared": safety_cleared,
            "blocking_contraindications": blocking,
            "proceed_with_warnings": warnings,
        },
        "status": "composition",
        "_decisions": decisions,
    }
