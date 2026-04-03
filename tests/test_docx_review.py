"""Tests for DOCX comment extraction and review-driven regeneration."""
import pytest
from pathlib import Path


FIXTURE_PATH = Path("tests/fixtures/reviewed_parkinsons.docx")


# ── Comment Extraction Tests ─────────────────────────────────────────────


class TestDocxCommentExtraction:
    @pytest.fixture
    def result(self):
        from sozo_generator.knowledge.revision.docx_comments import extract_docx_comments
        return extract_docx_comments(str(FIXTURE_PATH))

    def test_extracts_5_comments(self, result):
        assert result.comments_extracted == 5

    def test_comment_authors(self, result):
        authors = {c.author for c in result.comments}
        assert "Dr. Smith" in authors
        assert "Dr. Jones" in authors

    def test_comment_text_preserved(self, result):
        texts = [c.text for c in result.comments]
        assert any("TPS rationale" in t for t in texts)
        assert any("contraindications" in t.lower() for t in texts)
        assert any("pathophysiology" in t.lower() for t in texts)

    def test_extraction_from_nonexistent_file(self):
        from sozo_generator.knowledge.revision.docx_comments import extract_docx_comments
        result = extract_docx_comments("/nonexistent/file.docx")
        assert result.comments_extracted == 0
        assert len(result.extraction_warnings) > 0


# ── Section Mapping Tests ────────────────────────────────────────────────


class TestSectionMapping:
    @pytest.fixture
    def mapped_result(self):
        from sozo_generator.knowledge.revision.docx_comments import (
            extract_docx_comments, map_comments_to_sections
        )
        result = extract_docx_comments(str(FIXTURE_PATH))
        return map_comments_to_sections(result)

    def test_all_comments_mapped(self, mapped_result):
        assert mapped_result.comments_mapped == 5

    def test_tps_comment_maps_to_protocols(self, mapped_result):
        tps_comment = next(c for c in mapped_result.comments if "TPS" in c.text)
        assert tps_comment.mapped_section == "protocols_tps"

    def test_contraindication_maps_to_safety(self, mapped_result):
        safety_comment = next(c for c in mapped_result.comments if "contraindication" in c.text.lower())
        assert safety_comment.mapped_section == "safety"

    def test_pathophysiology_maps_correctly(self, mapped_result):
        patho_comment = next(c for c in mapped_result.comments if "pathophysiology" in c.text.lower())
        assert patho_comment.mapped_section == "pathophysiology"
        assert patho_comment.mapping_confidence > 0.5

    def test_network_comment_maps_to_network_profiles(self, mapped_result):
        net_comment = next(c for c in mapped_result.comments if "network" in c.text.lower())
        assert net_comment.mapped_section == "network_profiles"

    def test_mapping_confidence_present(self, mapped_result):
        for c in mapped_result.comments:
            assert c.mapping_confidence > 0

    def test_pathophysiology_high_confidence(self, mapped_result):
        """Pathophysiology has multiple strong signal matches → high confidence."""
        patho = next(c for c in mapped_result.comments if "pathophysiology" in c.text.lower())
        assert patho.mapping_confidence >= 0.9
        assert patho.mapping_state == "high_confidence"

    def test_safety_high_confidence(self, mapped_result):
        """Contraindications + pregnancy = strong safety signal."""
        safety = next(c for c in mapped_result.comments if "contraindication" in c.text.lower())
        assert safety.mapping_confidence >= 0.7
        assert safety.mapping_state == "high_confidence"

    def test_mapping_has_explanation(self, mapped_result):
        for c in mapped_result.comments:
            assert c.mapping_explanation, f"Comment '{c.text[:30]}' missing explanation"

    def test_mapping_has_signals(self, mapped_result):
        for c in mapped_result.comments:
            assert len(c.mapping_signals) > 0, f"Comment '{c.text[:30]}' has no signals"

    def test_mapping_state_set(self, mapped_result):
        states = {c.mapping_state for c in mapped_result.comments}
        assert "unmapped" not in states  # All should be mapped


# ── Integration with Review Pipeline ─────────────────────────────────────


class TestDocxToReviewPipeline:
    def test_convert_to_review_set(self):
        from sozo_generator.knowledge.revision.docx_comments import (
            extract_docx_comments, map_comments_to_sections, docx_comments_to_review_set
        )
        result = extract_docx_comments(str(FIXTURE_PATH))
        result = map_comments_to_sections(result)
        review_set = docx_comments_to_review_set(result, "parkinsons", "evidence_based_protocol", "fellow")

        assert len(review_set.comments) == 5
        assert review_set.condition_slug == "parkinsons"
        assert review_set.blueprint_slug == "evidence_based_protocol"

    def test_review_set_has_section_targets(self):
        from sozo_generator.knowledge.revision.docx_comments import (
            extract_docx_comments, map_comments_to_sections, docx_comments_to_review_set
        )
        result = extract_docx_comments(str(FIXTURE_PATH))
        result = map_comments_to_sections(result)
        review_set = docx_comments_to_review_set(result, "parkinsons", "evidence_based_protocol", "fellow")

        sections = [c.target_section_slug for c in review_set.comments]
        assert "protocols_tps" in sections
        assert "safety" in sections

    def test_full_pipeline_to_change_plan(self):
        from sozo_generator.knowledge.revision.docx_comments import (
            extract_docx_comments, map_comments_to_sections, docx_comments_to_review_set
        )
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        result = extract_docx_comments(str(FIXTURE_PATH))
        result = map_comments_to_sections(result)
        review_set = docx_comments_to_review_set(result, "parkinsons", "evidence_based_protocol", "fellow")

        engine = RevisionEngine()
        plan = engine.create_change_plan(review_set)

        assert plan.total_changes >= 4
        assert plan.condition_slug == "parkinsons"

    def test_full_pipeline_to_regeneration(self):
        from sozo_generator.knowledge.revision.docx_comments import (
            extract_docx_comments, map_comments_to_sections, docx_comments_to_review_set
        )
        from sozo_generator.knowledge.revision.engine import RevisionEngine

        result = extract_docx_comments(str(FIXTURE_PATH))
        result = map_comments_to_sections(result)
        review_set = docx_comments_to_review_set(result, "parkinsons", "evidence_based_protocol", "fellow")

        engine = RevisionEngine()
        regen = engine.review_and_regenerate(
            document_id="docx-test",
            condition="parkinsons",
            blueprint="evidence_based_protocol",
            tier="fellow",
            comments=review_set,
            force=True,
        )

        assert regen.success
        assert regen.output_path
        assert Path(regen.output_path).exists()


# ── Ingest Result Model Tests ────────────────────────────────────────────


class TestIngestResultModel:
    def test_to_text(self):
        from sozo_generator.knowledge.revision.docx_comments import (
            extract_docx_comments, map_comments_to_sections
        )
        result = extract_docx_comments(str(FIXTURE_PATH))
        result = map_comments_to_sections(result)
        text = result.to_text()
        assert "DOCX REVIEW INGEST" in text
        assert "Comments extracted: 5" in text
