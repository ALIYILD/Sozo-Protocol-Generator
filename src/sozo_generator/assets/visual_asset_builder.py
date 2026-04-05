"""
VisualAssetBuilder — orchestrates all asset generation for a document.

Coordinates FigureBuilder, ChartBuilder, and TableBuilder to produce
and register all assets for a DocumentBlueprint in one call.
"""
from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class VisualAssetBuilder:
    """
    Builds all visual assets for a condition/document and registers them
    in the AssetRegistry.
    """

    def __init__(self, output_dir: str = "outputs/assets"):
        self.output_dir = output_dir

    def _get_builders(self, output_dir: str):
        from sozo_generator.assets.figure_builder import FigureBuilder
        from sozo_generator.assets.chart_builder import ChartBuilder
        from sozo_generator.assets.table_builder import TableBuilder
        return (
            FigureBuilder(output_dir=output_dir),
            ChartBuilder(output_dir=output_dir),
            TableBuilder(),
        )

    def build_all_assets(
        self,
        condition,
        variant: str,
        asset_registry,
        section_map: Optional[dict] = None,
    ) -> dict:
        """
        Build all figures, charts, and tables for a condition.
        Registers each in asset_registry.
        Returns {"generated": N, "failed": N, "total": N, "paths": [...]}
        """
        out_dir = os.path.join(self.output_dir, getattr(condition, "slug", "unknown"), variant)
        os.makedirs(out_dir, exist_ok=True)

        figure_builder, chart_builder, table_builder = self._get_builders(out_dir)
        condition_slug = getattr(condition, "slug", "unknown")

        generated, failed, paths = 0, 0, []

        # --- Figures ---
        # Default section targets for each figure type
        _figure_section_defaults = {
            "qeeg_topomap": "neuromodulation_targets",
            "montage_diagram": "protocol_parameters",
            "network_diagram": "network_involvement",
            "patient_journey": "patient_pathway",
            "treatment_timeline": "treatment_protocol",
            "symptom_flow": "clinical_presentation",
            "connectivity_map": "network_involvement",
            "protocol_panel": "protocol_parameters",
            "brain_map": "neuromodulation_targets",
            "spectral_topomap": "neuromodulation_targets",
            "dose_response": "clinical_outcomes",
            "impedance_map": "protocol_parameters",
        }
        figure_types = list(_figure_section_defaults.keys())
        for ft in figure_types:
            section_target = (section_map or {}).get(
                ft, _figure_section_defaults.get(ft, "section_figures")
            )
            try:
                fig, asset_id = figure_builder.build_and_register(
                    figure_type=ft,
                    condition=condition,
                    asset_registry=asset_registry,
                    section_target=section_target,
                    variant=variant,
                )
                if fig.image_path:
                    generated += 1
                    paths.append(fig.image_path)
                else:
                    failed += 1
            except Exception as exc:
                logger.warning("VisualAssetBuilder: figure %s failed: %s", ft, exc)
                failed += 1

        # --- Charts ---
        chart_builders = [
            ("evidence_bar", chart_builder.build_evidence_bar_chart),
            ("session_timeline", chart_builder.build_session_timeline_chart),
            ("network_radar", chart_builder.build_network_dysfunction_radar),
        ]
        for chart_type, build_fn in chart_builders:
            section_target = (section_map or {}).get(chart_type, "section_charts")
            try:
                chart, chart_path = build_fn(condition)
                record = asset_registry.register(
                    asset_type="chart",
                    condition_slug=condition_slug,
                    section_target=section_target,
                    renderer_type=chart_type,
                    source_data={"chart_type": chart_type},
                    caption=chart.title,
                    variant_tags=[variant],
                )
                if chart_path and os.path.exists(chart_path):
                    asset_registry.update_status(record.asset_id, "generated", output_path=chart_path)
                    generated += 1
                    paths.append(chart_path)
                else:
                    asset_registry.update_status(record.asset_id, "failed")
                    failed += 1
            except Exception as exc:
                logger.warning("VisualAssetBuilder: chart %s failed: %s", chart_type, exc)
                failed += 1

        # --- Tables ---
        table_builders_map = [
            ("protocol_parameters", table_builder.build_protocol_parameters_table),
            ("assessment_tools", table_builder.build_assessment_tools_table),
            ("contraindications", table_builder.build_contraindications_table),
            ("stimulation_targets", table_builder.build_stimulation_targets_table),
            ("evidence_summary", table_builder.build_evidence_summary_table),
        ]
        for table_type, build_fn in table_builders_map:
            section_target = (section_map or {}).get(table_type, "section_tables")
            try:
                table = build_fn(condition)
                record = asset_registry.register(
                    asset_type="table",
                    condition_slug=condition_slug,
                    section_target=section_target,
                    renderer_type="table_builder",
                    source_data={
                        "headers": table.headers,
                        "rows": table.rows,
                        "title": table.title,
                        "landscape": table.landscape,
                        "footer": table.footer,
                    },
                    caption=table.title,
                    variant_tags=[variant],
                )
                asset_registry.update_status(record.asset_id, "generated")
                generated += 1
            except Exception as exc:
                logger.warning("VisualAssetBuilder: table %s failed: %s", table_type, exc)
                failed += 1

        total = generated + failed
        # Note: finalize_numbering() is called by the DocumentAssembler — do NOT call it here
        return {"generated": generated, "failed": failed, "total": total, "paths": paths}

    def build_figures_for_document(
        self,
        condition,
        variant: str,
        blueprint,
        asset_registry,
    ) -> list:
        """Walk blueprint, find all figure/chart blocks, build and register each."""
        out_dir = os.path.join(self.output_dir, getattr(condition, "slug", "unknown"), variant)
        os.makedirs(out_dir, exist_ok=True)
        figure_builder, _, _ = self._get_builders(out_dir)

        results = []
        for spec in (blueprint.sections or []):
            for block in (spec.blocks or []):
                if block.block_type in ("figure", "chart", "diagram", "topomap", "montage"):
                    asset_id = block.asset_id or ""
                    renderer = getattr(block, "metadata", {}).get("renderer_type", "qeeg_topomap")
                    try:
                        fig, reg_id = figure_builder.build_and_register(
                            figure_type=renderer,
                            condition=condition,
                            asset_registry=asset_registry,
                            section_target=spec.section_id,
                            variant=variant,
                        )
                        results.append(fig)
                    except Exception as exc:
                        logger.warning("build_figures_for_document: %s failed: %s", renderer, exc)
        return results
