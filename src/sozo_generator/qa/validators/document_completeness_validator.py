"""Validator 1 — Document completeness."""
from __future__ import annotations

import time

from sozo_generator.schemas.canonical import CanonicalDocument, QAValidationIssue, QAValidationResult
from .base import BaseDocumentValidator


class DocumentCompletenessValidator(BaseDocumentValidator):
    """Checks that all required sections are present.

    Rules:
    - Document must have at least 3 sections
    - Must have a references section (section_type=="references") OR at least
      one section with evidence_pmids
    - Must have at least one body section
    - Must have a title (document.title must not be empty/placeholder)
    - For "handbook" document_type: check that these section titles exist
      (case-insensitive): "protocol", "safety", "evidence"
      (WARN if missing, not BLOCK)
    """

    validator_id: str = "document_completeness"
    description: str = (
        "Checks that all required sections are present and the document has "
        "a valid title."
    )

    # Strings that indicate an unfilled title placeholder
    _PLACEHOLDER_TITLES = {
        "[title]",
        "[document title]",
        "[untitled]",
        "untitled",
        "todo",
        "[todo]",
        "[missing]",
    }

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        sections = document.sections or []

        # --- Rule: title must not be empty or placeholder -------------------
        raw_title = (document.title or "").strip()
        if not raw_title:
            issues.append(
                self._issue(
                    severity="block",
                    category="missing_title",
                    message="Document has no title.",
                    location="document",
                )
            )
        elif raw_title.lower() in self._PLACEHOLDER_TITLES:
            issues.append(
                self._issue(
                    severity="block",
                    category="placeholder_title",
                    message=f"Document title appears to be a placeholder: '{raw_title}'.",
                    location="document",
                    context={"title": raw_title},
                )
            )

        # --- Rule: at least 3 sections --------------------------------------
        if len(sections) < 3:
            issues.append(
                self._issue(
                    severity="block",
                    category="too_few_sections",
                    message=(
                        f"Document has only {len(sections)} section(s); "
                        "minimum required is 3."
                    ),
                    location="document",
                    context={"section_count": len(sections)},
                )
            )

        # --- Rule: references section or evidence pmids ---------------------
        has_references_section = any(
            s.section_type == "references" for s in sections
        )
        has_any_pmids = any(s.evidence_pmids for s in sections)
        if not has_references_section and not has_any_pmids:
            issues.append(
                self._issue(
                    severity="warning",
                    category="missing_references",
                    message=(
                        "Document has no references section and no section "
                        "with evidence PMIDs."
                    ),
                    location="document",
                )
            )

        # --- Rule: at least one body section --------------------------------
        has_body = any(s.section_type == "body" for s in sections)
        if not has_body:
            issues.append(
                self._issue(
                    severity="block",
                    category="missing_body_section",
                    message="Document has no body sections (section_type=='body').",
                    location="document",
                )
            )

        # --- Rule: handbook section titles ----------------------------------
        if document.document_type and document.document_type.lower() == "handbook":
            required_keywords = ["protocol", "safety", "evidence"]
            existing_titles_lower = {s.title.lower() for s in sections}
            for keyword in required_keywords:
                found = any(keyword in t for t in existing_titles_lower)
                if not found:
                    issues.append(
                        self._issue(
                            severity="warning",
                            category="missing_handbook_section",
                            message=(
                                f"Handbook document is missing a section "
                                f"containing '{keyword}' in the title."
                            ),
                            location="document",
                            context={"expected_keyword": keyword},
                        )
                    )

        duration = time.monotonic() - start
        return self._result(
            document_id=document.document_id,
            condition_slug=document.condition_slug,
            issues=issues,
            duration_seconds=duration,
        )
