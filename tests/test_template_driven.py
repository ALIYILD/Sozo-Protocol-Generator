"""Comprehensive tests for the template-driven AI generation system."""
import json
import pytest
from pathlib import Path


# ── Schema Model Tests ─────────────────────────────────────────────────────


class TestTemplateProfileModels:
    def test_template_profile_creation(self):
        from sozo_generator.template_profiles.models import (
            TemplateProfile, TemplateSectionSpec, FormattingProfile, ToneProfile,
        )
        profile = TemplateProfile(
            profile_id="tp-test",
            name="Test Profile",
            source_filename="test.docx",
            section_map=[
                TemplateSectionSpec(section_id="s1", title="Section 1", order_index=0),
                TemplateSectionSpec(section_id="s2", title="Section 2", order_index=1),
            ],
        )
        assert profile.total_sections == 2
        assert profile.section_ids() == ["s1", "s2"]
        assert profile.get_section("s1").title == "Section 1"
        assert profile.get_section("nonexistent") is None

    def test_research_bundle(self):
        from sozo_generator.template_profiles.models import ResearchBundle, ResearchSource
        bundle = ResearchBundle(
            condition_slug="depression",
            section_id="pathophysiology",
            sources=[
                ResearchSource(title="Article 1", pmid="12345678"),
                ResearchSource(title="Article 2", pmid="87654321"),
                ResearchSource(title="Web Source", source_type="web"),
            ],
        )
        assert bundle.source_count == 3
        assert bundle.pmid_count == 2

    def test_section_brief(self):
        from sozo_generator.template_profiles.models import SectionBrief, TemplateSectionSpec
        brief = SectionBrief(
            target_condition="depression",
            target_condition_name="Major Depressive Disorder",
            tier="partners",
            doc_type="handbook",
            section_spec=TemplateSectionSpec(section_id="s1", title="Overview"),
        )
        assert len(brief.prohibited_claims) >= 4
        assert "fabricate" in brief.prohibited_claims[0].lower()

    def test_drafted_section(self):
        from sozo_generator.template_profiles.models import DraftedSection
        draft = DraftedSection(
            section_id="pathophysiology",
            title="Pathophysiology",
            content="MDD involves prefrontal-limbic dysfunction.",
            citations_used=["12345678"],
            generation_method="data_driven",
        )
        assert draft.generation_method == "data_driven"
        assert len(draft.citations_used) == 1

    def test_build_manifest(self):
        from sozo_generator.template_profiles.models import DocumentBuildManifest
        manifest = DocumentBuildManifest(
            build_id="build-test",
            condition_slug="depression",
            condition_name="MDD",
            tier="partners",
            doc_type="handbook",
            template_profile_id="tp-test",
            template_name="Test",
            sections_generated=["s1", "s2", "s3"],
            sections_from_ai=1,
            sections_from_data=2,
        )
        assert len(manifest.sections_generated) == 3
        assert manifest.sections_from_ai == 1


# ── Template Profile Store Tests ───────────────────────────────────────────


class TestTemplateProfileStore:
    def test_save_and_load(self, tmp_path):
        from sozo_generator.template_profiles.store import TemplateProfileStore
        from sozo_generator.template_profiles.models import TemplateProfile

        store = TemplateProfileStore(tmp_path / "profiles")
        profile = TemplateProfile(
            profile_id="tp-store-test",
            name="Store Test",
            source_filename="test.docx",
        )
        store.save(profile)
        loaded = store.load("tp-store-test")
        assert loaded.name == "Store Test"

    def test_list_profiles(self, tmp_path):
        from sozo_generator.template_profiles.store import TemplateProfileStore
        from sozo_generator.template_profiles.models import TemplateProfile

        store = TemplateProfileStore(tmp_path / "profiles")
        for i in range(3):
            store.save(TemplateProfile(
                profile_id=f"tp-{i}",
                name=f"Profile {i}",
                source_filename=f"test_{i}.docx",
            ))
        profiles = store.list_profiles()
        assert len(profiles) == 3

    def test_delete(self, tmp_path):
        from sozo_generator.template_profiles.store import TemplateProfileStore
        from sozo_generator.template_profiles.models import TemplateProfile

        store = TemplateProfileStore(tmp_path / "profiles")
        store.save(TemplateProfile(profile_id="tp-del", name="Del", source_filename="x.docx"))
        assert store.exists("tp-del")
        store.delete("tp-del")
        assert not store.exists("tp-del")


