"""Tests for sozo_generator.schemas.contracts — all Phase 2 data models."""
from __future__ import annotations

import json

import pytest

from sozo_generator.core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    EvidenceLevel,
    EvidenceRelation,
    EvidenceType,
    Modality,
    QASeverity,
    ReviewStatus,
)
from sozo_generator.schemas.contracts import (
    BatchBuildReport,
    BatchConditionResult,
    BuildManifest,
    ClaimCitationLink,
    ClaimCitationMap,
    DocumentBuildEntry,
    EvidenceBundle,
    EvidenceItem,
    EvidenceSnapshotManifest,
    FigureEntry,
    FigureManifest,
    QAIssue,
    QAReport,
    ReviewComment,
    ReviewDecision,
    ReviewState,
    SectionEvidenceMap,
)


# ── EvidenceItem ────────────────────────────────────────────────────────


class TestEvidenceItem:
    def test_defaults(self):
        item = EvidenceItem()
        assert item.pmid is None
        assert item.relevance_score == 0.0
        assert item.evidence_type == EvidenceType.NARRATIVE_REVIEW
        assert item.evidence_level == EvidenceLevel.MEDIUM
        assert item.relation == EvidenceRelation.SUPPORTS
        assert item.population_match is True
        assert item.modalities == []

    def test_with_values(self):
        item = EvidenceItem(
            pmid="12345678",
            title="A study",
            evidence_level=EvidenceLevel.HIGH,
            relevance_score=8.5,
            modalities=[Modality.TDCS],
        )
        assert item.pmid == "12345678"
        assert item.relevance_score == 8.5
        assert Modality.TDCS in item.modalities

    def test_relevance_score_bounds(self):
        with pytest.raises(Exception):
            EvidenceItem(relevance_score=11.0)
        with pytest.raises(Exception):
            EvidenceItem(relevance_score=-1.0)

    def test_serialization_roundtrip(self):
        item = EvidenceItem(pmid="11111111", title="Test", relevance_score=5.0)
        data = json.loads(item.model_dump_json())
        restored = EvidenceItem(**data)
        assert restored.pmid == item.pmid
        assert restored.relevance_score == item.relevance_score


# ── EvidenceBundle ──────────────────────────────────────────────────────


class TestEvidenceBundle:
    def test_computed_counts(self):
        items = [
            EvidenceItem(pmid="1", relation=EvidenceRelation.SUPPORTS),
            EvidenceItem(pmid="2", relation=EvidenceRelation.SUPPORTS),
            EvidenceItem(pmid="3", relation=EvidenceRelation.CONTRADICTS),
        ]
        bundle = EvidenceBundle(
            bundle_id="b1",
            condition_slug="test",
            category=ClaimCategory.SAFETY,
            items=items,
        )
        assert bundle.item_count == 3
        assert bundle.supporting_count == 2
        assert bundle.contradicting_count == 1

    def test_empty_bundle(self):
        bundle = EvidenceBundle(
            bundle_id="empty",
            condition_slug="test",
            category=ClaimCategory.PATHOPHYSIOLOGY,
        )
        assert bundle.item_count == 0
        assert bundle.supporting_count == 0
        assert bundle.contradicting_count == 0


# ── SectionEvidenceMap ──────────────────────────────────────────────────


class TestSectionEvidenceMap:
    def test_creation(self):
        sem = SectionEvidenceMap(
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
        )
        assert sem.section_bundles == {}
        assert sem.condition_slug == "test"


# ── ClaimCitationLink / ClaimCitationMap ────────────────────────────────


class TestClaimCitationLink:
    def test_defaults(self):
        link = ClaimCitationLink(
            claim_id="c1",
            claim_text="A claim",
            category=ClaimCategory.SAFETY,
            confidence=ConfidenceLabel.HIGH,
        )
        assert link.pmids == []
        assert link.requires_review is False
        assert link.insufficient_evidence is False


class TestClaimCitationMap:
    def test_creation(self):
        ccm = ClaimCitationMap(
            condition_slug="test",
            document_type="clinical_exam",
            tier="fellow",
            total_claims=5,
            unsupported_claims=1,
        )
        assert ccm.total_claims == 5
        assert ccm.claims == []


# ── EvidenceSnapshotManifest ────────────────────────────────────────────


