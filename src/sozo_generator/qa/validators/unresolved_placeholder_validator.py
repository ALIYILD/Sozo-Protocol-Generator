"""Validator 4 — Unresolved placeholders."""
from __future__ import annotations

import re
import time

from sozo_generator.schemas.canonical import (
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator

# Matches [ALL_CAPS_WITH_UNDERSCORES] — typical placeholder pattern
_UPPER_BRACKET_RE = re.compile(r"\[[A-Z][A-Z0-9_\s]{0,30}\]")


class UnresolvedPlaceholderValidator(BaseDocumentValidator):
    """Checks for unresolved placeholder blocks.

    Rules:
    - Any block where placeholder_resolved == False: WARNING
    - Any block where content contains '[' and ']' with only uppercase inside
      (e.g. "[PLACEHOLDER]", "[TODO]", "[MISSING]"): WARNING
    - Any block where block_type == "text" and content starts/ends with
      brackets: WARNING
    - Count total unresolved: if > 5: BLOCK
    """

    validator_id: str = "unresolved_placeholder"
    description: str = (
        "Checks for unresolved placeholder blocks and bracket-style "
        "placeholder tokens in text content."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        unresolved_count = 0
        unresolved_count += self._check_sections(document.sections, issues)

        # If total unresolved exceeds threshold, add a blocking issue
        if unresolved_count > 5:
            issues.append(
                self._issue(
                    severity="block",
                    category="too_many_unresolved_placeholders",
                    message=(
                        f"Document has {unresolved_count} unresolved "
                        "placeholder indicators (threshold: 5)."
                    ),
                    location="document",
                    context={"unresolved_count": unresolved_count},
                )
            )

        duration = time.monotonic() - start
        return self._result(
            document_id=document.document_id,
            condition_slug=document.condition_slug,
            issues=issues,
            duration_seconds=duration,
        )

    def _check_sections(
        self,
        sections: list[CanonicalSection],
        issues: list[QAValidationIssue],
    ) -> int:
        """Return the number of unresolved placeholder incidents found."""
        count = 0
        for section in sections:
            for block in section.blocks:
                count += self._check_block(block, section.section_id, issues)
            if section.subsections:
                count += self._check_sections(section.subsections, issues)
        return count

    def _check_block(
        self,
        block: CanonicalBlock,
        section_id: str,
        issues: list[QAValidationIssue],
    ) -> int:
        """Check a single block. Returns number of placeholder incidents."""
        count = 0
        location = f"{section_id}/{block.block_id}"

        # Rule: placeholder_resolved == False
        if not block.placeholder_resolved:
            issues.append(
                self._issue(
                    severity="warning",
                    category="unresolved_placeholder_flag",
                    message=(
                        f"Block '{block.block_id}' (type: {block.block_type}) "
                        "has placeholder_resolved=False."
                    ),
                    location=location,
                    context={
                        "block_id": block.block_id,
                        "block_type": block.block_type,
                    },
                )
            )
            count += 1

        content = block.content or ""

        # Rule: bracket-uppercase placeholder tokens
        matches = _UPPER_BRACKET_RE.findall(content)
        if matches:
            issues.append(
                self._issue(
                    severity="warning",
                    category="bracket_placeholder_token",
                    message=(
                        f"Block '{block.block_id}' contains unresolved "
                        f"placeholder token(s): {matches!r}."
                    ),
                    location=location,
                    context={
                        "block_id": block.block_id,
                        "tokens": matches,
                    },
                )
            )
            count += 1

        # Rule: text block whose content starts or ends with brackets
        if block.block_type == "text" and content:
            stripped = content.strip()
            if stripped.startswith("[") or stripped.endswith("]"):
                issues.append(
                    self._issue(
                        severity="warning",
                        category="bracket_wrapped_content",
                        message=(
                            f"Text block '{block.block_id}' content starts or "
                            "ends with square brackets, suggesting unresolved "
                            "placeholder."
                        ),
                        location=location,
                        context={
                            "block_id": block.block_id,
                            "content_preview": stripped[:120],
                        },
                    )
                )
                count += 1

        return count
