"""Review workflow manager -- tracks review lifecycle for generated documents.

Provides persistence and state-transition logic for the review process.
Each build output gets a ReviewState that progresses through:
DRAFT -> NEEDS_REVIEW -> APPROVED -> EXPORTED (or REJECTED -> back to NEEDS_REVIEW).
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..core.enums import ReviewStatus
from ..schemas.contracts import ReviewComment, ReviewDecision, ReviewState

logger = logging.getLogger(__name__)


class ReviewManager:
    """Manages review state persistence and transitions.

    Each review state is stored as a JSON file under ``reviews_dir/{build_id}.json``.
    All state changes go through :py:meth:`ReviewState.transition` to enforce
    valid status transitions with a full audit trail.
    """

    def __init__(self, reviews_dir: Path) -> None:
        self.reviews_dir = Path(reviews_dir)
        self.reviews_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ReviewManager initialised with reviews_dir=%s", self.reviews_dir)

    # ── Creation ────────────────────────────────────────────────────────

    def create_review(
        self,
        build_id: str,
        condition_slug: str,
        document_type: str,
        tier: str,
        qa_report_id: Optional[str] = None,
        evidence_snapshot_id: Optional[str] = None,
    ) -> ReviewState:
        """Create a new review in DRAFT status and persist it.

        Parameters
        ----------
        build_id:
            Unique identifier for the build output being reviewed.
        condition_slug:
            Slug for the condition (e.g. ``"depression"``).
        document_type:
            Document type string (e.g. ``"clinical_exam"``).
        tier:
            Tier string (e.g. ``"fellow"`` or ``"partners"``).
        qa_report_id:
            Optional QA report identifier linked to this review.
        evidence_snapshot_id:
            Optional evidence snapshot identifier linked to this review.

        Returns
        -------
        ReviewState
            The newly created review state in DRAFT status.
        """
        review_id = f"rev-{condition_slug}-{document_type}-{tier}"
        state = ReviewState(
            build_id=build_id,
            condition_slug=condition_slug,
            document_type=document_type,
            tier=tier,
            status=ReviewStatus.DRAFT,
            qa_report_id=qa_report_id,
            evidence_snapshot_id=evidence_snapshot_id,
            version="1.0",
        )
        self._save(state)
        logger.info(
            "Created review %s for build %s (condition=%s, doc=%s, tier=%s)",
            review_id,
            build_id,
            condition_slug,
            document_type,
            tier,
        )
        return state

    # ── Retrieval ───────────────────────────────────────────────────────

    def get_review(self, build_id: str) -> Optional[ReviewState]:
        """Load a review state by build ID, or return ``None`` if not found."""
        state = self._load(build_id)
        if state is None:
            logger.debug("No review found for build_id=%s", build_id)
        return state

    # ── Transitions ─────────────────────────────────────────────────────

    def submit_for_review(self, build_id: str) -> ReviewState:
        """Transition a review from DRAFT to NEEDS_REVIEW.

        Raises
        ------
        FileNotFoundError
            If the review does not exist.
        ValueError
            If the transition is not valid from the current status.
        """
        state = self._load_or_raise(build_id)
        state.transition(ReviewStatus.NEEDS_REVIEW, reviewer="system", reason="Submitted for review")
        self._save(state)
        logger.info("Review %s submitted for review (DRAFT -> NEEDS_REVIEW)", build_id)
        return state

    def approve(self, build_id: str, reviewer: str, reason: str = "") -> ReviewState:
        """Approve a review (NEEDS_REVIEW -> APPROVED).

        Parameters
        ----------
        build_id:
            Build identifier.
        reviewer:
            Name or identifier of the reviewer approving.
        reason:
            Optional reason or notes for the approval.

        Raises
        ------
        FileNotFoundError
            If the review does not exist.
        ValueError
            If the transition is not valid from the current status.
        """
        state = self._load_or_raise(build_id)
        state.transition(ReviewStatus.APPROVED, reviewer=reviewer, reason=reason)
        self._save(state)
        logger.info("Review %s approved by %s", build_id, reviewer)
        return state

    def reject(self, build_id: str, reviewer: str, reason: str = "") -> ReviewState:
        """Reject a review (NEEDS_REVIEW -> REJECTED).

        Parameters
        ----------
        build_id:
            Build identifier.
        reviewer:
            Name or identifier of the reviewer rejecting.
        reason:
            Reason for rejection.

        Raises
        ------
        FileNotFoundError
            If the review does not exist.
        ValueError
            If the transition is not valid from the current status.
        """
        state = self._load_or_raise(build_id)
        state.transition(ReviewStatus.REJECTED, reviewer=reviewer, reason=reason)
        self._save(state)
        logger.info("Review %s rejected by %s: %s", build_id, reviewer, reason)
        return state

    def mark_exported(self, build_id: str, reviewer: str = "system") -> ReviewState:
        """Mark a review as exported (APPROVED -> EXPORTED).

        Raises
        ------
        FileNotFoundError
            If the review does not exist.
        ValueError
            If the transition is not valid from the current status.
        """
        state = self._load_or_raise(build_id)
        state.transition(ReviewStatus.EXPORTED, reviewer=reviewer, reason="Exported to DOCX")
        self._save(state)
        logger.info("Review %s marked as exported", build_id)
        return state

    # ── Auto-assignment ──────────────────────────────────────────────────

    def auto_assign_review_state(
        self,
        condition_slug: str,
        confidence_label: str,
        qa_report: object,  # expects .block_count attribute (QAReport)
    ) -> ReviewStatus:
        """Determine the initial review status based on QA and confidence.

        Returns
        -------
        ReviewStatus
            NEEDS_REVIEW if any red-flag conditions are met, otherwise DRAFT.
        """
        # QA blocks present
        block_count = getattr(qa_report, "block_count", 0)
        if block_count and block_count > 0:
            return ReviewStatus.NEEDS_REVIEW

        # Low or insufficient confidence
        if confidence_label in ("insufficient", "low_confidence"):
            return ReviewStatus.NEEDS_REVIEW

        # Known lower-evidence conditions
        if condition_slug in ("long_covid", "asd"):
            return ReviewStatus.NEEDS_REVIEW

        return ReviewStatus.DRAFT

    # ── Flagging ───────────────────────────────────────────────────────

    def add_flag(
        self,
        build_id: str,
        flag_reason: str,
        flagged_by: str,
    ) -> ReviewState:
        """Flag a document for further attention.

        Transitions the review to FLAGGED status (any state except EXPORTED).

        Parameters
        ----------
        build_id:
            Build identifier.
        flag_reason:
            Free-text reason the document is being flagged.
        flagged_by:
            Name or identifier of the person/system flagging the document.

        Raises
        ------
        FileNotFoundError
            If the review does not exist.
        ValueError
            If the transition is not valid from the current status.
        """
        state = self._load_or_raise(build_id)
        state.transition(ReviewStatus.FLAGGED, reviewer=flagged_by, reason=flag_reason)
        self._save(state)
        logger.info("Review %s flagged by %s: %s", build_id, flagged_by, flag_reason)
        return state

    def list_flagged(self) -> list[ReviewState]:
        """Return all reviews currently in FLAGGED status."""
        return [
            state
            for state in self._load_all()
            if state.status == ReviewStatus.FLAGGED
        ]

    # ── Comments ────────────────────────────────────────────────────────

    def add_section_comment(
        self,
        build_id: str,
        section_id: str,
        reviewer: str,
        text: str,
    ) -> ReviewState:
        """Add a reviewer comment on a specific document section.

        Parameters
        ----------
        build_id:
            Build identifier.
        section_id:
            The section within the document being commented on.
        reviewer:
            Name or identifier of the commenter.
        text:
            Comment text.

        Returns
        -------
        ReviewState
            Updated review state with the comment appended.
        """
        state = self._load_or_raise(build_id)
        comment = ReviewComment(
            comment_id=f"cmt-{_now_compact()}-{section_id[:8]}",
            reviewer=reviewer,
            section_id=section_id,
            text=text,
        )
        if section_id not in state.section_notes:
            state.section_notes[section_id] = []
        state.section_notes[section_id].append(comment)
        state.updated_at = _now_iso()
        self._save(state)
        logger.info(
            "Comment added to %s section '%s' by %s",
            build_id,
            section_id,
            reviewer,
        )
        return state

    # ── Listing ─────────────────────────────────────────────────────────

    def list_pending(self) -> list[ReviewState]:
        """Return all reviews currently in NEEDS_REVIEW status."""
        return [
            state
            for state in self._load_all()
            if state.status == ReviewStatus.NEEDS_REVIEW
        ]

    def list_all(self, condition_slug: Optional[str] = None) -> list[ReviewState]:
        """Return all reviews, optionally filtered by condition slug.

        Parameters
        ----------
        condition_slug:
            If provided, only return reviews for this condition.
        """
        states = self._load_all()
        if condition_slug is not None:
            states = [s for s in states if s.condition_slug == condition_slug]
        return states

    # ── Approval workflow ───────────────────────────────────────────────

    def list_by_status(self, status: str) -> list[ReviewState]:
        """List all reviews with a specific status."""
        target = ReviewStatus(status)
        return [s for s in self._load_all() if s.status == target]

    def list_approved(self) -> list[ReviewState]:
        """List all approved reviews."""
        return [
            s for s in self._load_all()
            if s.status == ReviewStatus.APPROVED
        ]

    def export_approved_only(self, output_dir: Path) -> list[Path]:
        """Copy approved document files to output_dir. Returns list of copied paths.

        Only exports documents whose review state is APPROVED or EXPORTED.
        After a successful copy the review state transitions to EXPORTED.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        copied: list[Path] = []

        for state in self._load_all():
            if state.status not in (ReviewStatus.APPROVED, ReviewStatus.EXPORTED):
                continue

            # Look up document path from the state's metadata dict
            metadata = getattr(state, "metadata", None) or {}
            doc_path_str = metadata.get("document_path", "") if isinstance(metadata, dict) else ""
            if not doc_path_str:
                logger.warning(
                    "No document_path in metadata for build %s — skipping export",
                    state.build_id,
                )
                continue

            src = Path(doc_path_str)
            if not src.exists():
                logger.warning(
                    "Document file does not exist for build %s: %s",
                    state.build_id,
                    src,
                )
                continue

            dest = output_dir / src.name
            shutil.copy2(src, dest)
            copied.append(dest)
            logger.info("Exported %s -> %s", src, dest)

            # Transition to EXPORTED if not already
            if state.status == ReviewStatus.APPROVED:
                state.transition(
                    ReviewStatus.EXPORTED, reviewer="system", reason="Exported to output directory"
                )
                self._save(state)

        return copied

    def get_review_queue(self) -> dict[str, list[ReviewState]]:
        """Return reviews grouped by status: {status: [reviews]}."""
        queue: dict[str, list[ReviewState]] = {}
        for state in self._load_all():
            key = state.status.value
            queue.setdefault(key, []).append(state)
        return queue

    def reject_with_revision(
        self,
        build_id: str,
        reviewer: str,
        reason: str,
        revision_notes: list[str] | None = None,
    ) -> ReviewState:
        """Reject and add revision notes for what needs to change.

        Parameters
        ----------
        build_id:
            Build identifier.
        reviewer:
            Name or identifier of the reviewer rejecting.
        reason:
            High-level reason for rejection.
        revision_notes:
            Specific items that need to change before re-submission.

        Raises
        ------
        FileNotFoundError
            If the review does not exist.
        ValueError
            If the transition is not valid from the current status.
        """
        state = self._load_or_raise(build_id)

        # Build combined reason with revision notes
        full_reason = reason
        if revision_notes:
            notes_str = "; ".join(revision_notes)
            full_reason = f"{reason} | Revision notes: {notes_str}"

        state.transition(ReviewStatus.REJECTED, reviewer=reviewer, reason=full_reason)

        # Store revision notes as section comments for traceability
        if revision_notes:
            for idx, note in enumerate(revision_notes):
                comment = ReviewComment(
                    comment_id=f"rev-{_now_compact()}-{idx}",
                    reviewer=reviewer,
                    section_id="revision_notes",
                    text=note,
                )
                if "revision_notes" not in state.section_notes:
                    state.section_notes["revision_notes"] = []
                state.section_notes["revision_notes"].append(comment)

        self._save(state)
        logger.info(
            "Review %s rejected with revision by %s: %s (notes: %d)",
            build_id,
            reviewer,
            reason,
            len(revision_notes or []),
        )
        return state

    # ── Persistence internals ───────────────────────────────────────────

    def _save(self, state: ReviewState) -> Path:
        """Serialise a ReviewState to JSON on disk."""
        path = self._review_path(state.build_id)
        path.write_text(
            json.dumps(state.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )
        logger.debug("Saved review state to %s", path)
        return path

    def _load(self, build_id: str) -> Optional[ReviewState]:
        """Load a ReviewState from JSON, or return ``None`` if missing."""
        path = self._review_path(build_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return ReviewState.model_validate(data)
        except (json.JSONDecodeError, Exception) as exc:
            logger.error("Failed to load review state from %s: %s", path, exc)
            return None

    def _load_or_raise(self, build_id: str) -> ReviewState:
        """Load a ReviewState or raise ``FileNotFoundError``."""
        state = self._load(build_id)
        if state is None:
            raise FileNotFoundError(
                f"No review state found for build_id='{build_id}' "
                f"in {self.reviews_dir}"
            )
        return state

    def _load_all(self) -> list[ReviewState]:
        """Load every ReviewState JSON file in the reviews directory."""
        states: list[ReviewState] = []
        for path in sorted(self.reviews_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                states.append(ReviewState.model_validate(data))
            except (json.JSONDecodeError, Exception) as exc:
                logger.warning("Skipping invalid review file %s: %s", path, exc)
        return states

    def _review_path(self, build_id: str) -> Path:
        """Return the filesystem path for a review's JSON file."""
        safe_id = build_id.replace("/", "_").replace("\\", "_")
        return self.reviews_dir / f"{safe_id}.json"


# ── Module-level helpers ────────────────────────────────────────────────


def _now_iso() -> str:
    """Return current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_compact() -> str:
    """Return current UTC time as a compact string for IDs."""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
