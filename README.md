# SOZO Brain Center — Clinical Document Generator

## Overview

`sozo_generator` is a clinical document generation platform for SOZO Brain Center. It produces
evidence-based, SOZO-branded clinical documents for 15 neurological and psychiatric conditions
treated with non-invasive neuromodulation: transcranial direct current stimulation (tDCS),
transcranial pulse stimulation (TPS), transcutaneous auricular vagus nerve stimulation (taVNS),
and cranial electrotherapy stimulation (CES).

All documents are grounded in the Functional Network-Oriented Neuromodulation (FNON) framework,
which targets dysfunctional brain networks rather than isolated symptoms. Clinical content is
backed by PubMed-indexed literature; every factual claim must carry a real PMID. Low-confidence
areas are automatically flagged for human review before any document is released for clinical use.

---

## Features

- **225 clinical documents** — 15 conditions x 15 document types (7 Fellow + 8 Partners)
- **Two clinical tiers** — Fellow (supervised training level) and Partners (full FNON framework)
- **Evidence-first architecture** — PubMed-backed, real PMIDs only; fabrication prohibited
- **FNON network framework** — 6 functional brain networks drive target selection and protocol design
- **SOZO branding** — Primary Brown `#996600`, Primary Blue `#2E75B6`, Dark Blue `#1B3A5C`
- **Visual figures** — brain maps, network diagrams, symptom flow charts, patient journey maps
- **QA system** — automated completeness checking with per-document pass/fail scoring
- **Full CLI** — Typer-based CLI for all build, evidence ingestion, QA, and visual rendering operations

---

## Supported Conditions

| Condition | Slug | ICD-10 | Evidence Quality |
|---|---|---|---|
| Parkinson's Disease | `parkinsons` | G20 | High |
| Major Depressive Disorder | `depression` | F32 | High |
| Generalized Anxiety Disorder | `anxiety` | F41.1 | High |
| Attention Deficit Hyperactivity Disorder | `adhd` | F90 | Medium |
| Alzheimer's Disease / MCI | `alzheimers` | G30 | High |
| Post-Stroke Rehabilitation | `stroke_rehab` | I69 | High |
| Traumatic Brain Injury | `tbi` | S09.90 | Medium |
| Chronic Pain / Fibromyalgia | `chronic_pain` | M79.7 | Medium |
| Post-Traumatic Stress Disorder | `ptsd` | F43.1 | Medium |
| Obsessive-Compulsive Disorder | `ocd` | F42 | Medium |
| Multiple Sclerosis | `ms` | G35 | Medium |
| Autism Spectrum Disorder | `asd` | F84.0 | Low |
| Long COVID / Brain Fog | `long_covid` | U09.9 | Emerging |
| Tinnitus | `tinnitus` | H93.1 | Medium |
| Insomnia / Sleep Disorder | `insomnia` | G47.0 | Medium |

---

## Document Types

Each condition produces up to 15 documents split across two tiers.

### Fellow Tier (7 documents)

| Document | Description |
|---|---|
| Clinical Examination Checklist | Structured intake checklist covering neurological exam, symptom severity scoring, and safety screening |
| Phenotype Classification | Phenotype subtype identification guide with network profiles and preferred modalities per subtype |
| Responder Tracking | Session-by-session outcome tracker with response criteria and non-responder escalation pathway |
| Psychological Intake / PRS Baseline | Standardized psychosocial intake form with Patient-Reported Symptom (PRS) baseline measures |
| SOZO Clinical Handbook | Clinician reference guide covering overview, anatomy, network involvement, and governance rules |
| FNON All-in-One Protocol | Condensed protocol card combining phenotype, network targets, stimulation parameters, and responder criteria |
| Evidence-Based Protocol | Full evidence-graded protocol document with PMID citations, confidence labels, and review flags |

### Partners Tier (8 documents)

All seven Fellow documents plus:

| Document | Description |
|---|---|
| 6-Network Bedside Assessment | Full FNON bedside evaluation scoring all six networks (DMN, CEN, SN, SMN, LIMBIC, ATTENTION), reserved for Partners tier only |

---

## Installation

```bash
cd sozo_generator
pip install -r requirements.txt
# Or install dependencies directly:
pip install python-docx>=1.2.0 pydantic>=2.0 pydantic-settings>=2.0 typer>=0.9 \
    httpx>=0.24 requests>=2.31 biopython>=1.81 jinja2>=3.1 pyyaml>=6.0 \
    pandas>=2.0 matplotlib>=3.7 pillow>=10.0 lxml>=4.9 beautifulsoup4>=4.12 \
    svgwrite>=1.4 pytest>=7.0 pytest-cov>=4.0

# Set PYTHONPATH — editable install is not required
export PYTHONPATH=src   # Linux/macOS
set PYTHONPATH=src      # Windows (cmd)
$env:PYTHONPATH="src"   # Windows (PowerShell)
```

