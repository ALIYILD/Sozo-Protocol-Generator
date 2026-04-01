"""
SOZO QA — Completeness rule checks (condition-level).

Validates that essential fields on the ConditionSchema are populated.  Named
``completeness_rules`` to avoid a clash with the existing file-level
``completeness.py`` checker in the parent package.
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


class CompletenessRules:
    """Rule checks for condition data completeness."""

    def check(self, condition: ConditionSchema) -> list[QAIssue]:
        """Run all completeness rules against a condition."""
        issues: list[QAIssue] = []
        issues.extend(self._empty_overview(condition))
        issues.extend(self._empty_pathophysiology(condition))
        issues.extend(self._no_networks(condition))
        issues.extend(self._no_evidence_summary(condition))
        issues.extend(self._no_brain_regions(condition))
        logger.debug(
            "CompletenessRules produced %d issue(s) for '%s'",
            len(issues),
            condition.slug,
        )
        return issues

    # ── Individual rules ────────────────────────────────────────────

    def _empty_overview(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.overview.strip():
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="completeness.empty_overview",
                    severity=QASeverity.BLOCK,
                    category="completeness",
                    location="condition.overview",
                    message=(
                        f"Condition '{condition.display_name}' has an empty overview. "
                        "A clinical overview is required for document generation."
                    ),
                )
            ]
        return []

    def _empty_pathophysiology(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.pathophysiology.strip():
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="completeness.empty_pathophysiology",
                    severity=QASeverity.WARNING,
                    category="completeness",
                    location="condition.pathophysiology",
                    message=(
                        f"Condition '{condition.display_name}' has an empty "
                        "pathophysiology section."
                    ),
                )
            ]
        return []

    def _no_networks(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.network_profiles:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="completeness.no_networks",
                    severity=QASeverity.WARNING,
                    category="completeness",
                    location="condition.network_profiles",
                    message=(
                        f"Condition '{condition.display_name}' has no network profiles "
                        "defined. Network involvement is expected for neuromodulation "
                        "protocols."
                    ),
                )
            ]
        return []

    def _no_evidence_summary(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.evidence_summary.strip():
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="completeness.no_evidence_summary",
                    severity=QASeverity.WARNING,
                    category="completeness",
                    location="condition.evidence_summary",
                    message=(
                        f"Condition '{condition.display_name}' has no evidence summary."
                    ),
                )
            ]
        return []

    def _no_brain_regions(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.key_brain_regions:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="completeness.no_brain_regions",
                    severity=QASeverity.INFO,
                    category="completeness",
                    location="condition.key_brain_regions",
                    message=(
                        f"Condition '{condition.display_name}' has no key brain "
                        "regions listed."
                    ),
                )
            ]
        return []
