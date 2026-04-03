"""Tests for Phase 6: fidelity, persistent review, batch workflows, retirement."""
import json
import pytest
from pathlib import Path


# ── Fidelity Improvement Tests ────────────────────────────────────────────


class TestOutputFidelity:
    @pytest.fixture(scope="class")
    def pd_spec(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        kb = KnowledgeBase()
        kb.load_all()
        assembler = CanonicalDocumentAssembler(kb)
        spec, _ = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        return spec

    def test_audience_is_tier_specific(self, pd_spec):
        assert pd_spec.audience == "Fellow clinician"

    def test_document_control_has_governance(self, pd_spec):
        dc = next(s for s in pd_spec.sections if s.section_id == "document_control")
        assert "SOZO Brain Center" in dc.content
        assert "GOVERNANCE RULE" in dc.content
        assert "Doctor authorization" in dc.content

    def test_document_control_has_icd10(self, pd_spec):
        dc = next(s for s in pd_spec.sections if s.section_id == "document_control")
        assert "G20" in dc.content  # PD ICD-10

    def test_followup_section_present(self, pd_spec):
        section_ids = [s.section_id for s in pd_spec.sections]
        assert "followup" in section_ids

    def test_evidence_summary_section_present(self, pd_spec):
        section_ids = [s.section_id for s in pd_spec.sections]
        assert "evidence_summary" in section_ids

    def test_section_count_matches_blueprint(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("evidence_based_protocol")
        fellow_sections = bp.get_sections_for_tier("fellow")

        from sozo_generator.knowledge.base import KnowledgeBase
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        kb = KnowledgeBase()
        kb.load_all()
        assembler = CanonicalDocumentAssembler(kb)
        spec, _ = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert len(spec.sections) == len(fellow_sections)

    def test_partners_audience(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        kb = KnowledgeBase()
        kb.load_all()
        assembler = CanonicalDocumentAssembler(kb)
        spec, _ = assembler.assemble("parkinsons", "evidence_based_protocol", "partners")
        assert spec.audience == "Partner clinician"


# ── Review Store Persistence Tests ────────────────────────────────────────


class TestReviewPersistence:
    def test_review_store_save_load(self, tmp_path):
        from sozo_generator.knowledge.batch import ReviewStore
        store = ReviewStore(tmp_path / "reviews")

        review_data = {
            "build_id": "test-001",
            "condition": "parkinsons",
            "status": "approved",
            "readiness": "ready",
            "updated_at": "2026-04-03",
        }
        store.save_review("test-001", review_data)

        loaded = store.load_review("test-001")
        assert loaded is not None
        assert loaded["status"] == "approved"

    def test_review_store_list(self, tmp_path):
        from sozo_generator.knowledge.batch import ReviewStore
        store = ReviewStore(tmp_path / "reviews")

        for i in range(3):
            store.save_review(f"test-{i}", {
                "build_id": f"test-{i}",
                "condition": f"cond-{i}",
                "status": "draft",
            })

        reviews = store.list_reviews()
        assert len(reviews) == 3

    def test_review_store_find_by_condition(self, tmp_path):
        from sozo_generator.knowledge.batch import ReviewStore
        store = ReviewStore(tmp_path / "reviews")

        store.save_review("pd-1", {"condition": "parkinsons", "status": "approved"})
        store.save_review("pd-2", {"condition": "parkinsons", "status": "draft"})
        store.save_review("dep-1", {"condition": "depression", "status": "draft"})

        pd_reviews = store.find_by_condition("parkinsons")
        assert len(pd_reviews) == 2


# ── Batch Workflow Tests ──────────────────────────────────────────────────


class TestBatchWorkflows:
    def test_readiness_report(self):
        from sozo_generator.knowledge.batch import BatchRunner
        runner = BatchRunner()
        report = runner.readiness_report("fellow")
        assert report.total == 128  # 16 conditions × 8 blueprints
        assert report.succeeded == 128
        assert report.failed == 0

    def test_readiness_report_text(self):
        from sozo_generator.knowledge.batch import BatchRunner
        runner = BatchRunner()
        report = runner.readiness_report("fellow")
        text = report.to_text()
        assert "BATCH REPORT" in text
        assert "Succeeded: 128" in text

    def test_generate_condition(self):
        from sozo_generator.knowledge.batch import BatchRunner
        runner = BatchRunner()
        report = runner.generate_condition("parkinsons", "fellow")
        assert report.total == 8  # 8 blueprints
        assert report.succeeded == 8

    def test_generate_blueprint(self):
        from sozo_generator.knowledge.batch import BatchRunner
        runner = BatchRunner()
        # Generate handbook for first 3 conditions only (faster)
        report = runner.generate_all_canonical(
            conditions=["parkinsons", "depression", "migraine"],
            blueprints=["handbook"],
            tier="fellow",
        )
        assert report.total == 3
        assert report.succeeded == 3

    def test_batch_report_save(self, tmp_path):
        from sozo_generator.knowledge.batch import BatchReport, BatchResult
        report = BatchReport(operation="test")
        report.results.append(BatchResult(
            condition="parkinsons", blueprint="handbook", tier="fellow",
            success=True, readiness="ready",
        ))
        report.finalize()

        path = tmp_path / "report.json"
        report.save(path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["succeeded"] == 1


# ── Retirement Matrix Tests ──────────────────────────────────────────────


class TestRetirementMatrix:
    def test_canonical_default_types_are_routed(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        for dt in ["evidence_based_protocol", "handbook", "clinical_exam"]:
            assert svc.can_route_canonical("parkinsons", dt), f"{dt} should be routable"

    def test_all_8_types_now_routable(self):
        """All 8 doc types now have canonical blueprints and route to canonical."""
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        for dt in ["all_in_one_protocol", "phenotype_classification", "responder_tracking",
                    "psych_intake", "network_assessment"]:
            assert svc.can_route_canonical("parkinsons", dt), f"{dt} should be routable"

    def test_all_conditions_routable_for_canonical_types(self):
        from sozo_generator.generation.service import GenerationService
        from sozo_generator.knowledge.base import KnowledgeBase
        svc = GenerationService()
        kb = KnowledgeBase()
        kb.load_all()

        for cond in kb.list_conditions():
            for dt in ["evidence_based_protocol", "handbook", "clinical_exam"]:
                assert svc.can_route_canonical(cond, dt), f"{cond}/{dt} should be routable"