Python 3.11 or later is required.

---

## Quick Start

```bash
# List all 15 supported conditions
PYTHONPATH=src python -m sozo_generator.cli.main list-conditions

# Print platform version
PYTHONPATH=src python -m sozo_generator.cli.main version

# Build all documents for one condition (both tiers, all document types)
PYTHONPATH=src python -m sozo_generator.cli.main build condition \
    --condition parkinsons --tier both --doc-type all

# Build everything — all 15 conditions
PYTHONPATH=src python -m sozo_generator.cli.main build all

# Generate visual figures for a specific condition
PYTHONPATH=src python -m sozo_generator.cli.main visuals render \
    --condition parkinsons --force

# Generate visuals for all conditions
PYTHONPATH=src python -m sozo_generator.cli.main visuals render --condition all

# Run QA checks and print a Markdown report to stdout
PYTHONPATH=src python -m sozo_generator.cli.main qa report \
    --condition all --format markdown

# Ingest PubMed evidence for a condition (populates local cache)
PYTHONPATH=src python -m sozo_generator.cli.main ingest-evidence ingest \
    --condition depression --max-results 30
```

---

## Canonical Generation (Recommended)

The unified `generate` command routes through the canonical `GenerationService` pipeline
with QA, evidence traceability, and visual generation support:

```bash
# Generate all documents for Parkinson's (both tiers)
PYTHONPATH=src python -m sozo_generator.cli.main generate parkinsons

# Generate a specific document type
PYTHONPATH=src python -m sozo_generator.cli.main generate parkinsons \
    --tier partners --doc-type handbook

# Generate everything for all 15 conditions
PYTHONPATH=src python -m sozo_generator.cli.main generate all

# Skip visuals and QA for faster generation
PYTHONPATH=src python -m sozo_generator.cli.main generate parkinsons --no-visuals --no-qa
```

Or programmatically:

```python
from sozo_generator.generation.service import GenerationService

service = GenerationService()
results = service.generate(
    condition="parkinsons",
    tier="partners",
    doc_type="evidence_based_protocol",
)
for r in results:
    print(f"{r.doc_type}: {'OK' if r.success else r.error}")
```

See `docs/MIGRATION_PLAN.md` for the full architecture and migration details.

---

## CLI Reference

All commands are invoked as:

```
PYTHONPATH=src python -m sozo_generator.cli.main [COMMAND GROUP] [SUBCOMMAND] [OPTIONS]
```

### `version`

```
python -m sozo_generator.cli.main version
```

Prints the current platform version.

---

### `list-conditions`

```
python -m sozo_generator.cli.main list-conditions
```

Lists all 15 supported condition slugs with their display names.

---

### `build condition`

```
python -m sozo_generator.cli.main build condition [OPTIONS]
```

Builds clinical documents for a single condition.

| Option | Default | Description |
|---|---|---|
| `--condition` | required | Condition slug (e.g. `parkinsons`) |
| `--tier` | `both` | `fellow`, `partners`, or `both` |
| `--doc-type` | `all` | Document type value or `all` (see `DocumentType` enum) |
| `--with-visuals` / `--no-visuals` | `--with-visuals` | Include visual figure generation |
| `--output-dir` | settings default | Override the output directory |

---

### `build all`

```
python -m sozo_generator.cli.main build all [OPTIONS]
```

Builds clinical documents for all 15 conditions.

| Option | Default | Description |
|---|---|---|
| `--tier` | `both` | `fellow`, `partners`, or `both` |
| `--doc-type` | `all` | Document type value or `all` |
| `--with-visuals` / `--no-visuals` | `--with-visuals` | Include visual figure generation |
| `--output-dir` | settings default | Override the output directory |
| `--skip-existing` / `--no-skip-existing` | `--skip-existing` | Skip conditions that already have output files |
| `--conditions` | all | Comma-separated subset of condition slugs |

---

### `visuals render`

```
python -m sozo_generator.cli.main visuals render [OPTIONS]
```

Renders visual figures (brain maps, network diagrams) for one or all conditions.

| Option | Default | Description |
|---|---|---|
| `--condition` | required | Condition slug or `all` |
| `--force` / `--no-force` | `--no-force` | Regenerate even if output files already exist |
| `--output-dir` | settings default | Override the output directory |

---

### `qa report`

```
python -m sozo_generator.cli.main qa report [OPTIONS]
```

Runs QA completeness checks and generates a review report.

