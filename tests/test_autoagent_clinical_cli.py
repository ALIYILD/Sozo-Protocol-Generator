"""CLI behavior for AutoAgent-Clinical (CI-oriented flags)."""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from typer.testing import CliRunner

from autoagent_clinical.cli import app
from autoagent_clinical.runner import load_all_benchmark_files
from autoagent_clinical.schemas import BenchmarkSuite


def test_run_strict_exit_ok_filtered_suite() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "run",
            "-h",
            "baseline_fixture",
            "-c",
            "parkinsons_protocol",
            "--strict-exit-code",
            "--quiet",
        ],
    )
    assert r.exit_code == 0


def test_run_strict_full_pass_ok_single_case_yaml(tmp_path: Path) -> None:
    suite = load_all_benchmark_files()
    one = next(c for c in suite.cases if c.id == "device_tdcs_consistent_v1")
    mini = BenchmarkSuite(suite=suite.suite, version=suite.version, cases=[one])
    y = tmp_path / "one.yaml"
    y.write_text(yaml.safe_dump(mini.model_dump(mode="json")), encoding="utf-8")
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "run",
            "-h",
            "baseline_fixture",
            "-s",
            str(y),
            "--strict-full-pass",
            "--quiet",
        ],
    )
    assert r.exit_code == 0


def test_run_strict_full_pass_fails_when_eval_not_all_pass(tmp_path: Path) -> None:
    """Parkinsons baseline has 2/3 full pass — strict-full-pass must exit 1."""
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "run",
            "-h",
            "baseline_fixture",
            "-c",
            "parkinsons_protocol",
            "--strict-full-pass",
            "--quiet",
        ],
    )
    assert r.exit_code == 1


def test_run_strict_exit_fails_empty_suite(tmp_path: Path) -> None:
    y = tmp_path / "empty.yaml"
    y.write_text(
        "suite: empty\nversion: '1'\ncases: []\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "run",
            "-h",
            "baseline_fixture",
            "-s",
            str(y),
            "--strict-exit-code",
            "--quiet",
        ],
    )
    assert r.exit_code == 1


def test_run_quiet_suppresses_stdout_json() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        ["run", "-h", "baseline_fixture", "-c", "parkinsons_protocol", "--quiet"],
    )
    assert r.exit_code == 0
    assert '"run_id"' not in r.stdout


def test_compare_strict_exit_ok_parkinsons() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "compare",
            "-b",
            "baseline_fixture",
            "-p",
            "generator_with_qa_stub",
            "-c",
            "parkinsons_protocol",
            "--strict-exit-code",
            "--quiet",
        ],
    )
    assert r.exit_code == 0


def test_compare_quiet_suppresses_stdout_json() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "compare",
            "-b",
            "baseline_fixture",
            "-p",
            "generator_with_qa_stub",
            "-c",
            "parkinsons_protocol",
            "--quiet",
        ],
    )
    assert r.exit_code == 0
    assert not r.stdout.strip()


def test_compare_min_mean_delta_threshold_can_fail() -> None:
    """Mean Δ is slightly negative on parkinsons; requiring ≥ 0 fails."""
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "compare",
            "-b",
            "baseline_fixture",
            "-p",
            "generator_with_qa_stub",
            "-c",
            "parkinsons_protocol",
            "--min-mean-delta",
            "0",
            "--quiet",
        ],
    )
    assert r.exit_code == 1


def test_compare_max_mean_expectation_issues_delta_can_fail() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "compare",
            "-b",
            "baseline_fixture",
            "-p",
            "generator_with_qa_stub",
            "-c",
            "parkinsons_protocol",
            "--max-mean-expectation-issues-delta",
            "-0.1",
            "--quiet",
        ],
    )
    assert r.exit_code == 1


def test_compare_strict_full_pass_fails_when_challenger_not_all_green() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "compare",
            "-b",
            "baseline_fixture",
            "-p",
            "generator_with_qa_stub",
            "-c",
            "parkinsons_protocol",
            "--strict-full-pass",
            "--quiet",
        ],
    )
    assert r.exit_code == 1


def test_run_min_mean_overall_too_high_fails() -> None:
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "run",
            "-h",
            "baseline_fixture",
            "-c",
            "parkinsons_protocol",
            "--min-mean-overall",
            "0.99",
            "--quiet",
        ],
    )
    assert r.exit_code == 1


def test_emit_github_step_summary_writes_when_env_set(tmp_path: Path) -> None:
    summary = tmp_path / "gh.md"
    runner = CliRunner()
    r = runner.invoke(
        app,
        [
            "run",
            "-h",
            "baseline_fixture",
            "-c",
            "parkinsons_protocol",
            "--quiet",
            "--emit-github-step-summary",
        ],
        env={**os.environ, "GITHUB_STEP_SUMMARY": str(summary)},
    )
    assert r.exit_code == 0
    text = summary.read_text(encoding="utf-8")
    assert "AutoAgent-Clinical run" in text
    assert "baseline_fixture" in text
