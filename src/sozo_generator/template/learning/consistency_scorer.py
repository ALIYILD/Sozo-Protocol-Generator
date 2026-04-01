"""
Consistency scorer — compares a newly generated document against the
master template profile and existing document family to detect drift.

Produces a ConsistencyReport with scores and specific warnings.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from .document_ingester import DocumentFingerprint
from .pattern_extractor import MasterTemplateProfile, DocumentTypePattern

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyWarning:
    """A specific consistency issue found."""
    code: str = ""  # e.g., "section_missing", "table_mismatch"
    severity: str = "warning"  # info, warning, error
    message: str = ""
    expected: str = ""
    actual: str = ""


@dataclass
class ConsistencyReport:
    """Result of comparing a document against the master profile."""
    file_name: str = ""
    condition_slug: str = ""
    doc_type: str = ""
    tier: str = ""
    # Scores (0.0 to 1.0)
    structure_score: float = 0.0  # section ordering similarity
    formatting_score: float = 0.0  # font/style consistency
    table_score: float = 0.0  # table layout match
    completeness_score: float = 0.0  # all expected sections present
    overall_score: float = 0.0
    # Warnings
    warnings: list[ConsistencyWarning] = field(default_factory=list)
    # Summary
    passed: bool = False  # overall_score >= threshold

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


class ConsistencyScorer:
    """Scores how consistent a document is with the learned master template."""

    def __init__(self, profile: MasterTemplateProfile, threshold: float = 0.7):
        self.profile = profile
        self.threshold = threshold

    def score_document(self, fingerprint: DocumentFingerprint) -> ConsistencyReport:
        """Score a single document's consistency with the master template."""
        report = ConsistencyReport(
            file_name=fingerprint.file_name,
            condition_slug=fingerprint.condition_slug,
            doc_type=fingerprint.doc_type,
            tier=fingerprint.tier,
        )

        # Get the expected pattern for this doc type
        expected = self.profile.doc_type_patterns.get(fingerprint.doc_type)
        if not expected:
            report.warnings.append(ConsistencyWarning(
                code="unknown_doc_type",
                severity="warning",
                message=f"No pattern learned for doc type '{fingerprint.doc_type}'",
            ))
            report.overall_score = 0.5
            return report

        # ── Structure score (section ordering) ──
        report.structure_score = self._score_structure(fingerprint, expected, report)

        # ── Formatting score ──
        report.formatting_score = self._score_formatting(fingerprint, report)

        # ── Table score ──
        report.table_score = self._score_tables(fingerprint, expected, report)

        # ── Completeness score ──
        report.completeness_score = self._score_completeness(fingerprint, expected, report)

        # ── Overall ──
        report.overall_score = (
            report.structure_score * 0.3
            + report.formatting_score * 0.2
            + report.table_score * 0.2
            + report.completeness_score * 0.3
        )
        report.passed = report.overall_score >= self.threshold

        if not report.passed:
            logger.warning(
                "Document %s failed consistency check: %.2f (threshold: %.2f)",
                fingerprint.file_name,
                report.overall_score,
                self.threshold,
            )

        return report

    def score_batch(self, fingerprints: list[DocumentFingerprint]) -> list[ConsistencyReport]:
        """Score multiple documents."""
        return [self.score_document(fp) for fp in fingerprints]

    def _score_structure(
        self,
        fp: DocumentFingerprint,
        expected: DocumentTypePattern,
        report: ConsistencyReport,
    ) -> float:
        """Score how well section ordering matches the expected pattern."""
        actual_ids = [s.section_id for s in fp.sections]
        expected_ids = expected.typical_section_order

        if not expected_ids:
            return 1.0

        # Count sections in expected order that appear in actual
        matched = 0
        actual_set = set(actual_ids)
        for eid in expected_ids:
            if eid in actual_set:
                matched += 1

        score = matched / len(expected_ids) if expected_ids else 1.0

        # Check for unexpected sections
        expected_set = set(expected_ids)
        unexpected = [s for s in actual_ids if s not in expected_set]
        if unexpected:
            report.warnings.append(ConsistencyWarning(
                code="unexpected_sections",
                severity="info",
                message=f"{len(unexpected)} section(s) not in expected pattern",
                expected=str(expected_ids[:5]),
                actual=str(unexpected[:5]),
            ))

        return score

    def _score_formatting(
        self,
        fp: DocumentFingerprint,
        report: ConsistencyReport,
    ) -> float:
        """Score formatting consistency with master template."""
        score = 1.0

        # Check primary font
        if self.profile.primary_font not in fp.fonts_used:
            score -= 0.3
            report.warnings.append(ConsistencyWarning(
                code="font_mismatch",
                severity="warning",
                message=f"Expected font '{self.profile.primary_font}' not found",
                expected=self.profile.primary_font,
                actual=str(fp.fonts_used[:3]),
            ))

        # Check expected styles
        if "Normal" not in fp.styles_used:
            score -= 0.1

        return max(0.0, score)

    def _score_tables(
        self,
        fp: DocumentFingerprint,
        expected: DocumentTypePattern,
        report: ConsistencyReport,
    ) -> float:
        """Score table layout consistency."""
        expected_count = expected.typical_table_count
        actual_count = fp.total_tables

        if expected_count == 0:
            return 1.0 if actual_count == 0 else 0.8

        # Count match ratio
        ratio = min(actual_count, expected_count) / max(actual_count, expected_count)

        if abs(actual_count - expected_count) > 2:
            report.warnings.append(ConsistencyWarning(
                code="table_count_drift",
                severity="warning",
                message=f"Expected ~{expected_count} tables, found {actual_count}",
                expected=str(expected_count),
                actual=str(actual_count),
            ))

        # Check if table headers match expected patterns
        if expected.table_patterns and fp.tables:
            expected_headers = set()
            for tp in expected.table_patterns:
                expected_headers.add(tuple(tp.headers))

            matched_tables = 0
            for tf in fp.tables:
                if tuple(tf.headers) in expected_headers:
                    matched_tables += 1

            if fp.tables:
                header_score = matched_tables / len(fp.tables)
                ratio = (ratio + header_score) / 2

        return ratio

    def _score_completeness(
        self,
        fp: DocumentFingerprint,
        expected: DocumentTypePattern,
        report: ConsistencyReport,
    ) -> float:
        """Score whether all expected sections are present."""
        expected_ids = set(expected.typical_section_order)
        actual_ids = set(s.section_id for s in fp.sections)

        if not expected_ids:
            return 1.0

        missing = expected_ids - actual_ids
        if missing:
            report.warnings.append(ConsistencyWarning(
                code="missing_sections",
                severity="warning",
                message=f"{len(missing)} expected section(s) missing",
                expected=str(sorted(missing)[:5]),
                actual=str(sorted(actual_ids)[:5]),
            ))

        present = expected_ids & actual_ids
        return len(present) / len(expected_ids)
