"""Visual Protocol Agent — generates brain/protocol/montage diagrams."""
from __future__ import annotations
import logging
from pathlib import Path
from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)

@register_agent
class VisualProtocolAgent(BaseAgent):
    name = "visual_agent"
    role = "Generate protocol visuals: montage diagrams, target maps, protocol cards"
    requires_human_review = False

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        from ..conditions.registry import get_registry
        from ..visuals.montage_diagrams import MontageDiagramGenerator
        from ..visuals.exporters import VisualsExporter

        conditions = input_data.get("conditions", [])
        job = kwargs.get("job")
        if not conditions and job:
            conditions = job.target_conditions

        registry = get_registry()
        montage_gen = MontageDiagramGenerator()
        visuals_dir = Path(workspace_path) / "visuals"
        visuals_dir.mkdir(parents=True, exist_ok=True)

        all_paths = []
        visual_summary = []

        for slug in conditions:
            try:
                condition = registry.get(slug)
                self._log(workspace_path, f"Generating visuals for {condition.display_name}")

                # Montage/target/protocol card diagrams
                cond_dir = visuals_dir / slug
                cond_dir.mkdir(exist_ok=True)
                paths = montage_gen.generate_all_for_condition(condition, cond_dir)

                # Also generate standard visuals (brain map, network diagram)
                try:
                    vis_exporter = VisualsExporter(visuals_dir)
                    std_results = vis_exporter.generate_all(condition, force=True)
                    for vtype, vpath in std_results.items():
                        if vpath and vpath.exists():
                            paths.append(vpath)
                except Exception as e:
                    self._log(workspace_path, f"Standard visuals warning: {e}")

                all_paths.extend(paths)
                visual_summary.append({
                    "condition": slug,
                    "visuals_generated": len(paths),
                    "paths": [str(p) for p in paths],
                })

            except Exception as e:
                self._log(workspace_path, f"Error generating visuals for {slug}: {e}")
                visual_summary.append({"condition": slug, "error": str(e)})

        artifacts = [
            {"type": "visual", "path": str(p), "description": p.stem}
            for p in all_paths
        ]

        return AgentResult(
            success=True,
            artifacts=artifacts,
            output_data={
                "total_visuals": len(all_paths),
                "conditions": visual_summary,
            },
        )
