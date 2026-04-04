"""Write JSON and Markdown reports for internal QA."""
from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .schemas import BenchmarkRunReport, HarnessComparisonReport


def write_json_report(
    report: BaseModel,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def write_markdown_summary(run: BenchmarkRunReport, path: Path) -> None:
    lines = [
        "# AutoAgent-Clinical benchmark summary",
        "",
        "_Internal engineering lab output — not for clinical decision-making._",
        "",
        f"- **Run ID:** `{run.run_id}`",
        f"- **Suite:** {run.suite}",
        f"- **Harness:** `{run.harness_id}`",
        f"- **Started:** {run.started_at}",
        f"- **Finished:** {run.finished_at}",
        "",
        "## Summary",
        "",
    ]
    s = run.summary
    lines.extend(
        [
            f"- Total cases: **{s.get('total_cases', 0)}**",
            f"- Evaluator pass: **{s.get('evaluator_pass_count', 0)}**",
            f"- Expectation satisfied: **{s.get('benchmark_expectation_sat_count', 0)}**",
            f"- Full pass (eval + expectations): **{s.get('full_pass_count', 0)}**",
            "",
        ]
    )
    tax = s.get("failure_taxonomy_counts") or {}
    if tax:
        lines.append("### Failure taxonomy (counts across cases)")
        lines.append("")
        lines.append("| Code | Count |")
        lines.append("|---|---:|")
        for k in sorted(tax.keys()):
            lines.append(f"| `{k}` | {tax[k]} |")
        lines.append("")

    # Finding counts by validator (structure-native vs markdown-oriented)
    v_counts: dict[str, int] = {}
    for c in run.case_results:
        for rep in c.validator_reports:
            n = len(rep.findings)
            if n:
                v_counts[rep.validator_id] = v_counts.get(rep.validator_id, 0) + n
    if v_counts:
        lines.append("### Findings by validator")
        lines.append("")
        lines.append("| Validator | Total findings |")
        lines.append("|---|---:|")
        for vid in sorted(v_counts.keys()):
            lines.append(f"| `{vid}` | {v_counts[vid]} |")
        lines.append(
            "_Structure-native:_ `structured_spec_validator`, `document_spec_invariants`. "
            "_Markdown / mixed:_ other rows."
        )
        lines.append("")

    lines.append("## Per-case results")
    lines.append("")
    lines.append(
        "| Case | Category | Overall | Eval pass | Expect OK | Issues |",
    )
    lines.append("|---|---|---:|---|---|---|")
    for c in run.case_results:
        viol = len(c.expectation_violations)
        lines.append(
            f"| {c.case_id} | {c.category} | {c.overall_score} | "
            f"{'yes' if c.passed else 'no'} | "
            f"{'yes' if viol == 0 else 'no'} | "
            f"{viol} |",
        )
    lines.append("")

    detail_blocks: list[str] = []
    for c in run.case_results:
        sub: list[str] = []
        for rep in c.validator_reports:
            if not rep.findings:
                continue
            codes = sorted({f.code for f in rep.findings})
            codes_cell = ", ".join(f"`{x}`" for x in codes)
            sub.append(
                f"| `{rep.validator_id}` | {len(rep.findings)} | {codes_cell} |",
            )
        if sub:
            detail_blocks.append(f"### `{c.case_id}`")
            detail_blocks.append("")
            detail_blocks.append("| Validator | Findings | Codes |")
            detail_blocks.append("|---|---:|---|")
            detail_blocks.extend(sub)
            detail_blocks.append("")
    if detail_blocks:
        lines.append("## Per-case validator findings")
        lines.append("")
        lines.extend(detail_blocks)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _yes_no_pass(value: object | None) -> str:
    if value is None:
        return "—"
    return "yes" if value else "no"


def _md_category(value: object | None) -> str:
    if value is None or value == "":
        return "—"
    return str(value)


def _md_expect_issues(row: dict[str, Any], key: str) -> str:
    if key not in row:
        return "—"
    v = row[key]
    return str(int(v)) if isinstance(v, int) else "—"


def _expect_issue_count(row: dict[str, Any], key: str) -> int | None:
    v = row.get(key)
    if isinstance(v, int) and v >= 0:
        return v
    return None


def _md_expect_issues_delta(row: dict[str, Any]) -> str:
    if isinstance(row.get("expectation_issues_delta"), int):
        return str(row["expectation_issues_delta"])
    b = _expect_issue_count(row, "baseline_expectation_issues")
    c = _expect_issue_count(row, "compare_expectation_issues")
    if b is None or c is None:
        return "—"
    return str(c - b)


def _md_optional_bool_yes_no(row: dict[str, Any], key: str) -> str:
    v = row.get(key)
    if v is None:
        return "—"
    return "yes" if v else "no"


def write_junit_run_report(run: BenchmarkRunReport, path: Path) -> None:
    """Emit a JUnit XML file from a benchmark run (for CI test tabs)."""
    tsuites = ET.Element("testsuites")
    cases = run.case_results
    n = len(cases)
    failures = sum(
        1 for c in cases if not (c.passed and not c.expectation_violations)
    )
    ts = ET.SubElement(
        tsuites,
        "testsuite",
        {
            "name": f"{run.suite}::{run.harness_id}",
            "tests": str(n),
            "failures": str(failures),
            "errors": "0",
        },
    )
    for c in cases:
        ok = c.passed and not c.expectation_violations
        tc = ET.SubElement(
            ts, "testcase", {"name": c.case_id, "classname": c.category}
        )
        if not ok:
            parts: list[str] = []
            if not c.passed:
                parts.append("evaluator did not pass")
            parts.extend(c.expectation_violations)
            body = "\n".join(parts) if parts else "failed"
            msg = (parts[0] if parts else "failed")[:500]
            fl = ET.SubElement(tc, "failure", {"message": msg})
            fl.text = body
    path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(tsuites)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def format_run_step_summary(run: BenchmarkRunReport) -> str:
    s = run.summary
    return "\n".join(
        [
            "## AutoAgent-Clinical run",
            "",
            f"- **Harness:** `{run.harness_id}` · **Suite:** {run.suite}",
            f"- **Cases:** {s.get('total_cases', 0)}",
            f"- **Benchmark expectations satisfied:** "
            f"{s.get('benchmark_expectation_sat_count', 0)} / {s.get('total_cases', 0)}",
            f"- **Full pass:** {s.get('full_pass_count', 0)} / {s.get('total_cases', 0)}",
            f"- **Evaluator pass:** {s.get('evaluator_pass_count', 0)} / {s.get('total_cases', 0)}",
            "",
            "_Internal engineering lab — not for clinical decision-making._",
            "",
        ]
    )


def format_compare_step_summary(cmp: HarnessComparisonReport) -> str:
    a = cmp.aggregate
    return "\n".join(
        [
            "## AutoAgent-Clinical harness compare",
            "",
            f"- **Baseline:** `{cmp.baseline_harness}` · **Compare:** `{cmp.compare_harness}`",
            f"- **Cases:** {a.get('cases_compared', 0)}",
            f"- **Mean score Δ:** {a.get('mean_delta', 0)}",
            f"- **Mean expectation issues Δ:** {a.get('mean_expectation_issues_delta', 0)}",
            f"- **Eval pass lost:** {a.get('eval_pass_lost_count', 0)} · "
            f"**Expect sat lost:** {a.get('benchmark_expectation_sat_lost_count', 0)}",
            f"- **Full pass:** {a.get('baseline_full_pass_count', '—')} → "
            f"{a.get('compare_full_pass_count', '—')} (baseline → compare)",
            "",
            "_Internal engineering lab — not for clinical decision-making._",
            "",
        ]
    )


def append_github_step_summary(markdown: str) -> bool:
    """Append markdown to ``GITHUB_STEP_SUMMARY`` when set (GitHub Actions)."""
    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if not out:
        return False
    with open(out, "a", encoding="utf-8") as fh:
        fh.write(markdown.rstrip() + "\n")
    return True


def write_junit_compare_report(cmp: HarnessComparisonReport, path: Path) -> None:
    """JUnit XML for the **compare** harness (challenger full-pass per case)."""
    tsuites = ET.Element("testsuites")
    rows = cmp.per_case_delta
    n = len(rows)
    failures = sum(
        1 for r in rows if not r.get("compare_full_pass", False)
    )
    ts = ET.SubElement(
        tsuites,
        "testsuite",
        {
            "name": f"{cmp.suite}::compare::{cmp.compare_harness}",
            "tests": str(n),
            "failures": str(failures),
            "errors": "0",
        },
    )
    for r in rows:
        cid = str(r.get("case_id", ""))
        cat = str(r.get("category", ""))
        ok = bool(r.get("compare_full_pass"))
        tc = ET.SubElement(ts, "testcase", {"name": cid, "classname": cat})
        if not ok:
            msg = (
                f"challenger not full pass (score={r.get('compare_score')}, "
                f"expect_issues={r.get('compare_expectation_issues')})"
            )
            fl = ET.SubElement(tc, "failure", {"message": msg[:500]})
            fl.text = msg
    path.parent.mkdir(parents=True, exist_ok=True)
    tree = ET.ElementTree(tsuites)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def write_comparison_markdown(
    cmp: HarnessComparisonReport,
    path: Path,
) -> None:
    rows = cmp.per_case_delta
    n = len(rows)
    base_pass = sum(1 for r in rows if r.get("baseline_pass") is True)
    cmp_pass = sum(1 for r in rows if r.get("compare_pass") is True)
    gain = sum(
        1
        for r in rows
        if r.get("baseline_pass") is False and r.get("compare_pass") is True
    )
    loss = sum(
        1
        for r in rows
        if r.get("baseline_pass") is True and r.get("compare_pass") is False
    )
    exp_sat_gain = sum(
        1
        for r in rows
        if (bi := _expect_issue_count(r, "baseline_expectation_issues")) is not None
        and (ci := _expect_issue_count(r, "compare_expectation_issues")) is not None
        and bi > 0
        and ci == 0
    )
    exp_sat_loss = sum(
        1
        for r in rows
        if (bi := _expect_issue_count(r, "baseline_expectation_issues")) is not None
        and (ci := _expect_issue_count(r, "compare_expectation_issues")) is not None
        and bi == 0
        and ci > 0
    )

    lines = [
        "# Harness comparison",
        "",
        f"- Baseline: `{cmp.baseline_harness}`",
        f"- Compare: `{cmp.compare_harness}`",
        f"- Suite: {cmp.suite}",
        "",
        "## Aggregate",
        "",
        f"- Mean overall score delta: **{cmp.aggregate.get('mean_delta', 0)}**",
        f"- Cases: **{cmp.aggregate.get('cases_compared', 0)}**",
    ]
    agg = cmp.aggregate
    if n:
        lines.extend(
            [
                f"- Baseline eval pass: **{base_pass}** / {n}",
                f"- Compare eval pass: **{cmp_pass}** / {n}",
                f"- Gained pass (baseline fail → compare pass): **{gain}**",
                f"- Lost pass (baseline pass → compare fail): **{loss}**",
            ]
        )
        mid = agg.get("mean_expectation_issues_delta")
        if isinstance(mid, (int, float)):
            lines.append(
                f"- Mean expectation issues delta (compare − baseline): **{mid}** "
                "(negative is fewer violations on compare)",
            )
        b_sat = agg.get("baseline_benchmark_expectation_sat_count")
        c_sat = agg.get("compare_benchmark_expectation_sat_count")
        if isinstance(b_sat, int) and isinstance(c_sat, int):
            lines.append(
                f"- Benchmark expectations satisfied: **{b_sat}** → **{c_sat}** / {n} "
                "(baseline → compare; zero expectation violations per case)",
            )
        lines.append(
            f"- Gained expectation satisfaction (had issues → none): **{exp_sat_gain}**",
        )
        lines.append(
            f"- Lost expectation satisfaction (none → had issues): **{exp_sat_loss}**",
        )
    lines.extend(
        [
            "",
            "## Per-case delta",
            "",
            "| Case | Category | Baseline | Compare | Δ score | "
            "Baseline pass | Compare pass | Full pass (B) | Full pass (C) | "
            "Expect issues (B) | Expect issues (C) | Δ expect issues |",
            "|---|---|---:|---:|---:|---|---|---|---|---:|---:|---:|",
        ]
    )
    for row in rows:
        bp = row.get("baseline_pass")
        cp = row.get("compare_pass")
        lines.append(
            f"| {row['case_id']} | {_md_category(row.get('category'))} | "
            f"{row['baseline_score']} | "
            f"{row['compare_score']} | {row['delta']} | "
            f"{_yes_no_pass(bp)} | {_yes_no_pass(cp)} | "
            f"{_md_optional_bool_yes_no(row, 'baseline_full_pass')} | "
            f"{_md_optional_bool_yes_no(row, 'compare_full_pass')} | "
            f"{_md_expect_issues(row, 'baseline_expectation_issues')} | "
            f"{_md_expect_issues(row, 'compare_expectation_issues')} | "
            f"{_md_expect_issues_delta(row)} |",
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def dump_comparison_json(cmp: HarnessComparisonReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(cmp.model_dump(), indent=2),
        encoding="utf-8",
    )
