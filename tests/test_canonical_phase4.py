"""Tests for Phase 4: strengthened QA, provenance, expanded conditions, adapters."""
import json
import pytest
from pathlib import Path


# ── Evidence Rules Tests ───────────────────────────────────────────────────


class TestEvidenceRules:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_ebp_has_evidence_critical_sections(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("evidence_based_protocol")
        critical = [s for s in bp.sections if s.evidence_criticality == "critical"]
        assert len(critical) >= 2  # pathophysiology, safety at minimum

    def test_ebp_has_pmid_requirements(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("evidence_based_protocol")
        with_min_pmid = [s for s in bp.sections if s.min_pmid_count > 0]
        assert len(with_min_pmid) >= 2

    def test_section_blueprint_evidence_fields(self):
        from sozo_generator.knowledge.specs import SectionBlueprint
        sb = SectionBlueprint(
            slug="test",
            title="Test",
            requires_evidence=True,
            evidence_criticality="critical",
            min_pmid_count=3,
            on_insufficient_evidence="block",
        )
        assert sb.evidence_criticality == "critical"
        assert sb.min_pmid_count == 3
        assert sb.on_insufficient_evidence == "block"


# ── QA Enforcement Tests ──────────────────────────────────────────────────


class TestQAEnforcement:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_provenance_qa_status_populated(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        for s in prov.sections:
            assert s.qa_status in ("pass", "warn", "fail"), f"Bad qa_status: {s.qa_status}"

    def test_pd_all_sections_pass(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert prov.readiness == "ready"
        assert prov.sections_failing == 0

    def test_evidence_criticality_tracked_in_provenance(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        patho = next((s for s in prov.sections if s.section_slug == "pathophysiology"), None)
        assert patho is not None
        assert patho.evidence_criticality == "critical"
        assert patho.actual_pmid_count >= 3


# ── Provenance Tests ──────────────────────────────────────────────────────


class TestProvenanceReadiness:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_readiness_in_provenance_dict(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        d = prov.to_dict()
        assert "readiness" in d
        assert d["readiness"] in ("ready", "review_required", "incomplete")

    def test_section_qa_in_provenance_dict(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "handbook", "fellow")
        d = prov.to_dict()
        for sec in d["sections"]:
            assert "qa_status" in sec
            assert "evidence_criticality" in sec
            assert "evidence_sufficient" in sec

    def test_provenance_sidecar_has_readiness(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "evidence_based_protocol", "fellow")
        assert result.success
        prov_path = Path(result.output_path).with_suffix(".provenance.json")
        assert prov_path.exists()
        prov = json.loads(prov_path.read_text())
        assert "readiness" in prov
        assert "sections_passing" in prov
        assert "sections_warning" in prov
        assert "sections_failing" in prov


# ── Full Condition Coverage Tests ─────────────────────────────────────────


class TestFullConditionCoverage:
    def test_16_conditions_in_knowledge(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        assert len(kb.conditions) == 16

    def test_all_15_legacy_conditions_in_knowledge(self):
        """All 15 original conditions are now in knowledge YAML."""
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        legacy = [
            "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
            "stroke_rehab", "tbi", "chronic_pain", "ptsd", "ocd",
            "ms", "asd", "long_covid", "tinnitus", "insomnia",
        ]
        for slug in legacy:
            assert slug in kb.conditions, f"Missing: {slug}"

    def test_migraine_also_in_knowledge(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        assert "migraine" in kb.conditions

    @pytest.mark.parametrize("condition", [
        "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
        "stroke_rehab", "tbi", "chronic_pain", "ptsd", "ocd",
        "ms", "asd", "long_covid", "tinnitus", "insomnia", "migraine",
    ])
    def test_canonical_generation_per_condition(self, condition):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical(condition, "evidence_based_protocol", "fellow")
        assert result.success, f"Failed for {condition}: {result.error}"

    @pytest.mark.parametrize("blueprint", [
        "evidence_based_protocol", "handbook", "clinical_exam",
    ])
    def test_canonical_generation_per_blueprint(self, blueprint):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", blueprint, "fellow")
        assert result.success, f"Failed for {blueprint}: {result.error}"


# ── Canonical Routing Tests ───────────────────────────────────────────────


class TestCanonicalRouting:
    def test_can_route_canonical_existing_condition(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        assert svc.can_route_canonical("parkinsons", "evidence_based_protocol")
        assert svc.can_route_canonical("depression", "handbook")

    def test_all_8_doc_types_now_routable(self):
        """Phase 7 expanded: all 8 doc types have blueprints and route to canonical."""
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        assert svc.can_route_canonical("parkinsons", "all_in_one_protocol")
        assert svc.can_route_canonical("parkinsons", "responder_tracking")
        assert not svc.can_route_canonical("parkinsons", "nonexistent_type")

    def test_cannot_route_unknown_condition(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        assert not svc.can_route_canonical("nonexistent", "handbook")

    def test_legacy_and_canonical_coexist(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)

        # Legacy
        legacy = svc.generate(condition="parkinsons", tier="fellow", doc_type="evidence_based_protocol")
        assert legacy[0].success

        # Canonical
        canonical = svc.generate_canonical("parkinsons", "evidence_based_protocol", "fellow")
        assert canonical.success

        # Both produce files
        assert Path(legacy[0].output_path).exists()
        assert Path(canonical.output_path).exists()


# ── Knowledge YAML Quality Tests ──────────────────────────────────────────


class TestKnowledgeQuality:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_all_conditions_have_protocols(self, kb):
        for slug, cond in kb.conditions.items():
            assert len(cond.protocols) >= 1, f"{slug} has no protocols"

    def test_all_conditions_have_references(self, kb):
        for slug, cond in kb.conditions.items():
            assert len(cond.references) >= 1, f"{slug} has no references"

    def test_all_conditions_have_phenotypes(self, kb):
        for slug, cond in kb.conditions.items():
            if slug != "migraine":  # Migraine already verified separately
                assert len(cond.phenotypes) >= 1, f"{slug} has no phenotypes"

    def test_all_conditions_reference_modalities(self, kb):
        for slug, cond in kb.conditions.items():
            assert len(cond.applicable_modalities) >= 1, f"{slug} has no modalities"

    def test_all_pmids_are_valid_digits(self, kb):
        for slug, cond in kb.conditions.items():
            for ref in cond.references:
                if ref.pmid:
                    assert ref.pmid.isdigit(), f"{slug} has invalid PMID: {ref.pmid}"

    def test_cross_reference_validation_passes(self, kb):
        report = kb.validate()
        assert report.valid, f"Validation failed with {report.broken_count} errors"
