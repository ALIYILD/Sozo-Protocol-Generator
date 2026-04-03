"""Tests for the canonical blueprint-driven generation path."""
import pytest
from pathlib import Path


# ── Spec Schema Tests ──────────────────────────────────────────────────────


class TestSpecSchemas:
    def test_document_blueprint(self):
        from sozo_generator.knowledge.specs import DocumentBlueprint, SectionBlueprint
        bp = DocumentBlueprint(
            slug="test",
            title_template="Test — {condition_name}",
            doc_type="test",
            sections=[
                SectionBlueprint(slug="s1", title="Section 1", tier="both", order=0),
                SectionBlueprint(slug="s2", title="Section 2", tier="partners", order=1),
                SectionBlueprint(slug="s3", title="Section 3", tier="fellow", order=2),
            ],
        )
        assert bp.slug == "test"
        assert len(bp.sections) == 3

        fellow = bp.get_sections_for_tier("fellow")
        assert len(fellow) == 2  # s1 (both) + s3 (fellow)
        assert fellow[0].slug == "s1"
        assert fellow[1].slug == "s3"

        partners = bp.get_sections_for_tier("partners")
        assert len(partners) == 2  # s1 (both) + s2 (partners)

    def test_section_blueprint(self):
        from sozo_generator.knowledge.specs import SectionBlueprint, VisualRequirement
        sb = SectionBlueprint(
            slug="protocols",
            title="Protocols",
            content_type="table",
            table_headers=["ID", "Label", "Target"],
            table_row_source="protocols",
            modality_filter="tdcs",
            visuals=[
                VisualRequirement(visual_type="qeeg_topomap"),
            ],
        )
        assert sb.modality_filter == "tdcs"
        assert len(sb.visuals) == 1

    def test_visual_requirement(self):
        from sozo_generator.knowledge.specs import VisualRequirement
        vr = VisualRequirement(
            visual_type="brain_map",
            caption_template="{condition_name} — Brain Targets",
            required=True,
        )
        assert vr.visual_type == "brain_map"
        assert "{condition_name}" in vr.caption_template


# ── Blueprint Loading Tests ────────────────────────────────────────────────


