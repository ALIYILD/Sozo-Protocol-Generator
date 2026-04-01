"""
SOZO QA — Population rule checks.

Validates that inclusion criteria, phenotype subtypes, and assessment tools
are defined for the condition.
"""
from __future__ import annotations

import logging
import uuid

from ...core.enums import QASeverity
from ...schemas.condition import ConditionSchema
from ...schemas.contracts import QAIssue

logger = logging.getLogger(__name__)


def _uid() -> str:
    return uuid.uuid4().hex[:12]


class PopulationRules:
    """Rule checks for population and assessment completeness."""

    def check(self, condition: ConditionSchema) -> list[QAIssue]:
        """Run all population rules against a condition."""
        issues: list[QAIssue] = []
        issues.extend(self._no_inclusion_criteria(condition))
        issues.extend(self._no_phenotypes(condition))
        issues.extend(self._no_assessment_tools(condition))
        logger.debug(
            "PopulationRules produced %d issue(s) for '%s'",
            len(issues),
            condition.slug,
        )
        return issues

    # ── Individual rules ────────────────────────────────────────────

    def _no_inclusion_criteria(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.inclusion_criteria:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="population.no_inclusion_criteria",
                    severity=QASeverity.WARNING,
                    category="population",
                    location="condition.inclusion_criteria",
                    message=(
                        f"Condition '{condition.display_name}' has no inclusion criteria. "
                        "Inclusion criteria are recommended for clinical protocols."
                    ),
                )
            ]
        return []

    def _no_phenotypes(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.phenotypes:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="population.no_phenotypes",
                    severity=QASeverity.WARNING,
                    category="population",
                    location="condition.phenotypes",
                    message=(
                        f"Condition '{condition.display_name}' has no clinical "
                        "phenotype subtypes defined."
                    ),
                )
            ]
        return []

    def _no_assessment_tools(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.assessment_tools:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="population.no_assessment_tools",
                    severity=QASeverity.WARNING,
                    category="population",
                    location="condition.assessment_tools",
                    message=(
                        f"Condition '{condition.display_name}' has no assessment tools. "
                        "Validated outcome measures should be specified."
                    ),
                )
            ]
        return []
