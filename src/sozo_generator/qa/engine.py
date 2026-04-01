"""
SOZO QA — Main QA engine.

Orchestrates all rule modules to produce a unified :class:`QAReport` for a
condition or document.  Raises :class:`QABlockError` when blocking issues are
detected and no override is in effect.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from ..core.enums import QASeverity
from ..core.exceptions import QABlockError
from ..schemas.condition import ConditionSchema
from ..schemas.contracts import EvidenceBundle, QAIssue, QAReport
from ..schemas.documents import DocumentSpec
from .rules.citations import CitationRules
from .rules.completeness_rules import CompletenessRules
from .rules.language import LanguageRules
from .rules.modality import ModalityRules
from .rules.population import PopulationRules
from .rules.safety import SafetyRules

logger = logging.getLogger(__name__)


def _uid() -> str:
    return uuid.uuid4().hex[:12]


class QAEngine:
    """Central QA engine that runs all registered rule modules.

    Usage::

        engine = QAEngine()
        report = engine.run_document_qa(condition, spec)
        if engine.check_blocking(report):
            raise QABlockError(report.issues)
    """

    def __init__(self) -> None:
        """Register all rule modules."""
        self._citation_rules = CitationRules()
        self._safety_rules = SafetyRules()
        self._modality_rules = ModalityRules()
        self._population_rules = PopulationRules()
        self._language_rules = LanguageRules()
        self._completeness_rules = CompletenessRules()
        logger.info("QAEngine initialised with 6 rule modules")

    # ── Public API ──────────────────────────────────────────────────

    def run_document_qa(
        self,
        condition: ConditionSchema,
        spec: DocumentSpec,
        bundles: Optional[list[EvidenceBundle]] = None,
    ) -> QAReport:
        """Run full QA for a single document within a condition.

        Parameters
        ----------
        condition:
            The structured condition data.
        spec:
            The document specification being validated.
        bundles:
            Optional evidence bundles for deeper evidence-level checks.

        Returns
        -------
        QAReport
            Aggregated report with all issues and severity counts.
        """
        logger.info(
            "Running document QA for '%s' — %s/%s",
            condition.slug,
            spec.document_type.value,
            spec.tier.value,
        )

        issues: list[QAIssue] = []

        # Condition-level rules
        issues.extend(self._completeness_rules.check(condition))
        issues.extend(self._safety_rules.check(condition))
        issues.extend(self._modality_rules.check(condition))
        issues.extend(self._population_rules.check(condition))

        # Rules that accept both condition and spec
        issues.extend(self._citation_rules.check(condition, spec=spec))
        issues.extend(self._language_rules.check(condition, spec=spec))

        report = QAReport(
            report_id=f"qa-{_uid()}",
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            document_type=spec.document_type.value,
            tier=spec.tier.value,
            issues=issues,
        )
        report.compute_counts()

        logger.info(
            "Document QA complete for '%s': %d BLOCK, %d WARNING, %d INFO — passed=%s",
            condition.slug,
            report.block_count,
            report.warning_count,
            report.info_count,
            report.passed,
        )
        return report

    def run_condition_qa(
        self,
        condition: ConditionSchema,
        specs: Optional[list[DocumentSpec]] = None,
    ) -> QAReport:
        """Run QA across all documents for a condition.

        Parameters
        ----------
        condition:
            The structured condition data.
        specs:
            Optional list of document specs.  If provided, document-aware
            rules (citations, language) are run per-spec and issues merged.

        Returns
        -------
        QAReport
            Aggregated report covering the whole condition.
        """
        logger.info("Running condition-level QA for '%s'", condition.slug)

        issues: list[QAIssue] = []

        # Condition-only rules (run once)
        issues.extend(self._completeness_rules.check(condition))
        issues.extend(self._safety_rules.check(condition))
        issues.extend(self._modality_rules.check(condition))
        issues.extend(self._population_rules.check(condition))

        # Document-aware rules
        if specs:
            for spec in specs:
                issues.extend(self._citation_rules.check(condition, spec=spec))
                issues.extend(self._language_rules.check(condition, spec=spec))
        else:
            # Run without spec context
            issues.extend(self._citation_rules.check(condition))
            issues.extend(self._language_rules.check(condition))

        report = QAReport(
            report_id=f"qa-{_uid()}",
            condition_slug=condition.slug,
            condition_name=condition.display_name,
            issues=issues,
        )
        report.compute_counts()

        logger.info(
            "Condition QA complete for '%s': %d BLOCK, %d WARNING, %d INFO — passed=%s",
            condition.slug,
            report.block_count,
            report.warning_count,
            report.info_count,
            report.passed,
        )
        return report

    def check_blocking(self, report: QAReport) -> bool:
        """Return ``True`` if the report contains any BLOCK-severity issues."""
        return report.block_count > 0
