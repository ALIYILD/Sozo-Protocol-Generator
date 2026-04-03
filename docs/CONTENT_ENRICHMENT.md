# Content Enrichment — Legacy Prose Migration

**Date**: 2026-04-03

## What Was Done

Rich clinical prose from the deprecated Python condition generators was mined and
migrated into the canonical YAML knowledge system. This makes canonical outputs
not only structurally superior, but also richer in narrative depth.

## Enrichment Results

| Condition | Overview | Pathophysiology | Symptoms | FNON | Evidence |
|-----------|----------|----------------|----------|------|----------|
| Parkinson's | 362→694c (+92%) | 300→1137c (+279%) | 6→8+11 items | 309→435c | 246→625c |
| Depression | 335→711c (+112%) | 367→1261c (+244%) | 9+4→9+6 items | 368→499c | 273→610c |
| ADHD | 293→1068c (+264%) | 288→1215c (+322%) | 6→7+6 items | 304→667c | 233→707c |
| ASD | 289→1163c (+302%) | 341→1340c (+293%) | 5→7+7 items | 314→534c | 223→435c |
| Remaining 11 | Already at full depth (auto-extracted in Phase 4) | | | | |

## What Content Was Migrated

- **Condition overviews**: epidemiology, prevalence, disease burden, treatment-resistance context
- **Pathophysiology**: multi-paragraph mechanistic descriptions (Braak staging, network models, neuroinflammation, HPA axis)
- **Symptom lists**: expanded with prevalence qualifiers (e.g., "~70% of patients")
- **FNON rationale**: detailed network targeting strategy per condition
- **Evidence summaries**: richer context about evidence landscape
- **Clinical tips**: practical clinician guidance
- **Governance rules**: condition-specific governance language

## What Was Added

- **Tier guidance** (`shared/tier_guidance.yaml`): 4 rules defining Fellow vs Partner content style
  - Fellow: foundational, explanatory, safety-emphasized
  - Partner: advanced, FNON-integrated, strategic
- **Blueprint preambles**: clinical context for key sections
- **Content depth verification**: validation that enriched files parse and generate correctly

## What Was NOT Migrated

- Stale text with outdated statistics
- Excessive boilerplate that adds length without clinical value
- Content that duplicates shared rules already in YAML
- Prose that would break schema validation

## Content Depth Verification

All 28 YAML files pass validation. All 128 generation paths still succeed.
No readiness regressions. PD EBP Fellow total content: 7,336 chars (was ~3,200).
