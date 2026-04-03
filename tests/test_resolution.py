"""Tests for reviewer disambiguation, resolution, and traceability."""
import json
import pytest
from pathlib import Path

FIXTURE_PATH = Path("tests/fixtures/reviewed_parkinsons.docx")


@pytest.fixture
def mapped_result():
    from sozo_generator.knowledge.revision.docx_comments import (
        extract_docx_comments, map_comments_to_sections
    )
    result = extract_docx_comments(str(FIXTURE_PATH))
    return map_comments_to_sections(result)


@pytest.fixture
def manager():
    from sozo_generator.knowledge.revision.resolution import ResolutionManager
    return ResolutionManager()


# ── Resolution Model Tests ───────────────────────────────────────────────


class TestResolutionModels:
    def test_resolution_decision(self):
        from sozo_generator.knowledge.revision.resolution import ResolutionDecision
        d = ResolutionDecision(
            extracted_comment_id="dxc-123",
            decided_by="Dr. Smith",
            chosen_section="safety",
        )
        assert d.resolution_id.startswith("res-")
        assert d.status == "resolved"

    def test_trace_record(self):
        from sozo_generator.knowledge.revision.resolution import CommentTraceRecord
        t = CommentTraceRecord(
            extracted_comment_id="dxc-123",
            original_text="Fix this",
            auto_mapped_section="safety",
            auto_confidence=0.95,
        )
        assert t.trace_id.startswith("trace-")
        d = t.to_dict()
        assert d["auto_mapped_section"] == "safety"

    def test_mapping_candidate(self):
        from sozo_generator.knowledge.revision.resolution import MappingCandidate
        c = MappingCandidate(
            section_slug="pathophysiology",
            score=8.5,
            confidence=0.95,
            explanation="Strong heading match",
        )
        assert c.confidence == 0.95


# ── Unresolved Detection Tests ───────────────────────────────────────────


class TestUnresolvedDetection:
    def test_get_unresolved(self, mapped_result, manager):
        unresolved = manager.get_unresolved(mapped_result)
        # Comments with confidence < 0.70 need resolution
        assert isinstance(unresolved, list)
        for c in unresolved:
            assert c.mapping_confidence < 0.70

    def test_get_auto_resolved(self, mapped_result, manager):
        auto = manager.get_auto_resolved(mapped_result)
        for c in auto:
            assert c.mapping_confidence >= 0.70

    def test_auto_plus_unresolved_equals_total(self, mapped_result, manager):
        auto = manager.get_auto_resolved(mapped_result)
        unresolved = manager.get_unresolved(mapped_result)
        assert len(auto) + len(unresolved) == len(mapped_result.comments)


# ── Candidate Inspection Tests ───────────────────────────────────────────


class TestCandidateInspection:
    def test_get_candidates(self, mapped_result, manager):
        for c in mapped_result.comments:
            candidates = manager.get_candidates(c)
            assert len(candidates) >= 1
            # Should include document_general as an option
            slugs = [cand.section_slug for cand in candidates]
            assert "(document_general)" in slugs

    def test_candidates_include_top_and_alternates(self, mapped_result, manager):
        patho = next(c for c in mapped_result.comments if "pathophysiology" in c.text.lower())
        candidates = manager.get_candidates(patho)
        slugs = [c.section_slug for c in candidates]
        assert "pathophysiology" in slugs


# ── Manual Resolution Tests ──────────────────────────────────────────────


