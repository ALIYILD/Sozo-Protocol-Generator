"""Tests for AssetRegistry."""
import hashlib
import json
import os
import tempfile

import pytest

from sozo_generator.services.asset_registry import (
    AssetRegistry,
    get_asset_registry,
    reset_registry,
)


class TestAssetRegistry:
    def setup_method(self):
        reset_registry()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def test_register_asset(self):
        """register() creates an AssetRecord."""
        registry = AssetRegistry()
        record = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="sec_001",
            renderer_type="table_builder",
            source_data={"headers": ["A", "B"], "rows": [["x", "y"]]},
            caption="Protocol Parameters",
        )
        assert record is not None
        assert record.asset_type == "table"
        assert record.condition_slug == "parkinsons"
        assert record.section_target == "sec_001"
        assert record.renderer_type == "table_builder"
        assert record.caption == "Protocol Parameters"

    def test_register_returns_asset_record(self):
        """register() returns AssetRecord with generated asset_id."""
        registry = AssetRegistry()
        record = registry.register(
            asset_type="figure",
            condition_slug="tbi",
            section_target="sec_002",
            renderer_type="figure_builder",
            source_data={},
        )
        assert record.asset_id
        assert len(record.asset_id) == 36  # UUID4 format
        assert record.status == "pending"

    def test_get_asset(self):
        """get() retrieves by asset_id."""
        registry = AssetRegistry()
        record = registry.register(
            asset_type="chart",
            condition_slug="depression",
            section_target="sec_003",
            renderer_type="chart_builder",
            source_data={},
        )
        retrieved = registry.get(record.asset_id)
        assert retrieved is not None
        assert retrieved.asset_id == record.asset_id
        assert retrieved.asset_type == "chart"

    def test_get_nonexistent_returns_none(self):
        """get() returns None for unknown asset_id."""
        registry = AssetRegistry()
        result = registry.get("nonexistent-id-12345")
        assert result is None

    def test_update_status(self):
        """update_status() changes status and updates updated_at."""
        registry = AssetRegistry()
        record = registry.register(
            asset_type="table",
            condition_slug="migraine",
            section_target="sec_001",
            renderer_type="table_builder",
            source_data={},
        )
        old_updated_at = record.updated_at

        updated = registry.update_status(record.asset_id, "generating")
        assert updated.status == "generating"
        # updated_at should be refreshed (may be the same second; just ensure not missing)
        assert updated.updated_at

    def test_update_status_with_path(self):
        """update_status() sets output_path."""
        registry = AssetRegistry()
        record = registry.register(
            asset_type="figure",
            condition_slug="alzheimers",
            section_target="sec_001",
            renderer_type="figure_builder",
            source_data={},
        )
        registry.update_status(
            record.asset_id, "generated", output_path="/tmp/figure_001.png"
        )
        retrieved = registry.get(record.asset_id)
        assert retrieved.status == "generated"
        assert retrieved.output_path == "/tmp/figure_001.png"

    # ------------------------------------------------------------------
    # Numbering
    # ------------------------------------------------------------------

    def test_finalize_numbering_tables(self):
        """finalize_numbering() assigns Table 1, Table 2, ... to generated tables."""
        registry = AssetRegistry()
        t1 = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="sec_001",
            renderer_type="table_builder",
            source_data={},
        )
        t2 = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="sec_002",
            renderer_type="table_builder",
            source_data={},
        )
        registry.update_status(t1.asset_id, "generated")
        registry.update_status(t2.asset_id, "generated")
        registry.finalize_numbering()

        r1 = registry.get(t1.asset_id)
        r2 = registry.get(t2.asset_id)
        labels = {r1.numbering_label, r2.numbering_label}
        assert "Table 1" in labels
        assert "Table 2" in labels

    def test_finalize_numbering_figures(self):
        """finalize_numbering() assigns Figure 1, Figure 2, ... to generated figures."""
        registry = AssetRegistry()
        f1 = registry.register(
            asset_type="figure",
            condition_slug="parkinsons",
            section_target="sec_001",
            renderer_type="figure_builder",
            source_data={},
        )
        f2 = registry.register(
            asset_type="figure",
            condition_slug="parkinsons",
            section_target="sec_002",
            renderer_type="figure_builder",
            source_data={},
        )
        registry.update_status(f1.asset_id, "generated")
        registry.update_status(f2.asset_id, "generated")
        registry.finalize_numbering()

        r1 = registry.get(f1.asset_id)
        r2 = registry.get(f2.asset_id)
        labels = {r1.numbering_label, r2.numbering_label}
        assert "Figure 1" in labels
        assert "Figure 2" in labels

    def test_finalize_numbering_charts_count_as_figures(self):
        """finalize_numbering() charts get Figure N numbering."""
        registry = AssetRegistry()
        c1 = registry.register(
            asset_type="chart",
            condition_slug="depression",
            section_target="sec_001",
            renderer_type="chart_builder",
            source_data={},
        )
        registry.update_status(c1.asset_id, "generated")
        registry.finalize_numbering()
        r = registry.get(c1.asset_id)
        assert r.numbering_label is not None
        assert r.numbering_label.startswith("Figure")

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def test_get_by_status(self):
        """get_by_status() filters correctly."""
        registry = AssetRegistry()
        r1 = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="sec_001",
            renderer_type="table_builder",
            source_data={},
        )
        r2 = registry.register(
            asset_type="figure",
            condition_slug="parkinsons",
            section_target="sec_002",
            renderer_type="figure_builder",
            source_data={},
        )
        registry.update_status(r1.asset_id, "generated")
        # r2 remains "pending"

        pending = registry.get_by_status("pending")
        generated = registry.get_by_status("generated")
        assert len(pending) == 1
        assert pending[0].asset_id == r2.asset_id
        assert len(generated) == 1
        assert generated[0].asset_id == r1.asset_id

    def test_get_missing_assets(self):
        """get_missing_assets() returns failed+missing assets."""
        registry = AssetRegistry()
        r_ok = registry.register(
            asset_type="table",
            condition_slug="tbi",
            section_target="sec_001",
            renderer_type="table_builder",
            source_data={},
        )
        r_fail = registry.register(
            asset_type="figure",
            condition_slug="tbi",
            section_target="sec_002",
            renderer_type="figure_builder",
            source_data={},
        )
        r_missing = registry.register(
            asset_type="chart",
            condition_slug="tbi",
            section_target="sec_003",
            renderer_type="chart_builder",
            source_data={},
        )
        registry.update_status(r_ok.asset_id, "generated")
        registry.update_status(r_fail.asset_id, "failed", error_message="Render error")
        registry.update_status(r_missing.asset_id, "missing")

        missing = registry.get_missing_assets()
        missing_ids = {m.asset_id for m in missing}
        assert r_fail.asset_id in missing_ids
        assert r_missing.asset_id in missing_ids
        assert r_ok.asset_id not in missing_ids

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def test_save_and_load(self):
        """save() and load() round-trip correctly."""
        registry = AssetRegistry()
        r1 = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="sec_001",
            renderer_type="table_builder",
            source_data={"headers": ["H1", "H2"], "rows": [["A", "B"]]},
            caption="Test Caption",
        )
        registry.update_status(r1.asset_id, "generated")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            registry.save(path)
            assert os.path.exists(path)

            loaded = AssetRegistry()
            loaded.load(path)

            retrieved = loaded.get(r1.asset_id)
            assert retrieved is not None
            assert retrieved.asset_type == "table"
            assert retrieved.status == "generated"
            assert retrieved.caption == "Test Caption"
        finally:
            os.unlink(path)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def test_summary(self):
        """summary() returns correct counts."""
        registry = AssetRegistry()
        registry.register(
            asset_type="table",
            condition_slug="test",
            section_target="s1",
            renderer_type="table_builder",
            source_data={},
        )
        registry.register(
            asset_type="figure",
            condition_slug="test",
            section_target="s2",
            renderer_type="figure_builder",
            source_data={},
        )
        summary = registry.summary()
        assert summary["total"] == 2
        assert "by_status" in summary
        assert "by_type" in summary
        assert summary["by_status"].get("pending") == 2
        assert summary["by_type"].get("table") == 1
        assert summary["by_type"].get("figure") == 1

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    def test_global_registry(self):
        """get_asset_registry() returns same instance."""
        reg1 = get_asset_registry()
        reg2 = get_asset_registry()
        assert reg1 is reg2

    def test_reset_condition(self):
        """reset_condition() removes assets for that condition only."""
        registry = AssetRegistry()
        r_pd = registry.register(
            asset_type="table",
            condition_slug="parkinsons",
            section_target="s1",
            renderer_type="table_builder",
            source_data={},
        )
        r_dep = registry.register(
            asset_type="table",
            condition_slug="depression",
            section_target="s2",
            renderer_type="table_builder",
            source_data={},
        )
        assert registry.get(r_pd.asset_id) is not None
        assert registry.get(r_dep.asset_id) is not None

        registry.reset_condition("parkinsons")

        assert registry.get(r_pd.asset_id) is None
        assert registry.get(r_dep.asset_id) is not None

    # ------------------------------------------------------------------
    # Checksum
    # ------------------------------------------------------------------

    def test_checksum_asset(self):
        """checksum_asset() computes SHA256 of file content."""
        registry = AssetRegistry()
        content = b"test file content for checksum"
        expected_sha = hashlib.sha256(content).hexdigest()

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(content)
            file_path = f.name

        try:
            record = registry.register(
                asset_type="figure",
                condition_slug="test",
                section_target="sec_001",
                renderer_type="figure_builder",
                source_data={},
            )
            registry.update_status(record.asset_id, "generated", output_path=file_path)

            digest = registry.checksum_asset(record.asset_id)
            assert digest == expected_sha

            # Check it was stored on the record
            retrieved = registry.get(record.asset_id)
            assert retrieved.checksum == expected_sha
        finally:
            os.unlink(file_path)
