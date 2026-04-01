"""Tests for section_evidence_mapper, evidence-aware QA, provenance, and cache."""
from __future__ import annotations

import pytest

from sozo_generator.core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    DocumentType,
    EvidenceLevel,
    EvidenceRelation,
    EvidenceType,
    Modality,
    Tier,
)
from sozo_generator.schemas.condition import (
    AssessmentTool,
    ConditionSchema,
)
from sozo_generator.schemas.contracts import EvidenceItem
from sozo_generator.schemas.documents import DocumentSpec, SectionContent

from sozo_generator.evidence.section_evidence_mapper import (
    DocumentEvidenceProfile,
    SectionEvidenceMapper,
    SectionEvidenceProfile,
)


# ── Helpers ─────────────────────────────────────────────────────────────


def _minimal_condition(**overrides) -> ConditionSchema:
    defaults = dict(
        slug="test",
        display_name="Test Condition",
        icd10="G00",
        overview="",
        pathophysiology="",
        evidence_summary="",
        references=[],
        contraindications=[],
        safety_notes=[],
        protocols=[],
        stimulation_targets=[],
        network_profiles=[],
        key_brain_regions=[],
        exclusion_criteria=[],
    )
    defaults.update(overrides)
    return ConditionSchema(**defaults)


def _make_spec(sections: list[SectionContent] | None = None,
               condition_slug: str = "test") -> DocumentSpec:
    return DocumentSpec(
        document_type=DocumentType.CLINICAL_EXAM,
        tier=Tier.FELLOW,
        condition_slug=condition_slug,
        condition_name="Test Condition",
        title="Test Document",
        sections=sections or [],
    )


