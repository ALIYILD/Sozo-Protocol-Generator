# SOZO Protocol Generator — Architecture & Migration Plan

**Date**: 2026-04-02
**Updated**: 2026-04-02
**Author**: Refactoring Lead
**Status**: Phase 1-8 complete. Canonical pipeline operational.

---

## 1. Current State Assessment

### Canonical Modules (KEEP & MAINTAIN)

These live under `src/sozo_generator/` and form the production-grade core:

| Module | Purpose | Status |
|--------|---------|--------|
| `core/` | Enums, settings, exceptions, utils | Stable |
| `schemas/` | Pydantic models (condition, evidence, contracts, documents, review, branding) | Stable |
| `conditions/registry.py` | Central condition registry | Stable |
| `conditions/generators/*.py` | 15 condition builders returning `ConditionSchema` | Stable |
| `conditions/builders/*.py` | Shared section-level helpers | Stable |
| `evidence/` | PubMed client, cache, ranking, dedup, clustering, contradiction, mapping | Stable |
| `content/` | Section assembly, claim tracing, citation insertion | Stable |
| `docx/` | DOCX rendering (exporter, renderer, styles, tables, headers, images) | Stable |
| `qa/` | QA engine + 6 rule modules (citations, safety, modality, population, language, completeness) | Stable |
| `review/` | Review state machine, manager, reports | Stable |
| `visuals/` | Brain maps, network diagrams, montage, symptom flow, patient journey | Stable |
| `template/` | Template parser, matcher, learning subsystem | Stable |
| `generation/` | Rich generator, revision engine | Stable |
| `agents/` | 9 agent implementations + registry + executor | Stable |
| `jobs/` | Job models, planner, workspace | Stable |
| `orchestration/` | Batch runner, versioning, pilot metrics | Stable |
| `ai/` | Chat engine, intent parser, comment normalizer | Stable |
| `cli/` | Typer CLI with 10+ subcommands | Stable |
| `persistence/` | File-based store | Stable |

### Canonical Entry Points (KEEP)

| Entry Point | Uses src/ pipeline | Generates |
|-------------|-------------------|-----------|
| `src/sozo_generator/cli/main.py` | Yes | All doc types via subcommands |
| `src/sozo_generator/cli/build_condition.py` | Yes | Single condition builds |
| `src/sozo_generator/cli/build_all.py` | Yes | Batch builds |
| `generate_all.py` (root) | Yes | Master pipeline runner |
| `app.py` (Streamlit) | Yes | Web UI for generation |

### Legacy Scripts (MIGRATE or DEPRECATE)

These are standalone generators that bypass the `src/` pipeline entirely:

| Script | Doc Type | Tier | Size | Action |
|--------|----------|------|------|--------|
| `generate_fellow_protocols.py` | all_in_one_protocol | Fellow | 387KB | Archive → migrate data to YAML |
| `generate_phenotype_partners_batch{1-7}.py` | phenotype_classification | Partners | 117KB total | Archive → canonical pipeline handles this |
| `generate_prs_baseline_partners_batch{1-2}.py` | psych_intake | Partners | 23KB total | Archive → canonical pipeline handles this |
| `_append_cond{2-6}.py`, `_append_conditions.py` | N/A (code gen helpers) | N/A | 316KB total | Archive after data extraction |
| `handbooks/` (6 files) | handbook | Fellow | ~60KB | Wrap → use template path from config |
| `handbooks_partners/` (6 files) | handbook | Partners | ~60KB | Wrap → use template path from config |
| `scripts/generate_clinical_checklists.py` | clinical_exam | Fellow | 96KB | Wrap as CLI |
| `scripts/generate_partners_checklists.py` | clinical_exam | Partners | ~96KB | Wrap as CLI |
| `scripts/generate_all_in_one.py` | all_in_one_protocol | Fellow | ~30KB | Wrap as CLI |
| `scripts/generate_partners_all_in_one.py` | all_in_one_protocol | Partners | ~30KB | Wrap as CLI |
| `scripts/generate_6network_bedside_partners.py` | network_assessment | Partners | 217KB | Wrap as CLI |
| `scripts/generate_responder_tracking_partners.py` | responder_tracking | Partners | ~20KB | Wrap as CLI |
| `scripts/generate_fnon_condition.js` | network protocol | Partners | JS | Deprecate → migrate to Python |

### Data-as-Code Files (EXTRACT to YAML/JSON)

| File | Size | Content |
|------|------|---------|
| `scripts/partners_all_in_one_data.py` | 397KB | Protocol data for 14 conditions |
| `scripts/protocol_data.py` | 81KB | TPS/tDCS parameters, safety data |
| `scripts/responder_conditions_data.py` | 66KB | Responder metrics |
| `scripts/responder_conditions_data_2.py` | 69KB | Additional responder data |
| `scripts/_partners_conditions.py` | 81KB | Partners condition definitions |
| `scripts/_cond_5to9.py`, `_cond_10to14.py` | 141KB | Condition data segments |
| `handbooks/cdata_{1,2,3}.py` | ~50KB | Fellow handbook condition data |
| `handbooks_partners/cdata_{1,2,3}.py` | ~50KB | Partners handbook condition data |

---

## 2. Critical Issues (Fix Immediately)

### Issue 1: Hardcoded Windows Paths (20 instances)
- **Risk**: Scripts fail on Mac/Linux/CI/Fly.io
- **Files**: 10 files across root, handbooks/, scripts/
- **Fix**: Replace with repo-relative `Path(__file__).parent` or config-driven `templates/` path
- **Pattern**: All reference `C:/Users/yildi/OneDrive/Desktop/Parkinson D/...` templates

