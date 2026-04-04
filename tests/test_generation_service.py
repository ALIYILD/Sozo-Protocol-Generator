"""Tests for the canonical GenerationService."""
import pytest

from sozo_generator.generation.service import GenerationService, GenerationResult
from sozo_generator.schemas.definitions import (
    get_document_definition,
    get_all_document_definitions,
    DocumentDefinition,
    VisualSpec,
    SectionSpec,
    GenerationRequest,
)
from sozo_generator.core.enums import DocumentType, Tier
from sozo_generator.core.data_loader import (
    load_shared_protocol_data,
    load_protocol_data,
    list_available_conditions,
)


# ── Document Definitions ────────────────────────────────────────────────────


class TestDocumentDefinitions:
    def test_all_8_types_defined(self):
        defs = get_all_document_definitions()
        assert len(defs) == 8
        for dt in DocumentType:
            assert dt in defs, f"Missing definition for {dt.value}"

    def test_network_assessment_partners_only(self):
        defn = get_document_definition(DocumentType.NETWORK_ASSESSMENT)
        assert Tier.PARTNERS in defn.applicable_tiers
        assert Tier.FELLOW not in defn.applicable_tiers

    def test_evidence_protocol_has_evidence_appendix(self):
        defn = get_document_definition(DocumentType.EVIDENCE_BASED_PROTOCOL)
        assert defn.requires_evidence_appendix is True
        assert len(defn.sections) >= 10

    def test_all_definitions_have_display_name(self):
        for dt, defn in get_all_document_definitions().items():
            assert defn.display_name, f"{dt.value} missing display_name"

    def test_visual_specs_on_protocol(self):
        defn = get_document_definition(DocumentType.EVIDENCE_BASED_PROTOCOL)
        assert len(defn.visuals) >= 1
        assert all(isinstance(v, VisualSpec) for v in defn.visuals)

    def test_section_specs_have_ids(self):
        for dt, defn in get_all_document_definitions().items():
            for sec in defn.sections:
                assert sec.section_id, f"{dt.value} section missing section_id"

    def test_template_names_exist(self):
        import os
        from pathlib import Path
        templates_dir = Path(__file__).parent.parent / "templates" / "gold_standard"
        for dt, defn in get_all_document_definitions().items():
            if defn.template_name:
                assert (templates_dir / defn.template_name).exists(), (
                    f"Template {defn.template_name} not found for {dt.value}"
                )


# ── Generation Request ──────────────────────────────────────────────────────


class TestGenerationRequest:
    def test_create_request(self):
        req = GenerationRequest(
            condition_slug="parkinsons",
            tier=Tier.PARTNERS,
            doc_type=DocumentType.HANDBOOK,
        )
        assert req.condition_slug == "parkinsons"
        assert req.with_visuals is True
        assert req.with_qa is True


# ── Data Loader ─────────────────────────────────────────────────────────────


class TestDataLoader:
    def test_load_shared_data(self):
        shared = load_shared_protocol_data()
        assert "contraindications_base" in shared
        assert "safety_side_effects" in shared
        assert len(shared["contraindications_base"]) >= 5

    def test_load_parkinsons_yaml(self):
        data = load_protocol_data("parkinsons")
        assert data is not None
        assert data["display_name"] == "Parkinson's Disease"
        assert len(data["tps"]) >= 5
        assert len(data["tdcs"]) >= 8

    def test_list_available_yaml(self):
        available = list_available_conditions()
        assert "parkinsons" in available

    def test_load_nonexistent_returns_none_or_fallback(self):
        result = load_protocol_data("nonexistent_condition_xyz")
        # Should return None if no legacy module has it either
        # (may return data if legacy module has it as fallback)
        # Just ensure it doesn't crash
        assert result is None or isinstance(result, dict)


# ── GenerationService ───────────────────────────────────────────────────────


class TestGenerationService:
    @pytest.fixture
    def svc(self):
        return GenerationService(with_visuals=False, with_qa=False)

    def test_list_conditions(self, svc):
        conditions = svc.list_conditions()
        assert len(conditions) >= 15
        assert "parkinsons" in conditions

    def test_list_doc_types(self, svc):
        types = svc.list_document_types()
        assert len(types) == 8
        assert "handbook" in types

    def test_generate_single(self, svc):
        results = svc.generate(
            condition="parkinsons",
            tier="fellow",
            doc_type="evidence_based_protocol",
        )
        assert len(results) == 1
        assert results[0].success is True
        assert results[0].output_path is not None
        assert results[0].error is None

    def test_generate_unknown_condition(self, svc):
        results = svc.generate(condition="unknown_xyz", tier="fellow", doc_type="handbook")
        assert len(results) == 1
        assert results[0].success is False
        assert "Unknown condition" in results[0].error

    def test_generate_all_for_condition(self, svc):
        results = svc.generate_all(condition="parkinsons", tier="fellow")
        # Fellow tier has 7 doc types (network_assessment is Partners-only)
        assert len(results) == 7
        assert all(r.success for r in results), [r.error for r in results if not r.success]

    def test_generate_partners_includes_network_assessment(self, svc):
        results = svc.generate_all(condition="parkinsons", tier="partners")
        doc_types = [r.doc_type for r in results]
        assert "network_assessment" in doc_types
        assert len(results) == 8  # All 8 types

    def test_generate_both_tiers(self, svc):
        results = svc.generate_all(condition="parkinsons", tier="both")
        assert len(results) == 15  # 7 fellow + 8 partners
        assert all(r.success for r in results)

    def test_generation_result_has_build_id(self, svc):
        results = svc.generate(
            condition="parkinsons",
            tier="fellow",
            doc_type="handbook",
        )
        bid = results[0].build_id
        assert bid.startswith("build-") or bid.startswith("canon-")

    def test_assemble_canonical_document_returns_spec(self, svc):
        out = svc.assemble_canonical_document(
            "parkinsons", "evidence_based_protocol", "fellow"
        )
        assert out.ok, out.error
        assert out.spec is not None
        assert len(out.spec.sections) >= 1
        assert out.provenance is not None
