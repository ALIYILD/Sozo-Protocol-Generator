# AutoAgent-Clinical reports

This directory is reserved for **machine-generated** benchmark outputs (JSON/Markdown).
Default CLI flags write artifacts wherever you choose; you may standardize on
`reports/runs/` locally (gitignored) or attach CI artifacts.

## What this subsystem does

AutoAgent-Clinical is an **internal engineering lab**: it loads YAML benchmark
cases, runs a selected **harness** (agent stub), executes **validators** and
**evaluators**, and writes reproducible reports. It is **not** autonomous clinical
software and does not replace clinician review.

## CLI and CI exit codes

- **`--quiet` / `-q`:** do not print JSON to stdout (use `--out-json` / `--out-md` for artifacts).
- **`run --strict-exit-code`:** exit **1** if no cases ran, or if **`benchmark_expectation_sat_count < total_cases`** (any YAML expectation not satisfied).
- **`run --strict-full-pass`:** exit **1** if no cases ran, or if **`full_pass_count < total_cases`** (stricter: every case must both pass the evaluator and have zero expectation violations). Can be combined with `--strict-exit-code` (both must hold).
- **`run --min-mean-overall`:** exit **1** if the mean **`overall_score`** across cases is below the given threshold (0–1), when at least one case ran.
- **`compare --strict-exit-code`:** exit **1** if no cases were compared, or if the challenger has any **`eval_pass_lost_count`** or **`benchmark_expectation_sat_lost_count`** vs baseline.
- **`compare --strict-full-pass`:** exit **1** unless the challenger achieves a **full pass** (evaluator pass + zero expectation violations) on **every** compared case.
- **`compare --min-mean-delta`:** exit **1** if **`mean_delta`** (compare − baseline scores) is **strictly below** the threshold (e.g. `0` fails when the challenger averages lower than baseline).
- **`compare --max-mean-expectation-issues-delta`:** exit **1** if **`mean_expectation_issues_delta`** is **strictly above** the threshold (too many net new expectation issues on the challenger).
- **`--out-junit`:** write JUnit XML (`run` = each benchmark case as a test; `compare` = challenger full-pass per case). Use with CI “test results” UIs.
- **`--emit-github-step-summary`:** append a short Markdown summary to **`GITHUB_STEP_SUMMARY`** when that environment variable is set (GitHub Actions job summaries).

Repository workflow: **`.github/workflows/autoagent-clinical.yml`** — PR/main runs the default suite + a Parkinsons compare (with a **mean score Δ** floor), uploads JSON/MD/JUnit/**`autoagent-metrics.md`** (from **`scripts/autoagent_metrics_summary.py`**), runs **`pytest`** for `test_autoagent*` with **`live_generation` excluded**. **Schedule / `workflow_dispatch`** runs **`--include-regression-gates`** with **`--strict-exit-code`**.

**Manual runs:** use **Actions → AutoAgent-Clinical → Run workflow** to set category, optional adapter/regression YAML flags, skip compare, or run **live GenerationService** pytest (opt-in; may fail without KB).

Contributor expectations (merge gates, live tests, frontend): see **`CONTRIBUTING.md`** at repo root.

## Add a benchmark case

1. Edit or create `src/autoagent_clinical/benchmarks/<topic>_cases.yaml`.
2. Add an entry under `cases:` with at least:

   - `id`, `category`, `title`
   - `inputs` (task fields: modality, audience, `required_headings`, flags such as
     `relaxed_citation_check`)
   - `fixture_markdown` (deterministic text the MVP harness emits)
   - `expectations` (optional: `expect_pass`, `expected_failure_codes`,
     `forbidden_failure_codes`, `min_overall_score`)

3. Run `autoagent-clinical run` (or `sozo autoagent-clinical run`) and inspect scores.

## Add a validator

1. Implement `run_<name>(text, *, case_inputs) -> ValidatorReport` under
   `src/autoagent_clinical/validators/`.
2. Export it from `validators/__init__.py`.
3. Wire it in `runner._run_validators` and, if needed, extend an evaluator in
   `evaluators/` so dimensions stay interpretable.

Prefer **rule-based** checks; keep any future LLM judge behind an explicit flag
and separate module.

## Structured output (Phase 3)

When ``benchmark_text_source`` is ``auto`` (default) and the in-process service is a
real ``GenerationService`` on a canonical route, the harness calls
``assemble_canonical_document()`` first, serializes the resulting
``DocumentSpec`` into the benchmark run (``HarnessResult.document_spec``), and
builds markdown via ``document_spec_to_benchmark_markdown``. Validators add
``structured_spec_validator``; evaluators add dimension ``structured_spec_quality``.

- **``benchmark_text_source``:** ``auto`` (structured → else DOCX), ``docx_only``
  (Phase 2 DOCX path only), ``structured_only`` (no DOCX fallback).
- **``document_invariant_mode``:** ``relaxed`` (default; EBP uses emit-aligned section
  ids + protocol branch check) or ``strict`` (full definition + slug aliases +
  optional FNON/network narrative check). Override lists via
  ``relaxed_required_section_ids``, ``relaxed_section_order_template``,
  ``min_document_references``, ``skip_document_spec_invariants``.
- **Report distinction:** ``validator_id`` **``structured_spec_validator``** = schema /
  coarse counts; **``document_spec_invariants``** = blueprint / tree / identity /
  reference row expectations. Matching dimensions: ``structured_spec_quality`` vs
  ``document_spec_invariants``.
- **Provenance sidecars** on the DOCX path are stored in ``assembly_provenance`` only,
  not in ``structured_protocol`` (which is reserved for SozoProtocol-shaped JSON).

## Real generation (`generation_service` harness)

The **`generation_service`** harness calls `GenerationService.generate` in-process
(no Celery): DOCX output is converted to pseudo-markdown via
`autoagent_clinical.normalize.docx_to_benchmark_markdown` so existing validators
keep working.

- **Opt-in cases:** `benchmarks/generation_adapter_cases.yaml` is **excluded**
  from the default suite. Pass
  `load_all_benchmark_files(include_adapter_benchmarks=True)` or use the CLI flag
  `--include-adapter-benchmarks`.
- **Regression gates:** `benchmarks/regression_gate_cases.yaml` is excluded by default.
  Enable with `load_all_benchmark_files(include_regression_gates=True)` or
  `--include-regression-gates` on the CLI (combine with adapter flags as needed).
- **Case inputs:** `condition` (required), `tier` or `audience` (`fellow` / `partner`
  → `partners`), optional `doc_type` (default `evidence_based_protocol`),
  optional `generation_output_dir` (passed through to `GenerationService.generate`).

Tests may inject a mock service:

```python
GenerationServiceHarness(service_factory=lambda: mock_service)
```

## Compare harness variants

Register a new harness in `registry.py`, then:

```text
autoagent-clinical compare --baseline baseline_fixture --compare generator_with_qa_stub
```

Use `per_case_delta` and `aggregate.mean_delta` in the JSON output for
iteration loops (prompt/orchestration experiments).

## Limitations (MVP)

- Harnesses use **fixtures**, not live `GenerationService` or LangGraph calls.
- Heuristic validators can **false positive / false negative**; tune YAML flags
  and rubrics before gating releases on scores alone.
- **LLM-as-judge** is not enabled in this version.