### Issue 2: Bare `except:` Clauses (5 instances)
- **Risk**: Swallows KeyboardInterrupt/SystemExit
- **Files**: 5 batch generator files
- **Fix**: Replace with `except Exception:`

### Issue 3: No PMID Validation
- **Risk**: Invalid PMIDs (empty strings, non-numeric) pass through pipeline
- **Files**: `schemas/evidence.py`, `schemas/contracts.py`, `schemas/condition.py`
- **Fix**: Add `field_validator` with `^\d{1,9}$` pattern; reject empty strings

### Issue 4: Unpinned Dependencies
- **Risk**: Builds break on new major versions
- **Files**: `requirements.txt`, `pyproject.toml`
- **Fix**: Add compatible-release upper bounds (`>=X.Y,<Z.0`)

### Issue 5: Duplicated DOCX Helpers (11+ files)
- **Risk**: Inconsistent behavior, maintenance burden
- **Functions**: `_para_replace`, `_para_set`, `_cell_write`, `_replace_table`, `_global_replace`
- **Fix**: Extract to `src/sozo_generator/docx/legacy_helpers.py`

---

## 3. Migration Phases

### Phase 1 — Stabilize (Current)
**Goal**: Fix critical bugs without changing behavior.

1. **1A**: Remove all hardcoded paths → config/repo-relative
2. **1B**: Fix bare `except:` → `except Exception:`
3. **1C**: Add PMID validation at schema layer
4. **1D**: Pin dependency versions
5. **1E**: Add smoke tests for critical generation paths

### Phase 2 — Consolidate Utilities
**Goal**: Eliminate duplication across legacy scripts.

1. Extract shared DOCX helpers into `src/sozo_generator/docx/legacy_helpers.py`
2. Update all 11+ callers to import from canonical module
3. Add unit tests for helper functions

### Phase 3 — Separate Data from Code
**Goal**: Move embedded Python dicts into structured YAML/JSON.

1. Define target schema for protocol data, condition data, handbook data
2. Migrate Parkinson's as reference condition first
3. Create YAML loaders in `src/sozo_generator/`
4. Migrate remaining conditions incrementally
5. Validate output parity

### Phase 4 — Canonical Generation Contracts
**Goal**: Typed definitions for all generation inputs.

1. `ConditionDefinition` — structured condition metadata (already exists as `ConditionSchema`)
2. `DocumentDefinition` — document type specs with required sections
3. `ProtocolDefinition` — stimulation parameters, device configs
4. `AssessmentDefinition` — scales, scoring, timing
5. `VisualSpec` — required figures per document type

### Phase 5 — Unified Generation Service
**Goal**: Single orchestrator for all generation flows.

```python
# Target API
from sozo_generator.generation.service import GenerationService

service = GenerationService()
result = service.generate(
    condition="parkinsons",
    tier="partners",
    doc_type="all_in_one_protocol",
    with_visuals=True,
    with_qa=True,
)
```

1. Create `GenerationService` that wraps existing `DocumentExporter`
2. Route all CLI/UI calls through service
3. Legacy scripts become thin wrappers or are archived

### Phase 6 — Visual Spec System
**Goal**: Systematic visual generation tied to document types.

1. Define `VisualSpec` per document type (which figures are required)
2. Standardize visual types: brain_map, network_diagram, montage_panel, symptom_flow, patient_journey
3. Each document definition declares its visual requirements
4. Visual pipeline generates exactly what's needed

### Phase 7 — Legacy Script Migration
**Goal**: Bring standalone generators into canonical pipeline.

1. For each legacy script, verify canonical pipeline produces equivalent output
2. Archive legacy scripts to `legacy/` directory
3. Update documentation

### Phase 8 — Strengthen QA & Review
**Goal**: Full traceability and review workflow.

1. Ensure every generated claim links to evidence metadata
2. QA engine runs automatically on every build
3. Review workflow integrated with Streamlit UI
4. Build manifests capture full provenance

---

## 4. Migration Order (Safest First)

```
Phase 1A: Fix paths          ← no behavior change, immediate portability
Phase 1B: Fix bare except    ← no behavior change, safety improvement
Phase 1C: PMID validation    ← schema-level, backward compatible
Phase 1D: Pin deps           ← build reproducibility
Phase 2:  Extract helpers    ← reduces duplication, enables testing
Phase 1E: Add smoke tests    ← safety net before heavier refactors
Phase 3:  Data separation    ← start with Parkinson's, expand
Phase 4:  Typed contracts    ← builds on existing ConditionSchema
Phase 5:  Generation service ← wraps existing DocumentExporter
Phase 6:  Visual specs       ← builds on existing visuals/
Phase 7:  Script migration   ← after canonical pipeline proven
Phase 8:  QA/review          ← polish and hardening
```

---

## 5. Files That Should NOT Be Changed (Yet)

- `src/sozo_generator/conditions/generators/*.py` — working condition builders
- `src/sozo_generator/evidence/*.py` — working evidence pipeline
- `src/sozo_generator/qa/rules/*.py` — working QA rules
- `src/sozo_generator/schemas/condition.py` — stable schema (extend, don't replace)
- `configs/*.yaml` — stable configuration files
- `data/reference/*.yaml` — stable reference data
- `templates/gold_standard/*.docx` — binary templates

---

## 6. Success Criteria

- [ ] All hardcoded paths removed; scripts run on Mac/Linux/CI
- [ ] No bare `except:` clauses in codebase
- [ ] PMID validation enforced at schema layer
- [ ] Dependencies pinned with compatible ranges
- [ ] Shared DOCX helpers extracted and tested
- [ ] Smoke tests pass for all 15 conditions
- [ ] Migration plan documented and tracked
- [ ] Legacy scripts identified with clear deprecation path
