"""DocumentQARunner — orchestrates all validators against a CanonicalDocument."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional

from sozo_generator.schemas.canonical import (
    CanonicalDocument,
    DocumentQAReport,
    QAValidationResult,
)
from .document_completeness_validator import DocumentCompletenessValidator
from .section_length_validator import SectionLengthValidator
from .citation_coverage_validator import CitationCoverageValidator
from .unresolved_placeholder_validator import UnresolvedPlaceholderValidator
from .asset_presence_validator import AssetPresenceValidator
from .table_integrity_validator import TableIntegrityValidator
from .numbering_consistency_validator import NumberingConsistencyValidator
from .figure_integrity_validator import FigureIntegrityValidator
from .cross_reference_validator import CrossReferenceValidator
from .style_consistency_validator import StyleConsistencyValidator
from .base import BaseDocumentValidator

logger = logging.getLogger(__name__)


class DocumentQARunner:
    """Runs all validators against a CanonicalDocument and produces a
    DocumentQAReport.

    Usage::

        runner = DocumentQARunner()
        report = runner.run(document)
        print(runner.to_human_readable(report))
    """

    DEFAULT_VALIDATORS = [
        DocumentCompletenessValidator,
        SectionLengthValidator,
        CitationCoverageValidator,
        UnresolvedPlaceholderValidator,
        AssetPresenceValidator,
        TableIntegrityValidator,
        NumberingConsistencyValidator,
        FigureIntegrityValidator,
        CrossReferenceValidator,
        StyleConsistencyValidator,
    ]

    def __init__(self, validators: Optional[list] = None) -> None:
        """Instantiate validators.

        Parameters
        ----------
        validators:
            Optional list of validator *classes* (not instances).  If None,
            ``DEFAULT_VALIDATORS`` is used.
        """
        self.validators: list[BaseDocumentValidator] = [
            v() for v in (validators or self.DEFAULT_VALIDATORS)
        ]
        logger.info(
            "DocumentQARunner initialised with %d validator(s): %s",
            len(self.validators),
            [v.validator_id for v in self.validators],
        )

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, document: CanonicalDocument) -> DocumentQAReport:
        """Run all validators and return a DocumentQAReport.

        Sets ``document.qa_status`` based on ``report.overall_passed`` and
        stores the report in ``document.qa_report``.

        Parameters
        ----------
        document:
            The CanonicalDocument to validate.

        Returns
        -------
        DocumentQAReport
        """
        logger.info(
            "Running QA for document '%s' (condition: %s, variant: %s)",
            document.document_id,
            document.condition_slug,
            document.variant,
        )

        report = DocumentQAReport(
            document_id=document.document_id,
            condition_slug=document.condition_slug,
            variant=document.variant,
        )

        for validator in self.validators:
            try:
                result = validator.validate(document)
                report.validator_results.append(result)
                logger.debug(
                    "Validator '%s' completed: passed=%s, issues=%d",
                    validator.validator_id,
                    result.passed,
                    len(result.issues),
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Validator '%s' raised an exception: %s",
                    validator.validator_id,
                    exc,
                )
                # Record the failure as a warning so the run still completes
                from sozo_generator.schemas.canonical import QAValidationIssue
                error_issue = QAValidationIssue(
                    validator_id=validator.validator_id,
                    severity="warning",
                    category="validator_exception",
                    message=f"Validator '{validator.validator_id}' raised: {exc}",
                    location="document",
                    context={"exception": str(exc)},
                )
                error_result = QAValidationResult(
                    validator_id=validator.validator_id,
                    document_id=document.document_id,
                    condition_slug=document.condition_slug,
                    passed=True,  # Don't let validator errors block the pipeline
                    issues=[error_issue],
                )
                report.validator_results.append(error_result)

        report.compute_counts()

        # Reflect QA outcome onto the document itself
        if report.overall_passed:
            document.qa_status = "complete"
        else:
            document.qa_status = "failed"
        document.qa_report = report

        logger.info(
            "QA complete for '%s': overall_passed=%s, blocks=%d, "
            "warnings=%d, info=%d",
            document.document_id,
            report.overall_passed,
            report.block_count,
            report.warning_count,
            report.info_count,
        )
        return report

    # ------------------------------------------------------------------
    # Single-validator run
    # ------------------------------------------------------------------

    def run_validator(
        self, validator_id: str, document: CanonicalDocument
    ) -> QAValidationResult:
        """Run a single validator by its validator_id.

        Parameters
        ----------
        validator_id:
            The ``validator_id`` class attribute of the target validator.
        document:
            The CanonicalDocument to validate.

        Returns
        -------
        QAValidationResult

        Raises
        ------
        ValueError
            If no validator with the given ``validator_id`` is registered.
        """
        for validator in self.validators:
            if validator.validator_id == validator_id:
                return validator.validate(document)
        registered = [v.validator_id for v in self.validators]
        raise ValueError(
            f"No validator with id '{validator_id}' is registered. "
            f"Registered validators: {registered}"
        )

    # ------------------------------------------------------------------
    # Report persistence
    # ------------------------------------------------------------------

    def save_report(self, report: DocumentQAReport, output_dir: str) -> str:
        """Save QA report as JSON.

        Output path::

            <output_dir>/outputs/qa/<condition_slug>/<variant>/
            qa_report_<document_id>.json

        Parameters
        ----------
        report:
            The report to serialise.
        output_dir:
            Root directory for output (e.g. project root).

        Returns
        -------
        str
            Absolute path to the written JSON file.
        """
        # Determine the variant from the report — stored in report.variant
        variant = report.variant or "shared"
        directory = os.path.join(
            output_dir,
            "outputs",
            "qa",
            report.condition_slug,
            variant,
        )
        os.makedirs(directory, exist_ok=True)

        filename = f"qa_report_{report.document_id}.json"
        path = os.path.join(directory, filename)

        with open(path, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, indent=2, default=str)

        logger.info("QA report saved to '%s'", path)
        return path

    # ------------------------------------------------------------------
    # Human-readable formatting
    # ------------------------------------------------------------------

    def to_human_readable(self, report: DocumentQAReport) -> str:
        """Format report as a human-readable text summary.

        Parameters
        ----------
        report:
            The report to format.

        Returns
        -------
        str
            Multi-line text summary.
        """
        status = "PASS" if report.overall_passed else "FAIL"
        lines: list[str] = [
            "=" * 70,
            f"QA REPORT — Document: {report.document_id}",
            f"Condition: {report.condition_slug} | Variant: {report.variant}",
            f"Overall: {status}",
            (
                f"Issues: {report.block_count} block(s), "
                f"{report.warning_count} warning(s), "
                f"{report.info_count} info"
            ),
            "=" * 70,
        ]

        # Group all issues by severity across all results
        blocks = []
        warnings = []
        infos = []

        for result in report.validator_results:
            for issue in result.issues:
                entry = (
                    f"  [{result.validator_id}] [{issue.category}] "
                    f"{issue.message}"
                    + (f" (location: {issue.location})" if issue.location else "")
                )
                if issue.severity == "block":
                    blocks.append(entry)
                elif issue.severity == "warning":
                    warnings.append(entry)
                else:
                    infos.append(entry)

        if blocks:
            lines.append("")
            lines.append("BLOCK ISSUES:")
            lines.extend(blocks)

        if warnings:
            lines.append("")
            lines.append("WARNINGS:")
            lines.extend(warnings)

        if infos:
            lines.append("")
            lines.append("INFO:")
            lines.extend(infos)

        if not blocks and not warnings and not infos:
            lines.append("")
            lines.append("  No issues found.")

        lines.append("")
        lines.append(
            f"Validators run: {len(report.validator_results)}  |  "
            f"Report ID: {report.report_id}"
        )
        lines.append("=" * 70)

        return "\n".join(lines)
