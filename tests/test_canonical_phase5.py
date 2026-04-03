"""Tests for Phase 5: canonical-by-default routing, review workflow, regression, validation."""
import json
import pytest
from pathlib import Path


# ── Canonical-by-Default Routing ──────────────────────────────────────────


class TestCanonicalByDefault:
    def test_generate_routes_ebp_to_canonical(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        results = svc.generate(condition="parkinsons", tier="fellow", doc_type="evidence_based_protocol")
        assert results[0].success
        assert results[0].build_id.startswith("canon-")

    def test_generate_routes_handbook_to_canonical(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        results = svc.generate(condition="depression", tier="fellow", doc_type="handbook")
        assert results[0].success
        assert results[0].build_id.startswith("canon-")

    def test_generate_routes_clinical_exam_to_canonical(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        results = svc.generate(condition="adhd", tier="fellow", doc_type="clinical_exam")
        assert results[0].success
        assert results[0].build_id.startswith("canon-")

    def test_generate_keeps_legacy_for_non_canonical_types(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        results = svc.generate(condition="parkinsons", tier="fellow", doc_type="all_in_one_protocol")
        assert results[0].success
        assert results[0].build_id.startswith("build-")

    def test_canonical_produces_provenance_sidecar(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        results = svc.generate(condition="parkinsons", tier="fellow", doc_type="evidence_based_protocol")
        prov_path = Path(results[0].output_path).with_suffix(".provenance.json")
        assert prov_path.exists()

    def test_legacy_does_not_produce_provenance(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        results = svc.generate(condition="parkinsons", tier="fellow", doc_type="all_in_one_protocol")
        prov_path = Path(results[0].output_path).with_suffix(".provenance.json")
        assert not prov_path.exists()


# ── Review Workflow ───────────────────────────────────────────────────────


class TestReviewWorkflow:
    @pytest.fixture
    def provenance(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        kb = KnowledgeBase()
        kb.load_all()
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        return prov

    def test_review_state_from_provenance(self, provenance):
        from sozo_generator.knowledge.review import ReviewState
        state = ReviewState.from_provenance(provenance, build_id="test-review")
        assert state.build_id == "test-review"
        assert state.condition == "parkinsons"
        assert state.status in ("draft", "review_required")

    def test_review_summary_built(self, provenance):
        from sozo_generator.knowledge.review import build_review_summary
        summary = build_review_summary(provenance)
        assert summary.readiness in ("ready", "review_required", "incomplete")
        assert summary.total_sections > 0
        assert summary.recommendation

    def test_review_summary_text(self, provenance):
        from sozo_generator.knowledge.review import build_review_summary
        summary = build_review_summary(provenance)
        text = summary.to_text()
        assert "REVIEW SUMMARY" in text
        assert "Condition: parkinsons" in text
        assert "RECOMMENDATION" in text

    def test_approve_reject_finalize(self, provenance):
        from sozo_generator.knowledge.review import ReviewState
        state = ReviewState.from_provenance(provenance)

        # Cannot finalize before approval
        with pytest.raises(ValueError):
            state.finalize("reviewer1")

        # Approve
        state.approve("reviewer1", "Content reviewed and accurate")
        assert state.status == "approved"

        # Finalize
        state.finalize("reviewer1")
        assert state.status == "finalized"
        assert len(state.decisions) == 2

    def test_reject_workflow(self, provenance):
        from sozo_generator.knowledge.review import ReviewState
        state = ReviewState.from_provenance(provenance)
        state.reject("reviewer1", "Insufficient evidence in pathophysiology section")
        assert state.status == "rejected"

    def test_review_state_serialization(self, provenance):
        from sozo_generator.knowledge.review import ReviewState
        state = ReviewState.from_provenance(provenance, build_id="serial-test")
        state.approve("reviewer1", "OK")
        d = state.to_dict()
        assert d["status"] == "approved"
        assert len(d["decisions"]) == 1
        json.dumps(d)  # Must be JSON-serializable


# ── Regression Comparison ────────────────────────────────────────────────


class TestRegressionComparison:
    def test_compare_pd_ebp(self):
        from sozo_generator.knowledge.regression import compare_outputs
        result = compare_outputs("parkinsons", "evidence_based_protocol", "fellow")
        assert result is not None
        assert result.legacy_section_count > 0
        assert result.canonical_section_count > 0
        assert result.parity_score > 0.3

    def test_compare_pd_handbook(self):
        from sozo_generator.knowledge.regression import compare_outputs
        result = compare_outputs("parkinsons", "handbook", "fellow")
        assert result is not None
        assert result.parity_score > 0.3

    def test_safe_to_route_check(self):
        from sozo_generator.knowledge.regression import compare_outputs
        result = compare_outputs("parkinsons", "evidence_based_protocol", "fellow")
        assert result is not None
        assert result.safe_to_route  # PD EBP should be safe

    def test_compare_text_output(self):
        from sozo_generator.knowledge.regression import compare_outputs
        result = compare_outputs("parkinsons", "evidence_based_protocol", "fellow")
        text = result.to_text()
        assert "REGRESSION COMPARISON" in text
        assert "Parity score" in text

    def test_compare_returns_none_for_unknown(self):
        from sozo_generator.knowledge.regression import compare_outputs
        result = compare_outputs("nonexistent", "handbook", "fellow")
        assert result is None


# ── YAML Validation ──────────────────────────────────────────────────────


class TestYAMLValidation:
    def test_validate_all(self):
        from sozo_generator.knowledge.validate import validate_all
        report = validate_all()
        assert report.files_checked >= 20  # conditions + modalities + blueprints
        assert report.files_valid >= 15

    def test_validate_passes(self):
        from sozo_generator.knowledge.validate import validate_all
        report = validate_all()
        assert report.passed, f"Validation failed: {report.to_text()}"

    def test_validate_single_condition(self):
        from sozo_generator.knowledge.validate import validate_condition
        report = validate_condition("parkinsons")
        assert report.files_checked == 1
        assert report.files_valid == 1

    def test_validate_nonexistent_condition(self):
        from sozo_generator.knowledge.validate import validate_condition
        report = validate_condition("nonexistent_xyz")
        assert report.files_checked == 0
        assert any(i.severity == "error" for i in report.issues)

    def test_validation_report_text(self):
        from sozo_generator.knowledge.validate import validate_all
        report = validate_all()
        text = report.to_text()
        assert "VALIDATION REPORT" in text
        assert "Files checked" in text