def _make_item(
    pmid: str = "12345678",
    title: str = "A study",
    level: EvidenceLevel = EvidenceLevel.MEDIUM,
    evidence_type: EvidenceType = EvidenceType.NARRATIVE_REVIEW,
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS,
    year: int | None = 2024,
    key_finding: str = "",
    modalities: list[Modality] | None = None,
    condition_slug: str | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        pmid=pmid,
        title=title,
        evidence_level=level,
        evidence_type=evidence_type,
        relation=relation,
        year=year,
        key_finding=key_finding,
        modalities=modalities or [],
        condition_slug=condition_slug,
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SectionEvidenceMapper
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSectionEvidenceMapper:

    def test_build_evidence_items_from_condition(self, parkinsons_condition):
        """Should extract items from references and assessment tools."""
        mapper = SectionEvidenceMapper()
        items = mapper.build_evidence_items_from_condition(parkinsons_condition)
        # Parkinsons condition has references -- we should get some items
        assert len(items) > 0
        # Every item should have either a pmid or a title
        for item in items:
            assert item.pmid or item.title

    def test_build_items_from_references(self):
        """References with pmid/title should produce EvidenceItems."""
        cond = _minimal_condition(
            references=[
                {"pmid": "11111111", "title": "Study A", "year": 2023,
                 "evidence_level": "high"},
                {"pmid": "22222222", "title": "Study B", "year": 2021},
            ],
        )
        mapper = SectionEvidenceMapper()
        items = mapper.build_evidence_items_from_condition(cond)
        assert len(items) == 2
        assert items[0].pmid == "11111111"
        assert items[0].evidence_level == EvidenceLevel.HIGH
        assert items[1].year == 2021

    def test_build_items_from_assessment_tools(self):
        """Assessment tools with evidence_pmid should produce items."""
        cond = _minimal_condition(
            assessment_tools=[
                AssessmentTool(
                    scale_key="moca",
                    name="Montreal Cognitive Assessment",
                    abbreviation="MoCA",
                    evidence_pmid="33333333",
                ),
                AssessmentTool(
                    scale_key="other",
                    name="Other Scale",
                    abbreviation="OS",
                    evidence_pmid="placeholder-skip",
                ),
            ],
        )
        mapper = SectionEvidenceMapper()
        items = mapper.build_evidence_items_from_condition(cond)
        # Only the non-placeholder should produce an item
        assert len(items) == 1
        assert items[0].pmid == "33333333"

    def test_map_to_sections(self, parkinsons_condition):
        """Build a minimal DocumentSpec, map evidence, check profiles exist."""
        mapper = SectionEvidenceMapper()
        items = mapper.build_evidence_items_from_condition(parkinsons_condition)

        spec = _make_spec(
            sections=[
                SectionContent(section_id="pathophysiology", title="Pathophysiology"),
                SectionContent(section_id="safety", title="Safety"),
            ],
            condition_slug=parkinsons_condition.slug,
        )

        profile = mapper.map_to_sections(spec, items)
        assert isinstance(profile, DocumentEvidenceProfile)
        assert profile.condition_slug == parkinsons_condition.slug
        assert "pathophysiology" in profile.sections
        assert "safety" in profile.sections

    def test_map_to_sections_with_items(self):
        """Manually create items and map them to verify profile stats."""
        mapper = SectionEvidenceMapper()
        items = [
            _make_item(pmid="1", title="pathophysiology mechanism study",
                       level=EvidenceLevel.HIGH, year=2024,
                       key_finding="pathophysiology mechanism"),
            _make_item(pmid="2", title="pathophysiology neurobiology",
                       level=EvidenceLevel.MEDIUM, year=2022,
                       key_finding="etiology study"),
            _make_item(pmid="3", title="safety adverse event analysis",
                       level=EvidenceLevel.HIGH, year=2023,
                       key_finding="safety tolerability"),
        ]
        spec = _make_spec(sections=[
            SectionContent(section_id="pathophysiology", title="Pathophysiology"),
            SectionContent(section_id="safety", title="Safety"),
        ])

        profile = mapper.map_to_sections(spec, items)
        patho = profile.sections["pathophysiology"]
        assert patho.article_count == 2
        assert patho.mean_evidence_score > 0
        assert "1" in patho.pmids
        assert "2" in patho.pmids

        safety = profile.sections["safety"]
        assert safety.article_count == 1
        assert "3" in safety.pmids

    def test_apply_evidence_to_spec(self):
        """Apply profile to spec, check confidence_label and claims set."""
        mapper = SectionEvidenceMapper()
        spec = _make_spec(sections=[
            SectionContent(section_id="safety", title="Safety"),
        ])

        # Create a profile manually
        sec_profile = SectionEvidenceProfile(
            section_id="safety",
            article_count=3,
            highest_evidence_level="high",
            mean_evidence_score=4.0,
            pmids=["111", "222", "333"],
            confidence=ConfidenceLabel.HIGH.value,
            clinical_language_prefix="Evidence-based:",
            needs_review=False,
        )
        profile = DocumentEvidenceProfile(
            condition_slug="test",
            total_articles=3,
            sections={"safety": sec_profile},
        )

        result = mapper.apply_evidence_to_spec(spec, profile)
        section = result.sections[0]
        assert section.confidence_label == ConfidenceLabel.HIGH.value
        assert section.evidence_pmids == ["111", "222", "333"]
        assert len(section.claims) == 1
        assert section.claims[0].claim_id == "evmap-safety"

    def test_weak_sections_detected(self):
        """Section with 0 items should appear as unsupported (weak)."""
        mapper = SectionEvidenceMapper()
        items: list[EvidenceItem] = []  # no items at all
        spec = _make_spec(sections=[
            SectionContent(section_id="safety", title="Safety"),
            SectionContent(section_id="pathophysiology", title="Pathophysiology"),
        ])

        profile = mapper.map_to_sections(spec, items)
        weak = mapper.get_weak_sections(profile)
        assert "safety" in weak
        assert "pathophysiology" in weak

    def test_outdated_sections_detected(self):
        """Items from 2015 should be outdated when max_age=5."""
        mapper = SectionEvidenceMapper()
        items = [
            _make_item(pmid="1", title="pathophysiology mechanism old study",
                       level=EvidenceLevel.MEDIUM, year=2015,
                       key_finding="pathophysiology"),
        ]
        spec = _make_spec(sections=[
            SectionContent(section_id="pathophysiology", title="Pathophysiology"),
        ])
        # Use a generous recency window so the item isn't filtered out
        profile = mapper.map_to_sections(spec, items, max_years=20)
        outdated = mapper.get_outdated_sections(profile, max_age_years=5)
        assert "pathophysiology" in outdated

    def test_modality_filter(self, parkinsons_condition):
        """Filter to TPS modality only."""
        mapper = SectionEvidenceMapper()
        all_items = mapper.build_evidence_items_from_condition(parkinsons_condition)

        # Add a TPS-specific item
        tps_item = _make_item(
            pmid="99999999",
            title="TPS safety tolerability study",
            key_finding="safety adverse events TPS",
            modalities=[Modality.TPS],
            year=2024,
        )
        items_with_tps = all_items + [tps_item]

        spec = _make_spec(
            sections=[
                SectionContent(section_id="safety", title="Safety"),
            ],
            condition_slug=parkinsons_condition.slug,
        )

        # With TPS filter, only items that either have TPS modality or no modality
        # should pass through
        profile = mapper.map_to_sections(spec, items_with_tps, modality_filter=Modality.TPS)
        assert isinstance(profile, DocumentEvidenceProfile)

    def test_recency_filter(self, parkinsons_condition):
        """Filter to last 3 years should exclude old items."""
        mapper = SectionEvidenceMapper()
        items = [
            _make_item(pmid="1", title="pathophysiology mechanism",
                       year=2024, key_finding="pathophysiology"),
            _make_item(pmid="2", title="pathophysiology old mechanism",
                       year=2018, key_finding="pathophysiology"),
        ]

        spec = _make_spec(sections=[
            SectionContent(section_id="pathophysiology", title="Pathophysiology"),
        ])

        profile = mapper.map_to_sections(spec, items, max_years=3)
        patho = profile.sections["pathophysiology"]
        # The 2018 item should be filtered out (current_year - 2018 > 3)
        assert "2" not in patho.pmids
        assert patho.article_count <= 1

    def test_contradiction_detection(self):
        """Items with SUPPORTS and CONTRADICTS should flag contradictions."""
        mapper = SectionEvidenceMapper()
        items = [
            _make_item(pmid="1", title="safety adverse study",
                       relation=EvidenceRelation.SUPPORTS, year=2024,
                       key_finding="safety"),
            _make_item(pmid="2", title="safety adverse events concern",
                       relation=EvidenceRelation.CONTRADICTS, year=2024,
                       key_finding="safety"),
        ]
        spec = _make_spec(sections=[
            SectionContent(section_id="safety", title="Safety"),
        ])
        profile = mapper.map_to_sections(spec, items)
        safety = profile.sections["safety"]
        assert safety.has_contradictions is True
        assert len(safety.contradiction_notes) > 0
        assert safety.confidence == ConfidenceLabel.REVIEW_REQUIRED.value

    def test_empty_condition_returns_empty_items(self):
        """Condition with no references should produce no items."""
        cond = _minimal_condition()
        mapper = SectionEvidenceMapper()
        items = mapper.build_evidence_items_from_condition(cond)
        assert items == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Evidence-aware QA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestEvidenceAwareQA:

    def test_weak_evidence_produces_qa_warning(self):
        """QAEngine on a condition with no references should produce citation warnings."""
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        cond = _minimal_condition(slug="no_refs", display_name="No Refs Condition")
        spec = _make_spec(sections=[
            SectionContent(section_id="overview", title="Overview", content="Some content."),
        ])

        report = engine.run_document_qa(cond, spec)
        # Should have citation-related issues (no references = BLOCK)
        citation_issues = [i for i in report.issues if i.category == "citations"]
        assert len(citation_issues) > 0
        assert any("no_references" in i.rule_id or "min_count" in i.rule_id
                    for i in citation_issues)

    def test_good_evidence_no_citation_block(self, parkinsons_condition):
        """Parkinsons has references so should not have a no_references block."""
        from sozo_generator.qa.engine import QAEngine

        engine = QAEngine()
        spec = _make_spec(
            sections=[
                SectionContent(section_id="overview", title="Overview",
                               content="Parkinson's disease overview."),
            ],
            condition_slug=parkinsons_condition.slug,
        )

        report = engine.run_document_qa(parkinsons_condition, spec)
        no_ref_issues = [i for i in report.issues
                         if i.rule_id == "citations.no_references"]
        assert len(no_ref_issues) == 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Provenance
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestEvidenceInProvenance:

    def test_provenance_captures_evidence_info(self, tmp_path):
        """Create provenance, set evidence fields, verify persistence."""
        from sozo_generator.orchestration.provenance import (
            DocumentProvenance,
            ProvenanceStore,
        )

        store = ProvenanceStore(tmp_path / "provenance")

        prov = DocumentProvenance(
            document_id="doc-test-001",
            condition_slug="parkinsons",
            document_type="clinical_exam",
            tier="fellow",
            evidence_bundle_version="v1.0",
            evidence_snapshot_id="snap-parkinsons-20240101",
            confidence_label=ConfidenceLabel.HIGH.value,
        )
        prov.add_revision("evidence_mapped", details="Mapped 15 articles to 8 sections")

        path = store.save(prov)
        assert path.exists()

        loaded = store.load("doc-test-001")
        assert loaded is not None
        assert loaded.evidence_snapshot_id == "snap-parkinsons-20240101"
        assert loaded.confidence_label == ConfidenceLabel.HIGH.value
        assert len(loaded.revision_history) == 1
        assert loaded.revision_history[0]["action"] == "evidence_mapped"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Cache roundtrip
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestCacheRoundtrip:

    def test_evidence_cache_set_get(self, tmp_path):
        """Cache some articles, retrieve them."""
        from sozo_generator.evidence.cache import EvidenceCache

        cache = EvidenceCache(tmp_path / "cache", ttl_days=30)

        articles = [
            {"pmid": "11111111", "title": "Study A"},
            {"pmid": "22222222", "title": "Study B"},
        ]
        cache.set("parkinsons_patho", articles)
        result = cache.get("parkinsons_patho")
        assert result is not None
        assert len(result) == 2
        assert result[0]["pmid"] == "11111111"

    def test_evidence_cache_expiry(self, tmp_path):
        """Set TTL to 0 days, should expire immediately."""
        from sozo_generator.evidence.cache import EvidenceCache

        cache = EvidenceCache(tmp_path / "cache", ttl_days=0)

        cache.set("expiring_key", {"data": "value"})
        result = cache.get("expiring_key")
        # With TTL=0, the entry should be expired
        assert result is None
