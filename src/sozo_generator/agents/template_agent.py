"""Template agent — parses uploaded templates and detects document structure."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)


@register_agent
class TemplateAgent(BaseAgent):
    """Parse uploaded template and detect structure."""

    name = "template_agent"
    role = "Parse uploaded template and detect structure"

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting template parsing")
        result = AgentResult()
        ws = Path(workspace_path)

        template_path = input_data.get("template_path", "")
        if not template_path:
            # Look for templates in the input folder
            input_dir = ws / "input"
            candidates = list(input_dir.glob("*.docx")) + list(input_dir.glob("*.txt"))
            if not candidates:
                result.error = "No template file provided or found in workspace/input/"
                self._log(workspace_path, f"FAILED: {result.error}")
                return result
            template_path = str(candidates[0])

        template_file = Path(template_path)
        if not template_file.exists():
            result.error = f"Template file not found: {template_path}"
            self._log(workspace_path, f"FAILED: {result.error}")
            return result

        # Parse using TemplateParser
        from ..template.parser import TemplateParser

        parser = TemplateParser(template_file)
        sections = parser.parse()

        if not sections:
            result.error = f"No sections detected in template: {template_file.name}"
            self._log(workspace_path, f"FAILED: {result.error}")
            return result

        self._log(workspace_path, f"Parsed {len(sections)} sections from {template_file.name}")

        # Write parsed structure to workspace
        parsed_dir = ws / "parsed_template"
        parsed_dir.mkdir(parents=True, exist_ok=True)

        section_data = []
        for s in sections:
            entry = {
                "section_id": s.section_id,
                "title": s.title,
                "heading_level": s.heading_level,
                "placeholder_count": s.placeholder_count,
                "placeholders": s.placeholders,
                "has_table": s.has_table,
                "content_preview": s.raw_content[:200] if s.raw_content else "",
            }
            section_data.append(entry)

        structure_path = parsed_dir / "template_structure.json"
        structure_path.write_text(
            json.dumps({
                "source_file": template_file.name,
                "total_sections": len(sections),
                "total_placeholders": parser.total_placeholders,
                "section_ids": parser.get_section_ids(),
                "sections": section_data,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Write all placeholders summary
        placeholders = parser.get_all_placeholders()
        if placeholders:
            placeholders_path = parsed_dir / "placeholders.json"
            placeholders_path.write_text(
                json.dumps(placeholders, indent=2), encoding="utf-8"
            )

        self._log(workspace_path, f"Wrote structure to {structure_path}")

        result.success = True
        result.artifacts.append({
            "type": "template_structure",
            "path": str(structure_path),
            "description": f"Parsed template: {len(sections)} sections, {parser.total_placeholders} placeholders",
        })
        result.output_data = {
            "section_ids": parser.get_section_ids(),
            "total_sections": len(sections),
            "total_placeholders": parser.total_placeholders,
            "source_file": template_file.name,
        }
        return result
