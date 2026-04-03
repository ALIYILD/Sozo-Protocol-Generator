"""Data structures for the personalization pipeline.

All request/response dataclasses live here to keep the engine module focused
on logic and to avoid circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PersonalizationRequest:
    """Inbound request carrying everything needed to personalise a protocol."""

    condition_slug: str
    patient_demographics: dict
    symptoms: list[dict]
    medications: list[dict]
    treatment_history: list[dict]
    medical_history: list[str]
    eeg_features: Optional[dict] = None
    target_modalities: Optional[list[str]] = None


@dataclass
class ProtocolCandidate:
    """A single scored protocol option returned by the ranker."""

    modality: str
    target: str
    montage: dict
    parameters: dict
    schedule: dict
    phenotype_slug: Optional[str]
    evidence_level: str
    score: float
    rationale: str


@dataclass
class PersonalizationResult:
    """Complete output of the 4-layer personalization engine."""

    condition_slug: str
    safety_cleared: bool
    blocked_modalities: list[str]
    restricted_modalities: list[str]
    safety_warnings: list[str]
    medication_interactions: list[dict]
    matched_phenotype: Optional[str]
    phenotype_confidence: float
    ranked_protocols: list[ProtocolCandidate]
    recommended_protocol: Optional[ProtocolCandidate]
    eeg_adjustments: list[dict]
    target_refinement: Optional[dict]
    explanation: str
    confidence_score: float
    confidence_band: str
    decision_trace: list[dict]
