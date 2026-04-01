"""
SOZO QA — Safety rule checks.

Validates that contraindications, safety notes, consent flags, and exclusion
criteria are present and consistent.
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


class SafetyRules:
    """Rule checks for clinical safety completeness."""

    def check(self, condition: ConditionSchema) -> list[QAIssue]:
        """Run all safety rules against a condition."""
        issues: list[QAIssue] = []
        issues.extend(self._no_contraindications(condition))
        issues.extend(self._no_safety_notes(condition))
        issues.extend(self._off_label_missing_consent(condition))
        issues.extend(self._missing_exclusion_criteria(condition))
        logger.debug(
            "SafetyRules produced %d issue(s) for '%s'",
            len(issues),
            condition.slug,
        )
        return issues

    # ── Individual rules ────────────────────────────────────────────

    def _no_contraindications(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.contraindications:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="safety.no_contraindications",
                    severity=QASeverity.BLOCK,
                    category="safety",
                    location="condition.contraindications",
                    message=(
                        f"Condition '{condition.display_name}' has no contraindications "
                        "listed. Every condition must declare contraindications."
                    ),
                )
            ]
        return []

    def _no_safety_notes(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.safety_notes:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="safety.no_safety_notes",
                    severity=QASeverity.BLOCK,
                    category="safety",
                    location="condition.safety_notes",
                    message=(
                        f"Condition '{condition.display_name}' has no safety notes. "
                        "Safety notes are mandatory for all conditions."
                    ),
                )
            ]
        return []

    def _off_label_missing_consent(self, condition: ConditionSchema) -> list[QAIssue]:
        issues: list[QAIssue] = []
        for idx, target in enumerate(condition.stimulation_targets):
            if target.off_label and not target.consent_required:
                issues.append(
                    QAIssue(
                        issue_id=_uid(),
                        rule_id="safety.off_label_missing_consent",
                        severity=QASeverity.WARNING,
                        category="safety",
                        location=f"condition.stimulation_targets[{idx}]",
                        message=(
                            f"Stimulation target '{target.target_region}' "
                            f"({target.modality.value}) is marked off-label but "
                            "consent_required is False. Off-label use requires "
                            "explicit informed consent."
                        ),
                    )
                )
        return issues

    def _missing_exclusion_criteria(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.exclusion_criteria:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="safety.missing_exclusion_criteria",
                    severity=QASeverity.WARNING,
                    category="safety",
                    location="condition.exclusion_criteria",
                    message=(
                        f"Condition '{condition.display_name}' has no exclusion criteria. "
                        "Exclusion criteria should be defined for clinical protocols."
                    ),
                )
            ]
        return []
