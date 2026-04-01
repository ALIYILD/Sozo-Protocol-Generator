"""Revision agent — applies doctor comments as structured revisions."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)


@register_agent
class RevisionAgent(BaseAgent):
    """Apply doctor comments as structured revisions."""

    name = "revision_agent"
    role = "Apply doctor comments as structured revisions"
    requires_human_review = True

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting revision processing")
        result = AgentResult()
        ws = Path(workspace_path)

        job = kwargs.get("job")
        comments = input_data.get("comments", [])
        if not comments and job:
            comments = job.doctor_comments

        if not comments:
            self._log(workspace_path, "No comments to process — skipping revision")
            result.success = True
            result.output_data = {"revisions_applied": 0, "reason": "no_comments"}
            return result

        # Get conditions from input or job
        conditions = input_data.get("conditions", [])
        if not conditions and job:
            conditions = job.target_conditions

        from ..ai.comment_normalizer import CommentNormalizer
        from ..ai.revision_instruction_builder import RevisionInstructionBuilder
        from ..generation.revision_engine import RevisionEngine
        from ..conditions.registry import get_registry

        normalizer = CommentNormalizer()
        builder = RevisionInstructionBuilder()
        engine = RevisionEngine()
        registry = get_registry()

        # Get section IDs from upstream template if available
        upstream_template = input_data.get("upstream_template", {})
        section_ids = upstream_template.get("section_ids")

        # Normalize comments into instructions
        normalized = normalizer.normalize(comments, section_ids=section_ids)
        self._log(workspace_path, f"Normalized {len(comments)} comments into {len(normalized.instructions)} instructions")

        if normalized.unresolved:
            for unresolved in normalized.unresolved:
                result.warnings.append(f"Unresolved comment: {unresolved}")
            self._log(workspace_path, f"  {len(normalized.unresolved)} comments could not be parsed")

        revisions_dir = ws / "revisions"
        revisions_dir.mkdir(parents=True, exist_ok=True)

        # Write normalized instructions
        instructions_path = revisions_dir / "normalized_instructions.json"
        instructions_path.write_text(
            json.dumps({
                "total_instructions": len(normalized.instructions),
                "unresolved_count": len(normalized.unresolved),
                "summary": normalized.summary,
                "instructions": [
                    {
                        "instruction_id": inst.instruction_id,
                        "target": inst.target,
                        "action": inst.action,
                        "section_id": inst.section_id,
                        "detail": inst.detail,
                        "priority": inst.priority,
                        "source_comment": inst.source_comment,
                    }
                    for inst in normalized.instructions
                ],
                "unresolved": normalized.unresolved,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Apply revisions to draft documents if they exist
        drafts_dir = ws / "drafts"
        upstream_drafts = input_data.get("upstream_draft", {})
        draft_docs = upstream_drafts.get("documents", [])

        revisions_applied = 0
        revised_docs = []

        if draft_docs and normalized.instructions:
            for doc_info in draft_docs:
                slug = doc_info.get("condition", "")
                if slug and registry.exists(slug):
                    try:
                        condition = registry.get(slug)

                        # Build a revision plan from the instructions
                        # Get the spec by regenerating (we don't persist specs)
                        from ..generation.rich_generator import RichDocumentGenerator
                        from ..docx.renderer import DocumentRenderer

                        generator = RichDocumentGenerator()
                        spec = generator.generate(
                            condition=condition,
                            doc_type=doc_info.get("doc_type", "evidence_based_protocol"),
                            tier=doc_info.get("tier", "fellow"),
                        )

                        plan = builder.build_plan(normalized.instructions, spec)
                        revised_spec, summary = engine.apply_revision(spec, plan, condition)

                        # Render revised document
                        renderer = DocumentRenderer(output_dir=str(revisions_dir))
                        revised_filename = f"{slug}_{doc_info.get('doc_type', 'protocol')}_{doc_info.get('tier', 'fellow')}_revised.docx"
                        revised_path = revisions_dir / revised_filename
                        renderer.render(revised_spec, output_path=revised_path)

                        # Write diff
                        diff_path = revisions_dir / f"{slug}_revision_diff.txt"
                        diff_path.write_text(
                            "\n".join(summary.diff_lines) if summary.diff_lines else "No changes detected",
                            encoding="utf-8",
                        )

                        revised_docs.append({
                            "condition": slug,
                            "original_path": doc_info.get("path", ""),
                            "revised_path": str(revised_path),
                            "diff_path": str(diff_path),
                            "sections_modified": summary.sections_modified,
                            "sections_removed": summary.sections_removed,
                            "tone_changes": summary.tone_changes,
                        })

                        result.artifacts.append({
                            "type": "document",
                            "path": str(revised_path),
                            "description": f"Revised: {revised_spec.title}",
                        })
                        result.artifacts.append({
                            "type": "diff",
                            "path": str(diff_path),
                            "description": f"Revision diff for {slug}",
                        })

                        revisions_applied += 1
                        self._log(workspace_path, f"  Revised {slug}: {summary.sections_modified} sections modified")

                    except Exception as e:
                        error_msg = f"Revision failed for {slug}: {e}"
                        result.warnings.append(error_msg)
                        self._log(workspace_path, f"  ERROR: {error_msg}")

        self._log(workspace_path, f"Revisions complete: {revisions_applied} documents revised")

        result.success = True
        result.artifacts.append({
            "type": "revision_instructions",
            "path": str(instructions_path),
            "description": f"{len(normalized.instructions)} revision instructions",
        })
        result.output_data = {
            "revisions_applied": revisions_applied,
            "total_instructions": len(normalized.instructions),
            "unresolved_comments": len(normalized.unresolved),
            "revised_documents": revised_docs,
        }
        if normalized.unresolved:
            result.output_data["unresolved"] = normalized.unresolved
        return result
