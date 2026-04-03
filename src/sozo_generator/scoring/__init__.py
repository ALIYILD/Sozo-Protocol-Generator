"""Personalization confidence scoring for Sozo Protocol Generator.

This subpackage computes composite confidence scores for personalized
protocol recommendations, combining evidence strength, patient data
completeness, and phenotype match quality into an actionable confidence
band that guides clinician review depth.
"""

from .confidence import (
    ConfidenceBand,
    ConfidenceBreakdown,
    ConfidenceScorer,
    DataCompletenessInput,
    EvidenceStrengthInput,
    PhenotypeMatchInput,
)

__all__ = [
    "ConfidenceBand",
    "ConfidenceBreakdown",
    "ConfidenceScorer",
    "DataCompletenessInput",
    "EvidenceStrengthInput",
    "PhenotypeMatchInput",
]
