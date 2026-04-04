"""Smoke tests for AutoAgent-Clinical benchmark runner."""
from __future__ import annotations

from pathlib import Path

import pytest

from autoagent_clinical.runner import (
    compare_harnesses,
    load_all_benchmark_files,
    run_suite,
)


def _bundled_suite():
    return load_all_benchmark_files()


def test_load_benchmark_suite():
    suite = _bundled_suite()
    assert len(suite.cases) >= 12
    cats = {c.category for c in suite.cases}
    assert "parkinsons_protocol" in cats
    assert "fellow_partner" in cats


def test_run_baseline_suite_smoke():
    report = run_suite(_bundled_suite(), "baseline_fixture")
    assert report.summary["total_cases"] == len(report.case_results)
    assert "failure_taxonomy_counts" in report.summary
    assert report.summary["benchmark_expectation_sat_count"] == report.summary["total_cases"]


@pytest.mark.parametrize(
    "case_id",
    [
        "pd_tdcs_fellow_v1",
        "montage_conflict_anodes_v1",
        "unsupported_fda_language_v1",
    ],
)
def test_specific_cases_evaluate(case_id: str):
    suite = _bundled_suite()
    one = next(c for c in suite.cases if c.id == case_id)
    mini = type(suite)(suite=suite.suite, version=suite.version, cases=[one])
    report = run_suite(mini, "baseline_fixture")
    assert len(report.case_results) == 1
    r0 = report.case_results[0]
    assert r0.case_id == case_id
    assert r0.dimensions


def test_compare_harness_produces_deltas():
    suite = _bundled_suite()
    cmp = compare_harnesses(
        suite,
        "baseline_fixture",
        "generator_with_qa_stub",
        category_filter="parkinsons_protocol",
    )
    n = cmp.aggregate["cases_compared"]
    assert n >= 1
    assert "mean_delta" in cmp.aggregate
    assert cmp.aggregate["baseline_eval_pass_count"] <= n
    assert cmp.aggregate["compare_eval_pass_count"] <= n
    assert cmp.aggregate["eval_pass_gained_count"] >= 0
    assert cmp.aggregate["eval_pass_lost_count"] >= 0
    assert (
        cmp.aggregate["eval_pass_gained_count"] + cmp.aggregate["eval_pass_lost_count"]
        <= n
    )
    assert cmp.aggregate["baseline_benchmark_expectation_sat_count"] <= n
    assert cmp.aggregate["compare_benchmark_expectation_sat_count"] <= n
    row0 = cmp.per_case_delta[0]
    assert "baseline_expectation_issues" in row0
    assert "compare_expectation_issues" in row0
    assert cmp.aggregate["benchmark_expectation_sat_gained_count"] >= 0
    assert cmp.aggregate["benchmark_expectation_sat_lost_count"] >= 0
    assert (
        cmp.aggregate["benchmark_expectation_sat_gained_count"]
        + cmp.aggregate["benchmark_expectation_sat_lost_count"]
        <= n
    )
    assert "mean_expectation_issues_delta" in cmp.aggregate
    assert row0["expectation_issues_delta"] == (
        row0["compare_expectation_issues"] - row0["baseline_expectation_issues"]
    )
    assert "baseline_full_pass" in row0
    assert "compare_full_pass" in row0
    assert cmp.aggregate["baseline_full_pass_count"] <= n
    assert cmp.aggregate["compare_full_pass_count"] <= n
    assert cmp.aggregate["full_pass_gained_count"] >= 0
    assert cmp.aggregate["full_pass_lost_count"] >= 0


def test_single_yaml_load(tmp_path: Path):
    from autoagent_clinical.runner import load_suite_from_path

    src = Path(__file__).resolve().parents[1] / "src" / "autoagent_clinical" / "benchmarks"
    y = src / "parkinsons_protocol_cases.yaml"
    suite = load_suite_from_path(y)
    assert len(suite.cases) == 3
