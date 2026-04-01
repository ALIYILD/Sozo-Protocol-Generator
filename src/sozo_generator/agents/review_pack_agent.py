"""Review pack agent — prepares review artifacts for operator approval."""
from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)


@register_agent
class ReviewPackAgent(BaseAgent):
    """Prepare review artifacts for operator approval."""

    name = "review_pack_agent"
    role = "Prepare review artifacts for operator approval"

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting review pack assembly")
        result = AgentResult()
        ws = Path(workspace_path)

        job = kwargs.get("job")
        conditions = input_data.get("conditions", [])
        if not conditions and job:
            conditions = job.target_conditions

        # Collect all artifacts from workspace
        reports_dir = ws / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        exports_dir = ws / "exports"
        exports_dir.mkdir(parents=True, exist_ok=True)

        # Gather artifacts from all workspace folders
        artifact_inventory = {}
        scan_folders = ["drafts", "revisions", "qa", "evidence", "parsed_template", "content_matches"]

        for folder_name in scan_folders:
            folder = ws / folder_name
            if folder.exists():
                files = sorted(folder.rglob("*"))
                artifact_inventory[folder_name] = [
                    {
                        "path": str(f),
                        "name": f.name,
                        "size_bytes": f.stat().st_size if f.is_file() else 0,
                        "is_dir": f.is_dir(),
                    }
                    for f in files
                    if f.is_file()
                ]

        # Get upstream data for the review summary
        upstream_qa = input_data.get("upstream_qa", {})
        upstream_draft = input_data.get("upstream_draft", {})
        upstream_evidence = input_data.get("upstream_evidence", {})
        upstream_revision = input_data.get("upstream_revision", {})

        # Build review summary
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        review_summary = {
            "generated_at": now_iso,
            "job_id": job.job_id if job else "standalone",
            "conditions": conditions,
            "document_generation": {
                "total_documents": upstream_draft.get("total_documents", 0),
                "documents": upstream_draft.get("documents", []),
            },
            "evidence": {
                "total_items": upstream_evidence.get("total_items", 0),
                "total_stale": upstream_evidence.get("total_stale", 0),
                "conditions_processed": upstream_evidence.get("conditions_processed", []),
            },
            "qa": {
                "total_passed": upstream_qa.get("total_passed", 0),
                "total_blocks": upstream_qa.get("total_blocks", 0),
                "has_blocking_issues": upstream_qa.get("has_blocking_issues", False),
                "conditions_passed": upstream_qa.get("conditions_passed", []),
                "conditions_failed": upstream_qa.get("conditions_failed", []),
            },
            "revisions": {
                "revisions_applied": upstream_revision.get("revisions_applied", 0),
                "total_instructions": upstream_revision.get("total_instructions", 0),
                "unresolved_comments": upstream_revision.get("unresolved_comments", 0),
            },
            "artifact_inventory": artifact_inventory,
        }

        # Generate review report
        try:
            review_report = self._generate_review_report(review_summary, conditions)
        except Exception as e:
            review_report = f"Error generating review report: {e}"
            result.warnings.append(f"Review report generation error: {e}")

        # Write review summary JSON
        summary_path = reports_dir / "review_summary.json"
        summary_path.write_text(
            json.dumps(review_summary, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )

        # Write human-readable review report
        report_path = reports_dir / "review_report.md"
        report_path.write_text(review_report, encoding="utf-8")

        # Copy final documents to exports
        exported_files = []

        # Copy drafts
        drafts_dir = ws / "drafts"
        if drafts_dir.exists():
            for docx_file in drafts_dir.glob("*.docx"):
                dest = exports_dir / docx_file.name
                shutil.copy2(docx_file, dest)
                exported_files.append(str(dest))

        # Copy revised documents (prefer revised over original)
        revisions_dir = ws / "revisions"
        if revisions_dir.exists():
            for docx_file in revisions_dir.glob("*.docx"):
                dest = exports_dir / docx_file.name
                shutil.copy2(docx_file, dest)
                exported_files.append(str(dest))

        # Copy QA reports
        qa_dir = ws / "qa"
        if qa_dir.exists():
            for qa_file in qa_dir.iterdir():
                if qa_file.is_file():
                    dest = exports_dir / f"qa_{qa_file.name}"
                    shutil.copy2(qa_file, dest)

        self._log(workspace_path, f"Exported {len(exported_files)} documents to exports/")

        result.success = True
        result.artifacts.append({
            "type": "review_summary",
            "path": str(summary_path),
            "description": "Review pack summary (JSON)",
        })
        result.artifacts.append({
            "type": "review_report",
            "path": str(report_path),
            "description": "Review report (Markdown)",
        })
        for exp_path in exported_files:
            result.artifacts.append({
                "type": "export",
                "path": exp_path,
                "description": f"Exported document: {Path(exp_path).name}",
            })

        result.output_data = {
            "review_summary_path": str(summary_path),
            "review_report_path": str(report_path),
            "exported_files": exported_files,
            "total_exported": len(exported_files),
            "has_blocking_issues": upstream_qa.get("has_blocking_issues", False),
        }
        return result

    def _generate_review_report(self, summary: dict, conditions: list[str]) -> str:
        """Generate a human-readable Markdown review report."""
        lines = [
            "# Document Review Pack",
            "",
            f"**Generated:** {summary['generated_at']}",
            f"**Job ID:** {summary['job_id']}",
            f"**Conditions:** {', '.join(conditions) if conditions else 'None specified'}",
            "",
        ]

        # Document generation summary
        gen = summary.get("document_generation", {})
        lines.append("## Documents Generated")
        lines.append("")
        lines.append(f"Total documents: **{gen.get('total_documents', 0)}**")
        lines.append("")
        for doc in gen.get("documents", []):
            flags = doc.get("review_flags", [])
            flag_str = f" [{len(flags)} flags]" if flags else ""
            lines.append(f"- {doc.get('title', doc.get('condition', 'Unknown'))}{flag_str}")
        lines.append("")

        # Evidence summary
        ev = summary.get("evidence", {})
        lines.append("## Evidence Summary")
        lines.append("")
        lines.append(f"- Total evidence items: {ev.get('total_items', 0)}")
        lines.append(f"- Stale items: {ev.get('total_stale', 0)}")
        lines.append("")

        # QA results
        qa = summary.get("qa", {})
        lines.append("## QA Results")
        lines.append("")
        blocking = qa.get("has_blocking_issues", False)
        if blocking:
            lines.append("**STATUS: BLOCKING ISSUES FOUND**")
        else:
            lines.append("**STATUS: No blocking issues**")
        lines.append("")
        lines.append(f"- Passed: {qa.get('total_passed', 0)}")
        lines.append(f"- Blocking issues: {qa.get('total_blocks', 0)}")
        if qa.get("conditions_failed"):
            lines.append(f"- Failed conditions: {', '.join(qa['conditions_failed'])}")
        lines.append("")

        # Revision summary
        rev = summary.get("revisions", {})
        if rev.get("total_instructions", 0) > 0:
            lines.append("## Revisions Applied")
            lines.append("")
            lines.append(f"- Total instructions: {rev.get('total_instructions', 0)}")
            lines.append(f"- Documents revised: {rev.get('revisions_applied', 0)}")
            lines.append(f"- Unresolved comments: {rev.get('unresolved_comments', 0)}")
            lines.append("")

        # Artifacts
        inv = summary.get("artifact_inventory", {})
        lines.append("## Artifact Inventory")
        lines.append("")
        for folder, files in inv.items():
            if files:
                lines.append(f"### {folder}/")
                for f in files:
                    size_kb = f.get("size_bytes", 0) / 1024
                    lines.append(f"- {f['name']} ({size_kb:.1f} KB)")
                lines.append("")

        return "\n".join(lines)
