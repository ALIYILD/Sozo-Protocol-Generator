"""
Pydantic schemas for the internal AutoAgent-Clinical benchmark lab.

This module defines benchmark cases, harness outputs, validation findings,
and evaluation reports. It is not a clinical runtime artifact.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class FailureTaxonomy(str, Enum):
    """Internal QA failure categories for benchmark reporting."""

    UNSUPPORTED_CLAIM = "unsupported_claim"
    WRONG_MODALITY = "wrong_modality"
    MISSING_CITATION = "missing_citation"
    MONTAGE_CONTRADICTION = "montage_contradiction"
    AUDIENCE_MISMATCH = "audience_mismatch"
    STRUCTURE_VIOLATION = "structure_violation"
    DEVICE_MISMATCH = "device_mismatch"
    EVIDENCE_GAP = "evidence_gap"
    REGULATORY_OVERCLAIM = "regulatory_overclaim"
    LATERALITY_INCONSISTENCY = "laterality_inconsistency"
    CITATION_WEAK_OR_MISMATCHED = "citation_weak_or_mismatched"
    MALFORMED_STRUCTURED_OUTPUT = "malformed_structured_output"
    # Structure-native DocumentSpec / blueprint checks (not markdown heuristics)
    MISSING_REQUIRED_SECTION = "missing_required_section"
    INSUFFICIENT_REFERENCES = "insufficient_references"
    SPEC_IDENTITY_MISMATCH = "spec_identity_mismatch"
    PLACEHOLDER_OR_EMPTY_SECTION = "placeholder_or_empty_section"
    SECTION_ORDER_OR_DEPTH_ANOMALY = "section_order_or_depth_anomaly"


class BenchmarkCategory(str, Enum):
    PARKINSONS_PROTOCOL = "parkinsons_protocol"
    MONTAGE_CONSISTENCY = "montage_consistency"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    EVIDENCE_MAPPING = "evidence_mapping"
    FELLOW_PARTNER = "fellow_partner"
    DEVICE_MISMATCH = "device_mismatch"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCK = "block"


class BenchmarkExpectations(BaseModel):
    """How to interpret validator output for pass/fail on a case."""

    expect_pass: Optional[bool] = None
    """If set, case fails when outcome disagrees."""

    expected_failure_codes: list[str] = Field(default_factory=list)
    """For negative cases: at least one of these codes should appear."""

    forbidden_failure_codes: list[str] = Field(default_factory=list)
    """If any of these appear, the case fails."""

    min_overall_score: float = Field(ge=0.0, le=1.0, default=0.0)
    """Minimum weighted overall score to count as pass when expect_pass is unset."""


class BenchmarkCase(BaseModel):
    """One benchmark task plus a deterministic fixture for the MVP harness."""

    id: str
    category: str
    title: str
    description: str = ""
    internal_note: str = Field(
        default="For internal drafting and QA only — not for autonomous clinical use.",
    )
    inputs: dict[str, Any] = Field(default_factory=dict)
    fixture_markdown: str = ""
    optional_protocol_json: Optional[dict[str, Any]] = None
    expectations: BenchmarkExpectations = Field(default_factory=BenchmarkExpectations)


class BenchmarkSuite(BaseModel):
    """Container loaded from YAML."""

    suite: str = "autoagent_clinical"
    version: str = "1"
    cases: list[BenchmarkCase] = Field(default_factory=list)


class HarnessMetadata(BaseModel):
    harness_id: str
    notes: list[str] = Field(default_factory=list)
    structured_source: Optional[str] = None
    """document_spec | docx_extract | failure — how benchmark markdown was produced."""


class HarnessResult(BaseModel):
    """Output from an agent harness for one case."""

    case_id: str
    output_text: str
    structured_protocol: Optional[dict[str, Any]] = None
    """Reserved for SozoProtocol-shaped JSON when available (not assembly provenance)."""
    document_spec: Optional[dict[str, Any]] = None
    """Serialized :class:`sozo_generator.schemas.documents.DocumentSpec` when captured."""
    assembly_provenance: Optional[dict[str, Any]] = None
    """Assembly provenance dict when structured path or DOCX sidecar provides it."""
    metadata: HarnessMetadata


class ValidationFinding(BaseModel):
    code: str
    severity: Severity
    message: str
    reasons: list[str] = Field(default_factory=list)
    locator: Optional[str] = None


class ValidatorReport(BaseModel):
    validator_id: str
    findings: list[ValidationFinding] = Field(default_factory=list)


class DimensionScore(BaseModel):
    """One evaluated dimension with explicit rationale."""

    name: str
    score: float = Field(ge=0.0, le=1.0)
    passed: bool
    reasons: list[str] = Field(default_factory=list)


class CaseEvaluation(BaseModel):
    case_id: str
    category: str
    harness_id: str
    validator_reports: list[ValidatorReport] = Field(default_factory=list)
    dimensions: list[DimensionScore] = Field(default_factory=list)
    overall_score: float = Field(ge=0.0, le=1.0, default=0.0)
    passed: bool = False
    expectation_violations: list[str] = Field(default_factory=list)
    failure_codes: list[str] = Field(default_factory=list)


class BenchmarkRunReport(BaseModel):
    """Full run across cases."""

    run_id: str
    started_at: str
    finished_at: str
    suite: str
    harness_id: str
    case_results: list[CaseEvaluation] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)

    @staticmethod
    def timestamps() -> tuple[str, str]:
        now = datetime.now(timezone.utc).isoformat()
        return now, now


class HarnessComparisonReport(BaseModel):
    """Score deltas between two harnesses on the same cases."""

    baseline_harness: str
    compare_harness: str
    suite: str
    per_case_delta: list[dict[str, Any]] = Field(default_factory=list)
    aggregate: dict[str, Any] = Field(default_factory=dict)
