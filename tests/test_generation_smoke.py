"""Smoke tests for critical generation entry points.

These tests verify that:
1. All 15 condition builders produce valid ConditionSchema objects
2. Every condition has required fields populated
3. Evidence PMIDs in assessment tools pass validation
4. The canonical pipeline can be imported and initialized
"""
import pytest

from sozo_generator.conditions.registry import get_registry


ALL_SLUGS = [
    "parkinsons",
    "depression",
    "anxiety",
    "adhd",
    "alzheimers",
    "stroke_rehab",
    "tbi",
    "chronic_pain",
    "ptsd",
    "ocd",
    "ms",
    "asd",
    "long_covid",
    "tinnitus",
    "insomnia",
]


@pytest.fixture(scope="module")
def reg():
    import sozo_generator.conditions.registry as reg_module
    reg_module._registry = None
    return reg_module.get_registry()


class TestAllConditionsSmoke:
    """Verify all 15 condition builders produce valid schemas."""

    def test_registry_has_all_15(self, reg):
        slugs = reg.list_slugs()
        assert len(slugs) == 15, f"Expected 15 conditions, got {len(slugs)}: {slugs}"
        for slug in ALL_SLUGS:
            assert slug in slugs, f"Missing condition: {slug}"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_display_name(self, reg, slug):
        schema = reg.get(slug)
        assert schema.display_name, f"{slug} missing display_name"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_icd10(self, reg, slug):
        schema = reg.get(slug)
        assert schema.icd10, f"{slug} missing ICD-10 code"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_network_profiles(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.network_profiles) >= 1, f"{slug} has no network profiles"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_phenotypes(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.phenotypes) >= 1, f"{slug} has no phenotypes"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_protocols(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.protocols) >= 1, f"{slug} has no protocols"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_references(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.references) >= 1, f"{slug} has no references"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_assessment_tools(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.assessment_tools) >= 1, f"{slug} has no assessment tools"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_assessment_pmids_valid(self, reg, slug):
        """Ensure all evidence_pmid values on assessment tools are valid digits or None."""
        schema = reg.get(slug)
        for tool in schema.assessment_tools:
            if tool.evidence_pmid is not None:
                assert tool.evidence_pmid.isdigit(), (
                    f"{slug} tool {tool.abbreviation} has invalid PMID: {tool.evidence_pmid}"
                )

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_safety_notes(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.safety_notes) >= 1, f"{slug} has no safety notes"

    @pytest.mark.parametrize("slug", ALL_SLUGS)
    def test_condition_has_stimulation_targets(self, reg, slug):
        schema = reg.get(slug)
        assert len(schema.stimulation_targets) >= 1, f"{slug} has no stimulation targets"


class TestCanonicalPipelineImports:
    """Verify the canonical pipeline modules can be imported."""

    def test_import_document_exporter(self):
        from sozo_generator.docx.exporter import DocumentExporter
        assert DocumentExporter is not None

    def test_import_qa_engine(self):
        from sozo_generator.qa.engine import QAEngine
        assert QAEngine is not None

    def test_import_evidence_cache(self):
        from sozo_generator.evidence.cache import EvidenceCache
        assert EvidenceCache is not None

    def test_import_content_assembler(self):
        from sozo_generator.content.assembler import ContentAssembler
        assert ContentAssembler is not None

    def test_import_settings(self):
        from sozo_generator.core.settings import get_settings
        settings = get_settings()
        assert settings.output_dir is not None

    def test_import_legacy_helpers(self):
        from sozo_generator.docx.legacy_helpers import (
            para_replace,
            para_set,
            cell_write,
            replace_table,
            global_replace,
            apply_global_replacements,
        )
        assert all(callable(f) for f in [
            para_replace, para_set, cell_write,
            replace_table, global_replace, apply_global_replacements,
        ])


class TestValidatorsModule:
    """Verify the validators module works correctly."""

    def test_import(self):
        from sozo_generator.schemas.validators import validate_pmid, validate_pmid_list
        assert callable(validate_pmid)
        assert callable(validate_pmid_list)

    def test_known_good_pmids(self):
        """Test with real PMIDs used in condition builders."""
        from sozo_generator.schemas.validators import validate_pmid
        known_pmids = ["19343477", "15817019", "14100341", "11556941"]
        for pmid in known_pmids:
            assert validate_pmid(pmid) == pmid
