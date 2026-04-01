"""Tests for sozo_generator.orchestration.versioning and batch report finalization."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sozo_generator.core.enums import ReviewStatus
from sozo_generator.schemas.contracts import (
    BatchBuildReport,
    BatchConditionResult,
    BuildManifest,
    DocumentBuildEntry,
    QAReport,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ManifestWriter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestManifestWriter:
    def test_create_manifest_valid(self, tmp_path):
        from sozo_generator.orchestration.versioning import ManifestWriter

        writer = ManifestWriter(tmp_path / "manifests")

        # Create fake document outputs
        doc_path = tmp_path / "test_doc.docx"
        doc_path.write_text("fake docx content")

        manifest = writer.create_manifest(
            build_id="build-test-20260401",
            condition_slug="parkinsons",
            condition_name="Parkinson's Disease",
            document_outputs={"fellow_clinical_exam": doc_path},
        )

        assert isinstance(manifest, BuildManifest)
        assert manifest.build_id == "build-test-20260401"
        assert manifest.condition_slug == "parkinsons"
        assert manifest.total_documents == 1
        assert manifest.total_passed == 1  # no QA issues
        assert manifest.content_hash != ""
        assert len(manifest.content_hash) == 16

    def test_create_manifest_multiple_docs(self, tmp_path):
        from sozo_generator.orchestration.versioning import ManifestWriter

        writer = ManifestWriter(tmp_path / "manifests")

        docs = {}
        for name in ["fellow_clinical_exam", "partners_handbook", "fellow_protocol"]:
            p = tmp_path / f"{name}.docx"
            p.write_text(f"content of {name}")
            docs[name] = p

        manifest = writer.create_manifest(
            build_id="build-multi-001",
            condition_slug="test",
            condition_name="Test",
            document_outputs=docs,
        )
        assert manifest.total_documents == 3

    def test_save_load_roundtrip(self, tmp_path):
        from sozo_generator.orchestration.versioning import ManifestWriter

        writer = ManifestWriter(tmp_path / "manifests")

        doc_path = tmp_path / "doc.docx"
        doc_path.write_text("content")

        manifest = writer.create_manifest(
            build_id="build-roundtrip-001",
            condition_slug="test",
            condition_name="Test Condition",
            document_outputs={"fellow_clinical_exam": doc_path},
        )
        saved_path = writer.save_manifest(manifest)
        assert saved_path.exists()

        loaded = writer.load_manifest("build-roundtrip-001")
        assert loaded is not None
        assert loaded.build_id == manifest.build_id
        assert loaded.condition_slug == manifest.condition_slug
        assert loaded.content_hash == manifest.content_hash
        assert loaded.total_documents == manifest.total_documents

    def test_load_nonexistent_returns_none(self, tmp_path):
        from sozo_generator.orchestration.versioning import ManifestWriter

        writer = ManifestWriter(tmp_path / "manifests")
        assert writer.load_manifest("nonexistent") is None

    def test_list_manifests(self, tmp_path):
        from sozo_generator.orchestration.versioning import ManifestWriter

        writer = ManifestWriter(tmp_path / "manifests")

        for slug in ["alpha", "beta"]:
            doc_path = tmp_path / f"{slug}.docx"
            doc_path.write_text("content")
            m = writer.create_manifest(
                build_id=f"build-{slug}-001",
                condition_slug=slug,
                condition_name=slug.title(),
                document_outputs={f"fellow_clinical_exam": doc_path},
            )
            writer.save_manifest(m)

        all_ids = writer.list_manifests()
        assert len(all_ids) == 2

        alpha_ids = writer.list_manifests(condition_slug="alpha")
        assert len(alpha_ids) == 1
        assert "alpha" in alpha_ids[0]

    def test_manifest_with_qa_report(self, tmp_path):
        from sozo_generator.orchestration.versioning import ManifestWriter
        from sozo_generator.core.enums import QASeverity
        from sozo_generator.schemas.contracts import QAIssue

        writer = ManifestWriter(tmp_path / "manifests")
        doc_path = tmp_path / "doc.docx"
        doc_path.write_text("content")

        qa_report = QAReport(
            report_id="qa-001",
            condition_slug="test",
            issues=[
                QAIssue(
                    severity=QASeverity.BLOCK,
                    category="safety",
                    location="safety.no_notes",
                    message="Missing safety notes",
                ),
            ],
            block_count=1,
        )

        manifest = writer.create_manifest(
            build_id="build-qa-001",
            condition_slug="test",
            condition_name="Test",
            document_outputs={"fellow_clinical_exam": doc_path},
            qa_summary=qa_report,
        )
        assert manifest.qa_summary is not None
        assert manifest.qa_summary.block_count == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# compute_file_hash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestComputeFileHash:
    def test_consistent_hash(self, tmp_path):
        from sozo_generator.orchestration.versioning import compute_file_hash

        f = tmp_path / "test.txt"
        f.write_text("Hello, world!")
        h1 = compute_file_hash(f)
        h2 = compute_file_hash(f)
        assert h1 == h2
        assert len(h1) == 16

    def test_different_content_different_hash(self, tmp_path):
        from sozo_generator.orchestration.versioning import compute_file_hash

        f1 = tmp_path / "a.txt"
        f1.write_text("content A")
        f2 = tmp_path / "b.txt"
        f2.write_text("content B")
        assert compute_file_hash(f1) != compute_file_hash(f2)

    def test_missing_file_returns_empty(self, tmp_path):
        from sozo_generator.orchestration.versioning import compute_file_hash

        h = compute_file_hash(tmp_path / "nonexistent.txt")
        assert h == ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# create_build_id
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestCreateBuildId:
    def test_format(self):
        from sozo_generator.orchestration.versioning import create_build_id

        bid = create_build_id("parkinsons")
        assert bid.startswith("build-parkinsons-")
        # Should have a timestamp suffix
        parts = bid.split("-")
        assert len(parts) == 3
        assert parts[2].isdigit()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BatchBuildReport.finalize
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestBatchBuildReportFinalize:
    def test_finalize_computes_counts(self):
        results = [
            BatchConditionResult(
                condition_slug="a", success=True, documents_generated=4
            ),
            BatchConditionResult(
                condition_slug="b",
                success=True,
                documents_generated=2,
                documents_blocked=1,
            ),
            BatchConditionResult(
                condition_slug="c",
                success=False,
                error="Import failed",
            ),
        ]
        report = BatchBuildReport(
            batch_id="batch-test",
            total_conditions=3,
            results=results,
        )
        report.finalize()

        assert report.successful_conditions == 2
        assert report.failed_conditions == 1
        assert report.blocked_conditions == 1
        assert report.total_documents == 6
        assert report.completed_at is not None
        assert len(report.retry_suggestions) == 1
        assert "c" in report.retry_suggestions[0]

    def test_finalize_all_success(self):
        results = [
            BatchConditionResult(condition_slug="a", success=True, documents_generated=3),
            BatchConditionResult(condition_slug="b", success=True, documents_generated=5),
        ]
        report = BatchBuildReport(
            batch_id="batch-ok",
            total_conditions=2,
            results=results,
        )
        report.finalize()

        assert report.successful_conditions == 2
        assert report.failed_conditions == 0
        assert report.total_documents == 8
        assert report.retry_suggestions == []

    def test_finalize_empty(self):
        report = BatchBuildReport(batch_id="batch-empty", total_conditions=0)
        report.finalize()
        assert report.successful_conditions == 0
        assert report.total_documents == 0
        assert report.completed_at is not None
