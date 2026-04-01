"""
Phase 2 shared contracts — the single source of truth for all Phase 2 data models.

Every module that needs these types MUST import from here. Do NOT redefine equivalents.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field, computed_field

from ..core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    EvidenceLevel,
    EvidenceRelation,
    EvidenceType,
    Modality,
    NetworkKey,
    QASeverity,
    ReviewFlag,
    ReviewStatus,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Evidence contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class EvidenceItem(BaseModel):
    """A single piece of evidence linked to a claim. Wraps an article reference
    with its relation to the claim and relevance metadata."""

    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str = ""
    authors_short: str = ""  # e.g. "Smith et al. 2024"
    journal: Optional[str] = None
    year: Optional[int] = None
    evidence_type: EvidenceType = EvidenceType.NARRATIVE_REVIEW
    evidence_level: EvidenceLevel = EvidenceLevel.MEDIUM
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS
    relevance_score: float = Field(default=0.0, ge=0.0, le=10.0)
    key_finding: str = ""
    population_match: bool = True
    condition_slug: Optional[str] = None
    modalities: list[Modality] = Field(default_factory=list)


class EvidenceBundle(BaseModel):
    """A cluster of evidence items for a specific claim category or section."""

    bundle_id: str
    condition_slug: str
    category: ClaimCategory
    section_id: Optional[str] = None
    items: list[EvidenceItem] = Field(default_factory=list)
    confidence: ConfidenceLabel = ConfidenceLabel.INSUFFICIENT
    has_contradictions: bool = False
    contradiction_notes: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: _now_iso())

    @computed_field
    @property
    def item_count(self) -> int:
        return len(self.items)

    @computed_field
    @property
    def supporting_count(self) -> int:
        return sum(1 for i in self.items if i.relation == EvidenceRelation.SUPPORTS)

    @computed_field
    @property
    def contradicting_count(self) -> int:
        return sum(1 for i in self.items if i.relation == EvidenceRelation.CONTRADICTS)


class SectionEvidenceMap(BaseModel):
    """Maps section IDs to their evidence bundles for a single document."""

    condition_slug: str
    document_type: str
    tier: str
    section_bundles: dict[str, list[EvidenceBundle]] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: _now_iso())


class ClaimCitationLink(BaseModel):
    """Links one claim to its supporting/contradicting citations."""

    claim_id: str
    claim_text: str
    category: ClaimCategory
    confidence: ConfidenceLabel
    pmids: list[str] = Field(default_factory=list)
    evidence_items: list[EvidenceItem] = Field(default_factory=list)
    requires_review: bool = False
    insufficient_evidence: bool = False


class ClaimCitationMap(BaseModel):
    """Complete claim-citation mapping for a document section or full document."""

    condition_slug: str
    document_type: str
    tier: str
    claims: list[ClaimCitationLink] = Field(default_factory=list)
    total_claims: int = 0
    unsupported_claims: int = 0
    review_required_claims: int = 0
    generated_at: str = Field(default_factory=lambda: _now_iso())


class EvidenceSnapshotManifest(BaseModel):
    """Versioned snapshot of all evidence used for a build."""

    snapshot_id: str
    condition_slug: str
    created_at: str = Field(default_factory=lambda: _now_iso())
    pubmed_fetch_date: Optional[str] = None
    total_articles: int = 0
    bundles: list[EvidenceBundle] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    content_hash: str = ""
    version: str = "1.0"
    notes: str = ""

    def compute_hash(self) -> str:
        """Compute deterministic hash of evidence content."""
        payload = json.dumps(
            [b.model_dump(exclude={"generated_at"}) for b in self.bundles],
            sort_keys=True,
            default=str,
        )
        self.content_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return self.content_hash


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QA contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class QAIssue(BaseModel):
    """A single QA finding with severity, location, and recommendation."""

    issue_id: str = ""
    rule_id: str = ""  # e.g. "citations.missing_pmid"
    severity: QASeverity = QASeverity.WARNING
    category: str = ""  # e.g. "citations", "safety", "language"
    location: str = ""  # section_id or field path
    message: str = ""
    suggestion: Optional[str] = None
    auto_fixable: bool = False
    evidence_ref: Optional[str] = None  # PMID or bundle_id if relevant


class QAReport(BaseModel):
    """Aggregated QA report for a single condition build."""

    report_id: str = ""
    condition_slug: str = ""
    condition_name: str = ""
    document_type: Optional[str] = None
    tier: Optional[str] = None
    generated_at: str = Field(default_factory=lambda: _now_iso())
    issues: list[QAIssue] = Field(default_factory=list)
    passed: bool = False
    block_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    evidence_snapshot_id: Optional[str] = None

    def compute_counts(self) -> None:
        self.block_count = sum(1 for i in self.issues if i.severity == QASeverity.BLOCK)
        self.warning_count = sum(1 for i in self.issues if i.severity == QASeverity.WARNING)
        self.info_count = sum(1 for i in self.issues if i.severity == QASeverity.INFO)
        self.passed = self.block_count == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Review workflow contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ReviewComment(BaseModel):
    """A reviewer comment on a section or document."""

    comment_id: str = ""
    reviewer: str = ""
    section_id: Optional[str] = None
    text: str = ""
    created_at: str = Field(default_factory=lambda: _now_iso())


class ReviewDecision(BaseModel):
    """A single review decision (approve/reject) with metadata."""

    decision_id: str = ""
    reviewer: str = ""
    status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    reason: str = ""
    comments: list[ReviewComment] = Field(default_factory=list)
    decided_at: str = Field(default_factory=lambda: _now_iso())


class ReviewState(BaseModel):
    """Full review state for one build output."""

    build_id: str = ""
    condition_slug: str = ""
    document_type: str = ""
    tier: str = ""
    status: ReviewStatus = ReviewStatus.DRAFT
    decisions: list[ReviewDecision] = Field(default_factory=list)
    section_notes: dict[str, list[ReviewComment]] = Field(default_factory=dict)
    qa_report_id: Optional[str] = None
    evidence_snapshot_id: Optional[str] = None
    version: str = "1.0"
    created_at: str = Field(default_factory=lambda: _now_iso())
    updated_at: str = Field(default_factory=lambda: _now_iso())

    def transition(self, new_status: ReviewStatus, reviewer: str, reason: str = "") -> None:
        """Transition to a new review status with audit trail."""
        _VALID_TRANSITIONS = {
            ReviewStatus.DRAFT: {ReviewStatus.NEEDS_REVIEW},
            ReviewStatus.NEEDS_REVIEW: {ReviewStatus.APPROVED, ReviewStatus.REJECTED},
            ReviewStatus.REJECTED: {ReviewStatus.NEEDS_REVIEW, ReviewStatus.DRAFT},
            ReviewStatus.APPROVED: {ReviewStatus.EXPORTED, ReviewStatus.NEEDS_REVIEW},
            ReviewStatus.EXPORTED: set(),
        }
        allowed = _VALID_TRANSITIONS.get(self.status, set())
        if new_status not in allowed:
            raise ValueError(
                f"Invalid transition: {self.status.value} → {new_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )
        decision = ReviewDecision(
            decision_id=f"dec-{_now_compact()}",
            reviewer=reviewer,
            status=new_status,
            reason=reason,
        )
        self.decisions.append(decision)
        self.status = new_status
        self.updated_at = _now_iso()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Build & figure manifest contracts
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class FigureEntry(BaseModel):
    """Metadata for a single generated figure."""

    figure_id: str = ""
    figure_type: str = ""  # brain_map, network_diagram, etc.
    file_path: str = ""
    condition_slug: str = ""
    content_hash: str = ""
    caption: str = ""
    generated_at: str = Field(default_factory=lambda: _now_iso())


class FigureManifest(BaseModel):
    """Manifest of all figures for a condition build."""

    condition_slug: str = ""
    figures: list[FigureEntry] = Field(default_factory=list)
    shared_legends: list[FigureEntry] = Field(default_factory=list)
    generated_at: str = Field(default_factory=lambda: _now_iso())


class DocumentBuildEntry(BaseModel):
    """Record of one document within a build."""

    document_type: str = ""
    tier: str = ""
    output_path: str = ""
    content_hash: str = ""
    section_count: int = 0
    claim_count: int = 0
    review_status: ReviewStatus = ReviewStatus.DRAFT
    qa_passed: bool = False
    qa_block_count: int = 0


class BuildManifest(BaseModel):
    """Complete manifest for a single condition build."""

    build_id: str = ""
    condition_slug: str = ""
    condition_name: str = ""
    generator_version: str = "1.0.0"
    template_version: str = "1.0"
    built_at: str = Field(default_factory=lambda: _now_iso())
    evidence_snapshot_id: Optional[str] = None
    documents: list[DocumentBuildEntry] = Field(default_factory=list)
    figure_manifest: Optional[FigureManifest] = None
    qa_summary: Optional[QAReport] = None
    claim_citation_map: Optional[ClaimCitationMap] = None
    total_documents: int = 0
    total_passed: int = 0
    total_blocked: int = 0
    content_hash: str = ""

    def compute_hash(self) -> str:
        payload = json.dumps(
            [d.model_dump() for d in self.documents],
            sort_keys=True,
            default=str,
        )
        self.content_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return self.content_hash


class BatchConditionResult(BaseModel):
    """Result of building one condition in a batch."""

    condition_slug: str = ""
    success: bool = False
    documents_generated: int = 0
    documents_blocked: int = 0
    error: Optional[str] = None
    build_manifest_path: Optional[str] = None
    qa_report_path: Optional[str] = None


class BatchBuildReport(BaseModel):
    """Summary report for a batch build across multiple conditions."""

    batch_id: str = ""
    started_at: str = Field(default_factory=lambda: _now_iso())
    completed_at: Optional[str] = None
    generator_version: str = "1.0.0"
    total_conditions: int = 0
    successful_conditions: int = 0
    failed_conditions: int = 0
    blocked_conditions: int = 0
    total_documents: int = 0
    results: list[BatchConditionResult] = Field(default_factory=list)
    retry_suggestions: list[str] = Field(default_factory=list)

    def finalize(self) -> None:
        self.completed_at = _now_iso()
        self.successful_conditions = sum(1 for r in self.results if r.success)
        self.failed_conditions = sum(1 for r in self.results if not r.success and r.error)
        self.blocked_conditions = sum(1 for r in self.results if r.documents_blocked > 0)
        self.total_documents = sum(r.documents_generated for r in self.results)
        self.retry_suggestions = [
            f"Retry: {r.condition_slug} — {r.error}"
            for r in self.results
            if not r.success and r.error
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
