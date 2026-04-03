# Phase 8 — Evidence Ingestion Pipeline

## Overview

Phase 8 is the evidence ingestion layer for the Sozo neuromodulation protocol generator. Its job is to build a structured, graded evidence corpus for each of the 15 supported clinical conditions so that downstream protocol generation (Phase 9+) is grounded in real clinical trial data rather than static heuristics.

For each condition, the pipeline:

1. Retrieves research papers from three complementary sources: OpenAlex (broad open-access coverage), Semantic Scholar (citation graph + TL;DRs), and PubMed (MeSH-indexed clinical literature).
2. Deduplicates papers across sources using DOI as the canonical key (falling back to title + year).
3. Sends abstracts to an LLM (Anthropic Claude primary, OpenAI GPT-4o fallback) for structured PICO extraction and neuromodulation protocol parameter extraction.
4. Grades each paper using a GRADE-inspired scheme (A / B / C / D / expert\_opinion).
5. Saves a typed `ConditionCorpus` JSON file per condition, plus a lightweight summary JSON.

The resulting corpus files are consumed by Phase 9 (risk-of-bias assessment via RobotReviewer) and by the protocol parameter synthesiser.

---

## Architecture

```
┌──────────────┐   ┌───────────────────┐   ┌──────────┐
│   OpenAlex   │   │ Semantic Scholar   │   │  PubMed  │
│  (pyalex)    │   │  (requests/S2 API) │   │ (Entrez) │
└──────┬───────┘   └────────┬──────────┘   └────┬─────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                     ┌──────▼──────┐
                     │   Dedup     │  (DOI → title+year fallback)
                     └──────┬──────┘
                            │
                     ┌──────▼──────────────────┐
                     │  Priority paper loader   │  (hardcoded landmark DOIs/PMIDs)
                     └──────┬──────────────────┘
                            │
                     ┌──────▼──────────────────────────────────┐
                     │  PICOExtractor (LLM batch extraction)    │
                     │  Claude (primary) → GPT-4o (fallback)   │
                     └──────┬──────────────────────────────────┘
                            │
                     ┌──────▼──────┐
                     │ grade_evidence()  │  GRADE A/B/C/D/expert_opinion
                     └──────┬──────┘
                            │
              ┌─────────────▼──────────────┐
              │       ConditionCorpus       │
              │  {condition}.json           │
              │  {condition}_summary.json   │
              └────────────────────────────┘
```

---

## How to Run

### Full run (all 15 conditions)

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest
```

This fetches up to `DEFAULT_MAX_PAPERS` (40) papers per source per condition, runs PICO extraction on all papers, and writes corpus JSON files to the default output directory (`output/evidence/phase8/`).

### Dry run (smoke test, minimal API usage)

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest --dry-run --conditions depression,anxiety
```

In dry-run mode, only one query is issued per source and the paper count is capped at 5. No corpus files are written. Useful for validating credentials and pipeline structure without cost.

### Skip LLM extraction (structural test only)

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest --skip-llm
```

Fetches and deduplicates papers but skips PICO and protocol parameter extraction. Records are saved with `pico=None` and `protocol_params=None`. Useful when iterating on retrieval queries without spending LLM tokens.

### Single condition

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest --conditions depression
```

### Custom output directory

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest \
    --conditions depression,tinnitus \
    --output-dir /data/corpora/phase8
```

### Force refresh (ignore cached corpus)

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest \
    --conditions depression \
    --force-refresh
```

---

## Configuration

The following environment variables must be set before running the pipeline. Store them in a `.env` file at the project root (never commit this file).

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes (primary LLM) | Claude API key — used for PICO batch extraction. |
| `OPENAI_API_KEY` | Recommended (fallback) | GPT-4o fallback when Anthropic is unavailable. |
| `NCBI_EMAIL` | Yes (PubMed) | Email address required by NCBI Entrez API. |
| `S2_API_KEY` | Optional | Semantic Scholar API key — rate limits are lower without it. |

