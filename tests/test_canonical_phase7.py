"""Tests for Phase 7: full blueprint coverage, release governance, batch signoff."""
import json
import pytest
from pathlib import Path


# ── Full Blueprint Coverage ───────────────────────────────────────────────


class TestAllBlueprintsExist:
    def test_8_blueprints_loaded(self):
        from sozo_generator.knowledge.loader import load_blueprints
        bps = load_blueprints()
        assert len(bps) == 8
        expected = [
            "evidence_based_protocol", "handbook", "clinical_exam",
            "all_in_one_protocol", "phenotype_classification",
            "responder_tracking", "psych_intake", "network_assessment",
        ]
        for slug in expected:
            assert slug in bps, f"Missing blueprint: {slug}"

    def test_network_assessment_is_partners_only(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("network_assessment")
        assert "partners" in bp.applicable_tiers
        assert "fellow" not in bp.applicable_tiers


class TestAllBlueprintsGenerate:
    @pytest.mark.parametrize("blueprint", [
        "evidence_based_protocol", "handbook", "clinical_exam",
        "all_in_one_protocol", "phenotype_classification",
        "responder_tracking", "psych_intake",
    ])
    def test_generate_canonical_fellow(self, blueprint):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", blueprint, "fellow")
        assert result.success, f"Failed: {blueprint}: {result.error}"

    def test_generate_network_assessment_partners(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "network_assessment", "partners")
        assert result.success


# ── All Doc Types Route to Canonical ──────────────────────────────────────


class TestCanonicalRoutingAll8:
    @pytest.mark.parametrize("doc_type", [
        "evidence_based_protocol", "handbook", "clinical_exam",
        "all_in_one_protocol", "phenotype_classification",
        "responder_tracking", "psych_intake", "network_assessment",
    ])
    def test_can_route_canonical(self, doc_type):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        assert svc.can_route_canonical("parkinsons", doc_type)

    def test_generate_routes_all_to_canonical(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        for dt in ["evidence_based_protocol", "handbook", "clinical_exam",
                    "all_in_one_protocol", "phenotype_classification",
                    "responder_tracking", "psych_intake"]:
            results = svc.generate(condition="parkinsons", tier="fellow", doc_type=dt)
            assert results[0].build_id.startswith("canon-"), f"{dt} not routed to canonical"


# ── Release Governance ────────────────────────────────────────────────────


class TestReleaseGovernance:
    @pytest.fixture
    def pd_provenance(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        kb = KnowledgeBase()
        kb.load_all()
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        return prov

    def test_release_blocked_without_approval(self, pd_provenance):
        from sozo_generator.knowledge.release import check_release_eligibility
        result = check_release_eligibility(pd_provenance)
        assert not result.eligible
        assert any("review state" in b.lower() or "reviewed" in b.lower() for b in result.blockers)

    def test_release_eligible_with_approval(self, pd_provenance):
        from sozo_generator.knowledge.release import check_release_eligibility, ReleasePolicy
        from sozo_generator.knowledge.review import ReviewState

        review = ReviewState.from_provenance(pd_provenance)
        review.approve("Dr. Smith", "Reviewed and approved")

        result = check_release_eligibility(pd_provenance, review_state=review)
        assert result.eligible or result.status == "conditional"

    def test_release_blocked_with_placeholders(self, pd_provenance):
        from sozo_generator.knowledge.release import check_release_eligibility, ReleasePolicy
        from sozo_generator.knowledge.review import ReviewState

        # Simulate placeholders
        pd_provenance.placeholder_sections = 3

        review = ReviewState.from_provenance(pd_provenance)
        review.approve("Dr. Smith", "Approved")

        result = check_release_eligibility(pd_provenance, review_state=review)
        assert not result.eligible
        assert any("placeholder" in b.lower() for b in result.blockers)

    def test_release_gate_text_output(self, pd_provenance):
        from sozo_generator.knowledge.release import check_release_eligibility
        result = check_release_eligibility(pd_provenance)
        text = result.to_text()
        assert "Release Status" in text

    def test_signoff_report(self):
        from sozo_generator.knowledge.release import generate_signoff_report
        results = [
            {"condition": "parkinsons", "blueprint": "handbook", "success": True, "readiness": "ready"},
            {"condition": "depression", "blueprint": "handbook", "success": True, "readiness": "review_required"},
            {"condition": "migraine", "blueprint": "handbook", "success": False, "readiness": "incomplete", "error": "test"},
        ]
        report = generate_signoff_report(results)
        assert "Total: 3" in report
        assert "parkinsons" in report


# ── Batch Full Matrix ────────────────────────────────────────────────────


class TestBatchFullMatrix:
    def test_128_combinations_fellow(self):
        from sozo_generator.knowledge.batch import BatchRunner
        runner = BatchRunner()
        report = runner.readiness_report("fellow")
        assert report.total == 128  # 16 conditions × 8 blueprints
        assert report.succeeded == 128
        assert report.failed == 0
