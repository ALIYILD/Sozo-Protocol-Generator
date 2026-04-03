# Legacy Scripts

This directory contains generator scripts that are **superseded** by the canonical
generation pipeline in `src/sozo_generator/`.

## Why these exist

The original platform was built as a collection of standalone Python scripts, each
generating specific document types by cloning a PD master template and applying
condition-specific text replacements. This worked but led to:

- Massive code duplication (same helpers copied 11+ times)
- Hardcoded Windows paths
- Data embedded inside Python files (400KB+ of dicts)
- No test coverage for generation logic
- Disconnected from the evidence pipeline, QA engine, and review workflow

## What replaced them

The canonical pipeline in `src/sozo_generator/` provides:

```python
from sozo_generator.generation.service import GenerationService

service = GenerationService()
results = service.generate(
    condition="parkinsons",
    tier="partners",
    doc_type="all_in_one_protocol",
)
```

Or via CLI:
```bash
PYTHONPATH=src python -m sozo_generator.cli.main build condition \
  --condition parkinsons --tier both --doc-type all
```

## Migration status

| Script | Doc Type | Status | Canonical Equivalent |
|--------|----------|--------|---------------------|
| `generate_fellow_protocols.py` | all_in_one (Fellow) | DEPRECATED | `GenerationService.generate(doc_type="all_in_one_protocol")` |
| `generate_phenotype_partners_batch*.py` | phenotype (Partners) | DEPRECATED | `GenerationService.generate(doc_type="phenotype_classification")` |
| `generate_prs_baseline_partners_batch*.py` | psych_intake (Partners) | DEPRECATED | `GenerationService.generate(doc_type="psych_intake")` |
| `handbooks/` | handbook (Fellow) | WRAPPER | Uses shared helpers from `src/` |
| `handbooks_partners/` | handbook (Partners) | WRAPPER | Uses shared helpers from `src/` |
| `scripts/generate_clinical_checklists.py` | clinical_exam (Fellow) | DEPRECATED | Canonical pipeline |
| `scripts/generate_partners_checklists.py` | clinical_exam (Partners) | DEPRECATED | Canonical pipeline |
| `scripts/generate_all_in_one.py` | all_in_one (Fellow) | DEPRECATED | Canonical pipeline |
| `scripts/generate_partners_all_in_one.py` | all_in_one (Partners) | DEPRECATED | Canonical pipeline |
| `scripts/generate_6network_bedside_partners.py` | network_assessment | DEPRECATED | Canonical pipeline |
| `scripts/generate_responder_tracking_partners.py` | responder_tracking | DEPRECATED | Canonical pipeline |
| `scripts/generate_fnon_condition.js` | FNON protocol (JS) | DEPRECATED | Migrate to Python |

## When to delete

A legacy script can be deleted when:
1. The canonical pipeline produces equivalent output for all conditions
2. Output parity has been verified by a clinician or QA review
3. No downstream process depends on the legacy script's file paths
