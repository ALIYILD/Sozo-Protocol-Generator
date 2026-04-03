"""
Release Governance — controls document finalization and release eligibility.

Enforces structured rules before a document can be marked as finalized/released:
- Readiness must be acceptable
- No blocking QA issues
- Required review state must be approved
- Evidence-critical sections must meet minimums
- Placeholders within policy
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .assembler import AssemblyProvenance
from .review import ReviewState

logger = logging.getLogger(__name__)


@dataclass
class ReleaseGateResult:
    """Result of release eligibility check."""

    eligible: bool = False
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    status: str = "blocked"  # eligible, blocked, conditional

    def to_text(self) -> str:
        lines = [f"Release Status: {self.status.upper()}"]
        if self.blockers:
            lines.append(f"\nBLOCKERS ({len(self.blockers)}):")
            for b in self.blockers:
                lines.append(f"  ! {b}")
        if self.warnings:
            lines.append(f"\nWARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"  - {w}")
        if self.eligible:
            lines.append("\nDocument is ELIGIBLE for release.")
        return "\n".join(lines)


@dataclass
class ReleasePolicy:
    """Configurable release policy rules."""

    require_approval: bool = True
    require_ready_or_review: bool = True  # readiness must be "ready" or "review_required" (not "incomplete")
    max_placeholders: int = 0  # 0 = no placeholders allowed
    max_failing_sections: int = 0
    require_min_pmids: int = 1  # At least 1 PMID somewhere in the document
    require_no_critical_qa_failures: bool = True
    allow_conditional_release: bool = True  # Allow release with warnings if no blockers


def check_release_eligibility(
    provenance: AssemblyProvenance,
    review_state: Optional[ReviewState] = None,
    policy: Optional[ReleasePolicy] = None,
) -> ReleaseGateResult:
    """Check whether a document meets release requirements.

    Args:
        provenance: Assembly provenance from canonical generation
        review_state: Current review state (optional)
        policy: Release policy rules (uses default if None)

    Returns:
        ReleaseGateResult with eligibility status and blockers/warnings
    """
    p = policy or ReleasePolicy()
    result = ReleaseGateResult()

    # 1. Readiness check
    if p.require_ready_or_review:
        if provenance.readiness == "incomplete":
            result.blockers.append(
                f"Document readiness is 'incomplete' — {provenance.sections_failing} sections failed QA"
            )
        elif provenance.readiness == "review_required":
            result.warnings.append(
                f"Document readiness is 'review_required' — {provenance.sections_warning} sections have warnings"
            )

    # 2. Placeholder check
    if provenance.placeholder_sections > p.max_placeholders:
        result.blockers.append(
            f"Document has {provenance.placeholder_sections} placeholder sections "
            f"(policy allows {p.max_placeholders})"
        )

    # 3. QA failure check
    if p.require_no_critical_qa_failures and provenance.sections_failing > p.max_failing_sections:
        result.blockers.append(
            f"{provenance.sections_failing} sections have failing QA status"
        )

    # 4. Evidence check
    if provenance.total_evidence_pmids < p.require_min_pmids:
        result.blockers.append(
            f"Document has {provenance.total_evidence_pmids} PMIDs "
            f"(minimum required: {p.require_min_pmids})"
        )

    # 5. Review state check
    if p.require_approval:
        if review_state is None:
            result.blockers.append("No review state — document has not been reviewed")
        elif review_state.status != "approved":
            result.blockers.append(
                f"Review status is '{review_state.status}' — must be 'approved' for release"
            )

    # Determine final eligibility
    if not result.blockers:
        result.eligible = True
        result.status = "eligible" if not result.warnings else "conditional"
    else:
        result.eligible = False
        result.status = "blocked"

    return result


def generate_signoff_report(
    results: list[dict],
    title: str = "Batch Signoff Report",
) -> str:
    """Generate a reviewer-facing signoff report from batch results.

    Args:
        results: List of dicts with keys: condition, blueprint, tier, readiness, success, etc.
        title: Report title

    Returns:
        Formatted text report
    """
    lines = [f"=== {title} ===", ""]

    # Summary
    total = len(results)
    ready = sum(1 for r in results if r.get("readiness") == "ready")
    review_req = sum(1 for r in results if r.get("readiness") == "review_required")
    incomplete = sum(1 for r in results if r.get("readiness") == "incomplete")
    failed = sum(1 for r in results if not r.get("success", True))

    lines.append(f"Total: {total} documents")
    lines.append(f"  Ready for release: {ready}")
    lines.append(f"  Needs review: {review_req}")
    lines.append(f"  Incomplete: {incomplete}")
    lines.append(f"  Failed: {failed}")
    lines.append("")

    # By condition
    conditions = sorted(set(r.get("condition", "") for r in results))
    lines.append("BY CONDITION:")
    for cond in conditions:
        cond_results = [r for r in results if r.get("condition") == cond]
        cond_ready = sum(1 for r in cond_results if r.get("readiness") == "ready")
        cond_total = len(cond_results)
        status = "READY" if cond_ready == cond_total else f"{cond_ready}/{cond_total} ready"
        lines.append(f"  {cond}: {status}")

    # Blockers
    blockers = [r for r in results if r.get("readiness") == "incomplete" or not r.get("success")]
    if blockers:
        lines.append("")
        lines.append(f"BLOCKERS ({len(blockers)}):")
        for b in blockers:
            lines.append(f"  ! {b.get('condition')}/{b.get('blueprint')}: {b.get('error', 'incomplete')}")

    return "\n".join(lines)
