"""
SOZO QA — Modality rule checks.

Validates protocol definitions, stimulation target declarations, and
modality-specific flags (e.g. TPS off-label status).
"""
from __future__ import annotations

import logging
import uuid

from ...core.enums import Modality, QASeverity
from ...schemas.condition import ConditionSchema
from ...schemas.contracts import QAIssue

logger = logging.getLogger(__name__)

# TPS is considered on-label only for Alzheimer's disease.
_TPS_ON_LABEL_SLUGS: frozenset[str] = frozenset({"alzheimers", "alzheimers_disease"})


def _uid() -> str:
    return uuid.uuid4().hex[:12]


class ModalityRules:
    """Rule checks for modality and protocol correctness."""

    def check(self, condition: ConditionSchema) -> list[QAIssue]:
        """Run all modality rules against a condition."""
        issues: list[QAIssue] = []
        issues.extend(self._no_protocols(condition))
        issues.extend(self._tps_not_flagged_off_label(condition))
        issues.extend(self._no_stimulation_targets(condition))
        issues.extend(self._protocol_missing_parameters(condition))
        logger.debug(
            "ModalityRules produced %d issue(s) for '%s'",
            len(issues),
            condition.slug,
        )
        return issues

    # ── Individual rules ────────────────────────────────────────────

    def _no_protocols(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.protocols:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="modality.no_protocols",
                    severity=QASeverity.BLOCK,
                    category="modality",
                    location="condition.protocols",
                    message=(
                        f"Condition '{condition.display_name}' has no protocols defined. "
                        "At least one stimulation protocol is required."
                    ),
                )
            ]
        return []

    def _tps_not_flagged_off_label(self, condition: ConditionSchema) -> list[QAIssue]:
        """TPS is off-label for everything except Alzheimer's."""
        if condition.slug in _TPS_ON_LABEL_SLUGS:
            return []

        issues: list[QAIssue] = []
        for idx, target in enumerate(condition.stimulation_targets):
            if target.modality == Modality.TPS and not target.off_label:
                issues.append(
                    QAIssue(
                        issue_id=_uid(),
                        rule_id="modality.tps_not_flagged_off_label",
                        severity=QASeverity.WARNING,
                        category="modality",
                        location=f"condition.stimulation_targets[{idx}]",
                        message=(
                            f"TPS target '{target.target_region}' is not flagged as "
                            "off-label. TPS is off-label for all conditions except "
                            "Alzheimer's disease."
                        ),
                    )
                )
        return issues

    def _no_stimulation_targets(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.stimulation_targets:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="modality.no_stimulation_targets",
                    severity=QASeverity.WARNING,
                    category="modality",
                    location="condition.stimulation_targets",
                    message=(
                        f"Condition '{condition.display_name}' has no stimulation "
                        "targets defined."
                    ),
                )
            ]
        return []

    def _protocol_missing_parameters(self, condition: ConditionSchema) -> list[QAIssue]:
        issues: list[QAIssue] = []
        for idx, protocol in enumerate(condition.protocols):
            if not protocol.parameters:
                issues.append(
                    QAIssue(
                        issue_id=_uid(),
                        rule_id="modality.protocol_missing_parameters",
                        severity=QASeverity.WARNING,
                        category="modality",
                        location=f"condition.protocols[{idx}]",
                        message=(
                            f"Protocol '{protocol.label}' ({protocol.protocol_id}) "
                            "has an empty parameters dict. Stimulation parameters "
                            "(intensity, duration, etc.) should be specified."
                        ),
                    )
                )
        return issues
