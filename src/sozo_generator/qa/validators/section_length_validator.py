"""Validator 2 — Section length."""
from __future__ import annotations

import time

from sozo_generator.schemas.canonical import (
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator


class SectionLengthValidator(BaseDocumentValidator):
    """Checks that sections meet length requirements.

    Rules:
    - Any body section with word_count == 0: BLOCK ("empty_section")
    - Any body section with word_count < 50: WARNING ("very_short_section")
    - Any body section where word_count < (spec target * 0.3) if target
      available: WARNING
    - Any body section with word_count > 5000: WARNING ("very_long_section")

    word_count is stored in CanonicalSection.word_count.
    If 0, recompute via section.compute_word_count().
    """

    validator_id: str = "section_length"
    description: str = (
        "Checks that body sections meet minimum and maximum length requirements."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        self._check_sections(document.sections, issues)

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
    ) -> None:
        for section in sections:
            if section.section_type == "body":
                # Recompute if stored count is 0
                wc = section.word_count
                if wc == 0:
                    wc = section.compute_word_count()

                location = section.section_id

                if wc == 0:
                    issues.append(
                        self._issue(
                            severity="block",
                            category="empty_section",
                            message=(
                                f"Body section '{section.title}' has zero words."
                            ),
                            location=location,
                            context={"section_title": section.title, "word_count": 0},
                        )
                    )
                elif wc < 50:
                    issues.append(
                        self._issue(
                            severity="warning",
                            category="very_short_section",
                            message=(
                                f"Body section '{section.title}' has only {wc} "
                                "word(s) (minimum recommended: 50)."
                            ),
                            location=location,
                            context={"section_title": section.title, "word_count": wc},
                        )
                    )

                # Target-relative check: look for target_word_count in
                # generation_metadata (stored by generator as hint)
                target = section.generation_metadata.get("target_word_count")
                if target and isinstance(target, (int, float)) and target > 0:
                    threshold = target * 0.3
                    if wc < threshold:
                        issues.append(
                            self._issue(
                                severity="warning",
                                category="below_target_word_count",
                                message=(
                                    f"Body section '{section.title}' has {wc} words "
                                    f"but target is {target} (below 30% threshold of "
                                    f"{threshold:.0f})."
                                ),
                                location=location,
                                context={
                                    "section_title": section.title,
                                    "word_count": wc,
                                    "target": target,
                                    "threshold": threshold,
                                },
                            )
                        )

                if wc > 5000:
                    issues.append(
                        self._issue(
                            severity="warning",
                            category="very_long_section",
                            message=(
                                f"Body section '{section.title}' has {wc} words "
                                "(exceeds recommended maximum of 5000)."
                            ),
                            location=location,
                            context={"section_title": section.title, "word_count": wc},
                        )
                    )

            # Recurse into subsections
            if section.subsections:
                self._check_sections(section.subsections, issues)