Set them in your shell or `.env`:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export NCBI_EMAIL="your@email.com"
export S2_API_KEY="..."       # optional but recommended
```

---

## Output Format

For each condition `{slug}`, two files are written to `output_dir`:

### `{slug}.json` — Full corpus

A serialised `ConditionCorpus` object containing:

| Field | Type | Description |
|---|---|---|
| `condition_slug` | `str` | Machine-readable condition identifier (e.g. `"depression"`). |
| `condition_name` | `str` | Human-readable name (e.g. `"Major Depressive Disorder"`). |
| `modalities_covered` | `list[str]` | Modalities for which evidence was retrieved. |
| `total_papers_fetched` | `int` | Papers retrieved across all sources before dedup. |
| `total_included` | `int` | Papers remaining after exclusion. |
| `total_excluded` | `int` | Papers removed by filters. |
| `records` | `list[EvidenceRecord]` | Full list of enriched records (included and excluded). |
| `sources_breakdown` | `dict` | Count of papers per retrieval source. |
| `evidence_grade_breakdown` | `dict` | Count of included papers per GRADE level. |
| `build_date` | `str` | UTC ISO 8601 timestamp of corpus build. |
| `pipeline_version` | `str` | Pipeline version tag (e.g. `"phase8_v1"`). |

Each `EvidenceRecord` within `records` contains:

- `paper` — raw bibliographic fields (`PaperRaw`): title, authors, year, journal, DOI, abstract, etc.
- `pico` — LLM-extracted PICO fields (`PICOExtract`): population, intervention, comparator, outcomes, effect size, p-value, relevance score, extraction confidence.
- `protocol_params` — extracted neuromodulation parameters (`ProtocolParameters`): modality, target region, frequency, intensity, sessions, electrode montage, etc.
- `evidence_grade` — GRADE-style grade (`"A"` / `"B"` / `"C"` / `"D"` / `"expert_opinion"`).
- `included` / `exclusion_reason` — inclusion status and reason for exclusion.
- `rob_risk` / `rob_domains` — reserved `None` fields for Phase 9 risk-of-bias assessment.

### `{slug}_summary.json` — Summary only

A lightweight summary dict (no `records` list) suitable for dashboards and CI status checks. Contains all aggregate fields from `to_summary_dict()`.

---

## Expected Output — Example Summary Dict

```json
{
  "condition_slug": "depression",
  "condition_name": "Major Depressive Disorder",
  "modalities_covered": ["tDCS", "TMS", "CES", "taVNS"],
  "total_papers_fetched": 112,
  "total_included": 98,
  "total_excluded": 14,
  "protocol_papers_count": 61,
  "sources_breakdown": {
    "openalex": 41,
    "semantic_scholar": 39,
    "pubmed": 32,
    "manual": 0
  },
  "evidence_grade_breakdown": {
    "A": 12,
    "B": 34,
    "C": 29,
    "D": 18,
    "expert_opinion": 5
  },
  "rob_breakdown": {
    "low": 0,
    "unclear": 0,
    "high": 0
  },
  "build_date": "2026-04-03T14:22:11.348271+00:00",
  "query_config_version": "",
  "pipeline_version": "phase8_v1"
}
```

---

## How to Extend to a New Condition

Follow these four steps to add a 16th (or later) condition to the pipeline.

**Step 1 — Add the slug to `condition_list.yaml`** (if you maintain one for documentation):

```yaml
conditions:
  - slug: fibromyalgia
    name: Fibromyalgia
    icd10: M79.3
```

**Step 2 — Add a `ConditionQueryConfig` to `config.py`:**

```python
"fibromyalgia": ConditionQueryConfig(
    condition_slug="fibromyalgia",
    condition_name="Fibromyalgia",
    icd10="M79.3",
    aliases=["fibromyalgia syndrome", "FMS"],
    primary_modalities=["tDCS", "TMS", "PEMF"],
    openalex_queries=[
        "transcranial direct current stimulation fibromyalgia randomized trial",
        "repetitive TMS fibromyalgia pain",
    ],
    s2_queries=[
        "tDCS fibromyalgia RCT",
        "TMS fibromyalgia pain reduction",
    ],
    pubmed_mesh_query=(
        '("Fibromyalgia"[MeSH]) AND ("Transcranial Magnetic Stimulation"[MeSH] '
        'OR "Transcranial Direct Current Stimulation"[MeSH])'
    ),
    priority_dois=["10.1016/j.pain.2020.05.001"],
    priority_pmids=[],
    notes="Focus on chronic pain and fatigue outcomes. VAS and FIQ are primary scales.",
),
```

**Step 3 — Add the slug to `ALL_CONDITION_SLUGS`:**

```python
ALL_CONDITION_SLUGS: list[str] = [
    ...
    "fibromyalgia",
]
```

**Step 4 — Run ingestion:**

```bash
python -m sozo_generator.evidence.phase8.evidence_ingest --conditions fibromyalgia
```

---

## Integrating with Phase 9 (Risk-of-Bias Assessment)

Each `EvidenceRecord` contains two fields reserved for Phase 9:

```python
rob_risk: Optional[Literal["low", "unclear", "high"]]  # always None in Phase 8
rob_domains: Optional[dict[str, str]]                  # always None in Phase 8
```

In Phase 9, RobotReviewer (a machine-learning RoB tool) will be run against the full text of included RCTs. Its output will be written into these fields using the Cochrane RoB 2.0 domain schema:

```json
{
  "rob_risk": "low",
  "rob_domains": {
    "randomization_process": "low",
    "deviations_from_intervention": "low",
    "missing_outcome_data": "unclear",
    "measurement_of_outcome": "low",
    "selection_of_reported_result": "low"
  }
}
```

Do not populate these fields manually in Phase 8 scripts — they are owned by the Phase 9 pipeline and will be overwritten.

---

## Running Tests

Run the full Phase 8 test suite with verbose output:

```bash
pytest tests/test_evidence_ingest.py -v
```

Run a specific test class:

```bash
pytest tests/test_evidence_ingest.py::TestConditionConfigs -v
```

Run deduplication and save/load integration tests only:

```bash
pytest tests/test_evidence_ingest.py -v -k "dedup or saves_and_loads"
```

All tests run fully offline — no real API calls are made. LLM calls are mocked with `unittest.mock.patch`. The fixture file at `tests/fixtures/phase8_sample_papers.json` provides six representative `PaperRaw` records covering an RCT, a meta-analysis, a pilot study, a no-DOI paper, a duplicate, and an irrelevant paper.
