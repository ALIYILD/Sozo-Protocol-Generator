"""Validator 8 — Figure integrity."""
from __future__ import annotations

import time

from sozo_generator.schemas.canonical import (
    AssetRecord,
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator

_FIGURE_BLOCK_TYPES = {"figure", "chart", "image", "diagram"}
_FIGURE_ASSET_TYPES = {"figure", "chart", "image", "diagram", "topomap", "montage",
                       "timeline", "flowchart"}


class FigureIntegrityValidator(BaseDocumentValidator):
    """Checks figure/image integrity.

    Rules:
    - Any figure asset_record where output_path is None and status=="generated": WARNING
    - Any figure asset_record where caption is None or "": WARNING
    - Any figure block (block_type in ["figure","chart","image","diagram"]) with
      no caption: WARNING
    - Figure assets without alt_text in source_data: INFO
    """

    validator_id: str = "figure_integrity"
    description: str = (
        "Checks that figure and image assets have captions, output paths, "
        "and alt text."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        # Check document-level asset records
        for ar in document.assets:
            if ar.asset_type in _FIGURE_ASSET_TYPES:
                self._check_figure_asset(ar, ar.asset_id, issues)

        # Check inline blocks
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
                self._check_block(block, section.section_id, issues)
            if section.subsections:
                self._check_sections(section.subsections, issues)

    def _check_block(
        self,
        block: CanonicalBlock,
        section_id: str,
        issues: list[QAValidationIssue],
    ) -> None:
        location = f"{section_id}/{block.block_id}"

        # Embedded asset_record for figure-type assets
        if block.asset_record and block.asset_record.asset_type in _FIGURE_ASSET_TYPES:
            self._check_figure_asset(block.asset_record, location, issues)

        # Block-level caption check for figure-type blocks
        if block.block_type in _FIGURE_BLOCK_TYPES:
            caption = (block.caption or "").strip()
            if not caption:
                issues.append(
                    self._issue(
                        severity="warning",
                        category="missing_figure_caption",
                        message=(
                            f"Figure block '{block.block_id}' (type: "
                            f"{block.block_type}) has no caption."
                        ),
                        location=location,
                        context={
                            "block_id": block.block_id,
                            "block_type": block.block_type,
                        },
                    )
                )

    def _check_figure_asset(
        self,
        ar: AssetRecord,
        location: str,
        issues: list[QAValidationIssue],
    ) -> None:
        # output_path missing when status is "generated"
        if ar.status == "generated" and ar.output_path is None:
            issues.append(
                self._issue(
                    severity="warning",
                    category="figure_missing_output_path",
                    message=(
                        f"Figure asset '{ar.asset_id}' (type: {ar.asset_type}) "
                        "has status='generated' but no output_path."
                    ),
                    location=location,
                    context={
                        "asset_id": ar.asset_id,
                        "asset_type": ar.asset_type,
                    },
                )
            )

        # caption missing or empty
        caption = (ar.caption or "").strip()
        if not caption:
            issues.append(
                self._issue(
                    severity="warning",
                    category="missing_figure_caption",
                    message=(
                        f"Figure asset '{ar.asset_id}' (type: {ar.asset_type}) "
                        "has no caption."
                    ),
                    location=location,
                    context={
                        "asset_id": ar.asset_id,
                        "asset_type": ar.asset_type,
                    },
                )
            )

        # alt_text in source_data
        alt_text = ar.source_data.get("alt_text", "")
        if not alt_text:
            issues.append(
                self._issue(
                    severity="info",
                    category="missing_alt_text",
                    message=(
                        f"Figure asset '{ar.asset_id}' (type: {ar.asset_type}) "
                        "has no alt_text in source_data."
                    ),
                    location=location,
                    context={
                        "asset_id": ar.asset_id,
                        "asset_type": ar.asset_type,
                    },
                )
            )
