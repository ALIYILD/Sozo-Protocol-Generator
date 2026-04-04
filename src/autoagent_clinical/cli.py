"""CLI for AutoAgent-Clinical benchmark runs."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from .registry import list_harnesses
from .report_writer import (
    append_github_step_summary,
    dump_comparison_json,
    format_compare_step_summary,
    format_run_step_summary,
    write_comparison_markdown,
    write_json_report,
    write_junit_compare_report,
    write_junit_run_report,
    write_markdown_summary,
)
from .runner import (
    compare_harnesses,
    load_all_benchmark_files,
    load_suite_from_path,
    run_suite,
)

app = typer.Typer(
    name="autoagent-clinical",
    help="Internal benchmark lab for SOZO agents (not a clinical runtime).",
    add_completion=False,
)


@app.command("list-harnesses")
def cmd_list_harnesses() -> None:
    """Print registered harness ids."""
    for h in list_harnesses():
        typer.echo(h)


@app.command("run")
def cmd_run(
    harness: str = typer.Option(
        "baseline_fixture",
        "--harness",
        "-h",
        help="Harness id (see list-harnesses).",
    ),
    suite_path: Optional[Path] = typer.Option(
        None,
        "--suite",
        "-s",
        help="Path to a single YAML suite file (default: bundled benchmarks/).",
    ),
    category: Optional[str] = typer.Option(
        None,
        "--category",
        "-c",
        help="Filter by benchmark category slug.",
    ),
    out_json: Optional[Path] = typer.Option(
        None,
        "--out-json",
        help="Write full JSON report to this path.",
    ),
    out_md: Optional[Path] = typer.Option(
        None,
        "--out-md",
        help="Write Markdown summary to this path.",
    ),
    out_junit: Optional[Path] = typer.Option(
        None,
        "--out-junit",
        help="Write JUnit XML to this path (for CI test result tabs).",
    ),
    include_adapter_benchmarks: bool = typer.Option(
        False,
        "--include-adapter-benchmarks",
        help="Include generation_adapter_cases.yaml (GenerationService-focused cases).",
    ),
    include_regression_gates: bool = typer.Option(
        False,
        "--include-regression-gates",
        help="Include regression_gate_cases.yaml (structure-native gate cases).",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Do not print the JSON report to stdout.",
    ),
    strict_exit_code: bool = typer.Option(
        False,
        "--strict-exit-code",
        help="Exit with code 1 if no cases ran, or if any case has benchmark expectation "
        "violations (YAML expectations not satisfied).",
    ),
    strict_full_pass: bool = typer.Option(
        False,
        "--strict-full-pass",
        help="Exit with code 1 if no cases ran, or if any case is not a full pass "
        "(evaluator pass and zero expectation violations). Stricter than --strict-exit-code.",
    ),
    min_mean_overall: Optional[float] = typer.Option(
        None,
        "--min-mean-overall",
        help="Exit with code 1 if mean overall score across cases is below this "
        "(0–1). Ignored when unset.",
    ),
    emit_github_step_summary: bool = typer.Option(
        False,
        "--emit-github-step-summary",
        help="Append a short Markdown summary to GITHUB_STEP_SUMMARY when that env "
        "var is set (GitHub Actions job summaries).",
    ),
) -> None:
    """Run benchmarks with the selected harness."""
    if suite_path:
        suite = load_suite_from_path(suite_path)
    else:
        suite = load_all_benchmark_files(
            include_adapter_benchmarks=include_adapter_benchmarks,
            include_regression_gates=include_regression_gates,
        )
    report = run_suite(suite, harness, category_filter=category)
    if not quiet:
        typer.echo(report.model_dump_json(indent=2))
    if out_json:
        write_json_report(report, out_json)
        typer.echo(typer.style(f"Wrote JSON: {out_json}", fg=typer.colors.GREEN))
    if out_md:
        write_markdown_summary(report, out_md)
        typer.echo(typer.style(f"Wrote Markdown: {out_md}", fg=typer.colors.GREEN))
    if out_junit:
        write_junit_run_report(report, out_junit)
        typer.echo(typer.style(f"Wrote JUnit: {out_junit}", fg=typer.colors.GREEN))
    if emit_github_step_summary:
        append_github_step_summary(format_run_step_summary(report))
    if strict_exit_code:
        s = report.summary
        total = int(s.get("total_cases", 0))
        sat = int(s.get("benchmark_expectation_sat_count", 0))
        if total == 0 or sat != total:
            raise typer.Exit(code=1)
    if strict_full_pass:
        s = report.summary
        total = int(s.get("total_cases", 0))
        full = int(s.get("full_pass_count", 0))
        if total == 0 or full != total:
            raise typer.Exit(code=1)
    if min_mean_overall is not None and report.case_results:
        mean = sum(c.overall_score for c in report.case_results) / len(
            report.case_results
        )
        if mean + 1e-9 < float(min_mean_overall):
            raise typer.Exit(code=1)


@app.command("compare")
def cmd_compare(
    baseline: str = typer.Option(
        "baseline_fixture",
        "--baseline",
        "-b",
        help="Baseline harness id.",
    ),
    compare: str = typer.Option(
        "generator_with_qa_stub",
        "--compare",
        "-p",
        help="Challenger harness id.",
    ),
    suite_path: Optional[Path] = typer.Option(None, "--suite", "-s"),
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    out_json: Optional[Path] = typer.Option(None, "--out-json"),
    out_md: Optional[Path] = typer.Option(None, "--out-md"),
    out_junit: Optional[Path] = typer.Option(
        None,
        "--out-junit",
        help="JUnit XML for the challenger harness (full-pass per case).",
    ),
    include_adapter_benchmarks: bool = typer.Option(
        False,
        "--include-adapter-benchmarks",
        help="Include generation_adapter_cases.yaml when loading the default suite.",
    ),
    include_regression_gates: bool = typer.Option(
        False,
        "--include-regression-gates",
        help="Include regression_gate_cases.yaml when loading the default suite.",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Do not print the JSON report to stdout.",
    ),
    strict_exit_code: bool = typer.Option(
        False,
        "--strict-exit-code",
        help="Exit with code 1 if no cases were compared, or if the challenger loses "
        "eval passes or benchmark expectation satisfaction vs baseline on any case.",
    ),
    strict_full_pass: bool = typer.Option(
        False,
        "--strict-full-pass",
        help="Exit with code 1 if the challenger is not a full pass on every compared "
        "case (evaluator pass and zero expectation violations).",
    ),
    min_mean_delta: Optional[float] = typer.Option(
        None,
        "--min-mean-delta",
        help="Exit with code 1 if mean score delta (compare − baseline) is strictly "
        "below this threshold. Example: -0.02 fails when average regression exceeds 0.02.",
    ),
    max_mean_expectation_issues_delta: Optional[float] = typer.Option(
        None,
        "--max-mean-expectation-issues-delta",
        help="Exit with code 1 if mean expectation-issues delta (compare − baseline) "
        "is above this (more net issues on challenger than baseline).",
    ),
    emit_github_step_summary: bool = typer.Option(
        False,
        "--emit-github-step-summary",
        help="Append Markdown to GITHUB_STEP_SUMMARY when set (GitHub Actions).",
    ),
) -> None:
    """Compare two harness variants on the same benchmark cases."""
    if suite_path:
        suite = load_suite_from_path(suite_path)
    else:
        suite = load_all_benchmark_files(
            include_adapter_benchmarks=include_adapter_benchmarks,
            include_regression_gates=include_regression_gates,
        )
    cmp = compare_harnesses(suite, baseline, compare, category_filter=category)
    if not quiet:
        typer.echo(cmp.model_dump_json(indent=2))
    if out_json:
        dump_comparison_json(cmp, out_json)
        typer.echo(typer.style(f"Wrote JSON: {out_json}", fg=typer.colors.GREEN))
    if out_md:
        write_comparison_markdown(cmp, out_md)
        typer.echo(typer.style(f"Wrote Markdown: {out_md}", fg=typer.colors.GREEN))
    if out_junit:
        write_junit_compare_report(cmp, out_junit)
        typer.echo(typer.style(f"Wrote JUnit: {out_junit}", fg=typer.colors.GREEN))
    if emit_github_step_summary:
        append_github_step_summary(format_compare_step_summary(cmp))
    if strict_exit_code:
        agg = cmp.aggregate
        n = int(agg.get("cases_compared", 0))
        lost_eval = int(agg.get("eval_pass_lost_count", 0))
        lost_sat = int(agg.get("benchmark_expectation_sat_lost_count", 0))
        if n == 0 or lost_eval > 0 or lost_sat > 0:
            raise typer.Exit(code=1)
    if strict_full_pass:
        agg = cmp.aggregate
        n = int(agg.get("cases_compared", 0))
        cfull = int(agg.get("compare_full_pass_count", 0))
        if n == 0 or cfull != n:
            raise typer.Exit(code=1)
    if min_mean_delta is not None:
        md = float(cmp.aggregate.get("mean_delta", 0.0))
        if md + 1e-9 < float(min_mean_delta):
            raise typer.Exit(code=1)
    if max_mean_expectation_issues_delta is not None:
        mid = float(cmp.aggregate.get("mean_expectation_issues_delta", 0.0))
        if mid - 1e-9 > float(max_mean_expectation_issues_delta):
            raise typer.Exit(code=1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
