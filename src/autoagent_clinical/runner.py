"""Benchmark runner — load cases, invoke harness, validators, evaluators."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from .evaluators import (
    evaluate_audience,
    evaluate_document_spec_invariants,
    evaluate_evidence_dimensions,
    evaluate_modality,
    evaluate_overall,
    evaluate_structure,
    evaluate_structured_spec,
)
from .registry import get_harness
from .schemas import (
    BenchmarkCase,
    BenchmarkRunReport,
    BenchmarkSuite,
    CaseEvaluation,
    HarnessComparisonReport,
    HarnessResult,
    ValidatorReport,
)
from .validators import (
    run_citation_completeness_check,
    run_device_modality_check,
    run_document_spec_invariants_validation,
    run_evidence_validation,
    run_montage_roi_check,
    run_protocol_structure_validation,
    run_structured_spec_validation,
)


def _benchmarks_dir() -> Path:
    return Path(__file__).resolve().parent / "benchmarks"


# Loaded only when ``include_adapter_benchmarks=True`` so default runs stay stable.
ADAPTER_BENCHMARKS_FILENAME = "generation_adapter_cases.yaml"
REGRESSION_GATE_BENCHMARKS_FILENAME = "regression_gate_cases.yaml"


def load_suite_from_path(path: Path) -> BenchmarkSuite:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return BenchmarkSuite.model_validate(raw)


def load_all_benchmark_files(
    directory: Optional[Path] = None,
    *,
    include_adapter_benchmarks: bool = False,
    include_regression_gates: bool = False,
) -> BenchmarkSuite:
    d = directory or _benchmarks_dir()
    merged_cases: list[BenchmarkCase] = []
    suite_name = "autoagent_clinical"
    version = "1"
    for p in sorted(d.glob("*.yaml")):
        if not include_adapter_benchmarks and p.name == ADAPTER_BENCHMARKS_FILENAME:
            continue
        if not include_regression_gates and p.name == REGRESSION_GATE_BENCHMARKS_FILENAME:
            continue
        partial = load_suite_from_path(p)
        merged_cases.extend(partial.cases)
        suite_name = partial.suite or suite_name
        version = partial.version or version
    return BenchmarkSuite(suite=suite_name, version=version, cases=merged_cases)


def _run_validators(result: HarnessResult, case: BenchmarkCase) -> list[ValidatorReport]:
    text = result.output_text
    inputs = dict(case.inputs)
    proto = result.structured_protocol
    reports = [
        run_protocol_structure_validation(
            text, case_inputs=inputs, structured_protocol=proto
        ),
        run_structured_spec_validation(
            result.document_spec,
            case_inputs=inputs,
        ),
        run_document_spec_invariants_validation(
            result.document_spec,
            case_inputs=inputs,
        ),
        run_evidence_validation(text, case_inputs=inputs),
        run_montage_roi_check(text, case_inputs=inputs),
        run_citation_completeness_check(text, case_inputs=inputs),
        run_device_modality_check(text, case_inputs=inputs),
    ]
    return reports


def _failure_codes(reports: list[ValidatorReport]) -> list[str]:
    codes: list[str] = []
    for r in reports:
        for f in r.findings:
            codes.append(f.code)
    return sorted(set(codes))


def _check_expectations(case: BenchmarkCase, ce: CaseEvaluation) -> list[str]:
    violations: list[str] = []
    codes = set(ce.failure_codes)
    ex = case.expectations

    if ex.forbidden_failure_codes:
        for fc in ex.forbidden_failure_codes:
            if fc in codes:
                violations.append(f"Forbidden failure code present: {fc}")

    if ex.expected_failure_codes:
        if not codes.intersection(set(ex.expected_failure_codes)):
            violations.append(
                "Expected at least one of "
                f"{ex.expected_failure_codes}, observed {sorted(codes)}"
            )

    if ex.expect_pass is not None:
        if ex.expect_pass != ce.passed:
            violations.append(
                f"expect_pass={ex.expect_pass} but evaluator passed={ce.passed}"
            )

    if ex.min_overall_score > 0 and ce.overall_score + 1e-6 < ex.min_overall_score:
        violations.append(
            f"overall_score {ce.overall_score} < min {ex.min_overall_score}"
        )

    return violations


def evaluate_case_result(
    case: BenchmarkCase,
    harness_id: str,
    result: HarnessResult,
) -> CaseEvaluation:
    reports = _run_validators(result, case)
    dims = [
        evaluate_structure(reports),
        evaluate_structured_spec(reports),
        evaluate_document_spec_invariants(reports),
        *evaluate_modality(reports),
        *evaluate_evidence_dimensions(reports),
        evaluate_audience(result.output_text, case.inputs),
    ]
    ce = CaseEvaluation(
        case_id=case.id,
        category=case.category,
        harness_id=harness_id,
        validator_reports=reports,
        dimensions=dims,
        failure_codes=_failure_codes(reports),
    )
    ce = evaluate_overall(ce)
    ce.expectation_violations = _check_expectations(case, ce)
    return ce


def run_suite(
    suite: BenchmarkSuite,
    harness_id: str,
    *,
    category_filter: Optional[str] = None,
) -> BenchmarkRunReport:
    harness = get_harness(harness_id)
    run_id = str(uuid.uuid4())
    started = datetime.now(timezone.utc).isoformat()
    results: list[CaseEvaluation] = []
    cases = suite.cases
    if category_filter:
        cases = [c for c in cases if c.category == category_filter]

    for case in cases:
        h_result = harness.run(case)
        if h_result.case_id != case.id:
            h_result = HarnessResult(
                case_id=case.id,
                output_text=h_result.output_text,
                structured_protocol=h_result.structured_protocol,
                document_spec=h_result.document_spec,
                assembly_provenance=h_result.assembly_provenance,
                metadata=h_result.metadata,
            )
        results.append(evaluate_case_result(case, harness_id, h_result))

    finished = datetime.now(timezone.utc).isoformat()
    passed = sum(1 for r in results if r.passed and not r.expectation_violations)
    taxonomy: dict[str, int] = {}
    for r in results:
        for code in r.failure_codes:
            taxonomy[code] = taxonomy.get(code, 0) + 1

    summary = {
        "total_cases": len(results),
        "evaluator_pass_count": sum(1 for r in results if r.passed),
        "benchmark_expectation_sat_count": sum(
            1 for r in results if not r.expectation_violations
        ),
        "full_pass_count": passed,
        "failure_taxonomy_counts": taxonomy,
        "harness_id": harness_id,
        "category_filter": category_filter,
    }
    return BenchmarkRunReport(
        run_id=run_id,
        started_at=started,
        finished_at=finished,
        suite=suite.suite,
        harness_id=harness_id,
        case_results=results,
        summary=summary,
    )


def compare_harnesses(
    suite: BenchmarkSuite,
    baseline_id: str,
    compare_id: str,
    *,
    category_filter: Optional[str] = None,
) -> HarnessComparisonReport:
    r_base = run_suite(suite, baseline_id, category_filter=category_filter)
    r_cmp = run_suite(suite, compare_id, category_filter=category_filter)
    by_id: dict[str, CaseEvaluation] = {c.case_id: c for c in r_cmp.case_results}
    per_case: list[dict[str, Any]] = []
    deltas: list[float] = []
    for a in r_base.case_results:
        b = by_id.get(a.case_id)
        if not b:
            continue
        d = round(b.overall_score - a.overall_score, 4)
        deltas.append(d)
        base_full = a.passed and not a.expectation_violations
        cmp_full = b.passed and not b.expectation_violations
        per_case.append(
            {
                "case_id": a.case_id,
                "category": a.category,
                "baseline_score": a.overall_score,
                "compare_score": b.overall_score,
                "delta": d,
                "baseline_pass": a.passed,
                "compare_pass": b.passed,
                "baseline_full_pass": base_full,
                "compare_full_pass": cmp_full,
                "baseline_expectation_issues": len(a.expectation_violations),
                "compare_expectation_issues": len(b.expectation_violations),
                "expectation_issues_delta": len(b.expectation_violations)
                - len(a.expectation_violations),
            }
        )
    n = len(per_case)
    base_ok = sum(1 for r in per_case if r["baseline_pass"])
    cmp_ok = sum(1 for r in per_case if r["compare_pass"])
    gained = sum(
        1 for r in per_case if not r["baseline_pass"] and r["compare_pass"]
    )
    lost = sum(1 for r in per_case if r["baseline_pass"] and not r["compare_pass"])
    base_expect_sat = sum(
        1 for r in per_case if r["baseline_expectation_issues"] == 0
    )
    cmp_expect_sat = sum(
        1 for r in per_case if r["compare_expectation_issues"] == 0
    )
    exp_sat_gained = sum(
        1
        for r in per_case
        if r["baseline_expectation_issues"] > 0
        and r["compare_expectation_issues"] == 0
    )
    exp_sat_lost = sum(
        1
        for r in per_case
        if r["baseline_expectation_issues"] == 0
        and r["compare_expectation_issues"] > 0
    )
    issue_deltas = [r["expectation_issues_delta"] for r in per_case]
    mean_issue_delta = (
        round(sum(issue_deltas) / len(issue_deltas), 4) if issue_deltas else 0.0
    )
    baseline_full_n = sum(1 for r in per_case if r["baseline_full_pass"])
    compare_full_n = sum(1 for r in per_case if r["compare_full_pass"])
    full_pass_gained = sum(
        1
        for r in per_case
        if not r["baseline_full_pass"] and r["compare_full_pass"]
    )
    full_pass_lost = sum(
        1 for r in per_case if r["baseline_full_pass"] and not r["compare_full_pass"]
    )
    agg = {
        "mean_delta": round(sum(deltas) / len(deltas), 4) if deltas else 0.0,
        "cases_compared": n,
        "category_filter": category_filter,
        "baseline_eval_pass_count": base_ok,
        "compare_eval_pass_count": cmp_ok,
        "eval_pass_gained_count": gained,
        "eval_pass_lost_count": lost,
        "baseline_benchmark_expectation_sat_count": base_expect_sat,
        "compare_benchmark_expectation_sat_count": cmp_expect_sat,
        "benchmark_expectation_sat_gained_count": exp_sat_gained,
        "benchmark_expectation_sat_lost_count": exp_sat_lost,
        "mean_expectation_issues_delta": mean_issue_delta,
        "baseline_full_pass_count": baseline_full_n,
        "compare_full_pass_count": compare_full_n,
        "full_pass_gained_count": full_pass_gained,
        "full_pass_lost_count": full_pass_lost,
    }
    return HarnessComparisonReport(
        baseline_harness=baseline_id,
        compare_harness=compare_id,
        suite=suite.suite,
        per_case_delta=per_case,
        aggregate=agg,
    )
