# SOZO Generator — Technical Architecture

## Phase 2 Architecture

See also:
- [Evidence Lifecycle](evidence_lifecycle.md)
- [QA Lifecycle](qa_lifecycle.md)
- [Reviewer Workflow](reviewer_workflow.md)
- [Batch Generation](batch_generation.md)
- [Safety & Evidence Policy](safety_evidence_policy.md)

### Phase 2 Module Map

| Package | Purpose |
|---------|---------|
| `schemas/contracts.py` | **Single source of truth** for all Phase 2 types |
| `evidence/query_planner.py` | Build PubMed query plans per condition |
| `evidence/deduper.py` | PMID deduplication with metadata merging |
| `evidence/ranker.py` | Multi-factor evidence ranking |
| `evidence/clusterer.py` | Group evidence into section-level bundles |
| `evidence/bundles.py` | Bundle persistence (JSON) |
| `evidence/snapshots.py` | Versioned evidence snapshots |
| `evidence/contradiction.py` | Contradiction detection |
| `content/claim_tracer.py` | Claim-evidence linking |
| `qa/engine.py` | QA orchestrator with 6 rule modules |
| `qa/rules/` | Citation, safety, modality, population, language, completeness rules |
| `review/manager.py` | Review state machine + persistence |
| `visuals/figure_manifest.py` | Figure manifest builder |
| `visuals/templates.py` | Deterministic visual templates |
| `orchestration/batch_runner.py` | Batch document generation |
| `orchestration/versioning.py` | Build manifests + content hashing |

---

## Original Module Dependency Graph

```
cli/main.py
  ├── cli/build_condition.py
  │     ├── core/enums.py          (Tier, DocumentType)
  │     ├── core/settings.py       (SozoSettings)
  │     ├── conditions/registry.py (get_registry)
  │     └── docx/exporter.py       (DocumentExporter)
  │
  ├── cli/build_all.py
  │     └── (same as build_condition)
  │
  ├── cli/qa_report.py
  │     ├── core/enums.py
  │     ├── core/settings.py
  │     ├── conditions/registry.py
  │     └── schemas/review.py      (ConditionQAReport, DocumentQAResult)
  │
  ├── cli/render_visuals.py
  │     ├── core/settings.py
  │     ├── conditions/registry.py
  │     └── visuals/exporters.py   (VisualsExporter)
  │
  ├── cli/ingest_evidence.py
  │     ├── core/enums.py          (ClaimCategory)
  │     ├── core/settings.py
  │     ├── conditions/registry.py
  │     ├── evidence/pubmed_client.py
  │     └── evidence/cache.py
  │
  └── cli/extract_template.py
        └── python-docx            (direct dependency)

conditions/registry.py
  └── conditions/generators/__init__.py  (CONDITION_BUILDERS)
        ├── conditions/generators/parkinsons.py
        ├── conditions/generators/depression.py
        ├── ... (13 more)
        └── conditions/generators/insomnia.py
              └── conditions/shared_condition_schema.py
                    └── schemas/condition.py
                          └── core/enums.py

schemas/condition.py
  ├── ConditionSchema
  ├── PhenotypeSubtype
  ├── NetworkProfile
  ├── StimulationTarget
  ├── AssessmentTool
  ├── SafetyNote
  └── ProtocolEntry

docx/exporter.py (DocumentExporter)
  ├── conditions/registry.py
  ├── schemas/condition.py
  ├── content/assembler.py       (ContentAssembler)
  └── docx/renderer.py           (DocumentRenderer)
        └── schemas/documents.py (DocumentSpec)

evidence/pubmed_client.py
  ├── biopython (Entrez)
  └── evidence/cache.py

evidence/confidence.py
  └── core/enums.py  (EvidenceLevel, ConfidenceLabel)

visuals/exporters.py (VisualsExporter)
  ├── schemas/condition.py
  ├── matplotlib
  └── svgwrite
```

---

## Data Flow: Document Generation

