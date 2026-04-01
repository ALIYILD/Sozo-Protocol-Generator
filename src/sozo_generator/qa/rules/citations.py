"""
SOZO QA — Citation rule checks.

Validates that condition references are present, well-formed, and free of
placeholder markers.
"""
from __future__ import annotations

import logging
import re
import uuid
from typing import Optional

from ...core.enums import QASeverity
from ...schemas.condition import ConditionSchema
from ...schemas.contracts import QAIssue
from ...schemas.documents import DocumentSpec

logger = logging.getLogger(__name__)

_PMID_PATTERN = re.compile(r"^\d{7,8}$")

_PLACEHOLDER_PATTERNS: list[str] = [
    "[CITATION NEEDED]",
    "[PLACEHOLDER]",
    "TBD",
    "XXX",
]


def _uid() -> str:
    return uuid.uuid4().hex[:12]


class CitationRules:
    """Rule checks for citation quality and completeness."""

    def check(
        self,
        condition: ConditionSchema,
        spec: Optional[DocumentSpec] = None,
    ) -> list[QAIssue]:
        """Run all citation rules against a condition and optional document spec."""
        issues: list[QAIssue] = []
        issues.extend(self._no_references(condition))
        issues.extend(self._missing_pmid(condition))
        issues.extend(self._placeholder(condition, spec))
        issues.extend(self._duplicate_pmid(condition))
        issues.extend(self._min_count(condition))
        logger.debug(
            "CitationRules produced %d issue(s) for '%s'",
            len(issues),
            condition.slug,
        )
        return issues

    # ── Individual rules ────────────────────────────────────────────

    def _no_references(self, condition: ConditionSchema) -> list[QAIssue]:
        if not condition.references:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="citations.no_references",
                    severity=QASeverity.BLOCK,
                    category="citations",
                    location="condition.references",
                    message=(
                        f"Condition '{condition.display_name}' has zero references. "
                        "At least one reference is required."
                    ),
                )
            ]
        return []

    def _missing_pmid(self, condition: ConditionSchema) -> list[QAIssue]:
        issues: list[QAIssue] = []
        for idx, ref in enumerate(condition.references):
            pmid = ref.get("pmid") or ref.get("PMID") or ""
            pmid_str = str(pmid).strip()
            if not _PMID_PATTERN.match(pmid_str):
                issues.append(
                    QAIssue(
                        issue_id=_uid(),
                        rule_id="citations.missing_pmid",
                        severity=QASeverity.WARNING,
                        category="citations",
                        location=f"condition.references[{idx}]",
                        message=(
                            f"Reference at index {idx} lacks a valid PMID "
                            f"(got '{pmid_str}'). Expected 7-8 digit format."
                        ),
                    )
                )
        return issues

    def _placeholder(
        self,
        condition: ConditionSchema,
        spec: Optional[DocumentSpec],
    ) -> list[QAIssue]:
        issues: list[QAIssue] = []
        # Scan condition text fields
        text_fields = {
            "condition.overview": condition.overview,
            "condition.pathophysiology": condition.pathophysiology,
            "condition.evidence_summary": condition.evidence_summary,
        }
        # Also scan document spec sections if provided
        if spec is not None:
            for section in spec.sections:
                text_fields[f"spec.section.{section.section_id}"] = section.content
        for location, text in text_fields.items():
            for marker in _PLACEHOLDER_PATTERNS:
                if marker in text.upper() if marker in ("TBD", "XXX") else marker in text:
                    issues.append(
                        QAIssue(
                            issue_id=_uid(),
                            rule_id="citations.placeholder",
                            severity=QASeverity.BLOCK,
                            category="citations",
                            location=location,
                            message=(
                                f"Placeholder marker '{marker}' found in {location}. "
                                "All placeholders must be resolved before export."
                            ),
                        )
                    )
        return issues

    def _duplicate_pmid(self, condition: ConditionSchema) -> list[QAIssue]:
        seen: dict[str, int] = {}
        for ref in condition.references:
            pmid = str(ref.get("pmid") or ref.get("PMID") or "").strip()
            if _PMID_PATTERN.match(pmid):
                seen[pmid] = seen.get(pmid, 0) + 1

        issues: list[QAIssue] = []
        for pmid, count in seen.items():
            if count > 1:
                issues.append(
                    QAIssue(
                        issue_id=_uid(),
                        rule_id="citations.duplicate_pmid",
                        severity=QASeverity.INFO,
                        category="citations",
                        location="condition.references",
                        message=(
                            f"PMID {pmid} appears {count} times in the reference list."
                        ),
                    )
                )
        return issues

    def _min_count(self, condition: ConditionSchema) -> list[QAIssue]:
        valid_count = sum(
            1
            for ref in condition.references
            if _PMID_PATTERN.match(
                str(ref.get("pmid") or ref.get("PMID") or "").strip()
            )
        )
        if valid_count < 3:
            return [
                QAIssue(
                    issue_id=_uid(),
                    rule_id="citations.min_count",
                    severity=QASeverity.WARNING,
                    category="citations",
                    location="condition.references",
                    message=(
                        f"Only {valid_count} valid PMID(s) found; "
                        "minimum recommended is 3."
                    ),
                )
            ]
        return []
