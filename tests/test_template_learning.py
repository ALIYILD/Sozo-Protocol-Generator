"""Tests for template learning pipeline — ingestion, pattern extraction,
consistency scoring, and profile-guided generation."""
from __future__ import annotations

import json
import pytest
from pathlib import Path


class TestDocumentIngester:
    def test_ingest_existing_document(self):
        """Ingest a real generated document and get valid fingerprint."""
        from sozo_generator.template.learning.document_ingester import ingest_document
        # Use one of the 225 generated documents
        doc_path = Path("outputs/documents/parkinsons/fellow/Evidence_Based_Protocol_Fellow.docx")
        if not doc_path.exists():
            pytest.skip("No generated documents found")
        fp = ingest_document(doc_path)
        assert fp.total_paragraphs > 50
        assert fp.total_tables >= 1
        assert fp.total_words > 200
        assert fp.condition_slug == "parkinsons"
        assert fp.doc_type == "evidence_based_protocol"
        assert fp.tier == "fellow"
        assert len(fp.sections) >= 5
        assert fp.content_hash != ""
        assert "Calibri" in fp.fonts_used

    def test_ingest_directory(self):
        """Ingest a directory of documents."""
        from sozo_generator.template.learning.document_ingester import ingest_directory
        doc_dir = Path("outputs/documents/parkinsons/")
        if not doc_dir.exists():
            pytest.skip("No generated documents found")
        fps = ingest_directory(doc_dir)
        assert len(fps) >= 10  # parkinsons has ~15 docs

    def test_infer_metadata_from_path(self):
        """Path-based metadata inference works correctly."""
        from sozo_generator.template.learning.document_ingester import _infer_metadata_from_path
        cond, dt, tier = _infer_metadata_from_path(
            Path("outputs/documents/depression/partners/SOZO_Clinical_Handbook_Partners.docx")
        )
        assert cond == "depression"
        assert dt == "handbook"
        assert tier == "partners"

    def test_fingerprint_serialization(self, tmp_path):
        """Fingerprints can be saved and loaded."""
        from sozo_generator.template.learning.document_ingester import (
            ingest_document, save_fingerprints, load_fingerprints
        )
        doc_path = Path("outputs/documents/parkinsons/fellow/Evidence_Based_Protocol_Fellow.docx")
        if not doc_path.exists():
            pytest.skip("No generated documents found")
        fp = ingest_document(doc_path)
        out = tmp_path / "fps.json"
        save_fingerprints([fp], out)
        loaded = load_fingerprints(out)
        assert len(loaded) == 1
        assert loaded[0].condition_slug == "parkinsons"


class TestPatternExtractor:
    @pytest.fixture
    def fingerprints(self):
        from sozo_generator.template.learning.document_ingester import ingest_directory
        doc_dir = Path("outputs/documents/")
        if not doc_dir.exists() or not list(doc_dir.rglob("*.docx")):
            pytest.skip("No generated documents found")
        return ingest_directory(doc_dir)

    def test_extract_master_profile(self, fingerprints):
        from sozo_generator.template.learning.pattern_extractor import PatternExtractor
        extractor = PatternExtractor(fingerprints)
        profile = extractor.extract_master_profile()
        assert profile.total_documents_analyzed >= 15
        assert len(profile.conditions_analyzed) >= 1
        assert profile.primary_font == "Calibri"
        assert len(profile.doc_type_patterns) >= 5

    def test_doc_type_patterns_have_sections(self, fingerprints):
        from sozo_generator.template.learning.pattern_extractor import PatternExtractor
        extractor = PatternExtractor(fingerprints)
        profile = extractor.extract_master_profile()
        for dt, pattern in profile.doc_type_patterns.items():
            assert pattern.typical_section_count > 0, f"{dt} has no sections"
            assert len(pattern.typical_section_order) > 0, f"{dt} has no section order"

    def test_table_patterns_extracted(self, fingerprints):
        from sozo_generator.template.learning.pattern_extractor import PatternExtractor
        extractor = PatternExtractor(fingerprints)
        profile = extractor.extract_master_profile()
        assert len(profile.table_patterns) >= 3

    def test_section_patterns_have_boilerplate(self, fingerprints):
        from sozo_generator.template.learning.pattern_extractor import PatternExtractor
        extractor = PatternExtractor(fingerprints)
        profile = extractor.extract_master_profile()
        boilerplate = [sp for sp in profile.section_patterns if sp.is_boilerplate]
        assert len(boilerplate) >= 1


class TestConsistencyScorer:
    def test_score_existing_document(self):
        """An existing document should score high against its own profile."""
        from sozo_generator.template.learning.learn import learn_from_existing
        from sozo_generator.template.learning.document_ingester import ingest_document
        from sozo_generator.template.learning.consistency_scorer import ConsistencyScorer

        doc_dir = Path("outputs/documents/")
        if not list(doc_dir.rglob("*.docx")):
            pytest.skip("No generated documents found")

        profile = learn_from_existing(doc_dir, Path("/tmp/test_learned/"))
        doc_path = Path("outputs/documents/parkinsons/fellow/Evidence_Based_Protocol_Fellow.docx")
        fp = ingest_document(doc_path)
        scorer = ConsistencyScorer(profile)
        report = scorer.score_document(fp)
        assert report.overall_score >= 0.7
        assert report.passed is True


class TestProfileGuidedGenerator:
    def test_generates_with_profile(self, parkinsons_condition):
        """Profile-guided generator produces valid DocumentSpec."""
        from sozo_generator.template.learning.learn import learn_from_existing
        from sozo_generator.template.learning.profile_guided_generator import ProfileGuidedGenerator
        from sozo_generator.core.enums import DocumentType, Tier

        doc_dir = Path("outputs/documents/")
        if not list(doc_dir.rglob("*.docx")):
            pytest.skip("No generated documents found")

        profile = learn_from_existing(doc_dir, Path("/tmp/test_learned/"))
        gen = ProfileGuidedGenerator(profile=profile)
        assert gen.has_profile

        spec = gen.generate(parkinsons_condition, DocumentType.EVIDENCE_BASED_PROTOCOL, Tier.FELLOW)
        assert spec.condition_slug == "parkinsons"
        assert len(spec.sections) > 0
        assert "Parkinson" in spec.title
        assert spec.output_filename.endswith(".docx")

    def test_falls_back_without_profile(self, parkinsons_condition):
        """Without a profile, falls back to standard generation."""
        from sozo_generator.template.learning.profile_guided_generator import ProfileGuidedGenerator
        from sozo_generator.core.enums import DocumentType, Tier

        gen = ProfileGuidedGenerator(profile_path=Path("/nonexistent/path.json"))
        assert not gen.has_profile

        spec = gen.generate(parkinsons_condition, DocumentType.HANDBOOK, Tier.FELLOW)
        assert spec.condition_slug == "parkinsons"
        assert len(spec.sections) > 0
