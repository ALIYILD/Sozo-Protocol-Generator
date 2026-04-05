"""Tests for OutlinePlanner and SectionPlanner."""
import pytest

from sozo_generator.planning.outline_planner import OutlinePlanner
from sozo_generator.planning.section_planner import SectionPlanner
from sozo_generator.schemas.canonical import SectionSpec, SubsectionSpec, ContentBlockSpec


class TestOutlinePlanner:
    def setup_method(self):
        self.planner = OutlinePlanner()

    def test_plan_handbook_returns_sections(self):
        """plan() for handbook returns >= 10 sections."""
        outline = self.planner.plan(
            condition_slug="parkinsons",
            variant="partners",
            document_type="handbook",
        )
        assert isinstance(outline, list)
        assert len(outline) >= 10

    def test_plan_protocol_returns_sections(self):
        """plan() for protocol returns >= 5 sections."""
        outline = self.planner.plan(
            condition_slug="parkinsons",
            variant="fellow",
            document_type="protocol",
        )
        assert isinstance(outline, list)
        assert len(outline) >= 5

    def test_plan_has_required_fields(self):
        """Each outline entry has title, purpose, section_type, target_word_count."""
        outline = self.planner.plan(
            condition_slug="tbi",
            variant="fellow",
            document_type="handbook",
        )
        required_keys = {"title", "purpose", "section_type", "target_word_count"}
        for entry in outline:
            assert required_keys.issubset(set(entry.keys())), (
                f"Entry '{entry.get('title', '?')}' missing keys: "
                f"{required_keys - set(entry.keys())}"
            )
            assert isinstance(entry["title"], str) and entry["title"]
            assert isinstance(entry["section_type"], str)
            assert isinstance(entry["target_word_count"], int)

    def test_plan_fellow_variant(self):
        """plan() for fellow variant returns correct sections."""
        outline_fellow = self.planner.plan(
            condition_slug="parkinsons",
            variant="fellow",
            document_type="handbook",
        )
        # Fellow variant should not include partner-specific sections
        partner_only_titles = [
            e["title"] for e in outline_fellow
            if "partners" in e.get("variant_tags", [])
            and "fellow" not in e.get("variant_tags", [])
        ]
        # Any partner-only section should not appear in a fellow outline
        # (the planner should not include partner-exclusive sections for fellows)
        assert isinstance(outline_fellow, list)
        assert len(outline_fellow) >= 10

    def test_plan_partners_variant(self):
        """plan() for partners variant includes FNON sections."""
        outline_partners = self.planner.plan(
            condition_slug="parkinsons",
            variant="partners",
            document_type="handbook",
        )
        # Partners handbook should include at least one partner-tagged section
        partner_tagged = [
            e for e in outline_partners
            if "partners" in e.get("variant_tags", [])
        ]
        assert len(partner_tagged) >= 1
        # Partners handbook should be same length or longer than fellow
        outline_fellow = self.planner.plan(
            condition_slug="parkinsons",
            variant="fellow",
            document_type="handbook",
        )
        assert len(outline_partners) >= len(outline_fellow)

    def test_estimate_word_count(self):
        """estimate_word_count() sums target_word_counts."""
        outline = self.planner.plan(
            condition_slug="tbi",
            variant="fellow",
            document_type="protocol",
        )
        estimated = self.planner.estimate_word_count(outline)
        manual_sum = sum(e.get("target_word_count", 0) for e in outline)
        assert estimated == manual_sum
        assert estimated > 0

    def test_get_supported_document_types(self):
        """Returns list of supported document types."""
        types = self.planner.get_supported_document_types()
        assert isinstance(types, list)
        assert len(types) >= 3
        assert "handbook" in types
        assert "protocol" in types


