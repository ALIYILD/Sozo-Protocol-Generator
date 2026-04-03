# Legacy Retirement Matrix

**Date**: 2026-04-03
**Status**: Active — canonical is default for 3 doc types

---

## Document Type Status

| Doc Type | Canonical Status | Legacy Status | Retirement Readiness |
|----------|-----------------|---------------|---------------------|
| **Evidence-Based Protocol** | DEFAULT | Fallback only | Ready for deprecation |
| **Handbook** | DEFAULT | Fallback only | Ready for deprecation |
| **Clinical Exam** | DEFAULT | Fallback only | Ready for deprecation |
| All-in-One Protocol | Not available | ACTIVE | Blocked — no blueprint |
| Phenotype Classification | Not available | ACTIVE | Blocked — no blueprint |
| Responder Tracking | Not available | ACTIVE | Blocked — no blueprint |
| Psych Intake | Not available | ACTIVE | Blocked — no blueprint |
| Network Assessment | Not available | ACTIVE | Blocked — no blueprint |

## Condition Generator Status

| Status | Count | Conditions |
|--------|-------|-----------|
| **Knowledge YAML + canonical** | 16 | All 15 original + migraine |
| **Python builder active** | 15 | All original conditions |
| **Python builder needed** | 5 doc types | For non-canonical doc types only |
| **Ready for read-only** | 3 doc types | EBP, handbook, clinical exam no longer need Python builders |

## What Blocks Full Retirement

### For EBP / Handbook / Clinical Exam generators:
- **Nothing** — canonical path produces equivalent or better output
- Recommendation: mark Python builders as **deprecated for these 3 doc types**
- Keep builders available for the 5 doc types that still need them

### For remaining 5 doc types:
- Need blueprint YAML definitions
- Need assembler support for doc-type-specific patterns
- Estimated effort: ~1 blueprint YAML + assembler extension per doc type

## Parity Evidence

| Doc Type | Legacy Sections | Canonical Sections | Section Parity | Ref Parity | Safe to Route |
|----------|----------------|-------------------|----------------|------------|---------------|
| Evidence-Based Protocol | 11 | 14 | 118% (canonical richer) | 71% | YES |
| Handbook | 12 | 14 | 117% (canonical richer) | 71% | YES |
| Clinical Exam | ~6 | 7-8 | ~100% | ~100% | YES |

## Migration Timeline

| Phase | Target | Status |
|-------|--------|--------|
| Phase 1-2 | Architecture + schemas | Complete |
| Phase 3 | 3 blueprints, 5 conditions | Complete |
| Phase 4 | 16 conditions, evidence QA | Complete |
| Phase 5 | Canonical-by-default, review workflow | Complete |
| Phase 6 | Fidelity, batch workflows, retirement | Complete |
| **Next** | Add 5 remaining blueprints | Planned |
| **Next** | Retire Python builders for 3 canonical doc types | Ready |
| **Future** | Full legacy retirement when all 8 doc types are canonical | Dependent on blueprint authoring |

## How to Retire a Legacy Generator

1. Verify canonical blueprint exists and produces acceptable output
2. Run regression comparison: `sozo regression-compare <condition> --doc-type <type>`
3. Run batch readiness report: check all conditions pass or review_required (not incomplete)
4. Update routing in `_CANONICAL_BLUEPRINTS` if not already present
5. Mark Python builder functions as deprecated
6. Monitor for regressions in production
