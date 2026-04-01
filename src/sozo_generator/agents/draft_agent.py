"""Draft agent — assembles document drafts using content library + condition data."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)


@register_agent
class DraftAgent(BaseAgent):
    """Assemble document drafts using content library + condition data."""

    name = "draft_agent"
    role = "Assemble document drafts using content library + condition data"
    requires_human_review = True

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting document draft generation")
        result = AgentResult()
        ws = Path(workspace_path)

        job = kwargs.get("job")
        conditions = input_data.get("conditions", [])
        doc_types = input_data.get("doc_types", [])
        tiers = input_data.get("tiers", ["fellow"])

        if not conditions and job:
            conditions = job.target_conditions
        if not doc_types and job:
            doc_types = job.target_doc_types or ["evidence_based_protocol"]
        if not tiers and job:
            tiers = job.target_tiers or ["fellow"]
        if not conditions:
            result.error = "No conditions specified for draft generation"
            self._log(workspace_path, f"FAILED: {result.error}")
            return result

        use_ai = input_data.get("use_ai", False)
        library_path = input_data.get("library_path", "")

        from ..conditions.registry import get_registry
        from ..generation.rich_generator import RichDocumentGenerator
        from ..docx.renderer import DocumentRenderer

        registry = get_registry()

        # Set up generator
        gen_kwargs = {}
        if library_path:
            gen_kwargs["library_path"] = Path(library_path)
        generator = RichDocumentGenerator(**gen_kwargs)

        drafts_dir = ws / "drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)
        renderer = DocumentRenderer(output_dir=str(drafts_dir))

        documents_generated = []

        for slug in conditions:
            if not registry.exists(slug):
                result.warnings.append(f"Condition '{slug}' not found in registry")
                self._log(workspace_path, f"WARNING: Condition '{slug}' not found")
                continue

            try:
                condition = registry.get(slug)
            except Exception as e:
                result.warnings.append(f"Could not load condition '{slug}': {e}")
                self._log(workspace_path, f"WARNING: Could not load '{slug}': {e}")
                continue

            for doc_type in doc_types:
                for tier in tiers:
                    self._log(workspace_path, f"  Generating {slug}/{doc_type}/{tier}")
                    try:
                        spec = generator.generate(
                            condition=condition,
                            doc_type=doc_type,
                            tier=tier,
                            use_ai=use_ai,
                        )

                        # Render to DOCX
                        output_path = drafts_dir / f"{slug}_{doc_type}_{tier}.docx"
                        rendered_path = renderer.render(spec, output_path=output_path)

                        doc_entry = {
                            "condition": slug,
                            "doc_type": doc_type,
                            "tier": tier,
                            "path": str(rendered_path),
                            "title": spec.title,
                            "section_count": len(spec.sections),
                            "review_flags": spec.review_flags,
                        }
                        documents_generated.append(doc_entry)

                        result.artifacts.append({
                            "type": "document",
                            "path": str(rendered_path),
                            "description": f"{spec.title} ({tier})",
                        })

                        self._log(workspace_path, f"  Generated: {rendered_path.name}")

                    except Exception as e:
                        error_msg = f"Failed to generate {slug}/{doc_type}/{tier}: {e}"
                        result.warnings.append(error_msg)
                        self._log(workspace_path, f"  ERROR: {error_msg}")

        # Write draft manifest
        manifest_path = drafts_dir / "draft_manifest.json"
        manifest_path.write_text(
            json.dumps({
                "total_documents": len(documents_generated),
                "documents": documents_generated,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        if not documents_generated:
            result.error = "No documents were generated"
            self._log(workspace_path, "FAILED: No documents generated")
            return result

        self._log(workspace_path, f"Generated {len(documents_generated)} document drafts")

        result.success = True
        result.output_data = {
            "total_documents": len(documents_generated),
            "documents": documents_generated,
        }
        return result
