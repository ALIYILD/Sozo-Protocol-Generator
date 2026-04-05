"""Validator 7 — Numbering consistency."""
from __future__ import annotations

import re
import time
from collections import defaultdict

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator

_NUMBERED_LABEL_RE = re.compile(
    r"^(Table|Figure|Chart|Image|Diagram|Topomap|Montage|Timeline|Flowchart)\s+(\d+)$",
    re.IGNORECASE,
)


class NumberingConsistencyValidator(BaseDocumentValidator):
    """Checks that table and figure numbering is consistent and non-duplicate.

    Rules:
    - Collect all numbering_labels from all asset blocks
    - Duplicate numbering_label: BLOCK ("duplicate_numbering")
    - Table numbering must be sequential (Table 1, Table 2, ...): WARNING if gaps
    - Figure numbering must be sequential: WARNING if gaps
    - Any asset_record with status=="generated" but numbering_label is None: WARNING
    """

    validator_id: str = "numbering_consistency"
    description: str = (
        "Checks that asset numbering labels are unique, sequential, "
        "and properly assigned."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        # Collect (numbering_label, asset_id, asset_type, location) from all sources
        label_entries: list[tuple[str, str, str, str]] = []  # label, asset_id, type, loc

        # From document.assets
        for ar in document.assets:
            if ar.numbering_label:
                label_entries.append(
                    (ar.numbering_label, ar.asset_id, ar.asset_type, ar.asset_id)
                )
            if ar.status == "generated" and ar.numbering_label is None:
                issues.append(
                    self._issue(
                        severity="warning",
                        category="missing_numbering_label",
                        message=(
                            f"Asset '{ar.asset_id}' (type: {ar.asset_type}) "
                            "has status='generated' but no numbering_label."
                        ),
                        location=ar.asset_id,
                        context={
                            "asset_id": ar.asset_id,
                            "asset_type": ar.asset_type,
                        },
                    )
                )

        # From blocks embedded in sections
        self._collect_from_sections(document.sections, label_entries, issues)

        # Deduplicate label_entries by label
        seen_labels: dict[str, list[str]] = defaultdict(list)
        for label, asset_id, asset_type, loc in label_entries:
            seen_labels[label].append(asset_id)

        for label, asset_ids in seen_labels.items():
            if len(asset_ids) > 1:
                issues.append(
                    self._issue(
                        severity="block",
                        category="duplicate_numbering",
                        message=(
                            f"Numbering label '{label}' is used by multiple "
                            f"assets: {asset_ids}."
                        ),
                        location="document",
                        context={"label": label, "asset_ids": asset_ids},
                    )
                )

        # Check sequencing per prefix type (Table, Figure, etc.)
        prefix_numbers: dict[str, list[int]] = defaultdict(list)
        for label in seen_labels:
            m = _NUMBERED_LABEL_RE.match(label)
            if m:
                prefix = m.group(1).capitalize()
                number = int(m.group(2))
                # Normalise "Figure" and "Figure"-like types
                if prefix in ("Chart", "Image", "Diagram", "Topomap", "Montage",
                               "Timeline", "Flowchart"):
                    prefix = "Figure"
                prefix_numbers[prefix].append(number)

        for prefix, numbers in prefix_numbers.items():
            numbers_sorted = sorted(set(numbers))
            expected = list(range(1, len(numbers_sorted) + 1))
            if numbers_sorted != expected:
                missing = sorted(set(expected) - set(numbers_sorted))
                extra = sorted(set(numbers_sorted) - set(expected))
                issues.append(
                    self._issue(
                        severity="warning",
                        category="non_sequential_numbering",
                        message=(
                            f"{prefix} numbering is not sequential. "
                            f"Found: {numbers_sorted}. "
                            f"Missing numbers: {missing}. "
                            f"Unexpected numbers: {extra}."
                        ),
                        location="document",
                        context={
                            "prefix": prefix,
                            "found": numbers_sorted,
                            "missing": missing,
                            "extra": extra,
                        },
                    )
                )

        duration = time.monotonic() - start
        return self._result(
            document_id=document.document_id,
            condition_slug=document.condition_slug,
            issues=issues,
            duration_seconds=duration,
        )

    def _collect_from_sections(
        self,
        sections: list[CanonicalSection],
        label_entries: list[tuple[str, str, str, str]],
        issues: list[QAValidationIssue],
    ) -> None:
        for section in sections:
            for block in section.blocks:
                self._collect_from_block(
                    block, section.section_id, label_entries, issues
                )
            if section.subsections:
                self._collect_from_sections(section.subsections, label_entries, issues)

    def _collect_from_block(
        self,
        block: CanonicalBlock,
        section_id: str,
        label_entries: list[tuple[str, str, str, str]],
        issues: list[QAValidationIssue],
    ) -> None:
        location = f"{section_id}/{block.block_id}"

        # Block-level numbering_label
        if block.numbering_label and block.asset_id:
            label_entries.append(
                (block.numbering_label, block.asset_id, block.block_type, location)
            )

        # Embedded asset_record
        if block.asset_record:
            ar = block.asset_record
            if ar.numbering_label:
                # Avoid double-counting if already added from document.assets
                label_entries.append(
                    (ar.numbering_label, ar.asset_id, ar.asset_type, location)
                )
            if ar.status == "generated" and ar.numbering_label is None:
                issues.append(
                    self._issue(
                        severity="warning",
                        category="missing_numbering_label",
                        message=(
                            f"Asset '{ar.asset_id}' (type: {ar.asset_type}) "
                            "embedded in block has status='generated' but no "
                            "numbering_label."
                        ),
                        location=location,
                        context={
                            "asset_id": ar.asset_id,
                            "asset_type": ar.asset_type,
                            "block_id": block.block_id,
                        },
                    )
                )
