"""Scoring evaluators built on validator reports."""

from .audience_evaluator import evaluate_audience
from .document_spec_invariants_evaluator import evaluate_document_spec_invariants
from .evidence_evaluator import evaluate_evidence_dimensions
from .modality_evaluator import evaluate_modality
from .overall_evaluator import evaluate_overall
from .structure_evaluator import evaluate_structure
from .structured_spec_evaluator import evaluate_structured_spec

__all__ = [
    "evaluate_audience",
    "evaluate_document_spec_invariants",
    "evaluate_evidence_dimensions",
    "evaluate_modality",
    "evaluate_overall",
    "evaluate_structure",
    "evaluate_structured_spec",
]