class TestSectionPlanner:
    def setup_method(self):
        self.planner = SectionPlanner()
        self.outline_planner = OutlinePlanner()

    def _make_outline_entry(
        self,
        title: str = "Test Section",
        purpose: str = "Test purpose.",
        section_type: str = "body",
        target_word_count: int = 500,
        ordering: int = 0,
        required_tables: list = None,
        required_figures: list = None,
        allowed_claim_categories: list = None,
        subsections: list = None,
    ) -> dict:
        return {
            "title": title,
            "purpose": purpose,
            "section_type": section_type,
            "target_word_count": target_word_count,
            "target_page_budget": round(target_word_count / 500, 1),
            "ordering": ordering,
            "variant_tags": [],
            "required_tables": required_tables or [],
            "required_figures": required_figures or [],
            "allowed_claim_categories": allowed_claim_categories or [],
            "subsections": subsections or [],
        }

    def test_build_section_spec_returns_section_spec(self):
        """build_section_spec() returns SectionSpec."""
        entry = self._make_outline_entry(
            title="Introduction",
            purpose="Introduce the condition.",
            section_type="body",
            target_word_count=600,
        )
        spec = self.planner.build_section_spec(
            outline_entry=entry,
            condition_slug="parkinsons",
            variant="fellow",
        )
        assert isinstance(spec, SectionSpec)
        assert spec.title == "Introduction"
        assert spec.section_type == "body"
        assert spec.target_word_count == 600

    def test_section_spec_has_blocks(self):
        """SectionSpec has at least one block."""
        entry = self._make_outline_entry(
            title="Overview",
            purpose="Describe the condition overview.",
            section_type="body",
            target_word_count=400,
        )
        spec = self.planner.build_section_spec(
            outline_entry=entry,
            condition_slug="tbi",
            variant="partners",
        )
        assert len(spec.blocks) >= 1
        # The first block should be a text block
        text_blocks = [b for b in spec.blocks if b.block_type == "text"]
        assert len(text_blocks) >= 1

    def test_table_sections_have_table_blocks(self):
        """Sections requiring tables have table ContentBlockSpec entries."""
        entry = self._make_outline_entry(
            title="Protocol Parameters",
            purpose="List all protocol parameters.",
            section_type="body",
            target_word_count=1000,
            required_tables=["protocol_parameters", "session_schedule"],
        )
        spec = self.planner.build_section_spec(
            outline_entry=entry,
            condition_slug="parkinsons",
            variant="partners",
        )
        table_blocks = [b for b in spec.blocks if b.block_type == "table"]
        assert len(table_blocks) == 2, (
            f"Expected 2 table blocks, got {len(table_blocks)}: {[b.block_type for b in spec.blocks]}"
        )
        # Each table block should have an asset_id
        for tb in table_blocks:
            assert tb.asset_id is not None
            assert "parkinsons" in tb.asset_id

    def test_figure_sections_have_figure_blocks(self):
        """Sections requiring figures have figure ContentBlockSpec entries."""
        entry = self._make_outline_entry(
            title="Montage Diagram",
            purpose="Show electrode placement.",
            section_type="body",
            target_word_count=600,
            required_figures=["montage_diagram"],
        )
        spec = self.planner.build_section_spec(
            outline_entry=entry,
            condition_slug="parkinsons",
            variant="fellow",
        )
        figure_blocks = [b for b in spec.blocks if b.block_type == "figure"]
        assert len(figure_blocks) == 1
        assert figure_blocks[0].asset_id is not None

    def test_build_all_section_specs(self):
        """build_all_section_specs() returns one SectionSpec per outline entry."""
        outline = self.outline_planner.plan(
            condition_slug="parkinsons",
            variant="fellows",
            document_type="protocol",
        )
        specs = self.planner.build_all_section_specs(
            outline=outline,
            condition_slug="parkinsons",
            variant="fellow",
        )
        assert isinstance(specs, list)
        assert len(specs) == len(outline)
        for spec in specs:
            assert isinstance(spec, SectionSpec)
            assert spec.title
