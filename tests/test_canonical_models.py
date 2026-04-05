"""Tests for canonical data models."""
import pytest
from sozo_generator.schemas.canonical import (
    CanonicalDocument,
    CanonicalSection,
    CanonicalBlock,
    DocumentBlueprint,
    SectionSpec,
    SubsectionSpec,
    ContentBlockSpec,
    AssetRecord,
    AssemblyProvenance,
    QAValidationIssue,
    QAValidationResult,
    DocumentQAReport,
    CanonicalTable,
    CanonicalFigure,
    CanonicalChart,
    CanonicalCitation,
)


class TestCanonicalModels:
    def test_canonical_document_creation(self):
        """CanonicalDocument creates with defaults."""
        doc = CanonicalDocument(
            condition_slug="test",
            variant="partners",
            document_type="handbook",
            title="Test Doc",
        )
        assert doc.document_id  # UUID auto-generated
        assert doc.condition_slug == "test"
        assert doc.variant == "partners"
        assert doc.document_type == "handbook"
        assert doc.title == "Test Doc"
        assert doc.version == "1.0"
        assert doc.sections == []
        assert doc.assets == []
        assert doc.references == []
        assert doc.qa_status == "pending"

    def test_canonical_document_total_word_count(self):
        """total_word_count sums across all sections."""
        sec1 = CanonicalSection(
            title="Section One",
            level=1,
            blocks=[CanonicalBlock(block_type="text", content="one two three four five")],
        )
        sec2 = CanonicalSection(
            title="Section Two",
            level=1,
            blocks=[CanonicalBlock(block_type="text", content="alpha beta gamma")],
        )
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Count Test",
            sections=[sec1, sec2],
        )
        total = doc.total_word_count()
        assert total == 8  # 5 + 3

    def test_canonical_document_get_section(self):
        """get_section finds sections by id recursively."""
        child = CanonicalSection(title="Child", level=2)
        parent = CanonicalSection(title="Parent", level=1, subsections=[child])
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Sec Test",
            sections=[parent],
        )
        # Find top-level
        found = doc.get_section(parent.section_id)
        assert found is not None
        assert found.title == "Parent"
        # Find child
        found_child = doc.get_section(child.section_id)
        assert found_child is not None
        assert found_child.title == "Child"
        # Non-existent
        assert doc.get_section("nonexistent-id") is None

    def test_canonical_document_get_asset(self):
        """get_asset finds assets by id."""
        asset = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_001",
            renderer_type="table_builder",
        )
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Asset Test",
            assets=[asset],
        )
        found = doc.get_asset(asset.asset_id)
        assert found is not None
        assert found.asset_id == asset.asset_id
        assert doc.get_asset("unknown-id") is None

    def test_canonical_document_unresolved_placeholders(self):
        """unresolved_placeholders returns correct list."""
        resolved_block = CanonicalBlock(
            block_type="text", content="Resolved.", placeholder_resolved=True
        )
        unresolved_block = CanonicalBlock(
            block_type="text", content="[PLACEHOLDER]", placeholder_resolved=False
        )
        sec = CanonicalSection(
            title="Sec",
            level=1,
            blocks=[resolved_block, unresolved_block],
        )
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Placeholder Test",
            sections=[sec],
        )
        unresolved = doc.unresolved_placeholders()
        assert len(unresolved) == 1
        assert unresolved[0] == unresolved_block.block_id

    def test_canonical_document_all_asset_ids(self):
        """all_asset_ids collects all block asset references."""
        block_with_asset = CanonicalBlock(
            block_type="table",
            asset_id="asset-abc",
        )
        block_no_asset = CanonicalBlock(block_type="text", content="hello")
        block_dup = CanonicalBlock(block_type="table", asset_id="asset-abc")
        sec = CanonicalSection(
            title="Sec",
            level=1,
            blocks=[block_with_asset, block_no_asset, block_dup],
        )
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="Asset IDs Test",
            sections=[sec],
        )
        ids = doc.all_asset_ids()
        assert ids == ["asset-abc"]  # deduplicated, no None

    def test_canonical_document_build_toc(self):
        """build_toc builds correct TOC entries from sections."""
        sec_a = CanonicalSection(title="Alpha", level=1, ordering=0)
        sec_b = CanonicalSection(title="Beta", level=1, ordering=1)
        doc = CanonicalDocument(
            condition_slug="test",
            variant="fellow",
            document_type="handbook",
            title="TOC Test",
            sections=[sec_b, sec_a],  # intentionally reversed
        )
        toc = doc.build_toc()
        # Should be sorted by ordering
        assert toc[0]["title"] == "Alpha"
        assert toc[1]["title"] == "Beta"
        assert all("section_id" in entry for entry in toc)
        assert all(entry["page_hint"] is None for entry in toc)

    def test_canonical_section_compute_word_count(self):
        """compute_word_count counts words in text blocks recursively."""
        child_block = CanonicalBlock(
            block_type="text", content="child words here"
        )
        child_section = CanonicalSection(
            title="Child", level=2, blocks=[child_block]
        )
        parent_block = CanonicalBlock(
            block_type="text", content="parent content now"
        )
        parent_section = CanonicalSection(
            title="Parent",
            level=1,
            blocks=[parent_block],
            subsections=[child_section],
        )
        count = parent_section.compute_word_count()
        # "parent content now" = 3, "child words here" = 3
        assert count == 6
        assert parent_section.word_count == 6

    def test_asset_record_defaults(self):
        """AssetRecord has correct defaults."""
        record = AssetRecord(
            asset_type="table",
            condition_slug="test",
            section_target="sec_001",
            renderer_type="table_builder",
        )
        assert record.asset_id  # auto UUID
        assert record.status == "pending"
        assert record.caption is None
        assert record.output_path is None
        assert record.numbering_slot is None
        assert record.numbering_label is None
        assert record.checksum is None
        assert record.variant_tags == []
        assert record.source_data == {}

    def test_asset_record_status_lifecycle(self):
        """AssetRecord status field accepts all valid values."""
        valid_statuses = [
            "pending", "generating", "generated", "failed", "validated", "missing"
        ]
        for status in valid_statuses:
            record = AssetRecord(
                asset_type="figure",
                condition_slug="test",
                section_target="sec_001",
                renderer_type="figure_builder",
                status=status,
            )
            assert record.status == status

    def test_document_blueprint_creation(self):
        """DocumentBlueprint creates with defaults."""
        bp = DocumentBlueprint(
            condition_slug="parkinsons",
            variant="partners",
            document_type="handbook",
            title="Parkinson's Handbook",
        )
        assert bp.blueprint_id  # auto UUID
        assert bp.condition_slug == "parkinsons"
        assert bp.variant == "partners"
        assert bp.document_type == "handbook"
        assert bp.target_page_count == 50
        assert bp.sections == []
        assert bp.version == "1.0"
        assert bp.created_at

    def test_qa_validation_result_passed(self):
        """QAValidationResult.passed=True only with zero block-severity issues."""
        block_issue = QAValidationIssue(
            validator_id="test",
            severity="block",
            category="test_block",
            message="This blocks export.",
        )
        warning_issue = QAValidationIssue(
            validator_id="test",
            severity="warning",
            category="test_warn",
            message="This is a warning.",
        )
        # With block: passed should be False
        result_with_block = QAValidationResult(
            validator_id="test",
            document_id="doc_001",
            condition_slug="test",
            passed=False,
            issues=[block_issue, warning_issue],
        )
        assert result_with_block.passed is False

        # With only warnings: can be True
        result_warnings_only = QAValidationResult(
            validator_id="test",
            document_id="doc_001",
            condition_slug="test",
            passed=True,
            issues=[warning_issue],
        )
        assert result_warnings_only.passed is True

    def test_document_qa_report_compute_counts(self):
        """DocumentQAReport.compute_counts() correctly tallies issues."""
        block_issue = QAValidationIssue(
            validator_id="v1",
            severity="block",
            category="b",
            message="block",
        )
        warn_issue = QAValidationIssue(
            validator_id="v1",
            severity="warning",
            category="w",
            message="warn",
        )
        info_issue = QAValidationIssue(
            validator_id="v2",
            severity="info",
            category="i",
            message="info",
        )
        result1 = QAValidationResult(
            validator_id="v1",
            document_id="doc_001",
            condition_slug="test",
            passed=False,
            issues=[block_issue, warn_issue],
        )
        result2 = QAValidationResult(
            validator_id="v2",
            document_id="doc_001",
            condition_slug="test",
            passed=True,
            issues=[info_issue],
        )
        report = DocumentQAReport(
            document_id="doc_001",
            condition_slug="test",
            variant="fellow",
            validator_results=[result1, result2],
        )
        report.compute_counts()
        assert report.block_count == 1
        assert report.warning_count == 1
        assert report.info_count == 1
        assert report.overall_passed is False  # one result has passed=False

    def test_document_qa_report_to_dict(self):
        """DocumentQAReport.to_dict() serializes cleanly."""
        report = DocumentQAReport(
            document_id="doc_001",
            condition_slug="test",
            variant="fellow",
        )
        report.compute_counts()
        d = report.to_dict()
        assert isinstance(d, dict)
        assert d["document_id"] == "doc_001"
        assert "report_id" in d
        assert "validator_results" in d
        assert "overall_passed" in d

    def test_content_block_spec_defaults(self):
        """ContentBlockSpec has uuid default for block_id."""
        spec = ContentBlockSpec()
        assert spec.block_id  # non-empty UUID
        assert len(spec.block_id) == 36  # UUID4 length
        assert spec.block_type == "text"
        assert spec.placeholder is False
        assert spec.variant_tags == []
        assert spec.target_word_count == 0

    def test_canonical_table_creation(self):
        """CanonicalTable basic creation."""
        table = CanonicalTable(
            title="Protocol Parameters",
            headers=["Protocol", "Modality", "Sessions"],
            rows=[["Alpha", "tDCS", "20"]],
        )
        assert table.table_id  # auto UUID
        assert table.title == "Protocol Parameters"
        assert len(table.headers) == 3
        assert len(table.rows) == 1
        assert table.rows[0][0] == "Alpha"
        assert table.landscape is False

    def test_assembly_provenance_creation(self):
        """AssemblyProvenance creates with required fields."""
        prov = AssemblyProvenance(
            document_id="doc_001",
            condition_slug="parkinsons",
            variant="partners",
        )
        assert prov.provenance_id  # auto UUID
        assert prov.document_id == "doc_001"
        assert prov.condition_slug == "parkinsons"
        assert prov.variant == "partners"
        assert prov.section_generation_log == []
        assert prov.asset_generation_log == []
        assert prov.assembly_log == []
        assert prov.errors == []
        assert prov.build_duration_seconds == 0.0
