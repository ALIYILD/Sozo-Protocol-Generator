"""Tests for canonical document QA validators."""
import json
import os

import pytest

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
)
from sozo_generator.qa.validators.document_completeness_validator import (
    DocumentCompletenessValidator,
)
from sozo_generator.qa.validators.section_length_validator import SectionLengthValidator
from sozo_generator.qa.validators.unresolved_placeholder_validator import (
    UnresolvedPlaceholderValidator,
)
from sozo_generator.qa.validators.asset_presence_validator import AssetPresenceValidator
from sozo_generator.qa.validators.numbering_consistency_validator import (
    NumberingConsistencyValidator,
)
from sozo_generator.qa.validators.citation_coverage_validator import (
    CitationCoverageValidator,
)
from sozo_generator.qa.validators.document_qa_runner import DocumentQARunner


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_text_block(content: str, placeholder_resolved: bool = True) -> CanonicalBlock:
    return CanonicalBlock(
        block_type="text", content=content, placeholder_resolved=placeholder_resolved
    )


def make_section(
    title: str,
    blocks: list,
    level: int = 1,
    section_type: str = "body",
) -> CanonicalSection:
    s = CanonicalSection(
        title=title,
        level=level,
        section_type=section_type,
        blocks=blocks,
    )
    s.word_count = s.compute_word_count()
    return s


def make_minimal_doc(sections=None) -> CanonicalDocument:
    if sections is None:
        sections = [
            make_section(
                "Overview",
                [make_text_block("This is the overview. " * 30)],
            ),
            make_section(
                "Protocol",
                [make_text_block("Protocol details here. " * 20)],
            ),
            make_section("References", [], section_type="references"),
        ]
    return CanonicalDocument(
        condition_slug="test_condition",
        variant="partners",
        document_type="handbook",
        title="Test Handbook",
        sections=sections,
    )


# ===========================================================================
# DocumentCompletenessValidator
# ===========================================================================


class TestDocumentCompletenessValidator:
    def setup_method(self):
        self.validator = DocumentCompletenessValidator()

    def test_minimal_doc_passes(self):
        """Minimal document with 3+ sections passes."""
        doc = make_minimal_doc()
        result = self.validator.validate(doc)
        assert result.passed
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert len(block_issues) == 0

    def test_empty_document_fails(self):
        """Document with 0 sections fails."""
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Empty Doc",
            sections=[],
        )
        result = self.validator.validate(doc)
        assert not result.passed
        categories = [i.category for i in result.issues]
        assert "too_few_sections" in categories

    def test_empty_title_fails(self):
        """Document with empty title issues a block."""
        doc = make_minimal_doc()
        doc.title = ""
        result = self.validator.validate(doc)
        assert not result.passed
        categories = [i.category for i in result.issues]
        assert "missing_title" in categories


# ===========================================================================
# SectionLengthValidator
# ===========================================================================


