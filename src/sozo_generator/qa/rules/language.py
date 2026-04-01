"""
SOZO QA — Language rule checks.

Detects overly certain clinical language, missing confidence labels, and
residual placeholder text in condition data and document specs.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Optional

from ...core.enums import QASeverity
from ...schemas.condition import ConditionSchema
from ...schemas.contracts import QAIssue
from ...schemas.documents import DocumentSpec, SectionContent

logger = logging.getLogger(__name__)

_EXCESSIVE_CERTAINTY_TERMS: list[str] = [
    "proven",
    "cures",
    "guaranteed",
    "definitively",
    "100%",
]

_PLACEHOLDER_MARKERS: list[str] = [
    "[PLACEHOLDER]",
    "[TODO]",
    "[FILL IN]",
    "XXX",
]

# Pre-compile a case-insensitive pattern for certainty terms
_CERTAINTY_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(t) for t in _EXCESSIVE_CERTAINTY_TERMS) + r")\b",
    re.IGNORECASE,
)


def _uid() -> str:
    return uuid.uuid4().hex[:12]


class LanguageRules:
    """Rule checks for clinical language quality."""

    def check(
        self,
        condition: ConditionSchema,
        spec: Optional[DocumentSpec] = None,
    ) -> list[QAIssue]:
        """Run all language rules against a condition and optional document spec."""
        issues: list[QAIssue] = []
        issues.extend(self._excessive_certainty(condition))
        issues.extend(self._missing_confidence_label(spec))
        issues.extend(self._placeholder_text(condition, spec))
        logger.debug(
            "LanguageRules produced %d issue(s) for '%s'",
            len(issues),
            condition.slug,
        )
        return issues

    # ── Individual rules ────────────────────────────────────────────

    def _excessive_certainty(self, condition: ConditionSchema) -> list[QAIssue]:
        """Check overview and pathophysiology for absolute-certainty language."""
        issues: list[QAIssue] = []
        fields = {
            "condition.overview": condition.overview,
            "condition.pathophysiology": condition.pathophysiology,
        }
        for location, text in fields.items():
            if not text:
                continue
            matches = _CERTAINTY_PATTERN.findall(text)
            for term in matches:
                issues.append(
                    QAIssue(
                        issue_id=_uid(),
                        rule_id="language.excessive_certainty",
                        severity=QASeverity.WARNING,
                        category="language",
                        location=location,
                        message=(
                            f"Excessive certainty term '{term}' found in "
                            f"{location}. Clinical content should use hedged "
                            "language (e.g. 'may', 'evidence suggests')."
                        ),
                    )
                )
        return issues

    def _missing_confidence_label(
        self, spec: Optional[DocumentSpec]
    ) -> list[QAIssue]:
        """Check that sections with claims have a confidence label set."""
        if spec is None:
            return []

        issues: list[QAIssue] = []
        for section in spec.sections:
            issues.extend(self._check_section_confidence(section))
        return issues

    def _check_section_confidence(self, section: SectionContent) -> list[QAIssue]:
        """Recursively check a section and its subsections."""
        issues: list[QAIssue] = []
        if section.claims and section.confidence_label is None:
            issues.append(
                QAIssue(
                    issue_id=_uid(),
                    rule_id="language.missing_confidence_label",
                    severity=QASeverity.INFO,
                    category="language",
                    location=f"spec.section.{section.section_id}",
                    message=(
                        f"Section '{section.title}' has {len(section.claims)} "
                        "claim(s) but no confidence_label assigned."
                    ),
                )
            )
        for subsection in section.subsections:
            issues.extend(self._check_section_confidence(subsection))
        return issues

    def _placeholder_text(
        self,
        condition: ConditionSchema,
        spec: Optional[DocumentSpec],
    ) -> list[QAIssue]:
        """Detect residual placeholder markers in condition and spec content."""
        issues: list[QAIssue] = []

        # Scan condition text fields
        text_fields: dict[str, str] = {
            "condition.overview": condition.overview,
            "condition.pathophysiology": condition.pathophysiology,
            "condition.evidence_summary": condition.evidence_summary,
        }

        # Scan document spec sections
        if spec is not None:
            for section in spec.sections:
                text_fields[f"spec.section.{section.section_id}"] = section.content

        for location, text in text_fields.items():
            if not text:
                continue
            text_upper = text.upper()
            for marker in _PLACEHOLDER_MARKERS:
                if marker.upper() in text_upper:
                    issues.append(
                        QAIssue(
                            issue_id=_uid(),
                            rule_id="language.placeholder_text",
                            severity=QASeverity.BLOCK,
                            category="language",
                            location=location,
                            message=(
                                f"Placeholder '{marker}' detected in {location}. "
                                "All placeholder text must be resolved before export."
                            ),
                        )
                    )
        return issues
