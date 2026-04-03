"""
Reviewer Disambiguation + Resolution + Traceability.

When DOCX comment mapping is ambiguous, this module provides:
- structured candidate inspection
- manual resolution workflow
- resolution persistence
- end-to-end traceability from Word comment → change → regeneration

Usage:
    from sozo_generator.knowledge.revision.resolution import ResolutionManager

    mgr = ResolutionManager()
    unresolved = mgr.get_unresolved(ingest_result)
    mgr.resolve(comment_id, section_slug="safety", decided_by="Dr. Smith")
    plan = mgr.create_plan_from_resolved(ingest_result, condition, blueprint, tier)
"""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .docx_comments import ExtractedDocxComment, DocxReviewIngestResult, MappingSignal

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ── Resolution Target Kinds ──────────────────────────────────────────────


class TargetKind:
    SECTION = "section"
    DOCUMENT_GENERAL = "document_general"
    VISUAL = "visual"
    TABLE = "table"
    BLOCKED = "blocked"
    DEFER = "defer_for_review"


# ── Mapping Resolution Thresholds ────────────────────────────────────────

HIGH_CONFIDENCE_THRESHOLD = 0.70
MEDIUM_CONFIDENCE_THRESHOLD = 0.40
AUTO_RESOLVE_THRESHOLD = 0.70  # Above this, no manual resolution needed


# ── Models ────────────────────────────────────────────────────────────────


@dataclass
class MappingCandidate:
    """One candidate section for a comment mapping."""
    section_slug: str
    score: float
    confidence: float
    explanation: str = ""
    signals: list[dict] = field(default_factory=list)


@dataclass
class ResolutionDecision:
    """A manual resolution decision for an ambiguous comment."""
    resolution_id: str = ""
    extracted_comment_id: str = ""
    document_id: str = ""
    decided_by: str = ""
    decided_at: str = ""
    target_kind: str = TargetKind.SECTION
    chosen_section: str = ""
    rejected_candidates: list[str] = field(default_factory=list)
    notes: str = ""
    status: str = "resolved"  # resolved, reopened, cancelled

    def __post_init__(self):
        if not self.resolution_id:
            self.resolution_id = _uid("res-")
        if not self.decided_at:
            self.decided_at = _now()

    def to_dict(self) -> dict:
        return {
            "resolution_id": self.resolution_id,
            "extracted_comment_id": self.extracted_comment_id,
            "document_id": self.document_id,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at,
            "target_kind": self.target_kind,
            "chosen_section": self.chosen_section,
            "rejected_candidates": self.rejected_candidates,
            "notes": self.notes,
            "status": self.status,
        }


@dataclass
class CommentTraceRecord:
    """End-to-end traceability from Word comment to regenerated output."""
    trace_id: str = ""
    extracted_comment_id: str = ""
    document_id: str = ""
    original_text: str = ""
    author: str = ""

    # Mapping
    auto_mapped_section: str = ""
    auto_confidence: float = 0.0
    mapping_state: str = ""

    # Resolution
    resolution_id: str = ""
    resolved_section: str = ""
    resolved_by: str = ""
    resolution_type: str = ""

    # Change
    change_request_id: str = ""
    change_plan_id: str = ""

    # Regeneration
    regeneration_id: str = ""
    final_status: str = "pending"  # pending, applied, blocked, deferred

    def __post_init__(self):
        if not self.trace_id:
            self.trace_id = _uid("trace-")

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "extracted_comment_id": self.extracted_comment_id,
            "original_text": self.original_text[:100],
            "author": self.author,
            "auto_mapped_section": self.auto_mapped_section,
            "auto_confidence": self.auto_confidence,
            "mapping_state": self.mapping_state,
            "resolution_id": self.resolution_id,
            "resolved_section": self.resolved_section,
            "resolved_by": self.resolved_by,
            "change_request_id": self.change_request_id,
            "regeneration_id": self.regeneration_id,
            "final_status": self.final_status,
        }


# ── Resolution Manager ───────────────────────────────────────────────────