# ── Template Ingestion Tests ───────────────────────────────────────────────


class TestTemplateIngestion:
    @pytest.fixture
    def templates_dir(self):
        return Path("templates/gold_standard")

    def test_ingest_evidence_protocol(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(templates_dir / "Evidence_Based_Protocol.docx")
        assert profile.total_sections >= 10
        assert profile.inferred_doc_type == "evidence_based_protocol"
        assert profile.template_type == "protocol"
        assert profile.formatting_profile.primary_font

    def test_ingest_handbook(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(templates_dir / "Clinical_Handbook.docx")
        assert profile.total_sections >= 5
        assert profile.inferred_doc_type == "handbook"

    def test_ingest_all_8_templates(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        for template_file in templates_dir.glob("*.docx"):
            profile = build_template_profile(template_file)
            assert profile.total_sections >= 1, f"No sections in {template_file.name}"
            assert profile.formatting_profile.primary_font, f"No font in {template_file.name}"
            assert profile.template_fingerprint, f"No fingerprint for {template_file.name}"

    def test_section_ids_are_normalized(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(templates_dir / "Evidence_Based_Protocol.docx")
        for s in profile.section_map:
            assert s.section_id.isascii()
            assert " " not in s.section_id
            assert s.section_id == s.section_id.lower()

    def test_heading_hierarchy_detected(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(templates_dir / "Evidence_Based_Protocol.docx")
        assert profile.heading_hierarchy  # Non-empty
        assert 1 in profile.heading_hierarchy  # Has H1 headings

    def test_formatting_profile_captured(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(templates_dir / "Evidence_Based_Protocol.docx")
        fp = profile.formatting_profile
        assert fp.primary_font
        assert fp.body_font_size_pt > 0
        assert fp.heading_sizes_pt  # Non-empty

    def test_tone_profile_built(self, templates_dir):
        from sozo_generator.template_profiles.builder import build_template_profile
        profile = build_template_profile(templates_dir / "Evidence_Based_Protocol.docx")
        tp = profile.tone_profile
        assert tp.audience == "clinician"
        assert tp.formality in ("formal", "semi_formal")


# ── Research Orchestration Tests ───────────────────────────────────────────


class TestResearchOrchestrator:
    def test_research_section(self):
        from sozo_generator.research.orchestrator import ResearchOrchestrator
        from sozo_generator.template_profiles.models import TemplateSectionSpec

        orch = ResearchOrchestrator(use_pubmed=False)
        section = TemplateSectionSpec(
            section_id="pathophysiology", title="Pathophysiology",
            requires_evidence=True,
        )
        bundle = orch.research_section("parkinsons", "Parkinson's Disease", section)
        assert bundle.condition_slug == "parkinsons"
        assert bundle.source_count >= 1  # Should have internal sources

    def test_research_all_sections(self):
        from sozo_generator.research.orchestrator import ResearchOrchestrator
        from sozo_generator.template_profiles.models import TemplateSectionSpec

        orch = ResearchOrchestrator(use_pubmed=False)
        sections = [
            TemplateSectionSpec(section_id="overview", title="Overview"),
            TemplateSectionSpec(section_id="protocols", title="Protocols"),
        ]
        bundles = orch.research_all_sections("depression", "Depression", sections)
        assert len(bundles) == 2
        assert "overview" in bundles
        assert "protocols" in bundles

    def test_deduplication(self):
        from sozo_generator.research.orchestrator import ResearchOrchestrator
        orch = ResearchOrchestrator(use_pubmed=False)
        from sozo_generator.template_profiles.models import ResearchSource
        sources = [
            ResearchSource(pmid="12345678", title="A"),
            ResearchSource(pmid="12345678", title="A duplicate"),
            ResearchSource(pmid="87654321", title="B"),
        ]
        deduped = orch._deduplicate(sources)
        assert len(deduped) == 2


# ── Section Writing Tests ──────────────────────────────────────────────────


class TestSectionWriter:
    @pytest.fixture
    def parkinsons(self):
        from sozo_generator.conditions.generators.parkinsons import build_parkinsons_condition
        return build_parkinsons_condition()

    def test_data_driven_writing(self, parkinsons):
        from sozo_generator.writers.section_writer import SectionWriter
        from sozo_generator.writers.brief_builder import BriefBuilder
        from sozo_generator.template_profiles.models import TemplateSectionSpec, ResearchBundle, ToneProfile

        sections = [
            TemplateSectionSpec(section_id="pathophysiology", title="Pathophysiology", requires_evidence=True),
        ]
        bundles = {"pathophysiology": ResearchBundle(condition_slug="parkinsons", section_id="pathophysiology")}

        builder = BriefBuilder(parkinsons, "partners", "protocol", sections, bundles, ToneProfile())
        briefs = builder.build_all()

        writer = SectionWriter()
        drafted = writer.write_section(briefs[0])

        assert drafted.section_id == "pathophysiology"
        assert drafted.generation_method == "data_driven"
        assert drafted.content  # Has content
        assert drafted.confidence in ("high", "medium", "low", "insufficient")

    def test_write_all_sections(self, parkinsons):
        from sozo_generator.writers.section_writer import SectionWriter
        from sozo_generator.writers.brief_builder import BriefBuilder
        from sozo_generator.template_profiles.models import TemplateSectionSpec, ResearchBundle, ToneProfile

        sections = [
            TemplateSectionSpec(section_id="overview", title="Clinical Overview"),
            TemplateSectionSpec(section_id="protocols", title="Treatment Protocols"),
            TemplateSectionSpec(section_id="safety", title="Safety"),
        ]
        bundles = {s.section_id: ResearchBundle(condition_slug="parkinsons", section_id=s.section_id) for s in sections}

        builder = BriefBuilder(parkinsons, "partners", "protocol", sections, bundles, ToneProfile())
        briefs = builder.build_all()

        writer = SectionWriter()
        drafted = writer.write_all(briefs)
        assert len(drafted) == 3
        for d in drafted:
            assert d.section_id
            assert d.title


# ── Grounding Validation Tests ─────────────────────────────────────────────


class TestGroundingValidator:
    def test_detect_strong_claims(self):
        from sozo_generator.grounding.validator import GroundingValidator
        from sozo_generator.template_profiles.models import DraftedSection, ResearchBundle

        validator = GroundingValidator()
        section = DraftedSection(
            section_id="test",
            title="Test",
            content="TPS has been proven to cure Parkinson's Disease completely.",
        )
        bundle = ResearchBundle(condition_slug="parkinsons", section_id="test")
        result = validator.validate_section(section, bundle)
        assert any(i.issue_type == "unsupported_claim" for i in result.issues)

    def test_detect_placeholder_leakage(self):
        from sozo_generator.grounding.validator import GroundingValidator
        from sozo_generator.template_profiles.models import DraftedSection, ResearchBundle

        validator = GroundingValidator()
        section = DraftedSection(
            section_id="test",
            title="Test",
            content="This [TODO] section needs [PLACEHOLDER] content.",
        )
        bundle = ResearchBundle(condition_slug="test", section_id="test")
        result = validator.validate_section(section, bundle)
        assert any(i.issue_type == "placeholder_leakage" for i in result.issues)

    def test_detect_condition_leakage(self):
        from sozo_generator.grounding.validator import GroundingValidator
        from sozo_generator.template_profiles.models import DraftedSection, ResearchBundle

        validator = GroundingValidator(target_condition_slug="depression")
        section = DraftedSection(
            section_id="test",
            title="Test",
            content="Parkinson's Disease motor symptoms respond to tDCS.",
        )
        bundle = ResearchBundle(condition_slug="depression", section_id="test")
        result = validator.validate_section(section, bundle, target_condition="depression")
        assert any(i.issue_type == "condition_leakage" for i in result.issues)

    def test_verify_pmids(self):
        from sozo_generator.grounding.validator import GroundingValidator
        from sozo_generator.template_profiles.models import DraftedSection, ResearchBundle, ResearchSource

        validator = GroundingValidator()
        section = DraftedSection(
            section_id="test",
            title="Test",
            content="Evidence supports this (PMID: 12345678).",
            citations_used=["12345678", "99999999"],
        )
        bundle = ResearchBundle(
            condition_slug="test",
            section_id="test",
            sources=[ResearchSource(pmid="12345678", title="Real Article")],
        )
        result = validator.validate_section(section, bundle)
        assert result.pmids_verified == 1
        assert result.pmids_unverified == 1

    def test_empty_section_flagged(self):
        from sozo_generator.grounding.validator import GroundingValidator
        from sozo_generator.template_profiles.models import DraftedSection, ResearchBundle

        validator = GroundingValidator()
        section = DraftedSection(section_id="empty", title="Empty", content="")
        bundle = ResearchBundle(condition_slug="test", section_id="empty")
        result = validator.validate_section(section, bundle)
        assert any(i.issue_type == "empty_section" for i in result.issues)


# ── End-to-End Generation Tests ───────────────────────────────────────────


class TestEndToEndGeneration:
    def test_generate_from_handbook_template(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_from_template(
            template_path="templates/gold_standard/Clinical_Handbook.docx",
            condition="depression",
            tier="partners",
            with_research=False,
        )
        assert result.success
        assert result.output_path
        assert Path(result.output_path).exists()

    def test_generate_from_protocol_template(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_from_template(
            template_path="templates/gold_standard/Evidence_Based_Protocol.docx",
            condition="adhd",
            tier="fellow",
            with_research=False,
        )
        assert result.success
        assert Path(result.output_path).exists()
        assert Path(result.output_path).stat().st_size > 10000

    def test_generate_produces_manifest(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_from_template(
            template_path="templates/gold_standard/Clinical_Handbook.docx",
            condition="ptsd",
            tier="partners",
            with_research=False,
        )
        assert result.success
        manifest_path = Path(result.output_path).parent / f"{result.build_id}_manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest["condition_slug"] == "ptsd"
        assert len(manifest["sections_generated"]) >= 5

    def test_generate_for_all_conditions(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        conditions = ["parkinsons", "depression", "anxiety", "adhd", "alzheimers"]
        for cond in conditions:
            result = svc.generate_from_template(
                template_path="templates/gold_standard/Clinical_Handbook.docx",
                condition=cond,
                tier="partners",
                with_research=False,
            )
            assert result.success, f"Failed for {cond}: {result.error}"

    def test_unknown_condition_fails_gracefully(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_from_template(
            template_path="templates/gold_standard/Clinical_Handbook.docx",
            condition="nonexistent_xyz",
            tier="partners",
        )
        assert not result.success
        assert "Unknown condition" in result.error

    def test_missing_template_fails_gracefully(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_from_template(
            template_path="/nonexistent/template.docx",
            condition="parkinsons",
        )
        assert not result.success

    def test_stored_profile_reuse(self):
        from sozo_generator.generation.service import GenerationService
        from sozo_generator.template_profiles.builder import build_template_profile
        from sozo_generator.template_profiles.store import TemplateProfileStore

        # First ingest
        profile = build_template_profile("templates/gold_standard/Clinical_Handbook.docx")
        store = TemplateProfileStore()
        store.save(profile)

        # Then generate from stored profile
        svc = GenerationService(with_visuals=False, with_qa=False)
        result = svc.generate_from_template(
            template_id=profile.profile_id,
            condition="anxiety",
            tier="fellow",
            with_research=False,
        )
        assert result.success
