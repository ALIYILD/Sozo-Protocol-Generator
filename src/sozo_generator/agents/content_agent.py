"""Content agent — retrieves matching content from the content library."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)

_DEFAULT_LIBRARY_PATH = Path("data/learned/content_library.json")


@register_agent
class ContentAgent(BaseAgent):
    """Retrieve matching content from the content library."""

    name = "content_agent"
    role = "Retrieve matching content from the content library"

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting content matching")
        result = AgentResult()
        ws = Path(workspace_path)

        # Resolve conditions and doc types from input or job
        job = kwargs.get("job")
        conditions = input_data.get("conditions", [])
        doc_types = input_data.get("doc_types", [])
        section_ids = input_data.get("section_ids", [])

        if not conditions and job:
            conditions = job.target_conditions
        if not doc_types and job:
            doc_types = job.target_doc_types

        if not conditions:
            result.error = "No conditions specified"
            self._log(workspace_path, f"FAILED: {result.error}")
            return result

        # Load content library
        from ..template.learning.content_harvester import ContentHarvester

        harvester = ContentHarvester()
        library_path = Path(input_data.get("library_path", str(_DEFAULT_LIBRARY_PATH)))

        if not library_path.exists():
            result.warnings.append(f"Content library not found at {library_path}")
            self._log(workspace_path, f"WARNING: Content library not found at {library_path}")
            # Return success with empty matches — downstream agents can still work
            result.success = True
            result.output_data = {"matches": {}, "total_matches": 0}
            return result

        library = harvester.load_library(library_path)
        self._log(workspace_path, f"Loaded library: {library.total_sections} sections from {library.total_documents} docs")

        # If no doc types specified, use all from library
        if not doc_types:
            doc_types = library.doc_types

        # If no section_ids, try to get from upstream template agent
        upstream = input_data.get("upstream_template", {})
        if not section_ids and upstream:
            section_ids = upstream.get("section_ids", [])

        # Find best matching sections
        matches_dir = ws / "content_matches"
        matches_dir.mkdir(parents=True, exist_ok=True)

        all_matches = {}
        total_matches = 0

        for condition_slug in conditions:
            condition_matches = {}
            for doc_type in doc_types:
                dt_matches = []
                # Get all section keys for this doc type from library
                dt_keys = sorted(
                    k for k in library.sections.keys()
                    if k.startswith(f"{doc_type}::")
                )

                target_sections = section_ids if section_ids else [
                    k.split("::", 1)[1] for k in dt_keys
                ]

                for sid in target_sections:
                    best = harvester.get_best_section(
                        library, doc_type, sid, prefer_condition=condition_slug
                    )
                    if best:
                        match_entry = {
                            "section_id": best.section_id,
                            "title": best.title,
                            "source_condition": best.source_condition,
                            "source_doc_type": best.source_doc_type,
                            "word_count": best.word_count,
                            "has_table": best.has_table,
                            "exact_match": best.source_condition == condition_slug,
                        }
                        dt_matches.append(match_entry)
                        total_matches += 1

                if dt_matches:
                    condition_matches[doc_type] = dt_matches

            all_matches[condition_slug] = condition_matches

        # Write matches to workspace
        matches_path = matches_dir / "content_matches.json"
        matches_path.write_text(
            json.dumps({
                "total_matches": total_matches,
                "conditions": list(all_matches.keys()),
                "doc_types": doc_types,
                "matches": all_matches,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        self._log(workspace_path, f"Found {total_matches} content matches across {len(conditions)} conditions")

        result.success = True
        result.artifacts.append({
            "type": "content_matches",
            "path": str(matches_path),
            "description": f"{total_matches} content matches for {len(conditions)} conditions",
        })
        result.output_data = {
            "matches": all_matches,
            "total_matches": total_matches,
            "doc_types": doc_types,
        }
        return result
