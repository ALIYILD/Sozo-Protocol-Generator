"""
End-to-end demo test for the canonical pipeline.
Uses 'parkinsons' condition + 'partners' variant + 'protocol' document type
(smaller than handbook, runs faster).
"""
import json
import os
import tempfile

import pytest


@pytest.mark.integration
class TestEndToEndDemo:
    def test_blueprint_builds(self):
        """Full blueprint builds for parkinsons/partners/protocol."""
        from sozo_generator.planning.document_blueprint_builder import (
            DocumentBlueprintBuilder,
        )

        builder = DocumentBlueprintBuilder()
        blueprint = builder.build(
            condition_slug="parkinsons",
            variant="partners",
            document_type="protocol",
            target_page_count=30,
        )
        assert blueprint.blueprint_id
        assert len(blueprint.sections) >= 5
        assert blueprint.condition_slug == "parkinsons"
        assert blueprint.variant == "partners"

    def test_section_generation(self):
        """Sections generate from blueprint without errors."""
        from sozo_generator.planning.document_blueprint_builder import (
            DocumentBlueprintBuilder,
        )
        from sozo_generator.generation.section_generator import SectionGenerator
        from sozo_generator.conditions.registry import get_registry

        builder = DocumentBlueprintBuilder()
        generator = SectionGenerator()

        blueprint = builder.build("parkinsons", "partners", "protocol", 30)

        try:
            condition = get_registry().get("parkinsons")
        except Exception:
            pytest.skip("Condition registry not available")

        sections = []
        for spec in blueprint.sections[:3]:  # only first 3 for speed
            section = generator.generate_section(spec, condition, "partners")
            assert section.section_id
            assert section.title
            sections.append(section)

        assert len(sections) == 3

    def test_table_builder_with_parkinsons(self):
        """TableBuilder builds protocol parameters table for parkinsons."""
        from sozo_generator.assets.table_builder import TableBuilder
        from sozo_generator.conditions.registry import get_registry

        try:
            condition = get_registry().get("parkinsons")
        except Exception:
            pytest.skip("Condition registry not available")

        builder = TableBuilder()
        table = builder.build_protocol_parameters_table(condition)

        assert table.headers
        assert len(table.headers) >= 4

    def test_asset_registry_lifecycle(self):
        """Full asset registry register → update → finalize cycle."""
        from sozo_generator.services.asset_registry import AssetRegistry

        registry = AssetRegistry()

        record = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="section_001",
            renderer_type="table_builder",
            source_data={"headers": ["Col1", "Col2"], "rows": [["A", "B"]]},
            caption="Protocol Parameters",
        )
        assert record.status == "pending"

        registry.update_status(record.asset_id, "generated", output_path="/tmp/table.docx")
        updated = registry.get(record.asset_id)
        assert updated.status == "generated"

        registry.finalize_numbering()
        finalized = registry.get(record.asset_id)
        assert finalized.numbering_label == "Table 1"

    def test_qa_runner_on_minimal_doc(self):
        """QA runner completes without errors on minimal document."""
        from sozo_generator.qa.validators.document_qa_runner import DocumentQARunner
        from sozo_generator.schemas.canonical import (
            CanonicalBlock,
            CanonicalDocument,
            CanonicalSection,
        )

        runner = DocumentQARunner()

        section = CanonicalSection(
            title="Overview",
            level=1,
            blocks=[
                CanonicalBlock(
                    block_type="text",
                    content="This is a test overview. " * 30,
                )
            ],
        )
        section.word_count = section.compute_word_count()

        doc = CanonicalDocument(
            condition_slug="parkinsons",
            variant="partners",
            document_type="handbook",
            title="Test Handbook",
            sections=[section],
        )

        report = runner.run(doc)
        assert report.report_id
        assert isinstance(report.overall_passed, bool)
        assert report.block_count >= 0

    def test_html_export(self, tmp_path):
        """HTMLPreviewExporter generates HTML file."""
        from sozo_generator.export.html_preview_exporter import HTMLPreviewExporter
        from sozo_generator.schemas.canonical import (
            CanonicalBlock,
            CanonicalDocument,
            CanonicalSection,
        )

        exporter = HTMLPreviewExporter(output_dir=str(tmp_path))

        doc = CanonicalDocument(
            condition_slug="parkinsons",
            variant="partners",
            document_type="handbook",
            title="Test Handbook",
            subtitle="A test document",
            sections=[
                CanonicalSection(
                    title="Overview",
                    level=1,
                    blocks=[
                        CanonicalBlock(
                            block_type="text", content="Overview content."
                        )
                    ],
                )
            ],
        )

        output_path = exporter.export(doc, output_path=str(tmp_path / "test.html"))
        assert os.path.exists(output_path)
        with open(output_path, encoding="utf-8") as f:
            content = f.read()
        assert "Test Handbook" in content
        assert "<html" in content.lower()

    def test_outline_planner_protocol(self):
        """OutlinePlanner produces valid protocol outline for parkinsons."""
        from sozo_generator.planning.outline_planner import OutlinePlanner

        planner = OutlinePlanner()
        outline = planner.plan(
            condition_slug="parkinsons",
            variant="partners",
            document_type="protocol",
            target_page_count=30,
        )
        assert len(outline) >= 5
        required_keys = {"title", "purpose", "section_type", "target_word_count"}
        for entry in outline:
            assert required_keys.issubset(set(entry.keys()))

    def test_qa_report_serialization(self):
        """QA report round-trips through JSON serialization."""
        from sozo_generator.qa.validators.document_qa_runner import DocumentQARunner
        from sozo_generator.schemas.canonical import (
            CanonicalBlock,
            CanonicalDocument,
            CanonicalSection,
        )

        runner = DocumentQARunner()

        section = CanonicalSection(
            title="Overview",
            level=1,
            blocks=[
                CanonicalBlock(
                    block_type="text",
                    content="Test content for serialization. " * 20,
                )
            ],
        )
        section.word_count = section.compute_word_count()

        doc = CanonicalDocument(
            condition_slug="parkinsons",
            variant="fellow",
            document_type="protocol",
            title="Serialization Test",
            sections=[
                section,
                CanonicalSection(
                    title="Protocol",
                    level=1,
                    blocks=[
                        CanonicalBlock(
                            block_type="text",
                            content="Protocol content. " * 20,
                        )
                    ],
                ),
                CanonicalSection(title="References", level=1, section_type="references"),
            ],
        )
        report = runner.run(doc)

        # Serialize and round-trip
        report_dict = report.to_dict()
        assert isinstance(report_dict, dict)
        serialized = json.dumps(report_dict, default=str)
        deserialized = json.loads(serialized)
        assert deserialized["document_id"] == doc.document_id
        assert deserialized["condition_slug"] == "parkinsons"
        assert "validator_results" in deserialized