class TestManualResolution:
    def test_resolve_to_section(self, mapped_result, manager):
        comment = mapped_result.comments[0]
        decision = manager.resolve(
            comment_id=comment.comment_id,
            section_slug="safety",
            decided_by="Dr. Test",
            notes="Clearly about safety",
        )
        assert decision.chosen_section == "safety"
        assert decision.decided_by == "Dr. Test"
        assert decision.status == "resolved"

    def test_resolve_to_document_general(self, mapped_result, manager):
        from sozo_generator.knowledge.revision.resolution import TargetKind
        comment = mapped_result.comments[0]
        decision = manager.resolve(
            comment_id=comment.comment_id,
            target_kind=TargetKind.DOCUMENT_GENERAL,
            decided_by="Dr. Test",
        )
        assert decision.target_kind == "document_general"

    def test_resolve_to_visual(self, mapped_result, manager):
        from sozo_generator.knowledge.revision.resolution import TargetKind
        comment = mapped_result.comments[0]
        decision = manager.resolve(
            comment_id=comment.comment_id,
            section_slug="brain_anatomy",
            target_kind=TargetKind.VISUAL,
            decided_by="Dr. Test",
        )
        assert decision.target_kind == "visual"

    def test_resolve_to_blocked(self, mapped_result, manager):
        from sozo_generator.knowledge.revision.resolution import TargetKind
        comment = mapped_result.comments[0]
        decision = manager.resolve(
            comment_id=comment.comment_id,
            target_kind=TargetKind.BLOCKED,
            decided_by="Dr. Test",
            notes="Too vague to resolve",
        )
        assert decision.target_kind == "blocked"

    def test_manual_takes_precedence(self, mapped_result, manager):
        comment = mapped_result.comments[0]
        # Auto-mapped section
        auto_section = comment.mapped_section

        # Manually resolve to different section
        manager.resolve(comment.comment_id, section_slug="references", decided_by="Dr. Test")

        effective, source = manager.get_effective_section(comment)
        assert effective == "references"
        assert source == "manual"

    def test_reopen_resolution(self, mapped_result, manager):
        comment = mapped_result.comments[0]
        manager.resolve(comment.comment_id, section_slug="safety", decided_by="Dr. Test")
        assert manager.reopen(comment.comment_id)
        res = manager.get_resolution(comment.comment_id)
        assert res.status == "reopened"

    def test_resolution_persisted(self, mapped_result, manager):
        comment = mapped_result.comments[0]
        decision = manager.resolve(comment.comment_id, section_slug="safety", decided_by="Dr. Test")
        path = manager.store_dir / f"{decision.resolution_id}.json"
        assert path.exists()


# ── Traceability Tests ───────────────────────────────────────────────────


class TestTraceability:
    def test_build_trace_auto(self, mapped_result, manager):
        # Pick a high-confidence comment
        auto_comments = manager.get_auto_resolved(mapped_result)
        if auto_comments:
            trace = manager.build_trace(auto_comments[0])
            assert trace.resolution_type == "auto"
            assert trace.auto_confidence > 0

    def test_build_trace_manual(self, mapped_result, manager):
        comment = mapped_result.comments[0]
        manager.resolve(comment.comment_id, section_slug="safety", decided_by="Dr. Test")
        trace = manager.build_trace(comment)
        assert trace.resolution_type == "manual"
        assert trace.resolved_by == "Dr. Test"
        assert trace.resolved_section == "safety"

    def test_trace_serializable(self, mapped_result, manager):
        comment = mapped_result.comments[0]
        trace = manager.build_trace(comment)
        d = trace.to_dict()
        json.dumps(d)  # Must be JSON-serializable

    def test_save_traces(self, mapped_result, manager, tmp_path):
        for c in mapped_result.comments:
            manager.build_trace(c)
        path = manager.save_traces(tmp_path / "traces.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert len(data) == len(mapped_result.comments)


# ── Resolved Review Set Tests ────────────────────────────────────────────


class TestResolvedReviewSet:
    def test_create_from_auto_resolved(self, mapped_result, manager):
        review_set = manager.create_resolved_review_set(
            mapped_result, "parkinsons", "evidence_based_protocol", "fellow"
        )
        # Should include at least auto-resolved comments
        assert len(review_set.comments) >= 1

    def test_require_all_resolved_raises(self, mapped_result, manager):
        unresolved = manager.get_unresolved(mapped_result)
        if unresolved:
            with pytest.raises(ValueError, match="unresolved"):
                manager.create_resolved_review_set(
                    mapped_result, "parkinsons", "evidence_based_protocol", "fellow",
                    require_all_resolved=True,
                )

    def test_resolved_comments_included(self, mapped_result, manager):
        # Resolve all unresolved comments
        for c in manager.get_unresolved(mapped_result):
            manager.resolve(c.comment_id, section_slug=c.mapped_section or "safety", decided_by="Dr. Test")

        review_set = manager.create_resolved_review_set(
            mapped_result, "parkinsons", "evidence_based_protocol", "fellow",
            require_all_resolved=True,
        )
        assert len(review_set.comments) == 5  # All 5 should now be included


# ── Summary Tests ────────────────────────────────────────────────────────


class TestSummary:
    def test_summary_text(self, mapped_result, manager):
        text = manager.summary(mapped_result)
        assert "RESOLUTION STATUS" in text
        assert "Total comments: 5" in text

    def test_summary_after_resolution(self, mapped_result, manager):
        for c in manager.get_unresolved(mapped_result):
            manager.resolve(c.comment_id, section_slug="safety", decided_by="Dr. Test")
        text = manager.summary(mapped_result)
        assert "Needs resolution: 0" in text
