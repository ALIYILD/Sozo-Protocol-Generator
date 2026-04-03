"""
Domain models for review-driven regeneration.

These models represent the full lifecycle:
  ReviewComment → ChangeRequest → ChangePlan → RegenerationResult

Every change flows through structured models, never through free-form rewriting.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ── Enums ──────────────────────────────────────────────────────────────────


class CommentCategory(str, Enum):
    WORDING = "wording"
    EVIDENCE_STRENGTH = "evidence_strength"
    CLINICAL_ACCURACY = "clinical_accuracy"
    CONTRAINDICATION = "contraindication"
    PROTOCOL_PARAMETER = "protocol_parameter"
    MODALITY_SPECIFICITY = "modality_specificity"
    AUDIENCE_TONE = "audience_tone"
    VISUAL_CHANGE = "visual_change"
    TABLE_CHANGE = "table_change"
    FORMATTING = "formatting"
    GOVERNANCE = "governance"
    MISSING_CONTENT = "missing_content"
    AMBIGUITY = "ambiguity"
    STYLE = "style"
    APPROVAL_NOTE = "approval_note"
    REJECTION_NOTE = "rejection_note"
    GENERAL = "general"


class ChangeTarget(str, Enum):
    SECTION_OVERRIDE = "section_override"  # One-document fix
    BLUEPRINT_PATCH = "blueprint_patch"  # Document-type fix
    KNOWLEDGE_PATCH = "knowledge_patch"  # Condition knowledge fix
    RENDERING_PATCH = "rendering_patch"  # Formatting/style fix
    SHARED_RULE_PATCH = "shared_rule_patch"  # Governance/safety fix
    VISUAL_PATCH = "visual_patch"  # Visual placement/type fix
    BLOCKED = "blocked"  # Cannot be applied safely


class ChangeStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    APPLIED = "applied"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class CommentSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


# ── Review Comment ─────────────────────────────────────────────────────────


class ReviewComment(BaseModel):
    """A single reviewer comment or annotation on a generated document."""

    comment_id: str = Field(default_factory=lambda: _uid("rc-"))
    document_id: str = ""  # build_id of the document being reviewed
    reviewer_id: str = ""
    reviewer_name: str = ""
    created_at: str = Field(default_factory=_now)

    # Content
    raw_text: str
    target_section_slug: str = ""  # If reviewer specified a section
    target_text_excerpt: str = ""  # Quote from the document

    # Classification (populated by parser)
    category: CommentCategory = CommentCategory.GENERAL
    severity: CommentSeverity = CommentSeverity.SUGGESTION
    parsed: bool = False
    confidence: float = 0.0  # Parser confidence 0-1

    # Status
    status: str = "pending"  # pending, mapped, applied, blocked, deferred


class ReviewCommentSet(BaseModel):
    """A collection of review comments for one document."""

    document_id: str
    condition_slug: str = ""
    blueprint_slug: str = ""
    tier: str = ""
    reviewer_name: str = ""
    comments: list[ReviewComment] = Field(default_factory=list)
    created_at: str = Field(default_factory=_now)

    def add(self, raw_text: str, section: str = "", severity: str = "suggestion") -> ReviewComment:
        """Add a comment to the set."""
        comment = ReviewComment(
            document_id=self.document_id,
            reviewer_name=self.reviewer_name,
            raw_text=raw_text,
            target_section_slug=section,
            severity=CommentSeverity(severity) if severity in [s.value for s in CommentSeverity] else CommentSeverity.SUGGESTION,
        )
        self.comments.append(comment)
        return comment


# ── Change Request ─────────────────────────────────────────────────────────


class ChangeRequest(BaseModel):
    """A structured change request derived from one or more review comments."""

    change_id: str = Field(default_factory=lambda: _uid("cr-"))
    source_comment_ids: list[str] = Field(default_factory=list)
    document_id: str = ""
    condition_slug: str = ""
    doc_type: str = ""
    tier: str = ""

    # Target
    target_type: ChangeTarget = ChangeTarget.SECTION_OVERRIDE
    target_section: str = ""  # Section slug
    target_field: str = ""  # Knowledge field or blueprint field

    # Change specification
    requested_action: str = ""  # add, remove, update, replace, expand, etc.
    rationale: str = ""
    proposed_resolution: str = ""
    original_comment: str = ""

    # Safety
    confidence: float = 0.5
    requires_manual_approval: bool = False
    evidence_sensitive: bool = False

    # Status
    status: ChangeStatus = ChangeStatus.PROPOSED


# ── Change Plan ────────────────────────────────────────────────────────────


class ChangePlan(BaseModel):
    """A plan for applying review-driven changes to a document."""

    plan_id: str = Field(default_factory=lambda: _uid("plan-"))
    document_id: str = ""
    condition_slug: str = ""
    blueprint_slug: str = ""
    tier: str = ""
    created_at: str = Field(default_factory=_now)

    # Changes
    changes: list[ChangeRequest] = Field(default_factory=list)

    # Impact analysis
    impacted_sections: list[str] = Field(default_factory=list)
    requires_regeneration: bool = True
    requires_evidence_review: bool = False
    requires_clinical_review: bool = False
    safe_to_auto_apply: bool = False

    # Warnings
    warnings: list[str] = Field(default_factory=list)
    blocked_changes: list[ChangeRequest] = Field(default_factory=list)

    @property
    def total_changes(self) -> int:
        return len(self.changes)

    @property
    def applicable_changes(self) -> list[ChangeRequest]:
        return [c for c in self.changes if c.status != ChangeStatus.BLOCKED]

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_changes) + sum(1 for c in self.changes if c.status == ChangeStatus.BLOCKED)

    def to_text(self) -> str:
        lines = [
            f"=== CHANGE PLAN: {self.plan_id} ===",
            f"Document: {self.condition_slug}/{self.blueprint_slug}/{self.tier}",
            f"Changes: {self.total_changes} proposed, {self.blocked_count} blocked",
            f"Impacted sections: {', '.join(self.impacted_sections) or 'none'}",
            f"Requires regeneration: {self.requires_regeneration}",
            f"Requires evidence review: {self.requires_evidence_review}",
            f"Safe to auto-apply: {self.safe_to_auto_apply}",
            "",
        ]
        for c in self.changes:
            ev = " [EVIDENCE-SENSITIVE]" if c.evidence_sensitive else ""
            manual = " [NEEDS APPROVAL]" if c.requires_manual_approval else ""
            lines.append(
                f"  [{c.status.value}] {c.change_id}: {c.requested_action} "
                f"→ {c.target_type.value}:{c.target_section}{ev}{manual}"
            )
            lines.append(f"    Comment: {c.original_comment[:80]}")
            if c.proposed_resolution:
                lines.append(f"    Resolution: {c.proposed_resolution[:80]}")

        if self.blocked_changes:
            lines.append(f"\nBLOCKED ({len(self.blocked_changes)}):")
            for b in self.blocked_changes:
                lines.append(f"  ! {b.original_comment[:60]}: {b.rationale}")

        if self.warnings:
            lines.append(f"\nWARNINGS:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        return "\n".join(lines)


# ── Regeneration Result ────────────────────────────────────────────────────


class RegenerationResult(BaseModel):
    """Result of a review-driven document regeneration."""

    result_id: str = Field(default_factory=lambda: _uid("regen-"))
    plan_id: str = ""
    old_document_id: str = ""
    new_document_id: str = ""
    condition_slug: str = ""
    blueprint_slug: str = ""
    tier: str = ""
    created_at: str = Field(default_factory=_now)

    # Changes applied
    applied_changes: list[str] = Field(default_factory=list)  # change_ids
    blocked_changes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    # Comparison
    readiness_before: str = ""
    readiness_after: str = ""
    sections_changed: list[str] = Field(default_factory=list)
    sections_added: list[str] = Field(default_factory=list)
    sections_removed: list[str] = Field(default_factory=list)
    pmids_before: int = 0
    pmids_after: int = 0

    # Output
    output_path: str = ""
    provenance_path: str = ""
    review_record_path: str = ""
    success: bool = False
    error: str = ""

    def to_text(self) -> str:
        lines = [
            f"=== REGENERATION RESULT: {self.result_id} ===",
            f"Plan: {self.plan_id}",
            f"Success: {self.success}",
            f"Applied: {len(self.applied_changes)} changes",
            f"Blocked: {len(self.blocked_changes)}",
            f"Readiness: {self.readiness_before} → {self.readiness_after}",
            f"PMIDs: {self.pmids_before} → {self.pmids_after}",
            f"Sections changed: {', '.join(self.sections_changed) or 'none'}",
        ]
        if self.output_path:
            lines.append(f"Output: {self.output_path}")
        if self.error:
            lines.append(f"Error: {self.error}")
        return "\n".join(lines)