class TestSectionLengthValidator:
    def setup_method(self):
        self.validator = SectionLengthValidator()

    def test_empty_section_blocks(self):
        """Section with no text blocks gets word_count=0 → BLOCK."""
        empty_section = CanonicalSection(
            title="Empty Body",
            level=1,
            section_type="body",
            blocks=[],
            word_count=0,
        )
        doc = make_minimal_doc(
            sections=[
                empty_section,
                make_section("Other", [make_text_block("Content." * 50)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        assert not result.passed
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert len(block_issues) >= 1
        assert any(i.category == "empty_section" for i in block_issues)

    def test_short_section_warns(self):
        """Section with < 50 words → WARNING."""
        short_section = make_section(
            "Short", [make_text_block("Only ten words are here now done.")],
        )
        # Ensure word_count is small
        doc = make_minimal_doc(
            sections=[
                short_section,
                make_section("Normal", [make_text_block("Content. " * 60)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        warning_issues = [i for i in result.issues if i.severity == "warning"]
        # Should have a very_short_section warning (8 words < 50)
        assert any(i.category == "very_short_section" for i in warning_issues)

    def test_normal_section_passes(self):
        """Section with 200 words passes."""
        section_200 = make_section(
            "Normal Section",
            [make_text_block("word " * 200)],
        )
        doc = make_minimal_doc(
            sections=[
                section_200,
                make_section("Another", [make_text_block("word " * 100)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        # Should pass — no block issues, and no very_short warnings for these sections
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert len(block_issues) == 0


# ===========================================================================
# UnresolvedPlaceholderValidator
# ===========================================================================


class TestUnresolvedPlaceholderValidator:
    def setup_method(self):
        self.validator = UnresolvedPlaceholderValidator()

    def test_no_placeholders_passes(self):
        """Document with no placeholders passes."""
        doc = make_minimal_doc()
        result = self.validator.validate(doc)
        assert result.passed
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert len(block_issues) == 0

    def test_single_placeholder_warns(self):
        """One placeholder_resolved=False → WARNING."""
        unresolved = make_text_block("Some content", placeholder_resolved=False)
        sec = make_section("Test", [unresolved])
        doc = make_minimal_doc(
            sections=[
                sec,
                make_section("Other", [make_text_block("Content. " * 50)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        warning_issues = [i for i in result.issues if i.severity == "warning"]
        assert any(
            i.category == "unresolved_placeholder_flag" for i in warning_issues
        )

    def test_many_placeholders_blocks(self):
        """6+ placeholders → BLOCK."""
        unresolved_blocks = [
            make_text_block(f"Unresolved content {j}", placeholder_resolved=False)
            for j in range(7)
        ]
        sec = make_section("Unresolved Section", unresolved_blocks)
        doc = make_minimal_doc(
            sections=[
                sec,
                make_section("Other", [make_text_block("Content. " * 50)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        assert not result.passed
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert any(
            i.category == "too_many_unresolved_placeholders" for i in block_issues
        )

    def test_bracket_placeholder_detected(self):
        """Block content '[PLACEHOLDER]' detected as placeholder."""
        block = CanonicalBlock(
            block_type="text",
            content="[PLACEHOLDER]",
            placeholder_resolved=True,  # flag is OK but content has brackets
        )
        sec = make_section("Test", [block])
        doc = make_minimal_doc(
            sections=[
                sec,
                make_section("Other", [make_text_block("Content. " * 50)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        # Should detect bracket placeholder in content
        all_categories = [i.category for i in result.issues]
        assert (
            "bracket_placeholder_token" in all_categories
            or "bracket_wrapped_content" in all_categories
        )


# ===========================================================================
# AssetPresenceValidator
# ===========================================================================


class TestAssetPresenceValidator:
    def setup_method(self):
        self.validator = AssetPresenceValidator()

    def test_no_assets_passes(self):
        """Document with no asset blocks passes."""
        doc = make_minimal_doc()
        result = self.validator.validate(doc)
        assert result.passed
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert len(block_issues) == 0

    def test_missing_asset_record_warns(self):
        """Block with asset_id but no asset_record → WARNING."""
        asset_block = CanonicalBlock(
            block_type="table",
            asset_id="asset-xyz-missing",
            asset_record=None,
        )
        sec = make_section("Tables", [asset_block])
        doc = make_minimal_doc(
            sections=[
                sec,
                make_section("Other", [make_text_block("Content. " * 50)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        warning_issues = [i for i in result.issues if i.severity == "warning"]
        assert any(i.category == "missing_asset_record" for i in warning_issues)

    def test_failed_asset_warns(self):
        """asset_record.status == 'failed' → WARNING."""
        failed_record = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_001",
            renderer_type="table_builder",
            status="failed",
            error_message="Render error",
        )
        asset_block = CanonicalBlock(
            block_type="table",
            asset_id=failed_record.asset_id,
            asset_record=failed_record,
        )
        sec = make_section("Tables", [asset_block])
        doc = make_minimal_doc(
            sections=[
                sec,
                make_section("Other", [make_text_block("Content. " * 50)]),
                make_section("References", [], section_type="references"),
            ]
        )
        result = self.validator.validate(doc)
        warning_issues = [i for i in result.issues if i.severity == "warning"]
        assert any(i.category == "asset_generation_failed" for i in warning_issues)


# ===========================================================================
# NumberingConsistencyValidator
# ===========================================================================


class TestNumberingConsistencyValidator:
    def setup_method(self):
        self.validator = NumberingConsistencyValidator()

    def test_sequential_tables_passes(self):
        """Table 1, Table 2 → passes."""
        asset1 = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_001",
            renderer_type="table_builder",
            status="generated",
            numbering_label="Table 1",
            numbering_slot=1,
        )
        asset2 = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_002",
            renderer_type="table_builder",
            status="generated",
            numbering_label="Table 2",
            numbering_slot=2,
        )
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Numbering Test",
            sections=[
                make_section("Overview", [make_text_block("Content. " * 50)]),
                make_section("Protocol", [make_text_block("Protocol. " * 50)]),
                make_section("References", [], section_type="references"),
            ],
            assets=[asset1, asset2],
        )
        result = self.validator.validate(doc)
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert len(block_issues) == 0

    def test_duplicate_numbering_blocks(self):
        """Two assets with same numbering_label → BLOCK."""
        asset1 = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_001",
            renderer_type="table_builder",
            status="generated",
            numbering_label="Table 1",
            numbering_slot=1,
        )
        asset2 = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_002",
            renderer_type="table_builder",
            status="generated",
            numbering_label="Table 1",  # duplicate!
            numbering_slot=1,
        )
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Duplicate Numbering Test",
            sections=[
                make_section("Overview", [make_text_block("Content. " * 50)]),
                make_section("Protocol", [make_text_block("Protocol. " * 50)]),
                make_section("References", [], section_type="references"),
            ],
            assets=[asset1, asset2],
        )
        result = self.validator.validate(doc)
        block_issues = [i for i in result.issues if i.severity == "block"]
        assert any(i.category == "duplicate_numbering" for i in block_issues)


# ===========================================================================
# DocumentQARunner
# ===========================================================================


class TestDocumentQARunner:
    def test_runner_produces_report(self):
        """DocumentQARunner.run() returns DocumentQAReport."""
        from sozo_generator.schemas.canonical import DocumentQAReport

        runner = DocumentQARunner()
        doc = make_minimal_doc()
        report = runner.run(doc)

        assert report is not None
        assert isinstance(report, DocumentQAReport)
        assert report.report_id
        assert report.document_id == doc.document_id
        assert report.condition_slug == "test_condition"
        assert isinstance(report.overall_passed, bool)
        assert isinstance(report.block_count, int)
        assert isinstance(report.warning_count, int)
        assert len(report.validator_results) > 0

    def test_runner_saves_report(self, tmp_path):
        """save_report() writes JSON file."""
        runner = DocumentQARunner()
        doc = make_minimal_doc()
        report = runner.run(doc)

        output_path = str(tmp_path / "qa_report.json")
        saved_path = runner.save_report(report, output_dir=str(tmp_path))
        assert os.path.exists(saved_path)

        with open(saved_path, encoding="utf-8") as fh:
            data = json.load(fh)
        assert data["document_id"] == doc.document_id
        assert "validator_results" in data

    def test_human_readable_output(self):
        """to_human_readable() returns non-empty string."""
        runner = DocumentQARunner()
        doc = make_minimal_doc()
        report = runner.run(doc)
        text = runner.to_human_readable(report)
        assert isinstance(text, str)
        assert len(text) > 0
        # Should contain the document id somewhere
        assert report.document_id in text or report.condition_slug in text

    def test_run_specific_validator(self):
        """run_validator() runs single validator by id."""
        from sozo_generator.schemas.canonical import QAValidationResult

        runner = DocumentQARunner()
        doc = make_minimal_doc()
        result = runner.run_validator("document_completeness", doc)
        assert isinstance(result, QAValidationResult)
        assert result.validator_id == "document_completeness"
        assert result.document_id == doc.document_id