| Option | Default | Description |
|---|---|---|
| `--condition` | required | Condition slug or `all` |
| `--format` | `json` | Output format: `json` or `markdown` |
| `--output` | stdout | File path to write the report |

---

### `ingest-evidence ingest`

```
python -m sozo_generator.cli.main ingest-evidence ingest [OPTIONS]
```

Fetches PubMed evidence for a condition and stores results in the local cache.

| Option | Default | Description |
|---|---|---|
| `--condition` | required | Condition slug |
| `--max-results` | `30` | Maximum PubMed results per category query |
| `--force-refresh` / `--no-force-refresh` | `--no-force-refresh` | Bypass cache and re-fetch from PubMed |
| `--categories` | all | Comma-separated claim categories to search |

Valid claim categories: `pathophysiology`, `brain_regions`, `network_involvement`,
`clinical_phenotypes`, `assessment_tools`, `stimulation_targets`, `stimulation_parameters`,
`modality_rationale`, `safety`, `contraindications`, `responder_criteria`,
`inclusion_criteria`, `exclusion_criteria`

---

### `extract-template extract`

```
python -m sozo_generator.cli.main extract-template extract [OPTIONS]
```

Analyzes a template directory of `.docx` files and produces a structured JSON report
of paragraph counts, heading structure, and table counts. Useful for auditing gold-standard templates.

| Option | Default | Description |
|---|---|---|
| `--input` | required | Path to the template folder |
| `--output` | stdout | Where to write the analysis JSON |

---

## Output Structure

```
outputs/
  documents/
    {condition_slug}/
      fellow/
        Clinical_Examination_Checklist_Fellow.docx
        Phenotype_Classification_Fellow.docx
        Responder_Tracking_Fellow.docx
        Psychological_Intake_PRS_Baseline_Fellow.docx
        SOZO_Clinical_Handbook_Fellow.docx
        All_In_One_Protocol_Fellow.docx
        Evidence_Based_Protocol_Fellow.docx
      partners/
        Clinical_Examination_Checklist_Partners.docx
        Phenotype_Classification_Partners.docx
        Responder_Tracking_Partners.docx
        Psychological_Intake_PRS_Baseline_Partners.docx
        6Network_Bedside_Assessment_Partners.docx
        SOZO_Clinical_Handbook_Partners.docx
        All_In_One_Protocol_Partners.docx
        Evidence_Based_Protocol_Partners.docx
  visuals/
    {condition_slug}/
      {condition_slug}_brain_map.png
      {condition_slug}_network_diagram.png
      {condition_slug}_symptom_flow.png
      {condition_slug}_patient_journey.png
    shared/
      evidence_legend.png
      network_color_legend.png
```

Documents are organized by condition slug, then by tier (`fellow` / `partners`).
Visuals for each condition live in a per-condition subfolder; shared legend assets
are written to `visuals/shared/`.

---

## Architecture

```
src/sozo_generator/
  cli/                    Typer CLI entry points
    main.py               Top-level app; registers all command groups
    build_condition.py    `build condition` command
    build_all.py          `build all` command
    qa_report.py          `qa report` command
    render_visuals.py     `visuals render` command
    ingest_evidence.py    `ingest-evidence ingest` command
    extract_template.py   `extract-template extract` command

  conditions/
    generators/           15 condition builder functions (one per condition)
      parkinsons.py, depression.py, ... insomnia.py
      __init__.py         CONDITION_BUILDERS registry dict
    builders/             Reusable section-level builder helpers
      clinical_overview.py, anatomy.py, networks.py, phenotype.py
      assessments.py, protocols.py, safety.py, responder_logic.py
      handbook_logic.py, common.py
    shared_condition_schema.py  Shared helpers: make_network(), make_tdcs_target(), etc.

  schemas/                Pydantic data models
    condition.py          ConditionSchema, PhenotypeSubtype, NetworkProfile,
                          StimulationTarget, AssessmentTool, ProtocolEntry, SafetyNote
    evidence.py           Evidence article and dossier models
    documents.py          DocumentSpec and section models
    branding.py           SOZO branding models
    review.py             QA report models (ConditionQAReport, DocumentQAResult)

  core/
    enums.py              All platform enums: Tier, DocumentType, EvidenceLevel,
                          EvidenceType, ClaimCategory, ConfidenceLabel, ReviewFlag,
                          Modality, NetworkKey, NetworkDysfunction
    settings.py           SozoSettings (Pydantic-settings; reads .env / configs/app.yaml)
    exceptions.py         Custom exception classes
    utils.py              Shared utilities

  evidence/               Evidence pipeline
    pubmed_client.py      PubMedClient — searches PubMed via Biopython Entrez
    cache.py              EvidenceCache — disk-backed JSON cache
    confidence.py         Confidence scoring from evidence level
    article_ranker.py     Article ranking by evidence type and publication date
    scales_resolver.py    Assessment scale lookup from scales_catalog.yaml
    guideline_loader.py   Clinical guideline loading
    summarizer.py         Evidence summarization helpers

  template/               Template parsing and gold-standard extraction
    gold_standard.py      Gold-standard document loader
    parser.py             DOCX structure parser
    extractor.py          Section extractor
    style_map.py          SOZO heading/paragraph style map
    doc_structure.py      Document structure models

  content/                Content assembly (ContentAssembler)
  docx/                   DOCX rendering (DocumentRenderer / DocumentExporter)
  visuals/                Visual figure generation (VisualsExporter)
  review/                 Review flag evaluation

configs/
  app.yaml                Application settings
  branding.yaml           SOZO brand colors and typography
  fnon_networks.yaml      FNON network definitions
  modalities.yaml         tDCS / TPS / taVNS / CES parameter defaults
  devices.yaml            Device specifications
  evidence_rules.yaml     Evidence scoring rules and review flag triggers
  review_thresholds.yaml  QA thresholds

data/
  reference/
    condition_list.yaml   Master list of all 15 conditions
    scales_catalog.yaml   Validated assessment scale definitions
    neuroanatomy_map.yaml Brain region reference
  raw/pubmed_cache/       PubMed API response cache (JSON)
  processed/conditions/   Serialized ConditionSchema JSON per condition
```

