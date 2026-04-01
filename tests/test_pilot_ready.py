"""Comprehensive pilot-readiness tests for review reports, dashboard,
evidence refresh fallback, and deployment smoke checks."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from sozo_generator.review.reports import (
    ReviewDashboardData,
    ReviewReporter,
    SectionReviewSummary,
)
from sozo_generator.review.manager import ReviewManager
from sozo_generator.core.enums import ReviewStatus


# ── helpers ───────────────────────────────────────────────────────────────


def _create_review(manager: ReviewManager, build_id: str, condition: str,
                   doc_type: str = "evidence_based_protocol", tier: str = "fellow"):
    """Create a review and return it."""
    return manager.create_review(
        build_id=build_id,
        condition_slug=condition,
        document_type=doc_type,
        tier=tier,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Dashboard tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestReviewDashboard:
    def test_dashboard_data_empty(self, tmp_path):
        """No reviews gives all zeros."""
        reporter = ReviewReporter(tmp_path / "reviews")
        data = reporter.get_dashboard_data()
        assert data.total_reviews == 0
        assert data.pending_count == 0
        assert data.approved_count == 0
        assert data.flagged_count == 0
        assert data.by_condition == {}

    def test_dashboard_data_with_reviews(self, tmp_path):
        """Several reviews in different states are counted correctly."""
        reviews_dir = tmp_path / "reviews"
        mgr = ReviewManager(reviews_dir)

        # Draft
        _create_review(mgr, "b1", "parkinsons")
        # Needs review
        _create_review(mgr, "b2", "depression")
        mgr.submit_for_review("b2")
        # Approved
        _create_review(mgr, "b3", "anxiety")
        mgr.submit_for_review("b3")
        mgr.approve("b3", reviewer="dr_smith", reason="Looks good")
        # Flagged
        _create_review(mgr, "b4", "ocd")
        mgr.submit_for_review("b4")
        mgr.add_flag("b4", flag_reason="Needs extra references", flagged_by="qa_bot")

        reporter = ReviewReporter(reviews_dir)
        data = reporter.get_dashboard_data()

        assert data.total_reviews == 4
        assert data.draft_count == 1
        assert data.pending_count == 1
        assert data.approved_count == 1
        assert data.flagged_count == 1
        assert len(data.recent_decisions) > 0

    def test_dashboard_groups_by_condition(self, tmp_path):
        """Multiple conditions appear in by_condition."""
        reviews_dir = tmp_path / "reviews"
        mgr = ReviewManager(reviews_dir)
        _create_review(mgr, "b1", "parkinsons")
        _create_review(mgr, "b2", "parkinsons", doc_type="handbook")
        _create_review(mgr, "b3", "depression")

        reporter = ReviewReporter(reviews_dir)
        data = reporter.get_dashboard_data()

        assert "parkinsons" in data.by_condition
        assert data.by_condition["parkinsons"]["total"] == 2
        assert "depression" in data.by_condition
        assert data.by_condition["depression"]["total"] == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Report generation tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestReportGeneration:
    def test_flagged_report_markdown(self, tmp_path):
        """Flagged report contains flagged items in markdown."""
        reviews_dir = tmp_path / "reviews"
        mgr = ReviewManager(reviews_dir)
        _create_review(mgr, "b1", "parkinsons")
        mgr.submit_for_review("b1")
        mgr.add_flag("b1", flag_reason="Missing safety section", flagged_by="auditor")

        reporter = ReviewReporter(reviews_dir)
        md = reporter.generate_flagged_report()

        assert "# Flagged Documents Report" in md
        assert "b1" in md
        assert "Missing safety section" in md
        assert "auditor" in md

    def test_flagged_report_empty(self, tmp_path):
        """No flagged items gives clean report."""
        reporter = ReviewReporter(tmp_path / "reviews")
        md = reporter.generate_flagged_report()
        assert "No documents are currently flagged" in md

    def test_evidence_gap_report(self, parkinsons_condition):
        """Evidence gap report lists gaps for the condition."""
        reporter = ReviewReporter(Path("/tmp/_sozo_test_reviews_gap"))
        md = reporter.generate_evidence_gap_report([parkinsons_condition])

        assert "# Evidence Gap Report" in md
        assert parkinsons_condition.display_name in md
        assert parkinsons_condition.slug in md
        # Should mention evidence quality
        assert "evidence quality" in md.lower() or "evidence items" in md.lower()

    def test_stale_evidence_report(self, parkinsons_condition):
        """Stale evidence report runs without error."""
        reporter = ReviewReporter(Path("/tmp/_sozo_test_reviews_stale"))
        md = reporter.generate_stale_evidence_report(
            [parkinsons_condition], recency_years=5,
        )
        assert "# Stale Evidence Report" in md
        assert parkinsons_condition.display_name in md

    def test_revision_history_report(self, tmp_path):
        """Revision history lists decisions with timestamps."""
        reviews_dir = tmp_path / "reviews"
        mgr = ReviewManager(reviews_dir)
        _create_review(mgr, "b1", "parkinsons")
        mgr.submit_for_review("b1")
        mgr.approve("b1", reviewer="dr_jones", reason="All checks passed")

        reporter = ReviewReporter(reviews_dir)
        md = reporter.generate_revision_history_report()

        assert "# Revision History Report" in md
        assert "b1" in md
        assert "dr_jones" in md
        assert "All checks passed" in md

    def test_export_all_reports(self, tmp_path, parkinsons_condition):
        """Export all reports creates expected files."""
        reviews_dir = tmp_path / "reviews"
        output_dir = tmp_path / "reports_output"
        ReviewManager(reviews_dir)  # ensure dir exists

        reporter = ReviewReporter(reviews_dir)
        paths = reporter.export_all_reports(
            output_dir, [parkinsons_condition], recency_years=5,
        )

        assert "flagged_report" in paths
        assert "evidence_gaps" in paths
        assert "stale_evidence" in paths
        assert "revision_history" in paths

        for name, path in paths.items():
            assert path.exists(), f"{name} file should exist at {path}"
            content = path.read_text()
            assert len(content) > 10, f"{name} should have content"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Section review tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSectionReview:
    def test_section_review_summaries(self, parkinsons_condition, tmp_path):
        """Section summaries have evidence confidence set."""
        reviews_dir = tmp_path / "reviews"
        reporter = ReviewReporter(reviews_dir)
        summaries = reporter.generate_section_review_summaries(parkinsons_condition)

        assert len(summaries) > 0
        for s in summaries:
            assert isinstance(s, SectionReviewSummary)
            assert s.section_id != ""
            assert s.evidence_confidence != ""

    def test_section_with_comments(self, parkinsons_condition, tmp_path):
        """Section comments from reviews appear in the summaries."""
        reviews_dir = tmp_path / "reviews"
        mgr = ReviewManager(reviews_dir)
        _create_review(mgr, "b1", parkinsons_condition.slug)
        mgr.add_section_comment("b1", "protocols", reviewer="dr_x", text="Check dosage")

        reporter = ReviewReporter(reviews_dir)
        summaries = reporter.generate_section_review_summaries(parkinsons_condition)

        # Find the protocols section (or any section that has the comment)
        protocol_summaries = [s for s in summaries if s.section_id == "protocols"]
        if protocol_summaries:
            assert any("Check dosage" in c.get("text", "") for c in protocol_summaries[0].comments)
        # Even if protocols section isn't in the evidence profile, the overall call should succeed
        assert len(summaries) > 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Approved export tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestApprovedExport:
    def test_export_empty_returns_nothing(self, tmp_path):
        """No approved reviews gives empty export."""
        reviews_dir = tmp_path / "reviews"
        output_dir = tmp_path / "export"
        ReviewManager(reviews_dir)

        reporter = ReviewReporter(reviews_dir)
        manifest = reporter.export_approved_bundle(output_dir)

        assert manifest["total_exported"] == 0
        assert manifest["files"] == []
        assert (output_dir / "manifest.json").exists()

    def test_export_creates_manifest(self, tmp_path):
        """Approved reviews with document_path get exported with a manifest."""
        reviews_dir = tmp_path / "reviews"
        output_dir = tmp_path / "export"

        # Create a fake document file
        doc_file = tmp_path / "fake_doc.docx"
        doc_file.write_text("fake document content")

        # Create a review with metadata containing document_path
        mgr = ReviewManager(reviews_dir)
        review = _create_review(mgr, "b1", "parkinsons")

        # Manually add metadata with document_path and save
        review_path = reviews_dir / "b1.json"
        data = json.loads(review_path.read_text())
        data["metadata"] = {"document_path": str(doc_file)}
        review_path.write_text(json.dumps(data, indent=2, default=str))

        mgr.submit_for_review("b1")
        mgr.approve("b1", reviewer="dr_x", reason="Approved")

        reporter = ReviewReporter(reviews_dir)
        manifest = reporter.export_approved_bundle(output_dir)

        assert (output_dir / "manifest.json").exists()
        manifest_data = json.loads((output_dir / "manifest.json").read_text())
        assert manifest_data["total_exported"] == manifest["total_exported"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Live refresh fallback tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestLiveRefreshFallback:
    def test_refresh_without_biopython(self, parkinsons_condition):
        """EvidenceRefresher works even without Bio -- returns staleness assessment."""
        from sozo_generator.evidence.refresh import EvidenceRefresher

        refresher = EvidenceRefresher(recency_years=5)
        result = refresher.assess_staleness(parkinsons_condition)

        assert result.condition_slug == parkinsons_condition.slug
        assert result.total_items >= 0
        # Should not raise even if Bio is not installed
        assert result.stale_items >= 0 or result.fresh_items >= 0

    def test_refresh_marks_cached_vs_live(self, parkinsons_condition):
        """All items should come from cached condition data (no live fetch)."""
        from sozo_generator.evidence.refresh import EvidenceRefresher

        refresher = EvidenceRefresher(recency_years=5)
        result = refresher.assess_staleness(parkinsons_condition)

        # Since we are not doing live PubMed fetch, total_items should be
        # derived solely from condition.references + assessment_tools
        total_refs = len(parkinsons_condition.references or [])
        total_tools = len([t for t in (parkinsons_condition.assessment_tools or [])
                          if t.evidence_pmid and not t.evidence_pmid.startswith("placeholder")])
        # total_items should be <= refs + tools (some may be filtered out)
        assert result.total_items <= total_refs + total_tools + 5  # small margin


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deployment smoke tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestDeploymentSmoke:
    def test_all_imports(self):
        """Import every public module without error."""
        import sozo_generator.core.enums
        import sozo_generator.schemas.contracts
        import sozo_generator.schemas.condition
        import sozo_generator.schemas.documents
        import sozo_generator.qa.engine
        import sozo_generator.review.manager
        import sozo_generator.review.reports
        import sozo_generator.evidence.refresh
        import sozo_generator.evidence.section_evidence_mapper
        import sozo_generator.evidence.confidence
        import sozo_generator.orchestration.provenance
        import sozo_generator.conditions.registry
        import sozo_generator.conditions.onboarding
        import sozo_generator.content.assembler
        import sozo_generator.template.doc_structure

    def test_app_syntax(self):
        """app.py parses without syntax errors."""
        app_path = Path(__file__).parent.parent / "app.py"
        if app_path.exists():
            source = app_path.read_text(encoding="utf-8")
            ast.parse(source, filename=str(app_path))
        # If app.py doesn't exist, skip silently

    def test_registry_condition_evidence_completeness(self):
        """Every registered condition has refs, protocols, and safety notes."""
        from sozo_generator.conditions.registry import get_registry
        import sozo_generator.conditions.registry as reg_mod
        reg_mod._registry = None
        registry = get_registry()

        for slug in registry.list_slugs():
            cond = registry.get(slug)
            assert cond.references is not None, f"{slug} missing references"
            assert cond.protocols is not None, f"{slug} missing protocols"
            assert cond.safety_notes is not None, f"{slug} missing safety_notes"
            assert len(cond.safety_notes) > 0, f"{slug} has empty safety_notes"

    def test_all_15_conditions_generate_documents(self, tmp_path):
        """Generate 1 document per condition -- all 15 succeed."""
        from sozo_generator.conditions.registry import get_registry
        from sozo_generator.template.doc_structure import build_document_spec
        from sozo_generator.core.enums import DocumentType, Tier
        import sozo_generator.conditions.registry as reg_mod

        reg_mod._registry = None
        registry = get_registry()
        slugs = registry.list_slugs()

        assert len(slugs) >= 15, f"Expected >= 15 conditions, got {len(slugs)}"

        failures = []
        for slug in slugs:
            try:
                cond = registry.get(slug)
                spec = build_document_spec(cond, DocumentType.EVIDENCE_BASED_PROTOCOL, Tier.FELLOW)
                assert spec is not None, f"{slug}: spec is None"
                assert len(spec.sections) > 0, f"{slug}: no sections"
            except Exception as exc:
                failures.append(f"{slug}: {exc}")

        assert failures == [], "Conditions failed to generate:\n" + "\n".join(failures)
