"""QA agent — runs QA checks on generated documents."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)


@register_agent
class QAAgent(BaseAgent):
    """Run QA checks on generated documents."""

    name = "qa_agent"
    role = "Run QA checks on generated documents"

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        self._log(workspace_path, "Starting QA checks")
        result = AgentResult()
        ws = Path(workspace_path)

        job = kwargs.get("job")
        conditions = input_data.get("conditions", [])
        if not conditions and job:
            conditions = job.target_conditions
        if not conditions:
            result.error = "No conditions specified for QA"
            self._log(workspace_path, f"FAILED: {result.error}")
            return result

        from ..conditions.registry import get_registry
        from ..qa.engine import QAEngine

        registry = get_registry()
        engine = QAEngine()

        qa_dir = ws / "qa"
        qa_dir.mkdir(parents=True, exist_ok=True)

        all_qa_results = {}
        total_blocks = 0
        total_warnings = 0
        total_passed = 0

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

            # Run condition-level QA
            try:
                report = engine.run_condition_qa(condition)
                report.compute_counts()

                qa_result = {
                    "condition_slug": slug,
                    "condition_name": condition.display_name,
                    "report_id": report.report_id,
                    "passed": report.passed,
                    "block_count": report.block_count,
                    "warning_count": report.warning_count,
                    "info_count": report.info_count,
                    "issues": [
                        {
                            "issue_id": issue.issue_id,
                            "severity": issue.severity.value,
                            "rule_id": issue.rule_id,
                            "message": issue.message,
                            "section_id": issue.section_id or "",
                            "suggestion": issue.suggestion or "",
                        }
                        for issue in report.issues
                    ],
                }

                all_qa_results[slug] = qa_result
                total_blocks += report.block_count
                total_warnings += report.warning_count
                if report.passed:
                    total_passed += 1

                self._log(
                    workspace_path,
                    f"  {slug}: {'PASSED' if report.passed else 'FAILED'} "
                    f"(blocks={report.block_count}, warnings={report.warning_count})",
                )

                # Check for blocking issues
                if engine.check_blocking(report):
                    result.warnings.append(
                        f"BLOCKING: {slug} has {report.block_count} blocking QA issue(s)"
                    )

            except Exception as e:
                error_msg = f"QA failed for {slug}: {e}"
                result.warnings.append(error_msg)
                self._log(workspace_path, f"  ERROR: {error_msg}")

        # Write QA report
        qa_report_path = qa_dir / "qa_report.json"
        qa_report_path.write_text(
            json.dumps({
                "total_conditions": len(all_qa_results),
                "total_passed": total_passed,
                "total_blocks": total_blocks,
                "total_warnings": total_warnings,
                "has_blocking_issues": total_blocks > 0,
                "results": all_qa_results,
            }, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Write a human-readable summary
        summary_lines = [
            "QA Summary",
            "=" * 40,
            f"Conditions checked: {len(all_qa_results)}",
            f"Passed: {total_passed}",
            f"Blocking issues: {total_blocks}",
            f"Warnings: {total_warnings}",
            "",
        ]
        for slug, qa in all_qa_results.items():
            status = "PASS" if qa["passed"] else "FAIL"
            summary_lines.append(
                f"  [{status}] {qa['condition_name']}: "
                f"{qa['block_count']} blocks, {qa['warning_count']} warnings"
            )
            # List blocking issues
            for issue in qa["issues"]:
                if issue["severity"] == "block":
                    summary_lines.append(f"    BLOCK: {issue['message']}")

        summary_path = qa_dir / "qa_summary.txt"
        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

        self._log(workspace_path, f"QA complete: {total_passed}/{len(all_qa_results)} passed, {total_blocks} blocking issues")

        result.success = True
        result.artifacts.append({
            "type": "qa_report",
            "path": str(qa_report_path),
            "description": f"QA report: {total_passed}/{len(all_qa_results)} passed",
        })
        result.artifacts.append({
            "type": "qa_summary",
            "path": str(summary_path),
            "description": "QA summary (human-readable)",
        })
        result.output_data = {
            "total_conditions": len(all_qa_results),
            "total_passed": total_passed,
            "total_blocks": total_blocks,
            "total_warnings": total_warnings,
            "has_blocking_issues": total_blocks > 0,
            "conditions_passed": [s for s, r in all_qa_results.items() if r["passed"]],
            "conditions_failed": [s for s, r in all_qa_results.items() if not r["passed"]],
        }
        return result
