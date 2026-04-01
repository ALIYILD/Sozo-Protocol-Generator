"""
Batch runner — generates documents for one or all conditions with full
manifest, QA, evidence snapshot, and figure tracking.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..conditions.registry import get_registry
from ..core.enums import DocumentType, Tier, ReviewStatus
from ..core.exceptions import QABlockError
from ..core.settings import get_settings
from ..docx.exporter import DocumentExporter
from ..schemas.condition import ConditionSchema
from ..schemas.contracts import (
    BatchBuildReport,
    BatchConditionResult,
    BuildManifest,
    QAReport,
)
from .versioning import ManifestWriter, create_build_id

logger = logging.getLogger(__name__)


class BatchRunner:
    """Orchestrates document generation with QA, manifests, and snapshots."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        manifests_dir: Optional[Path] = None,
        with_visuals: bool = True,
        enable_qa: bool = True,
        qa_blocking: bool = False,
    ):
        settings = get_settings()
        self.output_dir = Path(output_dir or settings.output_dir / "documents")
        self.manifests_dir = Path(manifests_dir or settings.manifests_dir)
        self.with_visuals = with_visuals
        self.enable_qa = enable_qa
        self.qa_blocking = qa_blocking
        self._manifest_writer = ManifestWriter(self.manifests_dir)

    def build_condition(
        self,
        condition_slug: str,
        tiers: Optional[list[Tier]] = None,
        doc_types: Optional[list[DocumentType]] = None,
        override_qa_block: bool = False,
    ) -> tuple[BuildManifest, Optional[QAReport]]:
        """
        Build all documents for one condition.

        Returns (BuildManifest, QAReport or None).
        Raises QABlockError if blocking issues found and not overridden.
        """
        registry = get_registry()
        condition = registry.get(condition_slug)

        build_id = create_build_id(condition_slug)
        logger.info("Starting build %s for %s", build_id, condition.display_name)

        # Export documents
        exporter = DocumentExporter(
            output_dir=str(self.output_dir),
            with_visuals=self.with_visuals,
        )
        tiers = tiers or [Tier.FELLOW, Tier.PARTNERS]
        doc_types = doc_types or list(DocumentType)

        outputs = exporter.export_condition(
            condition=condition,
            tiers=tiers,
            doc_types=doc_types,
            with_visuals=self.with_visuals,
        )

        # Run QA if enabled
        qa_report: Optional[QAReport] = None
        if self.enable_qa:
            qa_report = self._run_qa(condition, build_id)

            if self.qa_blocking and qa_report and qa_report.block_count > 0:
                if not override_qa_block:
                    blocking = [
                        i for i in qa_report.issues if i.severity.value == "block"
                    ]
                    raise QABlockError(
                        issues=blocking,
                        message=(
                            f"Build {build_id} blocked: {len(blocking)} BLOCK issue(s). "
                            f"Use --override-qa to force export."
                        ),
                    )

        # Create manifest
        manifest = self._manifest_writer.create_manifest(
            build_id=build_id,
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            document_outputs=outputs,
            qa_summary=qa_report,
        )
        self._manifest_writer.save_manifest(manifest)

        logger.info(
            "Build %s complete: %d docs, %d passed, %d blocked",
            build_id,
            manifest.total_documents,
            manifest.total_passed,
            manifest.total_blocked,
        )
        return manifest, qa_report

    def build_all(
        self,
        condition_slugs: Optional[list[str]] = None,
        tiers: Optional[list[Tier]] = None,
        doc_types: Optional[list[DocumentType]] = None,
        skip_existing: bool = False,
        override_qa_block: bool = False,
    ) -> BatchBuildReport:
        """
        Build documents for multiple conditions.

        Returns a BatchBuildReport with per-condition results.
        """
        registry = get_registry()
        slugs = condition_slugs or registry.list_slugs()

        batch_id = f"batch-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        report = BatchBuildReport(
            batch_id=batch_id,
            total_conditions=len(slugs),
        )

        logger.info("Batch %s: building %d conditions", batch_id, len(slugs))

        for slug in slugs:
            result = BatchConditionResult(condition_slug=slug)

            if skip_existing:
                condition_out = self.output_dir / slug.replace("_", " ").title().replace(" ", "_")
                if condition_out.exists() and any(condition_out.rglob("*.docx")):
                    result.success = True
                    result.documents_generated = len(list(condition_out.rglob("*.docx")))
                    report.results.append(result)
                    continue

            try:
                manifest, qa_report = self.build_condition(
                    condition_slug=slug,
                    tiers=tiers,
                    doc_types=doc_types,
                    override_qa_block=override_qa_block,
                )
                result.success = True
                result.documents_generated = manifest.total_documents
                result.documents_blocked = manifest.total_blocked
                result.build_manifest_path = str(
                    self.manifests_dir / f"{manifest.build_id}.json"
                )
            except QABlockError as e:
                result.success = False
                result.documents_blocked = len(e.issues)
                result.error = str(e)
                logger.warning("Build blocked for %s: %s", slug, e)
            except Exception as e:
                result.success = False
                result.error = str(e)
                logger.error("Build failed for %s: %s", slug, e, exc_info=True)

            report.results.append(result)

        report.finalize()

        # Save batch report
        report_path = self.manifests_dir / f"{batch_id}.json"
        report_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        logger.info(
            "Batch %s complete: %d/%d succeeded",
            batch_id,
            report.successful_conditions,
            report.total_conditions,
        )
        return report

    def _run_qa(self, condition: ConditionSchema, build_id: str) -> QAReport:
        """Run the QA engine on a condition."""
        try:
            from ..qa.engine import QAEngine

            engine = QAEngine()
            report = engine.run_condition_qa(condition)
            report.report_id = f"qa-{build_id}"
            return report
        except Exception as e:
            logger.warning("QA engine failed for %s: %s", condition.slug, e)
            return QAReport(
                report_id=f"qa-{build_id}",
                condition_slug=condition.slug,
                condition_name=condition.display_name,
                passed=False,
            )
