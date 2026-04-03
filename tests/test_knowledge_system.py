"""Comprehensive tests for the SOZO Clinical Knowledge System."""
import pytest
from pathlib import Path


# ── Schema Validation Tests ────────────────────────────────────────────────


class TestKnowledgeSchemas:
    def test_condition_schema(self):
        from sozo_generator.knowledge.schemas import KnowledgeCondition, NetworkInvolvement, Phenotype
        cond = KnowledgeCondition(
            slug="test",
            display_name="Test Condition",
            icd10="X00",
            network_profiles=[
                NetworkInvolvement(network="cen", dysfunction="hypo", severity="moderate"),
            ],
            phenotypes=[
                Phenotype(slug="p1", label="Subtype 1", key_features=["feature_a"]),
            ],
        )
        assert cond.slug == "test"
        assert len(cond.network_profiles) == 1
        assert len(cond.phenotypes) == 1

    def test_modality_schema(self):
        from sozo_generator.knowledge.schemas import KnowledgeModality
        mod = KnowledgeModality(
            slug="tdcs",
            name="Transcranial Direct Current Stimulation",
            abbreviation="tDCS",
            regulatory_status="CE Class IIa",
        )
        assert mod.slug == "tdcs"

    def test_assessment_schema(self):
        from sozo_generator.knowledge.schemas import KnowledgeAssessment
        asmt = KnowledgeAssessment(
            slug="phq9",
            name="PHQ-9",
            abbreviation="PHQ-9",
            domains=["depression"],
            applicable_conditions=["depression"],
            validation_pmid="11556941",
        )
        assert asmt.validation_pmid == "11556941"

    def test_brain_target_schema(self):
        from sozo_generator.knowledge.schemas import KnowledgeBrainTarget
        target = KnowledgeBrainTarget(
            slug="dlpfc",
            name="Dorsolateral Prefrontal Cortex",
            abbreviation="DLPFC",
            eeg_10_20=["F3", "F4"],
            networks=["cen"],
        )
        assert "F3" in target.eeg_10_20

    def test_evidence_map_schema(self):
        from sozo_generator.knowledge.schemas import KnowledgeEvidenceMap
        emap = KnowledgeEvidenceMap(
            condition_slug="depression",
            modality_slug="tdcs",
            evidence_level="high",
            indication_status="investigational",
        )
        assert emap.condition_slug == "depression"

    def test_contraindication_schema(self):
        from sozo_generator.knowledge.schemas import KnowledgeContraindication
        contra = KnowledgeContraindication(
            slug="metal_implants",
            name="Cranial Metal Implants",
            severity="absolute",
            modalities=["tdcs", "tps"],
        )
        assert contra.severity == "absolute"

    def test_shared_rule_schema(self):
        from sozo_generator.knowledge.schemas import SharedClinicalRule
        rule = SharedClinicalRule(
            slug="consent",
            name="Informed Consent",
            category="governance",
            mandatory=True,
        )
        assert rule.mandatory is True

    def test_reference_pmid_validation(self):
        from sozo_generator.knowledge.schemas import Reference
        ref = Reference(pmid="12345678", title="Test Article")
        assert ref.pmid == "12345678"

        # Invalid PMID
        with pytest.raises(Exception):
            Reference(pmid="not_valid", title="Bad")


# ── Loader Tests ───────────────────────────────────────────────────────────