```
CLI command
    │
    ▼
conditions/registry.py  ──── get_registry() ────► CONDITION_BUILDERS dict
    │                                                       │
    │                                          calls build_{slug}_condition()
    │                                                       │
    │                                                       ▼
    │                                          ConditionSchema (Pydantic model)
    │                                          filled with clinical content,
    │                                          network profiles, phenotypes,
    │                                          protocols, references
    │
    ▼
docx/exporter.py  (DocumentExporter.export_condition)
    │
    ├── For each (Tier, DocumentType) combination:
    │       │
    │       ▼
    │   content/assembler.py  (ContentAssembler)
    │       │  Reads ConditionSchema fields
    │       │  Applies evidence confidence labels
    │       │  Injects review flags for low-confidence claims
    │       │  Returns structured section content
    │       │
    │       ▼
    │   docx/renderer.py  (DocumentRenderer)
    │       │  Applies SOZO styles (heading levels, brand colors)
    │       │  Inserts tables, structured lists, figures
    │       │  Writes outputs/{condition}/{tier}/{filename}.docx
    │       │
    │       ▼
    │   outputs/documents/{slug}/{tier}/{DocumentType}_{Tier}.docx
    │
    └── (optional) visuals/exporters.py
            Generates PNG/SVG figures embedded or placed alongside documents
```

---

## Schema Relationships

```
ConditionSchema
  ├── slug: str
  ├── display_name: str
  ├── icd10: str
  ├── overview: str
  ├── pathophysiology: str
  ├── core_symptoms: list[str]
  │
  ├── network_profiles: list[NetworkProfile]
  │     └── NetworkProfile
  │           ├── network: NetworkKey          (DMN | CEN | SN | SMN | LIMBIC | ATTENTION)
  │           ├── dysfunction: NetworkDysfunction  (HYPO | NORMAL | HYPER)
  │           ├── relevance: str
  │           ├── severity: str
  │           ├── primary: bool
  │           └── evidence_note: str | None
  │
  ├── phenotypes: list[PhenotypeSubtype]
  │     └── PhenotypeSubtype
  │           ├── slug: str
  │           ├── label: str
  │           ├── description: str
  │           ├── key_features: list[str]
  │           ├── primary_networks: list[NetworkKey]
  │           └── preferred_modalities: list[Modality]
  │
  ├── assessment_tools: list[AssessmentTool]
  │     └── AssessmentTool
  │           ├── scale_key: str
  │           ├── name: str
  │           ├── abbreviation: str
  │           ├── domains: list[str]
  │           ├── timing: str          (baseline | weekly | monthly | endpoint)
  │           └── evidence_pmid: str | None
  │
  ├── stimulation_targets: list[StimulationTarget]
  │     └── StimulationTarget
  │           ├── modality: Modality   (TDCS | TPS | TAVNS | CES | MULTIMODAL)
  │           ├── target_region: str
  │           ├── target_abbreviation: str
  │           ├── laterality: str      (bilateral | left | right)
  │           ├── rationale: str
  │           ├── evidence_level: EvidenceLevel
  │           ├── off_label: bool
  │           └── consent_required: bool
  │
  ├── protocols: list[ProtocolEntry]
  │     └── ProtocolEntry
  │           ├── protocol_id: str
  │           ├── label: str
  │           ├── modality: Modality
  │           ├── target_region: str
  │           ├── phenotype_slugs: list[str]    (links to PhenotypeSubtype.slug)
  │           ├── network_targets: list[NetworkKey]
  │           ├── parameters: dict[str, ...]    (intensity, frequency, duration, etc.)
  │           ├── evidence_level: EvidenceLevel
  │           ├── off_label: bool
  │           └── session_count: int | None
  │
  ├── safety_notes: list[SafetyNote]
  │     └── SafetyNote
  │           ├── category: str     (contraindication | precaution | monitoring | stopping_rule)
  │           ├── description: str
  │           ├── severity: str     (low | moderate | high | absolute)
  │           └── source: str | None
  │
  ├── evidence_summary: str
  ├── evidence_gaps: list[str]
  ├── review_flags: list[str]
  ├── references: list[dict]           (each dict contains pmid, title, authors, year, etc.)
  └── overall_evidence_quality: EvidenceLevel
```

`ProtocolEntry.phenotype_slugs` creates a logical foreign-key relationship to
`PhenotypeSubtype.slug` within the same `ConditionSchema`. The content assembler uses
this to generate per-phenotype protocol sections.

---

## Evidence Pipeline

