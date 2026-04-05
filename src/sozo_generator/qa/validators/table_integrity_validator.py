"""Validator 6 — Table integrity."""
from __future__ import annotations

import time
from typing import Any

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator


class TableIntegrityValidator(BaseDocumentValidator):
    """Checks table structure integrity.

    Rules:
    - Any asset_record where asset_type=="table" and source_data is empty: WARNING
    - Any CanonicalTable (in asset_record.source_data) with 0 rows: WARNING
    - Any CanonicalTable with 0 headers: BLOCK ("no_table_headers")
    - Any row where len(row) != len(headers): WARNING ("row_column_mismatch")
    - Any table where all rows have all "N/A" values: INFO ("table_all_na")
    """

    validator_id: str = "table_integrity"
    description: str = (
        "Checks the structural integrity of table assets in the document."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        # Check assets registered at document level
        for ar in document.assets:
            if ar.asset_type == "table":
                self._check_table_asset(ar, issues)

        # Also check inline asset_records embedded in blocks
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
            for block in section.blocks:
                if block.asset_record and block.asset_record.asset_type == "table":
                    self._check_table_asset(block.asset_record, issues)
            if section.subsections:
                self._check_sections(section.subsections, issues)

    def _check_table_asset(
        self,
        ar: AssetRecord,
        issues: list[QAValidationIssue],
    ) -> None:
        location = ar.asset_id

        # Empty source_data
        if not ar.source_data:
            issues.append(
                self._issue(
                    severity="warning",
                    category="empty_table_source_data",
                    message=(
                        f"Table asset '{ar.asset_id}' has empty source_data."
                    ),
                    location=location,
                    context={"asset_id": ar.asset_id},
                )
            )
            return

        source = ar.source_data

        # Extract headers and rows from source_data dict
        # Supports both flat dict keys and nested CanonicalTable-like dicts
        headers: list[Any] = source.get("headers", [])
        rows: list[Any] = source.get("rows", [])

        # 0 headers → BLOCK
        if not headers:
            issues.append(
                self._issue(
                    severity="block",
                    category="no_table_headers",
                    message=(
                        f"Table asset '{ar.asset_id}' has no headers defined."
                    ),
                    location=location,
                    context={"asset_id": ar.asset_id},
                )
            )
            return  # Can't validate rows without headers

        # 0 rows → WARNING
        if not rows:
            issues.append(
                self._issue(
                    severity="warning",
                    category="empty_table",
                    message=(
                        f"Table asset '{ar.asset_id}' has no data rows."
                    ),
                    location=location,
                    context={"asset_id": ar.asset_id, "header_count": len(headers)},
                )
            )
            return

        header_count = len(headers)
        all_na = True  # Optimistically assume all-NA until proven otherwise

        for row_idx, row in enumerate(rows):
            if not isinstance(row, (list, tuple)):
                continue

            # Row width mismatch
            if len(row) != header_count:
                issues.append(
                    self._issue(
                        severity="warning",
                        category="row_column_mismatch",
                        message=(
                            f"Table asset '{ar.asset_id}' row {row_idx} has "
                            f"{len(row)} cell(s) but there are {header_count} "
                            "header(s)."
                        ),
                        location=location,
                        context={
                            "asset_id": ar.asset_id,
                            "row_index": row_idx,
                            "row_width": len(row),
                            "header_count": header_count,
                        },
                    )
                )

            # Check for all-NA row
            row_all_na = all(
                str(cell).strip().upper() in {"N/A", "NA", "-", ""}
                for cell in row
            )
            if not row_all_na:
                all_na = False

        if all_na and rows:
            issues.append(
                self._issue(
                    severity="info",
                    category="table_all_na",
                    message=(
                        f"Table asset '{ar.asset_id}' appears to contain only "
                        "N/A values across all rows."
                    ),
                    location=location,
                    context={"asset_id": ar.asset_id},
                )
            )
