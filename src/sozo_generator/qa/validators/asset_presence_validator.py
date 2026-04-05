"""Validator 5 — Asset presence."""
from __future__ import annotations

import os
import time

from sozo_generator.schemas.canonical import (
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator


class AssetPresenceValidator(BaseDocumentValidator):
    """Checks that all referenced assets are present.

    Rules:
    - Any block with asset_id set but asset_record is None: WARNING
    - Any block with asset_record.status == "failed": WARNING
    - Any block with asset_record.status == "missing": BLOCK
    - Any asset_record with output_path set but file doesn't exist: WARNING
    - If > 3 assets missing: BLOCK
    """

    validator_id: str = "asset_presence"
    description: str = (
        "Checks that all asset blocks have valid, present asset records and "
        "that output files exist on disk."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        missing_count = 0
        missing_count += self._check_sections(document.sections, issues)

        if missing_count > 3:
            issues.append(
                self._issue(
                    severity="block",
                    category="too_many_missing_assets",
                    message=(
                        f"Document has {missing_count} missing asset(s) "
                        "(threshold: 3)."
                    ),
                    location="document",
                    context={"missing_count": missing_count},
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
        missing = 0
        for section in sections:
            for block in section.blocks:
                missing += self._check_block(block, section.section_id, issues)
            if section.subsections:
                missing += self._check_sections(section.subsections, issues)
        return missing

    def _check_block(
        self,
        block: CanonicalBlock,
        section_id: str,
        issues: list[QAValidationIssue],
    ) -> int:
        if not block.asset_id:
            return 0

        missing = 0
        location = f"{section_id}/{block.block_id}"

        # No asset_record despite asset_id being set
        if block.asset_record is None:
            issues.append(
                self._issue(
                    severity="warning",
                    category="missing_asset_record",
                    message=(
                        f"Block '{block.block_id}' references asset_id "
                        f"'{block.asset_id}' but has no embedded asset_record."
                    ),
                    location=location,
                    context={
                        "block_id": block.block_id,
                        "asset_id": block.asset_id,
                    },
                )
            )
            missing += 1
            return missing

        ar = block.asset_record

        if ar.status == "failed":
            issues.append(
                self._issue(
                    severity="warning",
                    category="asset_generation_failed",
                    message=(
                        f"Asset '{ar.asset_id}' (type: {ar.asset_type}) has "
                        f"status='failed'. Error: {ar.error_message or 'unknown'}."
                    ),
                    location=location,
                    context={
                        "asset_id": ar.asset_id,
                        "asset_type": ar.asset_type,
                        "error_message": ar.error_message,
                    },
                )
            )
            missing += 1

        elif ar.status == "missing":
            issues.append(
                self._issue(
                    severity="block",
                    category="asset_file_missing",
                    message=(
                        f"Asset '{ar.asset_id}' (type: {ar.asset_type}) has "
                        "status='missing'."
                    ),
                    location=location,
                    context={
                        "asset_id": ar.asset_id,
                        "asset_type": ar.asset_type,
                    },
                )
            )
            missing += 1

        # Check output_path exists on disk
        if ar.output_path and not os.path.isfile(ar.output_path):
            issues.append(
                self._issue(
                    severity="warning",
                    category="asset_file_not_found",
                    message=(
                        f"Asset '{ar.asset_id}' output_path does not exist "
                        f"on disk: '{ar.output_path}'."
                    ),
                    location=location,
                    context={
                        "asset_id": ar.asset_id,
                        "output_path": ar.output_path,
                    },
                )
            )
            missing += 1

        return missing
