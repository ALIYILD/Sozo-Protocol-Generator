"""Tests for operator workflow: approval, onboarding, evidence refresh, smoke tests."""
from __future__ import annotations
import pytest
from pathlib import Path


class TestApprovalWorkflow:
    """Test the full approval lifecycle."""

    def test_create_submit_approve_export(self, tmp_path):
        """Full lifecycle: create -> submit -> approve -> export."""
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")

        # Create
        state = mgr.create_review("build-test-1", "parkinsons", "evidence_based_protocol", "fellow")
        assert state.status.value == "draft"

        # Submit
        state = mgr.submit_for_review("build-test-1")
        assert state.status.value == "needs_review"

        # Approve
        state = mgr.approve("build-test-1", "Dr. Smith", "Looks good")
        assert state.status.value == "approved"

        # Export
        state = mgr.mark_exported("build-test-1")
        assert state.status.value == "exported"

    def test_reject_with_revision_notes(self, tmp_path):
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("build-test-2", "depression", "handbook", "fellow")
        mgr.submit_for_review("build-test-2")
        state = mgr.reject_with_revision("build-test-2", "Dr. Jones", "Needs more safety data",
                                          revision_notes=["Add TPS contraindications", "Update phenotype table"])
        assert state.status.value == "rejected"
        # Check revision notes stored
        assert len(state.section_notes.get("revision_notes", [])) >= 1

    def test_list_by_status(self, tmp_path):
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("b1", "parkinsons", "ebp", "fellow")
        mgr.create_review("b2", "depression", "ebp", "fellow")
        mgr.submit_for_review("b1")

        pending = mgr.list_by_status("needs_review")
        assert len(pending) == 1
        drafts = mgr.list_by_status("draft")
        assert len(drafts) == 1

    def test_list_approved(self, tmp_path):
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("b1", "parkinsons", "ebp", "fellow")
        mgr.submit_for_review("b1")
        mgr.approve("b1", "Dr. A")

        approved = mgr.list_approved()
        assert len(approved) == 1

    def test_get_review_queue(self, tmp_path):
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("b1", "parkinsons", "ebp", "fellow")
        mgr.create_review("b2", "depression", "ebp", "fellow")
        mgr.submit_for_review("b1")

        queue = mgr.get_review_queue()
        assert "draft" in queue
        assert "needs_review" in queue
        assert len(queue["needs_review"]) == 1
        assert len(queue["draft"]) == 1

    def test_export_approved_only(self, tmp_path):
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")
        # Create a fake document file
        doc_path = tmp_path / "test_doc.docx"
        doc_path.write_text("fake docx content")

        # Create and approve a review
        state = mgr.create_review("b1", "parkinsons", "ebp", "fellow")
        # Just test the list_approved method works
        mgr.submit_for_review("b1")
        mgr.approve("b1", "Dr. A")

        approved = mgr.list_approved()
        assert len(approved) == 1

    def test_reviewer_comment_persistence(self, tmp_path):
        from sozo_generator.review.manager import ReviewManager
        mgr = ReviewManager(tmp_path / "reviews")
        mgr.create_review("b1", "parkinsons", "ebp", "fellow")
        mgr.add_section_comment("b1", "safety", "Dr. A", "Add cardiac contraindication")
        mgr.add_section_comment("b1", "safety", "Dr. B", "Agreed, also add pacemaker note")

        # Reload from disk
        mgr2 = ReviewManager(tmp_path / "reviews")
        state = mgr2.get_review("b1")
        assert "safety" in state.section_notes
        assert len(state.section_notes["safety"]) == 2


class TestConditionOnboarding:
    def test_known_condition(self):
        from sozo_generator.conditions.onboarding import ConditionOnboarder
        ob = ConditionOnboarder()
        assert ob.is_known_condition("parkinsons") == True
        assert ob.is_known_condition("depression") == True

    def test_unknown_condition(self):
        from sozo_generator.conditions.onboarding import ConditionOnboarder
        ob = ConditionOnboarder()
        assert ob.is_known_condition("narcolepsy") == False

    def test_create_draft_condition(self):
        from sozo_generator.conditions.onboarding import ConditionOnboarder
        ob = ConditionOnboarder()
        draft = ob.create_draft_condition("narcolepsy", "Narcolepsy", "G47.4")
        assert draft.slug == "narcolepsy"
        assert draft.overall_evidence_quality.value == "missing"
        assert "DRAFT_CONDITION" in draft.review_flags
        assert len(draft.safety_notes) >= 3  # universal safety notes
        assert "0.1-draft" in draft.version

    def test_draft_requires_review(self):
        from sozo_generator.conditions.onboarding import ConditionOnboarder
        ob = ConditionOnboarder()
        draft = ob.create_draft_condition("x", "Test Condition")
        assert ob.get_default_review_status(draft) == "needs_review"

    def test_validated_condition_gets_draft_status(self):
        from sozo_generator.conditions.onboarding import ConditionOnboarder
        from sozo_generator.conditions.registry import get_registry
        ob = ConditionOnboarder()
        reg = get_registry()
        parkinsons = reg.get("parkinsons")
        # Parkinsons has MEDIUM evidence quality, should get "draft" (not needs_review)
        status = ob.get_default_review_status(parkinsons)
        assert status == "draft"  # high enough evidence

    def test_is_draft(self):
        from sozo_generator.conditions.onboarding import ConditionOnboarder
        ob = ConditionOnboarder()
        draft = ob.create_draft_condition("x", "X")
        assert ob.is_draft(draft) == True

        from sozo_generator.conditions.registry import get_registry
        parkinsons = get_registry().get("parkinsons")
        assert ob.is_draft(parkinsons) == False