class TestBlueprintLoading:
    def test_load_evidence_based_protocol(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("evidence_based_protocol")
        assert bp is not None
        assert bp.doc_type == "evidence_based_protocol"
        assert len(bp.sections) >= 14

    def test_load_all_blueprints(self):
        from sozo_generator.knowledge.loader import load_blueprints
        bps = load_blueprints()
        assert "evidence_based_protocol" in bps

    def test_blueprint_has_tier_filtered_sections(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("evidence_based_protocol")
        fellow = bp.get_sections_for_tier("fellow")
        partners = bp.get_sections_for_tier("partners")
        # Partners should have MORE sections (network, symptom mapping)
        assert len(partners) > len(fellow)

    def test_blueprint_sections_have_order(self):
        from sozo_generator.knowledge.loader import load_blueprint
        bp = load_blueprint("evidence_based_protocol")
        orders = [s.order for s in bp.sections]
        assert orders == sorted(orders), "Sections should be ordered"

    def test_nonexistent_blueprint_returns_none(self):
        from sozo_generator.knowledge.loader import load_blueprint
        assert load_blueprint("nonexistent_xyz") is None


# ── Blueprint in KnowledgeBase Tests ───────────────────────────────────────


class TestBlueprintsInKB:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_blueprints_loaded(self, kb):
        assert len(kb.blueprints) >= 1
        assert "evidence_based_protocol" in kb.blueprints

    def test_get_blueprint(self, kb):
        bp = kb.get_blueprint("evidence_based_protocol")
        assert bp is not None
        assert bp.slug == "evidence_based_protocol"

    def test_list_blueprints(self, kb):
        slugs = kb.list_blueprints()
        assert "evidence_based_protocol" in slugs


# ── Canonical Assembler Tests ──────────────────────────────────────────────


class TestCanonicalAssembler:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_assemble_pd_fellow(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert spec.condition_slug == "parkinsons"
        assert spec.tier.value == "fellow"
        assert len(spec.sections) >= 10
        # Fellow should NOT have network_profiles or symptom_network_mapping
        section_ids = [s.section_id for s in spec.sections]
        assert "network_profiles" not in section_ids
        assert "symptom_network_mapping" not in section_ids

    def test_assemble_pd_partners(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("parkinsons", "evidence_based_protocol", "partners")
        section_ids = [s.section_id for s in spec.sections]
        # Partners SHOULD have network sections
        assert "network_profiles" in section_ids
        assert len(spec.sections) > 10

    def test_assemble_depression(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("depression", "evidence_based_protocol", "fellow")
        assert spec.condition_name == "Major Depressive Disorder"
        assert len(spec.sections) >= 10

    def test_assemble_migraine(self, kb):
        """Migraine only exists in knowledge system — proves YAML-only generation."""
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("migraine", "evidence_based_protocol", "fellow")
        assert spec.condition_name == "Migraine"
        assert len(spec.sections) >= 10

    def test_unknown_condition_raises(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        with pytest.raises(ValueError, match="not found"):
            assembler.assemble("nonexistent", "evidence_based_protocol", "fellow")

    def test_unknown_blueprint_raises(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        with pytest.raises(ValueError, match="not found"):
            assembler.assemble("parkinsons", "nonexistent", "fellow")

    def test_sections_have_content_or_tables(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        populated = 0
        for s in spec.sections:
            if s.content or s.tables or s.subsections:
                populated += 1
        assert populated >= 8, f"Only {populated} sections have content"

    def test_protocol_tables_filtered_by_modality(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        # Find tDCS section
        tdcs_section = next((s for s in spec.sections if s.section_id == "protocols_tdcs"), None)
        if tdcs_section and tdcs_section.tables:
            # All rows should be tDCS protocols
            for row in tdcs_section.tables[0].get("rows", []):
                # The protocol label should not be a TPS protocol
                assert "TPS" not in row[0], f"TPS protocol leaked into tDCS section: {row[0]}"

    def test_references_included(self, kb):
        from sozo_generator.knowledge.assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(kb)
        spec = assembler.assemble("parkinsons", "evidence_based_protocol", "fellow")
        assert len(spec.references) >= 3


# ── End-to-End Rendering Tests ─────────────────────────────────────────────


class TestCanonicalEndToEnd:
    def test_generate_canonical_pd_fellow(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "evidence_based_protocol", "fellow")
        assert result.success
        assert result.output_path
        assert Path(result.output_path).exists()
        assert Path(result.output_path).stat().st_size > 10000

    def test_generate_canonical_pd_partners(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("parkinsons", "evidence_based_protocol", "partners")
        assert result.success

    def test_generate_canonical_migraine(self):
        """Migraine generates from knowledge alone — no legacy Python builders."""
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("migraine", "evidence_based_protocol", "fellow")
        assert result.success
        assert Path(result.output_path).exists()

    def test_generate_canonical_all_knowledge_conditions(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        for condition in ["parkinsons", "depression", "adhd", "asd", "migraine"]:
            result = svc.generate_canonical(condition, "evidence_based_protocol", "fellow")
            assert result.success, f"Failed for {condition}: {result.error}"

    def test_generate_canonical_unknown_condition_fails(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_canonical("nonexistent", "evidence_based_protocol", "fellow")
        assert not result.success
        assert "not found" in result.error.lower()

    def test_canonical_and_legacy_both_work(self):
        """Verify both paths produce output for the same condition."""
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)

        # Canonical path (from knowledge)
        canon = svc.generate_canonical("parkinsons", "evidence_based_protocol", "fellow")
        assert canon.success

        # Legacy path (from registry)
        legacy = svc.generate(
            condition="parkinsons", tier="fellow",
            doc_type="evidence_based_protocol",
        )
        assert legacy[0].success

        # Both produced output
        assert Path(canon.output_path).exists()
        assert Path(legacy[0].output_path).exists()