class ResolutionManager:
    """Manages manual disambiguation and resolution of DOCX comment mappings.

    Tracks which comments need resolution, persists decisions, and feeds
    resolved comments into the change-plan / regeneration pipeline.
    """

    def __init__(self, store_dir: str | Path | None = None):
        self.store_dir = Path(store_dir) if store_dir else Path("outputs/resolutions")
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._resolutions: dict[str, ResolutionDecision] = {}
        self._traces: dict[str, CommentTraceRecord] = {}

    def get_unresolved(self, result: DocxReviewIngestResult) -> list[ExtractedDocxComment]:
        """Get comments that need manual resolution."""
        return [
            c for c in result.comments
            if c.mapping_confidence < AUTO_RESOLVE_THRESHOLD
            and c.comment_id not in self._resolutions
        ]

    def get_auto_resolved(self, result: DocxReviewIngestResult) -> list[ExtractedDocxComment]:
        """Get comments with high enough confidence for auto-resolution."""
        return [
            c for c in result.comments
            if c.mapping_confidence >= AUTO_RESOLVE_THRESHOLD
        ]

    def get_candidates(self, comment: ExtractedDocxComment) -> list[MappingCandidate]:
        """Get ranked candidates for a comment with score breakdowns."""
        candidates = []

        if comment.mapped_section:
            candidates.append(MappingCandidate(
                section_slug=comment.mapped_section,
                score=comment.mapping_confidence * 10,
                confidence=comment.mapping_confidence,
                explanation=comment.mapping_explanation,
                signals=[
                    {"type": s.signal_type, "section": s.section_slug,
                     "score": s.score, "explanation": s.explanation}
                    for s in comment.mapping_signals
                    if s.section_slug == comment.mapped_section
                ],
            ))

        for alt_slug in comment.alternate_sections:
            alt_signals = [
                s for s in comment.mapping_signals if s.section_slug == alt_slug
            ]
            alt_score = sum(s.score for s in alt_signals)
            candidates.append(MappingCandidate(
                section_slug=alt_slug,
                score=alt_score,
                confidence=min(alt_score / 8.0, 0.9),
                explanation="; ".join(s.explanation for s in alt_signals[:2]),
                signals=[
                    {"type": s.signal_type, "section": s.section_slug,
                     "score": s.score, "explanation": s.explanation}
                    for s in alt_signals
                ],
            ))

        # Add non-section options
        candidates.append(MappingCandidate(
            section_slug="(document_general)",
            score=0, confidence=0,
            explanation="Applies to the whole document, not a specific section",
        ))

        return candidates

    def resolve(
        self,
        comment_id: str,
        section_slug: str = "",
        target_kind: str = TargetKind.SECTION,
        decided_by: str = "",
        notes: str = "",
        document_id: str = "",
    ) -> ResolutionDecision:
        """Manually resolve a comment's section mapping."""
        decision = ResolutionDecision(
            extracted_comment_id=comment_id,
            document_id=document_id,
            decided_by=decided_by,
            target_kind=target_kind,
            chosen_section=section_slug,
            notes=notes,
        )
        self._resolutions[comment_id] = decision
        self._save_resolution(decision)
        logger.info(f"Resolved {comment_id} → {target_kind}:{section_slug} by {decided_by}")
        return decision

    def reopen(self, comment_id: str) -> bool:
        """Reopen a previously resolved comment for re-resolution."""
        if comment_id in self._resolutions:
            self._resolutions[comment_id].status = "reopened"
            self._save_resolution(self._resolutions[comment_id])
            return True
        return False

    def get_resolution(self, comment_id: str) -> Optional[ResolutionDecision]:
        """Get the resolution decision for a comment."""
        return self._resolutions.get(comment_id)

    def get_effective_section(self, comment: ExtractedDocxComment) -> tuple[str, str]:
        """Get the effective section for a comment (resolved or auto-mapped).

        Returns (section_slug, source) where source is "auto" or "manual".
        """
        # Manual resolution takes precedence
        resolution = self._resolutions.get(comment.comment_id)
        if resolution and resolution.status == "resolved":
            return resolution.chosen_section, "manual"

        # Auto-resolved if high confidence
        if comment.mapping_confidence >= AUTO_RESOLVE_THRESHOLD:
            return comment.mapped_section, "auto"

        return "", "unresolved"

    def build_trace(
        self,
        comment: ExtractedDocxComment,
        change_request_id: str = "",
        change_plan_id: str = "",
        regeneration_id: str = "",
    ) -> CommentTraceRecord:
        """Build an end-to-end trace record for a comment."""
        resolution = self._resolutions.get(comment.comment_id)
        effective_section, source = self.get_effective_section(comment)

        trace = CommentTraceRecord(
            extracted_comment_id=comment.comment_id,
            document_id=comment.source_docx,
            original_text=comment.text,
            author=comment.author,
            auto_mapped_section=comment.mapped_section,
            auto_confidence=comment.mapping_confidence,
            mapping_state=comment.mapping_state,
            resolution_id=resolution.resolution_id if resolution else "",
            resolved_section=effective_section,
            resolved_by=resolution.decided_by if resolution else ("auto" if source == "auto" else ""),
            resolution_type=source,
            change_request_id=change_request_id,
            change_plan_id=change_plan_id,
            regeneration_id=regeneration_id,
            final_status="applied" if regeneration_id else ("pending" if effective_section else "unresolved"),
        )
        self._traces[comment.comment_id] = trace
        return trace

    def create_resolved_review_set(
        self,
        ingest_result: DocxReviewIngestResult,
        condition_slug: str,
        blueprint_slug: str,
        tier: str,
        require_all_resolved: bool = False,
    ):
        """Create a ReviewCommentSet from resolved comments only.

        Args:
            require_all_resolved: If True, raises ValueError if any comments remain unresolved
        """
        from .models import ReviewCommentSet

        unresolved = self.get_unresolved(ingest_result)
        if require_all_resolved and unresolved:
            unresolved_ids = [c.comment_id for c in unresolved]
            raise ValueError(
                f"{len(unresolved)} comments remain unresolved: {unresolved_ids}. "
                f"Resolve them or use require_all_resolved=False."
            )

        comment_set = ReviewCommentSet(
            document_id=ingest_result.document_id or ingest_result.source_docx,
            condition_slug=condition_slug,
            blueprint_slug=blueprint_slug,
            tier=tier,
            reviewer_name=ingest_result.comments[0].author if ingest_result.comments else "",
        )

        for ec in ingest_result.comments:
            section, source = self.get_effective_section(ec)
            if not section:
                continue  # Skip unresolved

            comment_set.add(
                raw_text=ec.text,
                section=section,
                severity="major" if ec.mapping_confidence > 0.5 or source == "manual" else "suggestion",
            )

        return comment_set

    def summary(self, result: DocxReviewIngestResult) -> str:
        """Produce a reviewer-facing summary of mapping and resolution status."""
        lines = [
            f"=== DOCX REVIEW RESOLUTION STATUS ===",
            f"Total comments: {len(result.comments)}",
        ]

        auto_high = [c for c in result.comments if c.mapping_confidence >= AUTO_RESOLVE_THRESHOLD]
        needs_resolution = self.get_unresolved(result)
        manually_resolved = [
            c for c in result.comments
            if c.comment_id in self._resolutions
            and self._resolutions[c.comment_id].status == "resolved"
        ]

        lines.append(f"  Auto-resolved (high confidence): {len(auto_high)}")
        lines.append(f"  Manually resolved: {len(manually_resolved)}")
        lines.append(f"  Needs resolution: {len(needs_resolution)}")

        if needs_resolution:
            lines.append(f"\nUNRESOLVED ({len(needs_resolution)}):")
            for c in needs_resolution:
                conf = f"{c.mapping_confidence:.0%}"
                sec = c.mapped_section or "(none)"
                lines.append(f"  [{c.comment_id}] {conf} → {sec}: {c.text[:60]}")
                if c.alternate_sections:
                    lines.append(f"    Alternatives: {', '.join(c.alternate_sections[:3])}")

        if manually_resolved:
            lines.append(f"\nMANUALLY RESOLVED ({len(manually_resolved)}):")
            for c in manually_resolved:
                res = self._resolutions[c.comment_id]
                lines.append(
                    f"  [{c.comment_id}] → {res.target_kind}:{res.chosen_section} "
                    f"by {res.decided_by}"
                )

        return "\n".join(lines)

    def save_traces(self, output_path: Path | None = None) -> Path:
        """Save all trace records to JSON."""
        path = output_path or self.store_dir / "traces.json"
        data = [t.to_dict() for t in self._traces.values()]
        path.write_text(json.dumps(data, indent=2))
        return path

    def _save_resolution(self, decision: ResolutionDecision):
        """Persist a resolution decision."""
        path = self.store_dir / f"{decision.resolution_id}.json"
        path.write_text(json.dumps(decision.to_dict(), indent=2))
