"""
Medication interaction checker for neuromodulation safety.

Screens a patient's medication list against target modalities and produces
a structured report of all interactions, grouped by severity.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from sozo_generator.safety.drug_interactions import (
    DRUG_INTERACTIONS,
    DrugInteraction,
    get_interactions_for_drug_class,
)


@dataclass
class InteractionAlert:
    """A single interaction alert for a patient's medication."""

    drug_name: str
    drug_class: str
    modality: str
    severity: str  # contraindicated | major | moderate | minor
    mechanism: str
    recommendation: str
    evidence_pmids: list[str] = field(default_factory=list)


@dataclass
class InteractionCheckResult:
    """Full interaction screening result."""

    has_contraindications: bool
    has_major_interactions: bool
    interactions: list[InteractionAlert]
    safe_modalities: list[str]
    restricted_modalities: list[str]
    blocked_modalities: list[str]
    summary: str

    @property
    def is_safe(self) -> bool:
        return not self.has_contraindications


def check_interactions(
    medications: list[dict],
    target_modalities: list[str] | None = None,
) -> InteractionCheckResult:
    """Screen medications against neuromodulation modalities.

    Args:
        medications: List of dicts with keys: name, drug_class, dose (optional).
        target_modalities: Modalities to check. Defaults to all four.

    Returns:
        InteractionCheckResult with alerts grouped by severity.
    """
    if target_modalities is None:
        target_modalities = ["tdcs", "tps", "tavns", "ces"]

    target_set = {m.lower() for m in target_modalities}
    alerts: list[InteractionAlert] = []
    blocked: set[str] = set()
    restricted: set[str] = set()

    for med in medications:
        drug_name = med.get("name", "unknown")
        drug_class = med.get("drug_class", "")

        # Match by drug_class or by name against generic_examples
        matches = get_interactions_for_drug_class(drug_class)
        if not matches:
            matches = get_interactions_for_drug_class(drug_name)

        for interaction in matches:
            for modality in interaction.modalities_affected:
                if modality.lower() not in target_set:
                    continue

                alert = InteractionAlert(
                    drug_name=drug_name,
                    drug_class=interaction.drug_class,
                    modality=modality,
                    severity=interaction.severity,
                    mechanism=interaction.mechanism,
                    recommendation=interaction.recommendation,
                    evidence_pmids=interaction.evidence_pmids,
                )
                alerts.append(alert)

                if interaction.severity == "contraindicated":
                    blocked.add(modality.lower())
                elif interaction.severity == "major":
                    restricted.add(modality.lower())

    safe = sorted(target_set - blocked - restricted)
    blocked_list = sorted(blocked)
    restricted_list = sorted(restricted - blocked)

    has_contra = len(blocked) > 0
    has_major = len(restricted) > 0

    # Build summary
    parts: list[str] = []
    if has_contra:
        parts.append(
            f"CONTRAINDICATED modalities: {', '.join(blocked_list)}."
        )
    if has_major:
        parts.append(
            f"Major interactions for: {', '.join(restricted_list)}."
        )
    if safe:
        parts.append(f"Safe modalities: {', '.join(safe)}.")
    if not alerts:
        parts.append("No medication interactions detected.")

    return InteractionCheckResult(
        has_contraindications=has_contra,
        has_major_interactions=has_major,
        interactions=alerts,
        safe_modalities=safe,
        restricted_modalities=restricted_list,
        blocked_modalities=blocked_list,
        summary=" ".join(parts),
    )
