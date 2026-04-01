"""Run the clinical QA engine on conditions."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

try:
    from ..qa.engine import QAEngine
    from ..conditions.registry import get_registry
    from ..core.settings import SozoSettings
except ImportError as e:
    typer.echo(
        typer.style(
            f"Import error: {e}\n"
            "Ensure sozo_generator is installed and all dependencies are available.",
            fg=typer.colors.RED,
        )
    )
    raise SystemExit(1)

qa_engine_app = typer.Typer(
    name="qa2",
    help="Run the clinical QA engine on conditions.",
    add_completion=False,
)

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]


def _format_report(report, fmt: str) -> str:
    """Format a QAReport as JSON or markdown."""
    if fmt == "json":
        return json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False)

    # Markdown format
    status = "PASSED" if report.passed else "FAILED"
    lines = [
        f"# QA Engine Report: {report.condition_name} ({report.condition_slug})",
        "",
        f"- **Report ID:** {report.report_id}",
        f"- **Status:** {status}",
        f"- **Block:** {report.block_count}",
        f"- **Warning:** {report.warning_count}",
        f"- **Info:** {report.info_count}",
        "",
    ]
    if report.issues:
        lines.append("## Issues")
        lines.append("")
        for issue in report.issues:
            severity = issue.severity.value.upper()
            lines.append(f"- **[{severity}]** {issue.rule_id}: {issue.message}")
            if issue.location:
                lines.append(f"  - Location: {issue.location}")
        lines.append("")

    return "\n".join(lines)


def _print_summary(report) -> None:
    """Print a coloured summary line for a QA report."""
    status_color = typer.colors.GREEN if report.passed else typer.colors.RED
    status_label = "PASSED" if report.passed else "FAILED"
    typer.echo(
        typer.style(f"  [{status_label}] ", fg=status_color)
        + f"{report.condition_slug}: "
        + f"{report.block_count} block, {report.warning_count} warning, {report.info_count} info"
    )


@qa_engine_app.command("condition")
def qa_condition(
    condition: str = typer.Option(..., "--condition", help="Condition slug (e.g. parkinsons)"),
    format: str = typer.Option("json", "--format", help="Output format: 'json' or 'markdown'"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Write report to this directory"),
):
    """Run QA engine on a single condition."""
    if format not in ("json", "markdown"):
        typer.echo(typer.style(f"Invalid format '{format}'. Use 'json' or 'markdown'.", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Load condition from registry
    try:
        registry = get_registry()
        condition_obj = registry.get(condition)
    except Exception as e:
        typer.echo(typer.style(f"Condition '{condition}' not found: {e}", fg=typer.colors.RED))
        typer.echo(
            typer.style(f"Valid slugs: {', '.join(VALID_SLUGS)}", fg=typer.colors.YELLOW)
        )
        raise typer.Exit(code=1)

    typer.echo(
        typer.style(f"Running QA engine for: {condition}", fg=typer.colors.CYAN)
    )

    try:
        engine = QAEngine()
        report = engine.run_condition_qa(condition_obj)
    except Exception as e:
        typer.echo(typer.style(f"QA engine failed: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Print summary
    typer.echo("")
    _print_summary(report)

    # Format output
    output_str = _format_report(report, format)

    # Write to file or print
    if output_dir:
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            ext = "json" if format == "json" else "md"
            output_path = output_dir / f"qa-engine-{condition}.{ext}"
            output_path.write_text(output_str, encoding="utf-8")
            typer.echo("")
            typer.echo(typer.style(f"Report written to: {output_path}", fg=typer.colors.GREEN))
        except Exception as e:
            typer.echo(typer.style(f"Failed to write report: {e}", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    else:
        typer.echo("")
        typer.echo(output_str)


@qa_engine_app.command("all")
def qa_all(
    format: str = typer.Option("json", "--format", help="Output format: 'json' or 'markdown'"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Write reports to this directory"),
):
    """Run QA engine on all conditions."""
    if format not in ("json", "markdown"):
        typer.echo(typer.style(f"Invalid format '{format}'. Use 'json' or 'markdown'.", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Get all slugs from registry
    try:
        registry = get_registry()
        all_slugs = registry.list_slugs()
    except Exception:
        all_slugs = list(VALID_SLUGS)

    typer.echo(
        typer.style(
            f"Running QA engine for {len(all_slugs)} condition(s)...",
            fg=typer.colors.CYAN,
        )
    )

    engine = QAEngine()
    reports = []
    failed_slugs: list[str] = []

    for slug in all_slugs:
        try:
            condition_obj = registry.get(slug)
            report = engine.run_condition_qa(condition_obj)
            reports.append(report)
        except Exception as e:
            typer.echo(
                typer.style(f"  [FAIL] {slug}: {e}", fg=typer.colors.RED)
            )
            failed_slugs.append(slug)

    # Print summaries
    typer.echo("")
    for report in reports:
        _print_summary(report)

    if failed_slugs:
        typer.echo("")
        typer.echo(
            typer.style(
                f"Failed conditions: {', '.join(failed_slugs)}",
                fg=typer.colors.RED,
            )
        )

    # Write reports
    if output_dir:
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            for report in reports:
                output_str = _format_report(report, format)
                ext = "json" if format == "json" else "md"
                output_path = output_dir / f"qa-engine-{report.condition_slug}.{ext}"
                output_path.write_text(output_str, encoding="utf-8")
            typer.echo("")
            typer.echo(
                typer.style(
                    f"Reports written to: {output_dir}",
                    fg=typer.colors.GREEN,
                )
            )
        except Exception as e:
            typer.echo(typer.style(f"Failed to write reports: {e}", fg=typer.colors.RED))
            raise typer.Exit(code=1)

    # Overall summary
    passed_count = sum(1 for r in reports if r.passed)
    total = len(reports)
    typer.echo("")
    typer.echo(
        typer.style(
            f"QA engine complete: {passed_count}/{total} conditions passed.",
            fg=typer.colors.GREEN if passed_count == total else typer.colors.YELLOW,
        )
    )