```
PubMed (NCBI Entrez API)
    │
    ▼
evidence/pubmed_client.py  (PubMedClient)
    │  Constructs query: "{condition_name}[Title/Abstract] AND {category_terms}"
    │  Fetches up to max_results articles
    │  Returns list of parsed article objects
    │
    ▼
evidence/cache.py  (EvidenceCache)
    │  Disk-backed JSON cache at data/raw/pubmed_cache/
    │  Key format: "ingest|{slug}|{category}|{max_results}"
    │  Avoids repeat API calls; bypassed with --force-refresh
    │
    ▼
evidence/article_ranker.py  (ArticleRanker)
    │  Ranks articles by EvidenceType priority order:
    │  clinical_practice_guideline > systematic_review > meta_analysis >
    │  large_rct > rct > controlled_trial > cohort_study > narrative_review >
    │  consensus_statement > pilot_study > feasibility_study > case_series >
    │  case_report > expert_opinion > indirect_evidence
    │
    ▼
evidence/confidence.py
    │  Maps EvidenceLevel → ConfidenceLabel:
    │    HIGHEST/HIGH  → high_confidence
    │    MEDIUM        → medium_confidence
    │    LOW           → low_confidence
    │    VERY_LOW      → insufficient
    │    MISSING       → insufficient + review_required
    │
    ▼
EvidenceDossier (schemas/evidence.py)
    │  Aggregated evidence for a condition or claim category
    │  Stores top-ranked articles, overall confidence label, review flags
    │
    ▼
ContentAssembler (content/assembler.py)
    │  Injects confidence-labeled language into section text:
    │    high_confidence   → "Evidence-based:"
    │    medium_confidence → "Supported by emerging evidence:"
    │    low_confidence    → "Consensus-informed (limited evidence):"
    │    insufficient      → "REQUIRES CLINICAL REVIEW — Evidence insufficient:"
    │
    ▼
DocumentRenderer (docx/renderer.py)
    │  Writes evidence citations with PMID as footnote references
    └─► .docx output
```

---

## Registry Design: Metadata vs Schema Separation

The registry uses a two-layer design:

**Layer 1 — Metadata** (`data/reference/condition_list.yaml`)

Lightweight YAML listing all 15 conditions with slug, display name, ICD-10 code, aliases,
template status, and evidence quality band. This file is the authoritative condition roster.
CLI commands that only need to enumerate conditions (e.g. `list-conditions`) read this file
without executing any builder.

**Layer 2 — Full Schema** (`conditions/generators/{slug}.py`)

Each builder function (`build_{slug}_condition()`) constructs a fully populated
`ConditionSchema` instance with all clinical content, network profiles, phenotypes,
assessment tools, stimulation targets, protocols, safety notes, and references.
These are only executed when a document build or QA run is requested.

```
conditions/registry.py
  list_slugs()       → reads condition_list.yaml  (metadata only)
  list_all()         → reads condition_list.yaml  (metadata only)
  get(slug)          → calls CONDITION_BUILDERS[slug]()  (full schema)
```

This separation keeps CLI startup fast and prevents all 15 builders from running
on every invocation.

---

## Visuals Pipeline

```
CLI: visuals render --condition {slug}
    │
    ▼
conditions/registry.py → ConditionSchema
    │
    ▼
visuals/exporters.py  (VisualsExporter)
    │
    ├── generate_all(condition, force=False)
    │     ├── brain_map      → {slug}_brain_map.png
    │     │     Uses matplotlib + anatomical region data from ConditionSchema.key_brain_regions
    │     │
    │     ├── network_diagram → {slug}_network_diagram.png
    │     │     Plots all 6 FNON networks; highlights active networks from network_profiles
    │     │     Color-codes by dysfunction direction (hypo=cool, hyper=warm)
    │     │
    │     ├── symptom_flow   → {slug}_symptom_flow.png
    │     │     Flowchart: phenotype → network dysfunction → stimulation target → protocol
    │     │
    │     └── patient_journey → {slug}_patient_journey.png
    │           Timeline: intake → baseline → sessions → 4-week checkpoint → response/non-responder
    │
    └── generate_shared_legends()   (called only when --condition all)
          ├── evidence_legend.png      (EvidenceLevel color scale)
          └── network_color_legend.png (per-network brand colors)

Output location: outputs/visuals/{slug}/ and outputs/visuals/shared/
```

Visuals generation uses `matplotlib` for raster PNG output and `svgwrite` for SVG exports.
The `--force` flag bypasses the file-existence check and regenerates all figures.
If `matplotlib` or `numpy` is not installed, the visuals subcommand reports a clear error
without blocking document generation.
