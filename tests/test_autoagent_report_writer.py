"""Report writer enhancements for AutoAgent-Clinical."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from autoagent_clinical.report_writer import (
    write_comparison_markdown,
    write_junit_compare_report,
    write_junit_run_report,
    write_markdown_summary,
)
from autoagent_clinical.schemas import HarnessComparisonReport
from autoagent_clinical.runner import load_all_benchmark_files, run_suite


def test_markdown_summary_includes_validator_breakdown(tmp_path: Path) -> None:
    suite = load_all_benchmark_files()
    one = next(c for c in suite.cases if c.id == "unsupported_fda_language_v1")
    from autoagent_clinical.schemas import BenchmarkSuite

    report = run_suite(BenchmarkSuite(cases=[one]), "baseline_fixture")
    out = tmp_path / "s.md"
    write_markdown_summary(report, out)
    text = out.read_text(encoding="utf-8")
    assert "Findings by validator" in text
    assert "evidence_validator" in text
    assert "Per-case validator findings" in text
    assert "### `unsupported_fda_language_v1`" in text
    assert "regulatory_overclaim" in text


def test_comparison_markdown_shows_pass_columns_and_flip_counts(tmp_path: Path) -> None:
    cmp = HarnessComparisonReport(
        baseline_harness="baseline_fixture",
        compare_harness="other",
        suite="autoagent_clinical",
        per_case_delta=[
            {
                "case_id": "a",
                "category": "cat_a",
                "baseline_score": 0.2,
                "compare_score": 0.9,
                "delta": 0.7,
                "baseline_pass": False,
                "compare_pass": True,
                "baseline_expectation_issues": 1,
                "compare_expectation_issues": 0,
                "expectation_issues_delta": -1,
                "baseline_full_pass": False,
                "compare_full_pass": True,
            },
            {
                "case_id": "b",
                "category": "cat_b",
                "baseline_score": 0.9,
                "compare_score": 0.3,
                "delta": -0.6,
                "baseline_pass": True,
                "compare_pass": False,
                "baseline_expectation_issues": 0,
                "compare_expectation_issues": 2,
                "expectation_issues_delta": 2,
                "baseline_full_pass": True,
                "compare_full_pass": False,
            },
        ],
        aggregate={
            "mean_delta": 0.05,
            "cases_compared": 2,
            "baseline_benchmark_expectation_sat_count": 1,
            "compare_benchmark_expectation_sat_count": 1,
            "benchmark_expectation_sat_gained_count": 1,
            "benchmark_expectation_sat_lost_count": 1,
            "mean_expectation_issues_delta": 0.5,
        },
    )
    out = tmp_path / "cmp.md"
    write_comparison_markdown(cmp, out)
    text = out.read_text(encoding="utf-8")
    assert "Baseline eval pass: **1** / 2" in text
    assert "Compare eval pass: **1** / 2" in text
    assert "Gained pass (baseline fail → compare pass): **1**" in text
    assert "Lost pass (baseline pass → compare fail): **1**" in text
    assert "Benchmark expectations satisfied: **1** → **1** / 2" in text
    assert "Gained expectation satisfaction (had issues → none): **1**" in text
    assert "Lost expectation satisfaction (none → had issues): **1**" in text
    assert "Mean expectation issues delta (compare − baseline): **0.5**" in text
    assert (
        "| Case | Category | Baseline | Compare | Δ score | "
        "Baseline pass | Compare pass | Full pass (B) | Full pass (C) |"
    ) in text
    assert "Δ expect issues |" in text
    assert "| a | cat_a |" in text
    assert "| no | yes | no | yes |" in text  # row a passes + full pass columns
    assert "| 1 | 0 | -1 |" in text  # row a: issue counts and delta


def test_write_junit_run_and_compare(tmp_path: Path) -> None:
    suite = load_all_benchmark_files()
    one = next(c for c in suite.cases if c.id == "device_tdcs_consistent_v1")
    from autoagent_clinical.schemas import BenchmarkSuite

    report = run_suite(BenchmarkSuite(cases=[one]), "baseline_fixture")
    j1 = tmp_path / "run.xml"
    write_junit_run_report(report, j1)
    root = ET.parse(j1).getroot()
    assert root.tag == "testsuites"
    ts = root.find("testsuite")
    assert ts is not None
    assert int(ts.attrib["tests"]) == 1
    assert int(ts.attrib["failures"]) == 0

    from autoagent_clinical.schemas import HarnessComparisonReport

    cmp = HarnessComparisonReport(
        baseline_harness="a",
        compare_harness="b",
        suite="s",
        per_case_delta=[
            {
                "case_id": "c1",
                "category": "cat",
                "baseline_score": 1.0,
                "compare_score": 1.0,
                "delta": 0.0,
                "compare_full_pass": True,
            }
        ],
        aggregate={"cases_compared": 1},
    )
    j2 = tmp_path / "cmp.xml"
    write_junit_compare_report(cmp, j2)
    root2 = ET.parse(j2).getroot()
    ts2 = root2.find("testsuite")
    assert ts2 is not None
    assert int(ts2.attrib["failures"]) == 0