---

## Evidence Policy

- All clinical claims in generated documents must be backed by published, peer-reviewed literature.
- Every reference requires a real PubMed ID (PMID). Fabricated or placeholder PMIDs are prohibited.
- Evidence is classified by level: HIGHEST > HIGH > MEDIUM > LOW > VERY_LOW > MISSING.
- Confidence labels are applied per claim: `high_confidence`, `medium_confidence`, `low_confidence`, `insufficient`.
- Claims rated `insufficient` are prefixed with a review warning and flagged for human review before clinical release.
- Evidence gaps are documented explicitly in `ConditionSchema.evidence_gaps`; they are never silently omitted.
- Off-label use of any modality (tDCS, TPS, taVNS, CES) must be marked in `StimulationTarget.off_label = True`
  and requires documented informed consent.

See `docs/evidence_policy.md` for the full policy.

---

## FNON Framework

Functional Network-Oriented Neuromodulation (FNON) is SOZO's core clinical framework.
The principle: **do not stimulate symptoms — stimulate dysfunctional networks.**

Six functional brain networks are evaluated and targeted:

| Network | Abbreviation | Primary Brain Hubs | Key Clinical Relevance |
|---|---|---|---|
| Default Mode Network | DMN | mPFC, PCC, Angular Gyrus, Hippocampus, Precuneus | Self-referential processing, rumination, autobiographical memory |
| Central Executive Network | CEN | DLPFC, PPC, ACC | Working memory, cognitive control, goal-directed behavior |
| Salience Network | SN | Anterior Insula, ACC, Amygdala | Threat detection, network switching, autonomic regulation |
| Sensorimotor Network | SMN | M1, SMA, S1, Basal Ganglia, Cerebellum | Motor output, proprioception, motor learning |
| Limbic / Emotional Network | LIMBIC | Amygdala, Hippocampus, OFC, Ventral Striatum | Affect regulation, reward, stress response |
| Attention Networks | ATTENTION | IPS, FEF, TPJ, VFC | Sustained attention, attentional orienting, vigilance |

FNON follows a five-level clinical pathway:

1. **Phenotype identification** — determine clinical subtype
2. **Network prioritization** — identify primary, secondary, and tertiary dysfunctional networks
3. **Montage/target mapping** — select stimulation targets based on network dysfunction
4. **Response evaluation** — reassess network function at the 4-week checkpoint
5. **Non-responder pathway** — FNON-based adjustment of network targets and parameters

---

## Running Tests

```bash
# Run all tests
PYTHONPATH=src pytest tests/ -v

# Skip slow visual rendering tests
PYTHONPATH=src pytest tests/ -v -m "not slow"

# Run with coverage
PYTHONPATH=src pytest tests/ -v --cov=sozo_generator --cov-report=term-missing
```

---

## License / Confidentiality

**Confidential — SOZO Brain Center internal use only.**

This platform and all generated documents are proprietary clinical materials. Do not distribute,
publish, or share outside of authorized SOZO Brain Center personnel. All clinical documents must
be reviewed by a qualified clinician before use with patients.
