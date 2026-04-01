# Batch Generation & Versioning

## Overview

The batch runner generates documents for one or all 15 conditions, producing manifests, QA reports, and evidence snapshots alongside every output.

## BatchRunner

```python
from sozo_generator.orchestration.batch_runner import BatchRunner

runner = BatchRunner(
    output_dir=Path("outputs/documents/"),
    enable_qa=True,
    qa_blocking=False,  # Set True to halt on BLOCK issues
)

# Build one condition
manifest, qa_report = runner.build_condition("parkinsons")

# Build all conditions
batch_report = runner.build_all(skip_existing=True)
```

## CLI Usage

```bash
# Build single condition (existing command, unchanged)
sozo build condition --condition parkinsons

# Build all conditions
sozo build all --tier both --doc-type all

# Inspect build manifests
sozo manifests list
sozo manifests inspect --build-id build-parkinsons-20260401120000
```

## Build Manifest

Every build produces a `BuildManifest` JSON:

```json
{
  "build_id": "build-parkinsons-20260401120000",
  "condition_slug": "parkinsons",
  "generator_version": "1.0.0",
  "built_at": "2026-04-01T12:00:00Z",
  "evidence_snapshot_id": "snap-parkinsons-20260401115500",
  "total_documents": 15,
  "total_passed": 15,
  "total_blocked": 0,
  "content_hash": "a1b2c3d4e5f6g7h8",
  "documents": [...],
  "qa_summary": {...}
}
```

## Batch Report

When building all conditions, a `BatchBuildReport` aggregates results:

```json
{
  "batch_id": "batch-20260401120000",
  "total_conditions": 15,
  "successful_conditions": 14,
  "failed_conditions": 1,
  "total_documents": 210,
  "retry_suggestions": ["Retry: long_covid — EvidenceIngestionError: ..."]
}
```

## Content Hashing

Every document gets a SHA-256 content hash (first 16 hex chars). This enables:
- Regression detection (hash changed = content changed)
- Deduplication (same hash = identical output)
- Audit trail (hash recorded in manifest)

## Evidence Snapshots

```bash
# Freeze current evidence for a condition
sozo evidence freeze --condition parkinsons
```

Snapshots are immutable records of evidence state at build time. Each snapshot has:
- Snapshot ID: `snap-{condition}-{timestamp}`
- All evidence bundles
- Content hash
- Search queries used
