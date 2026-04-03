"""Tests for the review-driven regeneration system."""
import json
import pytest
from pathlib import Path


# ── Model Tests ───────────────────────────────────────────────────────────


class TestRevisionModels:
    def test_review_comment_creation(self):
        from sozo_generator.knowledge.revision.models import ReviewComment, CommentCategory
        rc = ReviewComment(raw_text="This needs more evidence")
        assert rc.comment_id.startswith("rc-")
        assert rc.category == CommentCategory.GENERAL
        assert rc.status == "pending"

    def test_review_comment_set(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        cs = ReviewCommentSet(document_id="test-doc", reviewer_name="Dr. Smith")
        cs.add("Fix the safety section", section="safety", severity="major")
        cs.add("Too technical for Fellows")
        assert len(cs.comments) == 2
        assert cs.comments[0].target_section_slug == "safety"

    def test_change_request_creation(self):
        from sozo_generator.knowledge.revision.models import ChangeRequest, ChangeTarget
        cr = ChangeRequest(
            target_type=ChangeTarget.SECTION_OVERRIDE,
            target_section="pathophysiology",
            requested_action="expand",
        )
        assert cr.change_id.startswith("cr-")
        assert cr.target_type == ChangeTarget.SECTION_OVERRIDE

    def test_change_plan_text(self):
        from sozo_generator.knowledge.revision.models import ChangePlan, ChangeRequest
        plan = ChangePlan(
            document_id="test",
            condition_slug="parkinsons",
            changes=[ChangeRequest(original_comment="test comment")],
        )
        text = plan.to_text()
        assert "CHANGE PLAN" in text
        assert "parkinsons" in text

    def test_regeneration_result(self):
        from sozo_generator.knowledge.revision.models import RegenerationResult
        rr = RegenerationResult(
            plan_id="plan-123",
            condition_slug="parkinsons",
            success=True,
        )
        assert rr.result_id.startswith("regen-")
        text = rr.to_text()
        assert "REGENERATION RESULT" in text


# ── Comment Parsing Tests ─────────────────────────────────────────────────


class TestCommentParsing:
    def test_ingest_from_text(self):
        from sozo_generator.knowledge.revision.parser import ingest_from_text
        cs = ingest_from_text(
            "Fix safety section\n[protocols_tps] Add TPS evidence\n# ignored",
            document_id="test-doc",
            condition_slug="parkinsons",
        )
        assert len(cs.comments) == 2
        assert cs.comments[1].target_section_slug == "protocols_tps"

    def test_classify_comment_evidence(self):
        from sozo_generator.knowledge.revision.models import ReviewComment, CommentCategory
        from sozo_generator.knowledge.revision.parser import classify_comment
        rc = ReviewComment(raw_text="Add more evidence and citations to support this claim")
        classify_comment(rc)
        assert rc.category == CommentCategory.EVIDENCE_STRENGTH
        assert rc.parsed is True

    def test_classify_comment_tone(self):
        from sozo_generator.knowledge.revision.models import ReviewComment, CommentCategory
        from sozo_generator.knowledge.revision.parser import classify_comment
        rc = ReviewComment(raw_text="This is too technical for Fellows")
        classify_comment(rc)
        assert rc.category == CommentCategory.AUDIENCE_TONE

    def test_classify_comment_visual(self):
        from sozo_generator.knowledge.revision.models import ReviewComment, CommentCategory
        from sozo_generator.knowledge.revision.parser import classify_comment
        rc = ReviewComment(raw_text="Move the EEG figure above the treatment section")
        classify_comment(rc)
        assert rc.category == CommentCategory.VISUAL_CHANGE

    def test_classify_comment_contraindication(self):
        from sozo_generator.knowledge.revision.models import ReviewComment, CommentCategory
        from sozo_generator.knowledge.revision.parser import classify_comment
        rc = ReviewComment(raw_text="The contraindications section needs to include pregnancy risk")
        classify_comment(rc)
        assert rc.category == CommentCategory.CONTRAINDICATION

    def test_classify_severity_critical(self):
        from sozo_generator.knowledge.revision.models import ReviewComment, CommentSeverity
        from sozo_generator.knowledge.revision.parser import classify_comment
        rc = ReviewComment(raw_text="This claim is incorrect and must be fixed")
        classify_comment(rc)
        assert rc.severity == CommentSeverity.CRITICAL

    def test_section_detection(self):
        from sozo_generator.knowledge.revision.models import ReviewComment
        from sozo_generator.knowledge.revision.parser import classify_comment
        rc = ReviewComment(raw_text="The pathophysiology mechanism description is too brief")
        classify_comment(rc)
        assert rc.target_section_slug == "pathophysiology"


# ── Change Request Generation Tests ──────────────────────────────────────


class TestChangeRequests:
    def test_comments_to_change_requests(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.parser import classify_all, comments_to_change_requests

        cs = ReviewCommentSet(document_id="test", condition_slug="parkinsons")
        cs.add("Add more evidence here")
        cs.add("Simplify for Fellows")
        classify_all(cs)

        requests = comments_to_change_requests(cs)
        assert len(requests) == 2
        assert all(r.change_id.startswith("cr-") for r in requests)

    def test_evidence_sensitive_flagging(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.parser import classify_all, comments_to_change_requests

        cs = ReviewCommentSet(document_id="test", condition_slug="parkinsons")
        cs.add("Add PMID evidence for this clinical claim")
        classify_all(cs)
        requests = comments_to_change_requests(cs)
        assert requests[0].evidence_sensitive is True
        assert requests[0].requires_manual_approval is True

    def test_broad_rewrite_blocked(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet, ChangeStatus
        from sozo_generator.knowledge.revision.parser import classify_all, comments_to_change_requests

        cs = ReviewCommentSet(document_id="test", condition_slug="parkinsons")
        cs.add("Rewrite everything from scratch")
        classify_all(cs)
        requests = comments_to_change_requests(cs)
        assert requests[0].status == ChangeStatus.BLOCKED


# ── Change Plan Tests ────────────────────────────────────────────────────


class TestChangePlan:
    def test_create_plan(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(
            document_id="test",
            condition_slug="parkinsons",
            blueprint_slug="evidence_based_protocol",
            tier="fellow",
        )
        cs.add("Add more detail to pathophysiology")
        cs.add("Simplify for Fellows")

        engine = RevisionEngine()
        plan = engine.create_change_plan(cs)
        assert plan.total_changes >= 2
        assert plan.condition_slug == "parkinsons"

    def test_plan_safety_flags(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(
            document_id="test",
            condition_slug="parkinsons",
            blueprint_slug="evidence_based_protocol",
            tier="fellow",
        )
        cs.add("Add PMID evidence for TPS claims")
        cs.add("Update the contraindication list")

        engine = RevisionEngine()
        plan = engine.create_change_plan(cs)
        assert plan.requires_evidence_review is True
        assert plan.safe_to_auto_apply is False


# ── End-to-End Regeneration Tests ────────────────────────────────────────


class TestRegeneration:
    def test_review_and_regenerate(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(document_id="test-doc", reviewer_name="Dr. Test")
        cs.add("Add more detail to pathophysiology section")
        cs.add("Simplify network analysis for Fellows")

        engine = RevisionEngine()
        result = engine.review_and_regenerate(
            document_id="test-regen",
            condition="parkinsons",
            blueprint="evidence_based_protocol",
            tier="fellow",
            comments=cs,
            force=True,
        )
        assert result.success
        assert result.output_path
        assert Path(result.output_path).exists()

    def test_regeneration_preserves_readiness(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(document_id="test-doc", reviewer_name="Dr. Test")
        cs.add("Minor wording improvement")

        engine = RevisionEngine()
        result = engine.review_and_regenerate(
            document_id="test-ready",
            condition="parkinsons",
            blueprint="evidence_based_protocol",
            tier="fellow",
            comments=cs,
            force=True,
        )
        assert result.success
        assert result.readiness_after in ("ready", "review_required")

    def test_regeneration_saves_history(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(document_id="test-doc", reviewer_name="Dr. Test")
        cs.add("Fix this section")

        engine = RevisionEngine()
        result = engine.review_and_regenerate(
            document_id="test-hist",
            condition="parkinsons",
            blueprint="handbook",
            tier="fellow",
            comments=cs,
            force=True,
        )
        assert result.success
        assert result.review_record_path
        assert Path(result.review_record_path).exists()

        # Verify history content
        history = json.loads(Path(result.review_record_path).read_text())
        assert history["condition"] == "parkinsons"
        assert history["success"] is True

    def test_blocked_without_force(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(document_id="test-doc", reviewer_name="Dr. Test")
        cs.add("Add PMID evidence for this critical claim")  # evidence-sensitive

        engine = RevisionEngine()
        result = engine.review_and_regenerate(
            document_id="test-block",
            condition="parkinsons",
            blueprint="evidence_based_protocol",
            tier="fellow",
            comments=cs,
            force=False,  # Don't force
        )
        assert not result.success
        assert "manual review" in result.error.lower()

    def test_provenance_includes_revision_metadata(self):
        from sozo_generator.knowledge.revision.models import ReviewCommentSet
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        cs = ReviewCommentSet(document_id="test-doc", reviewer_name="Dr. Test")
        cs.add("Minor fix")

        engine = RevisionEngine()
        result = engine.review_and_regenerate(
            document_id="test-prov",
            condition="depression",
            blueprint="evidence_based_protocol",
            tier="fellow",
            comments=cs,
            force=True,
        )
        assert result.success
        prov = json.loads(Path(result.provenance_path).read_text())
        assert "revision" in prov
        assert prov["revision"]["parent_document_id"] == "test-prov"
