#!/usr/bin/env python3
"""Summarize AutoAgent-Clinical JSON reports into markdown (CI artifacts, trends)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _top_taxonomy(summary: dict[str, Any], limit: int = 15) -> list[tuple[str, int]]:
    tax = summary.get("failure_taxonomy_counts") or {}
    rows = sorted(tax.items(), key=lambda x: (-x[1], x[0]))
    return rows[:limit]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-json", type=Path, help="BenchmarkRunReport JSON")
    ap.add_argument("--compare-json", type=Path, help="HarnessComparisonReport JSON")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    lines: list[str] = [
        "# AutoAgent-Clinical metrics snapshot",
        "",
        f"- **Recorded (UTC):** `{datetime.now(timezone.utc).isoformat()}`",
        "",
    ]

    if args.run_json and args.run_json.is_file():
        data = _load(args.run_json)
        s = data.get("summary") or {}
        lines.extend(
            [
                "## Run",
                "",
                f"- **Harness:** `{data.get('harness_id', '')}`",
                f"- **Suite:** {data.get('suite', '')}",
                f"- **Cases:** {s.get('total_cases', 0)}",
                f"- **Benchmark expectations satisfied:** "
                f"{s.get('benchmark_expectation_sat_count', 0)} / {s.get('total_cases', 0)}",
                f"- **Full pass:** {s.get('full_pass_count', 0)} / {s.get('total_cases', 0)}",
                f"- **Evaluator pass:** {s.get('evaluator_pass_count', 0)} / {s.get('total_cases', 0)}",
                "",
            ]
        )
        top = _top_taxonomy(s)
        if top:
            lines.append("### Failure taxonomy (top)")
            lines.append("")
            lines.append("| Code | Count |")
            lines.append("|---|---:|")
            for code, n in top:
                lines.append(f"| `{code}` | {n} |")
            lines.append("")

    if args.compare_json and args.compare_json.is_file():
        data = _load(args.compare_json)
        a = data.get("aggregate") or {}
        lines.extend(
            [
                "## Harness compare",
                "",
                f"- **Baseline:** `{data.get('baseline_harness', '')}`",
                f"- **Compare:** `{data.get('compare_harness', '')}`",
                f"- **Cases compared:** {a.get('cases_compared', 0)}",
                f"- **Mean score Δ (compare − baseline):** {a.get('mean_delta', 0)}",
                f"- **Mean expectation-issues Δ:** {a.get('mean_expectation_issues_delta', 0)}",
                f"- **Eval pass lost:** {a.get('eval_pass_lost_count', 0)}",
                f"- **Expectation sat lost:** {a.get('benchmark_expectation_sat_lost_count', 0)}",
                f"- **Full pass count:** {a.get('baseline_full_pass_count', '—')} → "
                f"{a.get('compare_full_pass_count', '—')} (baseline → compare)",
                "",
            ]
        )

    lines.append(
        "_Internal engineering lab - not for clinical decision-making. "
        "Use with human review and release process._\n"
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
