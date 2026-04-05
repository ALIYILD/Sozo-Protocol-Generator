"""Validator 9 — Cross-reference integrity."""
from __future__ import annotations

import re
import time
from collections import defaultdict

from sozo_generator.schemas.canonical import (
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator

# Patterns for cross-reference detection
_TABLE_REF_RE = re.compile(r"\bsee\s+Table\s+(\d+)\b", re.IGNORECASE)
_FIGURE_REF_RE = re.compile(r"\bsee\s+(?:Figure|Fig\.?)\s+(\d+)\b", re.IGNORECASE)
_SECTION_REF_RE = re.compile(r"\bSection\s+(\d+(?:\.\d+)*)\b", re.IGNORECASE)


class CrossReferenceValidator(BaseDocumentValidator):
    """Checks for broken cross-references within the document.

    Rules:
    - Scan all text block content for patterns like "see Table X", "see Figure X",
      "Section X"
    - For "Table X" references: check a table with that numbering_label exists:
      WARNING if not
    - For "Figure X" references: check a figure with that numbering_label exists:
      WARNING if not
    - For "Section X" cross-references: check section exists: INFO if not (hard
      to validate without page numbers)
    - Duplicate section titles (case-insensitive): WARNING
    """

    validator_id: str = "cross_reference"
    description: str = (
        "Checks that in-text cross-references to tables, figures, and sections "
        "are resolvable within the document."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        # Build lookup sets for existing numbering labels
        existing_table_labels: set[str] = set()
        existing_figure_labels: set[str] = set()
        _FIGURE_ASSET_TYPES = {
            "figure", "chart", "image", "diagram", "topomap",
            "montage", "timeline", "flowchart",
        }

        for ar in document.assets:
            if ar.numbering_label:
                m = re.match(r"^(\w+)\s+(\d+)$", ar.numbering_label, re.IGNORECASE)
                if m:
                    prefix = m.group(1).lower()
                    if prefix == "table":
                        existing_table_labels.add(ar.numbering_label)
                    else:
                        existing_figure_labels.add(ar.numbering_label)

        # Also collect from blocks
        self._collect_labels_from_sections(
            document.sections, existing_table_labels, existing_figure_labels
        )

        # Collect section titles for duplicate detection
        section_titles: list[str] = []
        self._collect_section_titles(document.sections, section_titles)

        # Check for duplicate section titles
        title_counts: dict[str, list[str]] = defaultdict(list)
        for title in section_titles:
            title_counts[title.lower()].append(title)

        for title_lower, titles in title_counts.items():
            if len(titles) > 1:
                issues.append(
                    self._issue(
                        severity="warning",
                        category="duplicate_section_title",
                        message=(
                            f"Section title '{titles[0]}' appears {len(titles)} "
                            "times in the document."
                        ),
                        location="document",
                        context={"title": titles[0], "count": len(titles)},
                    )
                )

        # Scan text content for cross-references
        self._check_sections(
            document.sections,
            existing_table_labels,
            existing_figure_labels,
            issues,
        )

        duration = time.monotonic() - start
        return self._result(
            document_id=document.document_id,
            condition_slug=document.condition_slug,
            issues=issues,
            duration_seconds=duration,
        )

    def _collect_labels_from_sections(
        self,
        sections: list[CanonicalSection],
        table_labels: set[str],
        figure_labels: set[str],
    ) -> None:
        for section in sections:
            for block in section.blocks:
                if block.numbering_label:
                    m = re.match(
                        r"^(\w+)\s+\d+$", block.numbering_label, re.IGNORECASE
                    )
                    if m:
                        prefix = m.group(1).lower()
                        if prefix == "table":
                            table_labels.add(block.numbering_label)
                        else:
                            figure_labels.add(block.numbering_label)
                if block.asset_record and block.asset_record.numbering_label:
                    ar = block.asset_record
                    m = re.match(
                        r"^(\w+)\s+\d+$", ar.numbering_label, re.IGNORECASE
                    )
                    if m:
                        prefix = m.group(1).lower()
                        if prefix == "table":
                            table_labels.add(ar.numbering_label)
                        else:
                            figure_labels.add(ar.numbering_label)
            if section.subsections:
                self._collect_labels_from_sections(
                    section.subsections, table_labels, figure_labels
                )

    def _collect_section_titles(
        self,
        sections: list[CanonicalSection],
        titles: list[str],
    ) -> None:
        for section in sections:
            titles.append(section.title)
            if section.subsections:
                self._collect_section_titles(section.subsections, titles)

    def _check_sections(
        self,
        sections: list[CanonicalSection],
        table_labels: set[str],
        figure_labels: set[str],
        issues: list[QAValidationIssue],
    ) -> None:
        for section in sections:
            for block in section.blocks:
                if block.block_type == "text" and block.content:
                    self._check_text(
                        block.content,
                        f"{section.section_id}/{block.block_id}",
                        table_labels,
                        figure_labels,
                        issues,
                    )
            if section.subsections:
                self._check_sections(
                    section.subsections, table_labels, figure_labels, issues
                )

    def _check_text(
        self,
        content: str,
        location: str,
        table_labels: set[str],
        figure_labels: set[str],
        issues: list[QAValidationIssue],
    ) -> None:
        # Table references
        for m in _TABLE_REF_RE.finditer(content):
            ref_label = f"Table {m.group(1)}"
            # Case-insensitive lookup
            if not any(
                lbl.lower() == ref_label.lower() for lbl in table_labels
            ):
                issues.append(
                    self._issue(
                        severity="warning",
                        category="broken_table_reference",
                        message=(
                            f"Text references '{ref_label}' but no table with "
                            "that numbering_label exists in the document."
                        ),
                        location=location,
                        context={"reference": ref_label},
                    )
                )

        # Figure references
        for m in _FIGURE_REF_RE.finditer(content):
            ref_label = f"Figure {m.group(1)}"
            if not any(
                lbl.lower() == ref_label.lower() for lbl in figure_labels
            ):
                issues.append(
                    self._issue(
                        severity="warning",
                        category="broken_figure_reference",
                        message=(
                            f"Text references '{ref_label}' but no figure with "
                            "that numbering_label exists in the document."
                        ),
                        location=location,
                        context={"reference": ref_label},
                    )
                )

        # Section cross-references (informational only)
        for m in _SECTION_REF_RE.finditer(content):
            ref = m.group(0)
            issues.append(
                self._issue(
                    severity="info",
                    category="section_cross_reference",
                    message=(
                        f"Text contains section cross-reference '{ref}'; "
                        "page-number validation is not possible at this stage."
                    ),
                    location=location,
                    context={"reference": ref},
                )
            )
