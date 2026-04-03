# Generation Pathway Migration Status

**Date**: 2026-04-03
**Updated**: Phase 3 — expanding canonical coverage

---

## Generation Pathways

| Pathway | Method | Status | Coverage |
|---------|--------|--------|----------|
| **Canonical** | `GenerationService.generate_canonical()` | Active — expanding | EBP (all tiers), Handbook, Clinical Exam |
| **Legacy** | `GenerationService.generate()` | Active — stable | All 8 doc types × 15 conditions |
| **Template** | `GenerationService.generate_from_template()` | Active — stable | Any template × any condition |

## Document Family Status

| Document Type | Canonical Blueprint | Legacy Active | Migration Status |
|---------------|-------------------|---------------|-----------------|
| Evidence-Based Protocol | `evidence_based_protocol.yaml` | Yes | **Canonical ready** — both paths produce output |
| Handbook | `handbook.yaml` | Yes | **Canonical ready** |
| Clinical Exam | `clinical_exam.yaml` | Yes | **Canonical ready** |
| All-in-One Protocol | Not yet | Yes | Legacy only |
| Phenotype Classification | Not yet | Yes | Legacy only |
| Responder Tracking | Not yet | Yes | Legacy only |
| Psych Intake | Not yet | Yes | Legacy only |
| Network Assessment | Not yet | Yes | Legacy only — Partners only |

## Knowledge System Status

| Knowledge Type | Count | Coverage |
|---------------|-------|----------|
| Conditions | 5 | PD, Depression, ADHD, ASD, Migraine |
| Modalities | 4 | tDCS, TPS, taVNS, CES |
| Contraindications | 7 | Universal set |
| Shared Rules | 15+ | Governance, safety, patient journey, responder classification |
| Blueprints | 3 | EBP, Handbook, Clinical Exam |

## Business Logic Migration

| Logic | Source | Target | Status |
|-------|--------|--------|--------|
| Patient journey stages | `handbook_logic.py` | `shared/patient_journey.yaml` | Migrated |
| Stage defaults | `handbook_logic.py` | `shared/patient_journey.yaml` | Migrated |
| Responder classification | `responder_logic.py` | `shared/responder_classification.yaml` | Migrated |
| FNON Level 5 pathway | `responder_logic.py` | `shared/responder_classification.yaml` | Migrated |
| Safety boilerplate | `safety.py` | Blueprint preamble fields | Migrated |
| FNON preamble | `networks.py` | Blueprint preamble fields | Migrated |
| TPS off-label warning | `protocols.py` | Blueprint preamble + knowledge safety_rules | Migrated |
| Tier section insertion | `exporter.py` | Blueprint `tier:` field per section | Migrated |
| Protocol table headers | `protocols.py` | Blueprint `table_headers` | Migrated |
| Assessment table headers | `assessments.py` | Blueprint `table_headers` | Migrated |

## What Remains Legacy

1. **Condition generators** (`conditions/generators/*.py`) — 15 files, ~9K LOC
   - Still the source of truth for ConditionSchema in legacy path
   - Knowledge YAML covers 5 conditions; 10 more need migration
2. **Private builders** (`_build_psych_intake_sections`, `_build_handbook_intro`)
   - Exporter-internal methods, not yet in blueprints
3. **Root-level batch scripts** — All deprecated, marked for removal
4. **JavaScript FNON generators** (`scripts/fnon_data/*.js`) — Deprecated

## How to Add a New Condition

**Canonical path (preferred):**
1. Create `sozo_knowledge/knowledge/conditions/<slug>.yaml`
2. No Python code needed
3. Generate: `sozo generate-canonical <slug> --doc-type evidence_based_protocol`

**Legacy path (existing 15 conditions):**
1. Create `src/sozo_generator/conditions/generators/<slug>.py`
2. Generate: `sozo generate <slug> --tier both --doc-type all`

## How to Add a New Document Type

1. Create `sozo_knowledge/blueprints/<doc_type>.yaml`
2. Define sections with data sources, table headers, visual requirements
3. No Python code needed — assembler handles it
4. Generate: `sozo generate-canonical <condition> --doc-type <doc_type>`
