"""
Review and Approval Workflow for Canonical Generation.

Provides structured review state management on top of provenance/readiness
metadata from the canonical assembler.

States:
    draft → review_required → approved / rejected → finalized

Usage:
    from sozo_generator.knowledge.review import ReviewState, ReviewSummary

    state = ReviewState.from_provenance(provenance)
    summary = state.summary()
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .assembler import AssemblyProvenance

logger = logging.getLogger(__name__)


@dataclass
class ReviewDecision:
    """A single review decision."""
    reviewer: str
    action: str  # "approve", "reject", "request_changes"
    reason: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class ReviewSummary:
    """Human-readable summary of document quality for review."""

    readiness: str  # ready, review_required, incomplete
    condition: str
    blueprint: str
    tier: str

    # Counts
    total_sections: int = 0
    sections_passing: int = 0
    sections_warning: int = 0
    sections_failing: int = 0
    placeholder_count: int = 0

    # Evidence
    total_pmids: int = 0
    evidence_gaps: list[str] = field(default_factory=list)

    # Visuals
    visuals_requested: int = 0
    visuals_unfulfilled: int = 0

    # Top issues by severity
    critical_issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Recommendation
    recommendation: str = ""

    def to_text(self) -> str:
        """Format as readable text for CLI or review tools."""
        lines = [
            f"=== REVIEW SUMMARY ===",
            f"Condition: {self.condition}",
            f"Blueprint: {self.blueprint} ({self.tier})",
            f"Readiness: {self.readiness.upper()}",
            f"",
            f"Sections: {self.sections_passing} pass, {self.sections_warning} warn, "
            f"{self.sections_failing} fail ({self.total_sections} total)",
            f"Placeholders: {self.placeholder_count}",
            f"Evidence: {self.total_pmids} PMIDs",
            f"Visuals: {self.visuals_requested} requested, {self.visuals_unfulfilled} unfulfilled",
        ]

        if self.critical_issues:
            lines.append(f"\nCRITICAL ISSUES ({len(self.critical_issues)}):")
            for issue in self.critical_issues:
                lines.append(f"  ! {issue}")

        if self.warnings:
            lines.append(f"\nWARNINGS ({len(self.warnings)}):")
            for w in self.warnings[:10]:
                lines.append(f"  - {w}")
            if len(self.warnings) > 10:
                lines.append(f"  ... and {len(self.warnings) - 10} more")

        if self.evidence_gaps:
            lines.append(f"\nEVIDENCE GAPS ({len(self.evidence_gaps)}):")
            for gap in self.evidence_gaps:
                lines.append(f"  ? {gap}")

        lines.append(f"\nRECOMMENDATION: {self.recommendation}")
        return "\n".join(lines)


@dataclass
class ReviewState:
    """Review state for a generated document."""

    build_id: str
    condition: str
    blueprint: str
    tier: str
    status: str = "draft"  # draft, review_required, approved, rejected, finalized
    readiness: str = "incomplete"
    decisions: list[ReviewDecision] = field(default_factory=list)
    summary: Optional[ReviewSummary] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    @classmethod
    def from_provenance(cls, provenance: AssemblyProvenance, build_id: str = "") -> "ReviewState":
        """Create a ReviewState from assembly provenance."""
        # Determine initial status from readiness
        if provenance.readiness == "ready":
            status = "draft"  # Ready for review
        elif provenance.readiness == "review_required":
            status = "review_required"
        else:
            status = "review_required"  # Incomplete also needs review

        state = cls(
            build_id=build_id or f"review-{provenance.condition_slug}",
            condition=provenance.condition_slug,
            blueprint=provenance.blueprint_slug,
            tier=provenance.tier,
            status=status,
            readiness=provenance.readiness,
        )

        # Build summary
        state.summary = build_review_summary(provenance)
        return state

    def approve(self, reviewer: str, reason: str = "") -> None:
        """Approve the document for release."""
        if self.readiness == "incomplete":
            raise ValueError("Cannot approve an incomplete document — resolve failures first")
        self.decisions.append(ReviewDecision(reviewer=reviewer, action="approve", reason=reason))
        self.status = "approved"
        self.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def reject(self, reviewer: str, reason: str) -> None:
        """Reject the document with reason."""
        self.decisions.append(ReviewDecision(reviewer=reviewer, action="reject", reason=reason))
        self.status = "rejected"
        self.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def finalize(self, reviewer: str) -> None:
        """Finalize an approved document."""
        if self.status != "approved":
            raise ValueError(f"Cannot finalize — status is {self.status}, not approved")
        self.decisions.append(ReviewDecision(reviewer=reviewer, action="finalize"))
        self.status = "finalized"
        self.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> dict:
        return {
            "build_id": self.build_id,
            "condition": self.condition,
            "blueprint": self.blueprint,
            "tier": self.tier,
            "status": self.status,
            "readiness": self.readiness,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "decisions": [
                {"reviewer": d.reviewer, "action": d.action, "reason": d.reason, "timestamp": d.timestamp}
                for d in self.decisions
            ],
            "summary": self.summary.to_text() if self.summary else None,
        }


def build_review_summary(provenance: AssemblyProvenance) -> ReviewSummary:
    """Build a reviewer-facing summary from assembly provenance."""

    critical_issues = []
    warnings = []
    evidence_gaps = []

    for s in provenance.sections:
        if s.qa_status == "fail":
            critical_issues.append(f"Section '{s.section_slug}' FAILED QA")
        if s.is_placeholder:
            warnings.append(f"Section '{s.section_slug}' is a placeholder")
        if not s.evidence_sufficient:
            evidence_gaps.append(
                f"Section '{s.section_slug}': needs {s.min_pmid_required} PMIDs, has {s.actual_pmid_count}"
            )
        for w in s.warnings:
            warnings.append(w)

    visuals_unfulfilled = sum(1 for s in provenance.sections if not s.visual_fulfilled)

    # Recommendation
    if provenance.readiness == "ready" and not critical_issues:
        recommendation = "Document is ready for clinical review and approval."
    elif critical_issues:
        recommendation = f"BLOCKED — {len(critical_issues)} critical issues must be resolved before review."
    elif provenance.placeholder_sections > 0:
        recommendation = f"Needs attention — {provenance.placeholder_sections} placeholder sections require clinical input."
    else:
        recommendation = "Document is mostly complete but has warnings that should be reviewed."

    return ReviewSummary(
        readiness=provenance.readiness,
        condition=provenance.condition_slug,
        blueprint=provenance.blueprint_slug,
        tier=provenance.tier,
        total_sections=provenance.total_sections,
        sections_passing=provenance.sections_passing,
        sections_warning=provenance.sections_warning,
        sections_failing=provenance.sections_failing,
        placeholder_count=provenance.placeholder_sections,
        total_pmids=provenance.total_evidence_pmids,
        evidence_gaps=evidence_gaps,
        visuals_requested=provenance.total_visuals_requested,
        visuals_unfulfilled=visuals_unfulfilled,
        critical_issues=critical_issues,
        warnings=warnings,
        recommendation=recommendation,
    )
