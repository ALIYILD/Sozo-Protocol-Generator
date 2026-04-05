"""Validator 3 — Citation coverage."""
from __future__ import annotations

import re
import time

from sozo_generator.schemas.canonical import (
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator

_PMID_RE = re.compile(r"^\d{1,9}$")


class CitationCoverageValidator(BaseDocumentValidator):
    """Checks that sections have citations.

    Rules:
    - Document-level: if document.references is empty: WARNING
    - Section-level: any body section with 0 evidence_pmids: INFO
    - Any section claiming evidence_level but no pmids: WARNING
    - PMID format: must match r'^\\d{1,9}$' — any invalid format: WARNING
    """

    validator_id: str = "citation_coverage"
    description: str = (
        "Checks that sections have citations and that PMID formats are valid."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        # --- Document-level: empty references list --------------------------
        if not document.references:
            issues.append(
                self._issue(
                    severity="warning",
                    category="empty_references_list",
                    message=(
                        "Document has no entries in its references list "
                        "(document.references is empty)."
                    ),
                    location="document",
                )
            )

        # --- Validate all PMIDs on citations --------------------------------
        for citation in document.references:
            pmid = citation.pmid
            if pmid is not None and not _PMID_RE.match(str(pmid)):
                issues.append(
                    self._issue(
                        severity="warning",
                        category="invalid_pmid_format",
                        message=(
                            f"Citation '{citation.citation_id}' has invalid PMID "
                            f"format: '{pmid}'."
                        ),
                        location=citation.citation_id,
                        context={"pmid": pmid, "citation_id": citation.citation_id},
                    )
                )

        # --- Section-level checks -------------------------------------------
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
                # Section with no pmids
                if not section.evidence_pmids:
                    issues.append(
                        self._issue(
                            severity="info",
                            category="section_no_citations",
                            message=(
                                f"Body section '{section.title}' has no "
                                "evidence PMIDs."
                            ),
                            location=section.section_id,
                            context={"section_title": section.title},
                        )
                    )

                # evidence_level set but no pmids
                evidence_level = section.generation_metadata.get("evidence_level")
                if evidence_level and not section.evidence_pmids:
                    issues.append(
                        self._issue(
                            severity="warning",
                            category="evidence_level_without_pmids",
                            message=(
                                f"Body section '{section.title}' claims "
                                f"evidence_level='{evidence_level}' but has "
                                "no associated PMIDs."
                            ),
                            location=section.section_id,
                            context={
                                "section_title": section.title,
                                "evidence_level": evidence_level,
                            },
                        )
                    )

                # Validate each PMID format
                for pmid in section.evidence_pmids:
                    if not _PMID_RE.match(str(pmid)):
                        issues.append(
                            self._issue(
                                severity="warning",
                                category="invalid_pmid_format",
                                message=(
                                    f"Section '{section.title}' contains "
                                    f"invalid PMID format: '{pmid}'."
                                ),
                                location=section.section_id,
                                context={
                                    "section_title": section.title,
                                    "pmid": pmid,
                                },
                            )
                        )

            if section.subsections:
                self._check_sections(section.subsections, issues)
