"""
Patient safety evaluation engine for neuromodulation.

Combines universal contraindications, medication interactions, and
demographic considerations to produce a comprehensive safety profile.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from sozo_generator.safety.interaction_checker import (
    InteractionCheckResult,
    check_interactions,
)


# Universal contraindications loaded from knowledge base
_CONTRAINDICATIONS_PATH = (
    Path(__file__).resolve().parents[3]
    / "sozo_knowledge"
    / "knowledge"
    / "contraindications"
    / "universal.yaml"
)


@dataclass
class PatientSafetyProfile:
    """Full patient safety assessment."""

    patient_id: str
    absolute_contraindications: list[str]
    relative_contraindications: list[str]
    medication_interactions: InteractionCheckResult
    age_considerations: list[str]
    modality_clearance: dict[str, bool]  # modality → cleared
    warnings: list[str]
    safety_cleared: bool

    @property
    def summary(self) -> str:
        if self.safety_cleared:
            prefix = "Patient cleared for treatment."
        else:
            prefix = "Patient NOT cleared — review required."
        parts = [prefix]
        if self.absolute_contraindications:
            parts.append(
                f"Absolute contraindications: {', '.join(self.absolute_contraindications)}."
            )
        if self.warnings:
            parts.append(f"Warnings: {len(self.warnings)}.")
        return " ".join(parts)


def _load_universal_contraindications() -> dict:
    """Load universal contraindications from YAML knowledge base.

    The YAML uses a flat `contraindications` list with `severity` field
    to distinguish absolute vs relative. Parse both formats.
    """
    if not _CONTRAINDICATIONS_PATH.exists():
        return {"absolute": [], "relative": []}
    with open(_CONTRAINDICATIONS_PATH) as f:
        data = yaml.safe_load(f) or {}

    # Format 1: already split into absolute/relative keys
    if "absolute" in data or "absolute_contraindications" in data:
        return {
            "absolute": data.get("absolute", data.get("absolute_contraindications", [])),
            "relative": data.get("relative", data.get("relative_contraindications", [])),
        }

    # Format 2: flat list under `contraindications` with severity field
    items = data.get("contraindications", [])
    absolute = []
    relative = []
    for item in items:
        if isinstance(item, dict):
            entry = {
                "description": item.get("description", item.get("name", "")),
                "slug": item.get("slug", ""),
                "modalities": item.get("modalities", []),
                "name": item.get("name", ""),
            }
            if item.get("severity") == "absolute":
                absolute.append(entry)
            else:
                relative.append(entry)
        elif isinstance(item, str):
            absolute.append({"description": item})

    return {"absolute": absolute, "relative": relative}


def evaluate_patient_safety(
    patient_demographics: dict,
    medications: list[dict],
    medical_history: list[str],
    target_modalities: list[str] | None = None,
) -> PatientSafetyProfile:
    """Full patient safety evaluation.

    Args:
        patient_demographics: dict with age, sex, handedness.
        medications: List of dicts with name, drug_class, dose.
        medical_history: List of medical conditions/history strings.
        target_modalities: Modalities to evaluate. Defaults to all four.
    """
    if target_modalities is None:
        target_modalities = ["tdcs", "tps", "tavns", "ces"]

    patient_id = patient_demographics.get("patient_id", "unknown")
    age = patient_demographics.get("age", 0)

    # Load universal contraindications
    contra_db = _load_universal_contraindications()

    # Check absolute contraindications against medical history
    history_lower = {h.lower() for h in medical_history}
    absolute_found: list[str] = []
    relative_found: list[str] = []

    def _matches_history(item: dict | str, history_terms: set[str]) -> bool:
        """Check if a contraindication matches any patient history term.

        Matches against description, name, and slug fields.
        Uses bidirectional substring matching for flexibility.
        """
        if isinstance(item, str):
            search_texts = [item.lower()]
        else:
            search_texts = [
                item.get("description", "").lower(),
                item.get("name", "").lower(),
                item.get("slug", "").replace("_", " ").lower(),
            ]
        for text in search_texts:
            if not text:
                continue
            for hist in history_terms:
                # Bidirectional: "pacemaker" matches "Implanted Cardiac Device / Pacemaker"
                # and "cardiac pacemaker" matches "cardiac_implant"
                hist_words = hist.split()
                text_words = text.split()
                # Any word overlap (at least one significant word matches)
                for hw in hist_words:
                    if len(hw) < 4:
                        continue  # skip short words like "or", "and"
                    if hw in text or any(hw in tw for tw in text_words):
                        return True
                # Full substring match
                if hist in text or text in hist:
                    return True
        return False

    for item in contra_db.get("absolute", []):
        if _matches_history(item, history_lower):
            desc = item if isinstance(item, str) else item.get("description", item.get("name", str(item)))
            absolute_found.append(desc)

    for item in contra_db.get("relative", []):
        if _matches_history(item, history_lower):
            desc = item if isinstance(item, str) else item.get("description", item.get("name", str(item)))
            relative_found.append(desc)

    # Check medication interactions
    med_result = check_interactions(medications, target_modalities)

    # Age-based considerations
    age_considerations: list[str] = []
    if age < 18:
        age_considerations.append(
            "Pediatric patient (<18): Most neuromodulation protocols are validated "
            "for adults only. Requires specialist review and parental consent."
        )
    elif age > 80:
        age_considerations.append(
            "Elderly patient (>80): Consider reduced intensity parameters. "
            "Monitor for increased skin sensitivity and cognitive effects."
        )
    if age > 65:
        age_considerations.append(
            "Age >65: Ensure adequate hydration, monitor blood pressure "
            "during TPS sessions."
        )

    # Compile warnings
    warnings: list[str] = []
    warnings.extend(age_considerations)
    if relative_found:
        warnings.extend(
            [f"Relative contraindication: {c}" for c in relative_found]
        )
    if med_result.has_major_interactions:
        warnings.append(
            f"Major medication interactions detected for: "
            f"{', '.join(med_result.restricted_modalities)}"
        )

    # Modality clearance
    blocked_set = set(med_result.blocked_modalities)
    # Block all modalities if absolute contraindications exist
    if absolute_found:
        clearance = {m: False for m in target_modalities}
    else:
        clearance = {
            m: m.lower() not in blocked_set for m in target_modalities
        }

    # Pediatric: block all unless specialist override
    if age < 18:
        clearance = {m: False for m in target_modalities}
        warnings.append("All modalities blocked for pediatric patients pending specialist review.")

    safety_cleared = (
        not absolute_found
        and not med_result.has_contraindications
        and age >= 18
    )

    return PatientSafetyProfile(
        patient_id=patient_id,
        absolute_contraindications=absolute_found,
        relative_contraindications=relative_found,
        medication_interactions=med_result,
        age_considerations=age_considerations,
        modality_clearance=clearance,
        warnings=warnings,
        safety_cleared=safety_cleared,
    )
