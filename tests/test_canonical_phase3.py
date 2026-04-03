"""Tests for Phase 3: expanded canonical coverage, provenance, migration."""
import json
import pytest
from pathlib import Path


# ── Blueprint Coverage Tests ───────────────────────────────────────────────


class TestBlueprintCoverage:
    def test_three_blueprints_exist(self):
        from sozo_generator.knowledge.loader import load_blueprints
        bps = load_blueprints()
        assert "evidence_based_protocol" in bps
        assert "handbook" in bps
        assert "clinical_exam" in bps

    def test_handbook_has_stage_sections(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("handbook")
        slugs = [s.slug for s in bp.sections]
        assert "stage_1" in slugs
        assert "stage_4" in slugs
        assert "stage_7" in slugs
        assert "stage_8" in slugs

    def test_handbook_partners_has_fnon(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("handbook")
        partner_sections = bp.get_sections_for_tier("partners")
        slugs = [s.slug for s in partner_sections]
        assert "fnon_framework" in slugs

    def test_handbook_fellow_no_fnon(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("handbook")
        fellow_sections = bp.get_sections_for_tier("fellow")
        slugs = [s.slug for s in fellow_sections]
        assert "fnon_framework" not in slugs

    def test_clinical_exam_partners_has_network_assessment(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("clinical_exam")
        partner_sections = bp.get_sections_for_tier("partners")
        slugs = [s.slug for s in partner_sections]
        assert "network_assessment" in slugs

    def test_clinical_exam_fellow_no_network_assessment(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("clinical_exam")
        fellow_sections = bp.get_sections_for_tier("fellow")
        slugs = [s.slug for s in fellow_sections]
        assert "network_assessment" not in slugs


# ── Shared Clinical Logic in Knowledge ─────────────────────────────────────


class TestSharedClinicalLogic:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_patient_journey_stages_in_knowledge(self, kb):
        rules = kb.get_shared_rules("patient_journey")
        assert len(rules) == 8
        slugs = [r.slug for r in rules]
        assert "patient_journey_stage_1" in slugs
        assert "patient_journey_stage_8" in slugs

    def test_responder_classification_in_knowledge(self, kb):
        rules = kb.get_shared_rules("responder")
        assert len(rules) >= 2
        slugs = [r.slug for r in rules]
        assert "responder_classification" in slugs
        assert "fnon_level5_pathway" in slugs

    def test_responder_classification_has_thresholds(self, kb):
        rules = kb.get_shared_rules("responder")
        rc = next(r for r in rules if r.slug == "responder_classification")
        assert "30%" in rc.rule_text
        assert "15-29%" in rc.rule_text or "15%" in rc.rule_text
        assert "Week 4" in rc.rule_text
        assert "Week 8" in rc.rule_text

    def test_fnon_level5_has_6_steps(self, kb):
        rules = kb.get_shared_rules("responder")
        l5 = next(r for r in rules if r.slug == "fnon_level5_pathway")
        # Should mention the 6-step reassessment
        assert "6-Network" in l5.rule_text or "re-evaluate" in l5.rule_text.lower()
        assert "Doctor review" in l5.rule_text


# ── Provenance Tests ───────────────────────────────────────────────────────


class TestAssemblyProvenance:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_provenance_returned(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert prov is not None
        assert prov.condition_slug == "parkinsons"
        assert prov.blueprint_slug == "evidence_based_protocol"
        assert prov.tier == "fellow"

    def test_provenance_section_count(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert prov.total_sections == len(spec.sections)
        assert prov.total_sections >= 10

    def test_provenance_tracks_knowledge_fields(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        # pathophysiology section should track its knowledge fields
        patho = next((s for s in prov.sections if s.section_slug == "pathophysiology"), None)
        assert patho is not None
        assert "pathophysiology" in patho.knowledge_fields_used

    def test_provenance_tracks_evidence(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert prov.total_evidence_pmids > 0

    def test_provenance_tracks_visuals(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "evidence_based_protocol", "partners")
        assert prov.total_visuals_requested > 0
        # Protocol sections should request visuals
        tdcs = next((s for s in prov.sections if s.section_slug == "protocols_tdcs"), None)
        assert tdcs is not None
        assert len(tdcs.visual_types_requested) >= 1

    def test_provenance_serializes_to_dict(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        _, prov = assembler.assemble("parkinsons", "handbook", "fellow")
        d = prov.to_dict()
        assert "sections" in d
        assert d["condition_slug"] == "parkinsons"
        # Verify JSON-serializable
        json.dumps(d)

    def test_provenance_sidecar_written(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "evidence_based_protocol", "fellow")
        assert result.success
        prov_path = Path(result.output_path).with_suffix(".provenance.json")
        assert prov_path.exists()
        prov = json.loads(prov_path.read_text())
        assert prov["condition_slug"] == "parkinsons"
        assert prov["total_sections"] >= 10


# ── Multi-Blueprint Generation Tests ──────────────────────────────────────


class TestMultiBlueprintGeneration:
    def test_generate_handbook_pd_fellow(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "handbook", "fellow")
        assert result.success
        assert Path(result.output_path).stat().st_size > 10000

    def test_generate_handbook_pd_partners(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "handbook", "partners")
        assert result.success

    def test_generate_clinical_exam_pd_fellow(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "clinical_exam", "fellow")
        assert result.success

    def test_generate_clinical_exam_pd_partners(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "clinical_exam", "partners")
        assert result.success

    def test_generate_all_blueprints_for_migraine(self):
        """Migraine has no legacy builder — pure knowledge path."""
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        for bp in ["evidence_based_protocol", "handbook", "clinical_exam"]:
            result = svc.generate_canonical("migraine", bp, "fellow")
            assert result.success, f"Failed: migraine/{bp}: {result.error}"

    def test_generate_all_conditions_all_blueprints(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        conditions = ["parkinsons", "depression", "adhd", "asd", "migraine"]
        blueprints = ["evidence_based_protocol", "handbook", "clinical_exam"]
        for cond in conditions:
            for bp in blueprints:
                result = svc.generate_canonical(cond, bp, "fellow")
                assert result.success, f"Failed: {cond}/{bp}: {result.error}"

    def test_partners_has_more_sections_than_fellow(self):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        assembler = CanonicalDocumentAssembler(kb)

        fellow_spec, _ = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        partners_spec, _ = assembler.assemble("parkinsons", "evidence_based_protocol", "partners")
        assert len(partners_spec.sections) > len(fellow_spec.sections)
