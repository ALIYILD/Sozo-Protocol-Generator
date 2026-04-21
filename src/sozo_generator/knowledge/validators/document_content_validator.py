from __future__ import annotations

from dataclasses import dataclass

from ...core.enums import QASeverity
from ..schemas import KnowledgeCondition


@dataclass
class ContentValidationIssue:
    severity: QASeverity
    location: str
    message: str


_BANNED_PLACEHOLDER_PMIDS = {
    "00000000",
    "99999999",
}


def validate_condition_content_blocks(condition: KnowledgeCondition) -> list[ContentValidationIssue]:
    """Validate structured authored content blocks on a knowledge condition.

    This runs before rendering in canonical generation to prevent silent unsafe output.
    """
    issues: list[ContentValidationIssue] = []

    for i, block in enumerate(getattr(condition, "content_blocks", []) or []):
        loc = f"condition.content_blocks[{i}]"

        if not block.block_id.strip():
            issues.append(
                ContentValidationIssue(
                    severity=QASeverity.BLOCK,
                    location=f"{loc}.block_id",
                    message="content block block_id must be non-empty",
                )
            )

        if block.kind == "table":
            if block.table is None:
                issues.append(
                    ContentValidationIssue(
                        severity=QASeverity.BLOCK,
                        location=f"{loc}.table",
                        message="table block must include table definition",
                    )
                )
            else:
                if not block.table.headers:
                    issues.append(
                        ContentValidationIssue(
                            severity=QASeverity.BLOCK,
                            location=f"{loc}.table.headers",
                            message="table block must include headers",
                        )
                    )
                for r_idx, row in enumerate(block.table.rows):
                    if block.table.headers and len(row) != len(block.table.headers):
                        issues.append(
                            ContentValidationIssue(
                                severity=QASeverity.BLOCK,
                                location=f"{loc}.table.rows[{r_idx}]",
                                message=(
                                    "table row length must match headers length "
                                    f"({len(row)} != {len(block.table.headers)})"
                                ),
                            )
                        )

        if block.kind == "figure" and block.figure is None:
            issues.append(
                ContentValidationIssue(
                    severity=QASeverity.BLOCK,
                    location=f"{loc}.figure",
                    message="figure block must include figure definition",
                )
            )

        # Patient-facing content must not be marked clinician-only
        if "patient_handouts" in (block.section_slugs or []) and block.clinician_only:
            issues.append(
                ContentValidationIssue(
                    severity=QASeverity.BLOCK,
                    location=f"{loc}.clinician_only",
                    message=(
                        "patient_handouts content blocks must set clinician_only=false "
                        "(prevent clinician-only language leakage into patient handouts)"
                    ),
                )
            )

        # Citation governance: no banned placeholder PMIDs
        for c_idx, c in enumerate(block.citations or []):
            if c.pmid and str(c.pmid) in _BANNED_PLACEHOLDER_PMIDS:
                issues.append(
                    ContentValidationIssue(
                        severity=QASeverity.BLOCK,
                        location=f"{loc}.citations[{c_idx}].pmid",
                        message=f"Placeholder PMID '{c.pmid}' is prohibited by evidence policy",
                    )
                )

    return issues

