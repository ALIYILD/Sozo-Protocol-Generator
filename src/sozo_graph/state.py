"""
SozoGraphState — the single shared state object for the entire LangGraph.

Every node reads from and writes to this state. No hidden mutable state.
All mutations are explicit, typed, and auditable.
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, Literal, Optional, TypedDict


# ── Nested State Types ─────────────────────────────────────────────────


class IntakeState(TypedDict, total=False):
    """Intake and normalization state."""
    user_prompt: Optional[str]
    uploaded_file: Optional[bytes]
    uploaded_filename: Optional[str]
    template_profile: Optional[dict]
    normalized_request: Optional[dict]
    parse_warnings: list[str]
    parse_error: Optional[str]


class ConditionState(TypedDict, total=False):
    """Resolved condition metadata."""
    slug: str
    display_name: str
    icd10: str
    schema_dict: dict  # serialized ConditionSchema — not named 'schema' to avoid conflict
    resolution_source: str  # registry | template_inferred | prompt_inferred
    condition_valid: bool


class PatientContextState(TypedDict, total=False):
    """Patient-specific context for personalization."""
    patient_id: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    diagnosis_icd10: Optional[str]
    current_medications: list[str]
    contraindications: list[str]
    prior_neuromodulation: list[str]
    assessment_scores: dict[str, Any]
    phenotype_slug: Optional[str]
    severity_level: Optional[str]


class EvidenceState(TypedDict, total=False):
    """Evidence pipeline state."""
    search_queries: list[str]
    source_counts: dict[str, int]
    raw_article_count: int
    unique_article_count: int
    screened_article_count: int
    articles: list[dict]  # serialized ScoredArticle objects
    extractions: dict[str, dict]  # identifier → ExtractionResult
    evidence_scores: dict[str, dict]  # identifier → EvidenceScore
    evidence_summary: dict
    evidence_sufficient: bool
    evidence_gaps: list[str]
    prisma_counts: dict
    pipeline_log_path: Optional[str]


class SafetyState(TypedDict, total=False):
    """Safety assessment state."""
    contraindications_found: list[dict]
    modality_restrictions: list[dict]
    consent_requirements: list[str]
    off_label_flags: list[str]
    safety_cleared: bool
    blocking_contraindications: list[str]
    proceed_with_warnings: list[str]


class ProtocolState(TypedDict, total=False):
    """Protocol composition state."""
    base_sequence: dict  # serialized ProtocolSequence
    template_source: str
    selection_rationale: str
    composed_sections: list[dict]  # serialized ComposedSection objects
    grounding_score: float
    grounding_issues: list[dict]
    doc_type: str
    tier: str


class EEGState(TypedDict, total=False):
    """EEG personalization state (optional)."""
    data_available: bool
    features: dict[str, float]
    quality_metrics: dict
    interpretation: Optional[dict]
    adjustments_applied: list[dict]
    adjustments_rejected: list[dict]
    personalized_protocol: Optional[dict]


class ReviewState(TypedDict, total=False):
    """Clinician review state."""
    status: str  # pending | approved | rejected | edited
    reviewer_id: Optional[str]
    reviewer_credentials: Optional[str]
    review_timestamp: Optional[str]
    review_notes: Optional[str]
    edits_applied: list[dict]
    parameter_overrides: list[dict]
    revision_number: int
    approval_stamp: Optional[dict]


class OutputState(TypedDict, total=False):
    """Final output state."""
    output_paths: dict[str, str]
    output_formats: list[str]
    audit_record_id: Optional[str]


class NodeHistoryEntry(TypedDict):
    """Audit record for one node execution."""
    node_id: str
    started_at: str
    completed_at: str
    duration_ms: float
    status: str  # success | error | skipped
    error: Optional[str]
    input_hash: str
    output_hash: str
    decisions: list[str]


class ErrorEntry(TypedDict):
    """Recorded error from a node."""
    node_id: str
    error_type: str
    message: str
    recoverable: bool
    timestamp: str


# ── Top-Level State ────────────────────────────────────────────────────


class SozoGraphState(TypedDict):
    """Complete shared state for the Sozo protocol generation graph.

    Rules:
    - Every node receives this state and returns a partial update dict.
    - No node may read fields it doesn't need (discipline, not enforced).
    - No node may write fields outside its documented output schema.
    - node_history and errors use Annotated[list, operator.add] for append semantics.
    """

    # Identity & lifecycle
    request_id: str
    created_at: str
    updated_at: str
    status: str  # intake | evidence | composition | personalization | review | approved | rejected | released | error

    # Source mode
    source_mode: str  # upload | prompt

    # Nested states
    intake: IntakeState
    condition: ConditionState
    patient_context: Optional[PatientContextState]
    evidence: EvidenceState
    safety: SafetyState
    protocol: ProtocolState
    eeg: Optional[EEGState]
    review: ReviewState
    output: OutputState

    # Audit trail — append-only via operator.add reducer
    node_history: Annotated[list[NodeHistoryEntry], operator.add]
    errors: Annotated[list[ErrorEntry], operator.add]

    # Versioning
    version: str  # state schema version
    graph_version: str  # graph definition version