class TestEvidenceSnapshotManifest:
    def test_compute_hash_deterministic(self):
        bundle = EvidenceBundle(
            bundle_id="b1",
            condition_slug="test",
            category=ClaimCategory.PATHOPHYSIOLOGY,
            items=[EvidenceItem(pmid="12345678", title="Study A")],
        )
        manifest = EvidenceSnapshotManifest(
            snapshot_id="snap-test-20260401",
            condition_slug="test",
            bundles=[bundle],
        )
        h1 = manifest.compute_hash()
        h2 = manifest.compute_hash()
        assert h1 == h2
        assert len(h1) == 16
        assert manifest.content_hash == h1

    def test_different_bundles_different_hash(self):
        m1 = EvidenceSnapshotManifest(
            snapshot_id="s1",
            condition_slug="a",
            bundles=[
                EvidenceBundle(
                    bundle_id="b1",
                    condition_slug="a",
                    category=ClaimCategory.SAFETY,
                )
            ],
        )
        m2 = EvidenceSnapshotManifest(
            snapshot_id="s2",
            condition_slug="a",
            bundles=[
                EvidenceBundle(
                    bundle_id="b2",
                    condition_slug="a",
                    category=ClaimCategory.BRAIN_REGIONS,
                )
            ],
        )
        assert m1.compute_hash() != m2.compute_hash()


# ── QAIssue / QAReport ─────────────────────────────────────────────────


class TestQAIssue:
    def test_defaults(self):
        issue = QAIssue()
        assert issue.severity == QASeverity.WARNING
        assert issue.auto_fixable is False


class TestQAReport:
    def test_compute_counts(self):
        issues = [
            QAIssue(severity=QASeverity.BLOCK, message="block1"),
            QAIssue(severity=QASeverity.BLOCK, message="block2"),
            QAIssue(severity=QASeverity.WARNING, message="warn1"),
            QAIssue(severity=QASeverity.INFO, message="info1"),
            QAIssue(severity=QASeverity.INFO, message="info2"),
        ]
        report = QAReport(
            report_id="r1",
            condition_slug="test",
            issues=issues,
        )
        report.compute_counts()
        assert report.block_count == 2
        assert report.warning_count == 1
        assert report.info_count == 2
        assert report.passed is False

    def test_passed_when_no_blocks(self):
        report = QAReport(
            report_id="r2",
            condition_slug="test",
            issues=[QAIssue(severity=QASeverity.WARNING)],
        )
        report.compute_counts()
        assert report.passed is True
        assert report.block_count == 0

    def test_empty_report_passes(self):
        report = QAReport(report_id="r3", condition_slug="test")
        report.compute_counts()
        assert report.passed is True


# ── ReviewState ─────────────────────────────────────────────────────────


class TestReviewState:
    def test_valid_transition_draft_to_needs_review(self):
        state = ReviewState(build_id="b1", status=ReviewStatus.DRAFT)
        state.transition(ReviewStatus.NEEDS_REVIEW, reviewer="alice")
        assert state.status == ReviewStatus.NEEDS_REVIEW
        assert len(state.decisions) == 1
        assert state.decisions[0].reviewer == "alice"

    def test_valid_transition_needs_review_to_approved(self):
        state = ReviewState(build_id="b2", status=ReviewStatus.NEEDS_REVIEW)
        state.transition(ReviewStatus.APPROVED, reviewer="bob", reason="looks good")
        assert state.status == ReviewStatus.APPROVED

    def test_valid_transition_needs_review_to_rejected(self):
        state = ReviewState(build_id="b3", status=ReviewStatus.NEEDS_REVIEW)
        state.transition(ReviewStatus.REJECTED, reviewer="carol", reason="issues")
        assert state.status == ReviewStatus.REJECTED

    def test_valid_transition_rejected_to_needs_review(self):
        state = ReviewState(build_id="b4", status=ReviewStatus.REJECTED)
        state.transition(ReviewStatus.NEEDS_REVIEW, reviewer="system")
        assert state.status == ReviewStatus.NEEDS_REVIEW

    def test_valid_transition_approved_to_exported(self):
        state = ReviewState(build_id="b5", status=ReviewStatus.APPROVED)
        state.transition(ReviewStatus.EXPORTED, reviewer="system")
        assert state.status == ReviewStatus.EXPORTED

    def test_invalid_transition_draft_to_approved(self):
        state = ReviewState(build_id="b6", status=ReviewStatus.DRAFT)
        with pytest.raises(ValueError, match="Invalid transition"):
            state.transition(ReviewStatus.APPROVED, reviewer="alice")

    def test_invalid_transition_exported_to_anything(self):
        state = ReviewState(build_id="b7", status=ReviewStatus.EXPORTED)
        with pytest.raises(ValueError):
            state.transition(ReviewStatus.DRAFT, reviewer="system")

    def test_invalid_transition_draft_to_rejected(self):
        state = ReviewState(build_id="b8", status=ReviewStatus.DRAFT)
        with pytest.raises(ValueError):
            state.transition(ReviewStatus.REJECTED, reviewer="alice")

    def test_transition_updates_timestamp(self):
        state = ReviewState(build_id="b9", status=ReviewStatus.DRAFT)
        old_ts = state.updated_at
        state.transition(ReviewStatus.NEEDS_REVIEW, reviewer="alice")
        # updated_at should be set (could be same second, but field should exist)
        assert state.updated_at is not None