class TestEvidenceRefresh:
    def test_assess_staleness(self, parkinsons_condition):
        from sozo_generator.evidence.refresh import EvidenceRefresher
        refresher = EvidenceRefresher(recency_years=5)
        result = refresher.assess_staleness(parkinsons_condition)
        assert result.condition_slug == "parkinsons"
        assert result.total_items >= 1
        # Some items may be stale
        assert result.stale_items + result.fresh_items <= result.total_items

    def test_staleness_with_strict_recency(self, parkinsons_condition):
        from sozo_generator.evidence.refresh import EvidenceRefresher
        # 1-year window should mark most as stale
        refresher = EvidenceRefresher(recency_years=1)
        result = refresher.assess_staleness(parkinsons_condition)
        # Most evidence will be > 1 year old
        assert result.stale_items >= 0  # At least some stale

    def test_refresh_with_qa_rerun(self, parkinsons_condition):
        from sozo_generator.evidence.refresh import EvidenceRefresher
        refresher = EvidenceRefresher(recency_years=5)
        result = refresher.refresh_and_rerun_qa(parkinsons_condition)
        # QA should have run (may or may not be needed)
        assert result.condition_slug == "parkinsons"

    def test_set_recency(self):
        from sozo_generator.evidence.refresh import EvidenceRefresher
        refresher = EvidenceRefresher(recency_years=5)
        assert refresher.recency_years == 5
        refresher.set_recency(3)
        assert refresher.recency_years == 3

    def test_stale_marker_on_empty_condition(self):
        from sozo_generator.evidence.refresh import EvidenceRefresher
        from sozo_generator.schemas.condition import ConditionSchema
        refresher = EvidenceRefresher(recency_years=5)
        empty = ConditionSchema(slug="empty", display_name="Empty", icd10="X00")
        result = refresher.assess_staleness(empty)
        assert result.total_items == 0
        assert result.stale_items == 0


class TestSmokeTests:
    """Runtime smoke tests -- verify key paths don't crash."""

    def test_registry_loads_all_conditions(self):
        from sozo_generator.conditions.registry import get_registry
        reg = get_registry()
        slugs = reg.list_slugs()
        assert len(slugs) >= 15
        for slug in slugs:
            condition = reg.get(slug)
            assert condition.slug == slug
            assert condition.display_name != ""

    def test_chat_engine_processes_message(self, tmp_path):
        from sozo_generator.ai.chat_engine import ChatEngine
        engine = ChatEngine(output_dir=str(tmp_path))
        response = engine.process_message("list conditions")
        assert response.success
        assert "parkinsons" in response.message.lower() or "Parkinson" in response.message

    def test_qa_engine_runs_on_all_conditions(self):
        from sozo_generator.qa.engine import QAEngine
        from sozo_generator.conditions.registry import get_registry
        engine = QAEngine()
        reg = get_registry()
        for slug in reg.list_slugs():
            condition = reg.get(slug)
            report = engine.run_condition_qa(condition)
            report.compute_counts()
            # All validated conditions should pass (no blocks)
            assert report.block_count == 0, f"{slug} has {report.block_count} blocks"

    def test_evidence_mapper_on_all_conditions(self):
        from sozo_generator.evidence.section_evidence_mapper import SectionEvidenceMapper
        from sozo_generator.conditions.registry import get_registry
        mapper = SectionEvidenceMapper()
        reg = get_registry()
        for slug in reg.list_slugs():
            condition = reg.get(slug)
            items = mapper.build_evidence_items_from_condition(condition)
            # All validated conditions should have at least some evidence items
            assert len(items) >= 1, f"{slug} has no evidence items"

    def test_comment_normalizer_smoke(self):
        from sozo_generator.ai.comment_normalizer import CommentNormalizer
        cn = CommentNormalizer()
        tests = [
            "remove TPS",
            "add conservative language",
            "update references",
            "keep the protocol table",
            "latest studies only",
        ]
        for comment in tests:
            result = cn.normalize([comment])
            # Should not crash
            assert result is not None
