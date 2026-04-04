# Contributing to Sozo-Protocol-Generator

## Merge expectations (benchmark lab)

The **AutoAgent-Clinical** package is an internal engineering benchmark lab. It is **not** a clinical safety or regulatory gate by itself.

### What CI enforces on PRs (see `.github/workflows/autoagent-clinical.yml`)

- **`autoagent-clinical run`** on the default bundled suite with **`--strict-exit-code`**: every case must satisfy YAML **benchmark expectations** (no expectation violations).
- **`autoagent-clinical compare`** (Parkinsons category) with **`--strict-exit-code`** and a floor on **mean score Δ** (`--min-mean-delta`): the challenger must not regress eval/expectation gates vs baseline, and average score must not drop beyond the configured threshold.
- **`scripts/autoagent_metrics_summary.py`** produces **`autoagent-metrics.md`** alongside JSON artifacts for trend-friendly snapshots.
- **Pytest** for `test_autoagent*` modules with **`-m "not live_generation"`** (see below).

Stricter local or release gates you may add manually:

- **`--strict-full-pass`** on `run`: every case must pass the **evaluator** and have zero expectation violations.
- **`--strict-full-pass`** on `compare`: the challenger must full-pass **every** compared case (often too strict for stub vs fixture baselines).

See `src/autoagent_clinical/reports/README.md` for all CLI flags (JUnit, GitHub step summary, thresholds).

### Live `GenerationService` tests (opt-in)

Tests that spin up a real in-process **`GenerationService`** (knowledge base / data on disk) are marked:

- `@pytest.mark.integration`
- `@pytest.mark.live_generation`

They **do not run** in the default AutoAgent pytest CI job. To run them locally:

```bash
set SOZO_AUTOAGENT_LIVE=1
python -m pytest tests/test_autoagent_generation_harness.py tests/test_autoagent_structured_phase3.py -m live_generation -v
```

Omit the env var to skip those tests (they will **`pytest.skip`** at the start). Mock-based tests remain the default path for fast, deterministic CI.

## Frontend (`frontend/`)

The Vite/React app lives under **`frontend/`**. Do **not** commit **`node_modules/`** or **`dist/`** (see `.gitignore`). Install and build locally:

```bash
cd frontend
npm ci
npm run build
```

If the app should live in a separate repository, keep this repo focused on the Python generator/API and maintain the SPA elsewhere.

## Local CI parity

To approximate the **AutoAgent-Clinical** workflow before pushing:

```bash
pip install -e .
autoagent-clinical run -h baseline_fixture --strict-exit-code -q --out-json run.json
autoagent-clinical compare -b baseline_fixture -p generator_with_qa_stub -c parkinsons_protocol --strict-exit-code -q --min-mean-delta -0.05 --out-json compare.json
python scripts/autoagent_metrics_summary.py --run-json run.json --compare-json compare.json -o metrics.md
python -m pytest tests/test_autoagent_clinical.py tests/test_autoagent_clinical_cli.py tests/test_autoagent_report_writer.py tests/test_autoagent_generation_harness.py tests/test_autoagent_structured_phase3.py tests/test_autoagent_document_spec_invariants.py -q --tb=short -m "not live_generation"
```

Scheduled / manual **regression gates** (with `regression_gate_cases.yaml`) run in the same workflow on **cron** and **`workflow_dispatch`** only.