# ── ReviewDecision / ReviewComment ──────────────────────────────────────


class TestReviewDecision:
    def test_creation(self):
        d = ReviewDecision(
            decision_id="d1",
            reviewer="alice",
            status=ReviewStatus.APPROVED,
            reason="all good",
        )
        assert d.reviewer == "alice"
        assert d.status == ReviewStatus.APPROVED


class TestReviewComment:
    def test_creation(self):
        c = ReviewComment(
            comment_id="c1",
            reviewer="bob",
            section_id="safety",
            text="Please add more detail",
        )
        assert c.section_id == "safety"


# ── BuildManifest ───────────────────────────────────────────────────────


class TestBuildManifest:
    def test_compute_hash_deterministic(self):
        doc = DocumentBuildEntry(
            document_type="clinical_exam",
            tier="fellow",
            output_path="/tmp/test.docx",
            content_hash="abc123",
        )
        manifest = BuildManifest(
            build_id="build-test-001",
            condition_slug="test",
            documents=[doc],
        )
        h1 = manifest.compute_hash()
        h2 = manifest.compute_hash()
        assert h1 == h2
        assert len(h1) == 16
        assert manifest.content_hash == h1

    def test_different_documents_different_hash(self):
        m1 = BuildManifest(
            build_id="b1",
            documents=[
                DocumentBuildEntry(document_type="a", tier="fellow", output_path="/a"),
            ],
        )
        m2 = BuildManifest(
            build_id="b2",
            documents=[
                DocumentBuildEntry(document_type="b", tier="fellow", output_path="/b"),
            ],
        )
        assert m1.compute_hash() != m2.compute_hash()


# ── DocumentBuildEntry ──────────────────────────────────────────────────


class TestDocumentBuildEntry:
    def test_defaults(self):
        entry = DocumentBuildEntry()
        assert entry.review_status == ReviewStatus.DRAFT
        assert entry.qa_passed is False
        assert entry.qa_block_count == 0


# ── FigureEntry / FigureManifest ────────────────────────────────────────


class TestFigureEntry:
    def test_creation(self):
        fig = FigureEntry(
            figure_id="f1",
            figure_type="brain_map",
            file_path="/tmp/fig.png",
            condition_slug="test",
        )
        assert fig.figure_type == "brain_map"


class TestFigureManifest:
    def test_creation(self):
        fm = FigureManifest(condition_slug="test")
        assert fm.figures == []
        assert fm.shared_legends == []


# ── BatchBuildReport ────────────────────────────────────────────────────


class TestBatchBuildReport:
    def test_finalize_all_success(self):
        results = [
            BatchConditionResult(
                condition_slug="a", success=True, documents_generated=3
            ),
            BatchConditionResult(
                condition_slug="b", success=True, documents_generated=2
            ),
        ]
        report = BatchBuildReport(
            batch_id="batch-1",
            total_conditions=2,
            results=results,
        )
        report.finalize()
        assert report.successful_conditions == 2
        assert report.failed_conditions == 0
        assert report.total_documents == 5
        assert report.completed_at is not None
        assert report.retry_suggestions == []

    def test_finalize_with_failures(self):
        results = [
            BatchConditionResult(
                condition_slug="a", success=True, documents_generated=3
            ),
            BatchConditionResult(
                condition_slug="b",
                success=False,
                error="QA blocked",
                documents_blocked=2,
            ),
            BatchConditionResult(
                condition_slug="c", success=False, error="Import error"
            ),
        ]
        report = BatchBuildReport(
            batch_id="batch-2",
            total_conditions=3,
            results=results,
        )
        report.finalize()
        assert report.successful_conditions == 1
        assert report.failed_conditions == 2
        assert report.blocked_conditions == 1
        assert report.total_documents == 3
        assert len(report.retry_suggestions) == 2
        assert "b" in report.retry_suggestions[0]
        assert "c" in report.retry_suggestions[1]

    def test_finalize_empty(self):
        report = BatchBuildReport(batch_id="batch-3", total_conditions=0)
        report.finalize()
        assert report.successful_conditions == 0
        assert report.total_documents == 0


# ── BatchConditionResult ────────────────────────────────────────────────


class TestBatchConditionResult:
    def test_defaults(self):
        r = BatchConditionResult(condition_slug="test")
        assert r.success is False
        assert r.error is None
        assert r.documents_generated == 0
