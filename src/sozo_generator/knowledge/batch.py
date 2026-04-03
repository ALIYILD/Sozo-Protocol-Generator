"""
Batch Workflows — operational batch generation, review, and reporting.

Provides tools for running generation and review across multiple
conditions and document types in a structured, tracked way.

Usage:
    from sozo_generator.knowledge.batch import BatchRunner

    runner = BatchRunner()
    report = runner.generate_all_canonical()
    report = runner.review_readiness_report()
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Result of one document in a batch."""
    condition: str
    blueprint: str
    tier: str
    success: bool
    output_path: str = ""
    readiness: str = ""
    sections: int = 0
    placeholders: int = 0
    pmids: int = 0
    error: str = ""


@dataclass
class BatchReport:
    """Summary of a batch operation."""
    operation: str
    started_at: str = ""
    completed_at: str = ""
    total: int = 0
    succeeded: int = 0
    failed: int = 0
    review_required: int = 0
    results: list[BatchResult] = field(default_factory=list)

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def finalize(self):
        self.completed_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.total = len(self.results)
        self.succeeded = sum(1 for r in self.results if r.success)
        self.failed = sum(1 for r in self.results if not r.success)
        self.review_required = sum(1 for r in self.results if r.readiness == "review_required")

    def to_text(self) -> str:
        lines = [
            f"=== BATCH REPORT: {self.operation} ===",
            f"Started: {self.started_at}",
            f"Total: {self.total} | Succeeded: {self.succeeded} | Failed: {self.failed}",
            f"Review required: {self.review_required}",
            "",
        ]
        for r in self.results:
            status = "OK" if r.success else "FAIL"
            extra = f" [{r.readiness}]" if r.readiness else ""
            err = f" ERROR: {r.error}" if r.error else ""
            lines.append(f"  [{status}] {r.condition}/{r.blueprint}/{r.tier}"
                        f" ({r.sections}s, {r.placeholders}ph, {r.pmids}pmid){extra}{err}")
        return "\n".join(lines)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "operation": self.operation,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total": self.total,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "review_required": self.review_required,
            "results": [
                {
                    "condition": r.condition,
                    "blueprint": r.blueprint,
                    "tier": r.tier,
                    "success": r.success,
                    "readiness": r.readiness,
                    "sections": r.sections,
                    "placeholders": r.placeholders,
                    "pmids": r.pmids,
                    "error": r.error,
                }
                for r in self.results
            ],
        }
        path.write_text(json.dumps(data, indent=2))


class ReviewStore:
    """Persistent storage for review state."""

    def __init__(self, store_dir: str | Path | None = None):
        self.store_dir = Path(store_dir) if store_dir else Path("outputs/reviews")
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def save_review(self, build_id: str, review_data: dict) -> Path:
        path = self.store_dir / f"{build_id}.review.json"
        path.write_text(json.dumps(review_data, indent=2, default=str))
        return path

    def load_review(self, build_id: str) -> Optional[dict]:
        path = self.store_dir / f"{build_id}.review.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list_reviews(self) -> list[dict]:
        reviews = []
        for path in sorted(self.store_dir.glob("*.review.json")):
            try:
                data = json.loads(path.read_text())
                reviews.append({
                    "build_id": data.get("build_id", path.stem.replace(".review", "")),
                    "condition": data.get("condition", ""),
                    "status": data.get("status", ""),
                    "readiness": data.get("readiness", ""),
                    "updated_at": data.get("updated_at", ""),
                })
            except Exception:
                pass
        return reviews

    def find_by_condition(self, condition: str) -> list[dict]:
        return [r for r in self.list_reviews() if r["condition"] == condition]


class BatchRunner:
    """Runs batch generation and review operations."""

    def __init__(self):
        self._service = None
        self._kb = None

    @property
    def service(self):
        if self._service is None:
            from ..generation.service import GenerationService
            self._service = GenerationService(with_visuals=False, with_qa=False)
        return self._service

    @property
    def kb(self):
        if self._kb is None:
            from .base import KnowledgeBase
            self._kb = KnowledgeBase()
            self._kb.load_all()
        return self._kb

    def generate_all_canonical(
        self,
        conditions: list[str] | None = None,
        blueprints: list[str] | None = None,
        tier: str = "fellow",
    ) -> BatchReport:
        """Generate all canonical documents in batch."""
        report = BatchReport(operation=f"generate_all_canonical_{tier}")

        conds = conditions or self.kb.list_conditions()
        bps = blueprints or self.kb.list_blueprints()

        for cond in conds:
            for bp in bps:
                result = self.service.generate_canonical(cond, bp, tier)
                # Read provenance for readiness
                readiness = ""
                sections = 0
                placeholders = 0
                pmids = 0
                if result.output_path:
                    prov_path = Path(result.output_path).with_suffix(".provenance.json")
                    if prov_path.exists():
                        try:
                            prov = json.loads(prov_path.read_text())
                            readiness = prov.get("readiness", "")
                            sections = prov.get("total_sections", 0)
                            placeholders = prov.get("placeholder_sections", 0)
                            pmids = prov.get("total_evidence_pmids", 0)
                        except Exception:
                            pass

                report.results.append(BatchResult(
                    condition=cond,
                    blueprint=bp,
                    tier=tier,
                    success=result.success,
                    output_path=result.output_path or "",
                    readiness=readiness,
                    sections=sections,
                    placeholders=placeholders,
                    pmids=pmids,
                    error=result.error or "",
                ))

        report.finalize()
        return report

    def generate_condition(self, condition: str, tier: str = "fellow") -> BatchReport:
        """Generate all blueprint types for one condition."""
        return self.generate_all_canonical(conditions=[condition], tier=tier)

    def generate_blueprint(self, blueprint: str, tier: str = "fellow") -> BatchReport:
        """Generate one blueprint type for all conditions."""
        return self.generate_all_canonical(blueprints=[blueprint], tier=tier)

    def readiness_report(self, tier: str = "fellow") -> BatchReport:
        """Generate readiness report for all canonical combinations without generating docs."""
        from .assembler import CanonicalDocumentAssembler

        report = BatchReport(operation=f"readiness_report_{tier}")
        assembler = CanonicalDocumentAssembler(self.kb)

        for cond in self.kb.list_conditions():
            for bp_slug in self.kb.list_blueprints():
                try:
                    _, prov = assembler.assemble(cond, bp_slug, tier)
                    report.results.append(BatchResult(
                        condition=cond,
                        blueprint=bp_slug,
                        tier=tier,
                        success=True,
                        readiness=prov.readiness,
                        sections=prov.total_sections,
                        placeholders=prov.placeholder_sections,
                        pmids=prov.total_evidence_pmids,
                    ))
                except Exception as e:
                    report.results.append(BatchResult(
                        condition=cond,
                        blueprint=bp_slug,
                        tier=tier,
                        success=False,
                        error=str(e),
                    ))

        report.finalize()
        return report
