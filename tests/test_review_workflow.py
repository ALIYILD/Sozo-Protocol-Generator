"""Tests for sozo_generator.review.manager — review workflow lifecycle."""
from __future__ import annotations

import pytest

from sozo_generator.core.enums import ReviewStatus
from sozo_generator.review.manager import ReviewManager
from sozo_generator.schemas.contracts import ReviewState


class TestReviewManager:
    def test_create_review_draft(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        state = mgr.create_review(
            build_id="build-test-001",
            condition_slug="parkinsons",
            document_type="clinical_exam",
            tier="fellow",
        )
        assert isinstance(state, ReviewState)
        assert state.status == ReviewStatus.DRAFT
        assert state.build_id == "build-test-001"
        assert state.condition_slug == "parkinsons"

    def test_submit_for_review(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b1",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        state = mgr.submit_for_review("b1")
        assert state.status == ReviewStatus.NEEDS_REVIEW
        assert len(state.decisions) == 1

    def test_approve(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b2",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        mgr.submit_for_review("b2")
        state = mgr.approve("b2", reviewer="dr_smith", reason="Looks good")
        assert state.status == ReviewStatus.APPROVED
        assert len(state.decisions) == 2  # submit + approve
        assert state.decisions[-1].reviewer == "dr_smith"

    def test_reject(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b3",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        mgr.submit_for_review("b3")
        state = mgr.reject("b3", reviewer="dr_jones", reason="Missing safety data")
        assert state.status == ReviewStatus.REJECTED
        assert len(state.decisions) == 2

    def test_invalid_transition_draft_to_approved_raises(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b4",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        with pytest.raises(ValueError, match="Invalid transition"):
            mgr.approve("b4", reviewer="dr_smith")

    def test_invalid_transition_approved_to_draft_raises(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b5",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        mgr.submit_for_review("b5")
        mgr.approve("b5", reviewer="dr_smith")
        # APPROVED cannot go to DRAFT (only to EXPORTED or NEEDS_REVIEW)
        with pytest.raises(ValueError):
            state = mgr.get_review("b5")
            state.transition(ReviewStatus.DRAFT, reviewer="system")

    def test_nonexistent_build_raises(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        with pytest.raises(FileNotFoundError):
            mgr.submit_for_review("nonexistent")

    def test_add_section_comment(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b6",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        state = mgr.add_section_comment(
            build_id="b6",
            section_id="safety",
            reviewer="dr_smith",
            text="Please clarify contraindications.",
        )
        assert "safety" in state.section_notes
        assert len(state.section_notes["safety"]) == 1
        assert state.section_notes["safety"][0].reviewer == "dr_smith"
        assert "clarify" in state.section_notes["safety"][0].text

    def test_add_multiple_comments(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review(
            build_id="b7",
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        mgr.add_section_comment("b7", "safety", "alice", "Comment 1")
        state = mgr.add_section_comment("b7", "safety", "bob", "Comment 2")
        assert len(state.section_notes["safety"]) == 2

    def test_list_pending(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        # Create several reviews in different states
        mgr.create_review("b1", "a", "clinical_exam", "fellow")
        mgr.create_review("b2", "b", "clinical_exam", "fellow")
        mgr.create_review("b3", "c", "clinical_exam", "fellow")

        mgr.submit_for_review("b1")
        mgr.submit_for_review("b2")
        # b3 stays in DRAFT

        pending = mgr.list_pending()
        assert len(pending) == 2
        pending_ids = {p.build_id for p in pending}
        assert "b1" in pending_ids
        assert "b2" in pending_ids
        assert "b3" not in pending_ids

    def test_persistence_roundtrip(self, tmp_path):
        reviews_dir = tmp_path / "reviews"
        mgr1 = ReviewManager(reviews_dir)
        mgr1.create_review("b1", "test", "clinical_exam", "fellow")
        mgr1.submit_for_review("b1")
        mgr1.add_section_comment("b1", "overview", "alice", "Needs work")

        # Create a new manager pointing at the same directory
        mgr2 = ReviewManager(reviews_dir)
        state = mgr2.get_review("b1")
        assert state is not None
        assert state.status == ReviewStatus.NEEDS_REVIEW
        assert "overview" in state.section_notes
        assert len(state.section_notes["overview"]) == 1

    def test_list_all(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("b1", "alpha", "clinical_exam", "fellow")
        mgr.create_review("b2", "beta", "clinical_exam", "fellow")
        mgr.create_review("b3", "alpha", "handbook", "partners")

        all_reviews = mgr.list_all()
        assert len(all_reviews) == 3

        alpha_reviews = mgr.list_all(condition_slug="alpha")
        assert len(alpha_reviews) == 2

    def test_get_review_nonexistent_returns_none(self, tmp_path):
        mgr = ReviewManager(tmp_path / "reviews")
        assert mgr.get_review("nope") is None

    def test_full_lifecycle(self, tmp_path):
        """DRAFT -> NEEDS_REVIEW -> REJECTED -> NEEDS_REVIEW -> APPROVED -> EXPORTED."""
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("lifecycle", "test", "clinical_exam", "fellow")

        mgr.submit_for_review("lifecycle")
        state = mgr.reject("lifecycle", "alice", "Missing data")
        assert state.status == ReviewStatus.REJECTED

        # Re-submit
        state = mgr.get_review("lifecycle")
        state.transition(ReviewStatus.NEEDS_REVIEW, reviewer="system", reason="Re-submitted")
        # Save manually since we used the model directly
        mgr._save(state)

        state = mgr.approve("lifecycle", "bob", "All good now")
        assert state.status == ReviewStatus.APPROVED

        state = mgr.mark_exported("lifecycle")
        assert state.status == ReviewStatus.EXPORTED
        assert len(state.decisions) == 5  # submit, reject, resubmit, approve, export