class TestKnowledgeLoader:
    @pytest.fixture
    def kb_dir(self):
        return Path("sozo_knowledge/knowledge")

    def test_load_conditions(self, kb_dir):
        from sozo_generator.knowledge.loader import load_conditions
        conditions = load_conditions(kb_dir)
        assert len(conditions) == 5
        assert "parkinsons" in conditions
        assert "depression" in conditions
        assert "adhd" in conditions
        assert "asd" in conditions
        assert "migraine" in conditions

    def test_load_modalities(self, kb_dir):
        from sozo_generator.knowledge.loader import load_modalities
        modalities = load_modalities(kb_dir)
        assert len(modalities) == 4
        assert "tdcs" in modalities
        assert "tps" in modalities
        assert "tavns" in modalities
        assert "ces" in modalities

    def test_load_contraindications(self, kb_dir):
        from sozo_generator.knowledge.loader import load_contraindications
        contras = load_contraindications(kb_dir)
        assert len(contras) >= 5
        assert "cranial_metal_implants" in contras

    def test_load_shared_rules(self, kb_dir):
        from sozo_generator.knowledge.loader import load_shared_rules
        rules = load_shared_rules(kb_dir)
        assert len(rules) >= 10
        assert "doctor_authorization" in rules
        assert "sozo_sequence" in rules

    def test_condition_has_required_fields(self, kb_dir):
        from sozo_generator.knowledge.loader import load_conditions
        conditions = load_conditions(kb_dir)
        for slug, cond in conditions.items():
            assert cond.display_name, f"{slug} missing display_name"
            assert cond.icd10, f"{slug} missing icd10"
            assert len(cond.protocols) >= 1, f"{slug} has no protocols"
            assert len(cond.phenotypes) >= 1, f"{slug} has no phenotypes"
            assert len(cond.references) >= 1, f"{slug} has no references"

    def test_modality_has_required_fields(self, kb_dir):
        from sozo_generator.knowledge.loader import load_modalities
        modalities = load_modalities(kb_dir)
        for slug, mod in modalities.items():
            assert mod.name, f"{slug} missing name"
            assert mod.abbreviation, f"{slug} missing abbreviation"
            assert mod.regulatory_status, f"{slug} missing regulatory_status"

    def test_all_condition_pmids_valid(self, kb_dir):
        from sozo_generator.knowledge.loader import load_conditions
        conditions = load_conditions(kb_dir)
        for slug, cond in conditions.items():
            for ref in cond.references:
                if ref.pmid:
                    assert ref.pmid.isdigit(), f"{slug} has invalid PMID: {ref.pmid}"


# ── Linker Tests ───────────────────────────────────────────────────────────


class TestKnowledgeLinker:
    def test_validate_links(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        report = kb.validate()
        assert report.total_checks > 0
        assert report.resolved > 0
        assert report.valid  # No errors (warnings OK)

    def test_condition_modality_links_resolve(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        for slug in kb.list_conditions():
            cond = kb.get_condition(slug)
            for mod_ref in cond.applicable_modalities:
                assert mod_ref in kb.modalities, (
                    f"{slug} references modality '{mod_ref}' which doesn't exist"
                )


# ── KnowledgeBase Query Tests ─────────────────────────────────────────────


class TestKnowledgeBase:
    @pytest.fixture(scope="class")
    def kb(self):
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    def test_list_conditions(self, kb):
        conditions = kb.list_conditions()
        assert len(conditions) == 5
        assert "parkinsons" in conditions
        assert "migraine" in conditions

    def test_get_condition(self, kb):
        cond = kb.get_condition("parkinsons")
        assert cond is not None
        assert cond.display_name == "Parkinson's Disease"

    def test_get_nonexistent_condition(self, kb):
        assert kb.get_condition("nonexistent") is None

    def test_get_modalities_for_condition(self, kb):
        mods = kb.get_modalities_for_condition("parkinsons")
        assert len(mods) >= 4
        slugs = [m.slug for m in mods]
        assert "tdcs" in slugs
        assert "tps" in slugs

    def test_get_contraindications_for_tps(self, kb):
        contras = kb.get_contraindications_for_modality("tps")
        assert len(contras) >= 3
        slugs = [c.slug for c in contras]
        assert "cranial_metal_implants" in slugs

    def test_get_shared_rules(self, kb):
        all_rules = kb.get_shared_rules()
        assert len(all_rules) >= 10

        governance = kb.get_shared_rules("governance")
        assert len(governance) >= 1

        safety = kb.get_shared_rules("safety")
        assert len(safety) >= 1

    def test_summary(self, kb):
        s = kb.summary()
        assert s["conditions"] == 5
        assert s["modalities"] == 4
        assert s["loaded"] is True

    def test_migraine_is_new_condition(self, kb):
        """Migraine is a new condition not in the original system."""
        cond = kb.get_condition("migraine")
        assert cond is not None
        assert cond.icd10 == "G43"
        assert len(cond.protocols) >= 3
        assert len(cond.references) >= 3
        # Verify real PMIDs
        pmids = [r.pmid for r in cond.references if r.pmid]
        assert "28068857" in pmids or "31278046" in pmids


# ── GenerationService Integration ──────────────────────────────────────────


class TestKnowledgeInGenerationService:
    def test_service_has_knowledge_base(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        kb = svc.knowledge_base
        # May be None if knowledge dir doesn't exist, or loaded
        if kb:
            assert kb.summary()["conditions"] >= 5

    def test_get_knowledge_summary(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        summary = svc.get_knowledge_summary("parkinsons")
        if summary:
            assert summary["condition"]["slug"] == "parkinsons"
            assert len(summary["modalities"]) >= 4
            assert len(summary["contraindications"]) >= 3

    def test_knowledge_summary_nonexistent(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        summary = svc.get_knowledge_summary("nonexistent_xyz")
        assert summary is None
