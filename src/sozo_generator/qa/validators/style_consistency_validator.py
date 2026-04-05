"""Validator 10 — Style and content consistency."""
from __future__ import annotations

import re
import time
from itertools import combinations

from sozo_generator.schemas.canonical import (
    CanonicalBlock,
    CanonicalDocument,
    CanonicalSection,
    QAValidationIssue,
    QAValidationResult,
)
from .base import BaseDocumentValidator

_FNON_RE = re.compile(r"\bFNON\b")


def _word_set(text: str) -> set[str]:
    """Return a lowercase set of words from text."""
    return set(re.findall(r"[a-z]+", text.lower()))


def _jaccard_similarity(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


class StyleConsistencyValidator(BaseDocumentValidator):
    """Checks style and content consistency.

    Rules:
    - Duplicate paragraph content across sections (>80% similarity by word
      overlap using Jaccard): WARNING
    - Any text block with content > 3000 words with no subsections: INFO
    - Any body section with only asset blocks (no text): INFO
    - Check that condition display_name appears at least once in document
      (case-insensitive): INFO
    - For variant="partners": check that "FNON" appears at least once: INFO
    - For variant="fellow": check "FNON" does not dominate (< 3 occurrences):
      INFO
    """

    validator_id: str = "style_consistency"
    description: str = (
        "Checks for duplicate content, monolithic sections, asset-only sections, "
        "and variant-specific style requirements."
    )

    def validate(self, document: CanonicalDocument) -> QAValidationResult:
        start = time.monotonic()
        issues: list[QAValidationIssue] = []

        # Collect all text block content items with location for comparison
        # List of (word_set, location_str, content_preview)
        text_blocks: list[tuple[set[str], str, str]] = []
        full_text_parts: list[str] = []

        self._collect_from_sections(
            document.sections, text_blocks, full_text_parts, issues
        )

        # --- Duplicate content check (>80% Jaccard similarity) --------------
        seen_pairs: set[frozenset[int]] = set()
        for i, (ws_i, loc_i, preview_i) in enumerate(text_blocks):
            for j, (ws_j, loc_j, preview_j) in enumerate(text_blocks):
                if i >= j:
                    continue
                pair = frozenset([i, j])
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)
                sim = _jaccard_similarity(ws_i, ws_j)
                if sim > 0.80:
                    issues.append(
                        self._issue(
                            severity="warning",
                            category="duplicate_content",
                            message=(
                                f"Text blocks at '{loc_i}' and '{loc_j}' have "
                                f"{sim:.0%} word overlap (threshold: 80%)."
                            ),
                            location=loc_i,
                            context={
                                "location_a": loc_i,
                                "location_b": loc_j,
                                "similarity": round(sim, 3),
                                "preview_a": preview_i,
                                "preview_b": preview_j,
                            },
                        )
                    )

        # --- Condition display_name presence --------------------------------
        display_name = (
            document.condition_slug.replace("-", " ").replace("_", " ").strip()
        )
        full_text = " ".join(full_text_parts).lower()
        if display_name and display_name.lower() not in full_text:
            issues.append(
                self._issue(
                    severity="info",
                    category="condition_name_absent",
                    message=(
                        f"Condition name '{display_name}' does not appear "
                        "anywhere in the document body text."
                    ),
                    location="document",
                    context={"condition_slug": document.condition_slug},
                )
            )

        # --- Variant-specific FNON checks -----------------------------------
        fnon_count = len(_FNON_RE.findall(" ".join(full_text_parts)))

        if document.variant == "partners" and fnon_count == 0:
            issues.append(
                self._issue(
                    severity="info",
                    category="missing_fnon_partners",
                    message=(
                        "Document variant is 'partners' but 'FNON' does not "
                        "appear in the document."
                    ),
                    location="document",
                    context={"variant": document.variant, "fnon_count": fnon_count},
                )
            )

        if document.variant == "fellow" and fnon_count >= 3:
            issues.append(
                self._issue(
                    severity="info",
                    category="fnon_dominates_fellow",
                    message=(
                        f"Document variant is 'fellow' but 'FNON' appears "
                        f"{fnon_count} time(s) (< 3 recommended for fellow variant)."
                    ),
                    location="document",
                    context={"variant": document.variant, "fnon_count": fnon_count},
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
        text_blocks: list[tuple[set[str], str, str]],
        full_text_parts: list[str],
        issues: list[QAValidationIssue],
    ) -> None:
        for section in sections:
            # --- Asset-only body section check ------------------------------
            if section.section_type == "body":
                has_text_block = any(
                    b.block_type == "text" and b.content
                    for b in section.blocks
                )
                has_asset_block = any(b.asset_id for b in section.blocks)
                if has_asset_block and not has_text_block and section.blocks:
                    issues.append(
                        self._issue(
                            severity="info",
                            category="asset_only_section",
                            message=(
                                f"Body section '{section.title}' contains only "
                                "asset blocks with no text content."
                            ),
                            location=section.section_id,
                            context={"section_title": section.title},
                        )
                    )

            for block in section.blocks:
                if block.block_type == "text" and block.content:
                    content = block.content
                    words = content.split()
                    location = f"{section.section_id}/{block.block_id}"
                    preview = content[:100]

                    full_text_parts.append(content)
                    text_blocks.append((_word_set(content), location, preview))

                    # --- Monolithic section check ---------------------------
                    if len(words) > 3000 and not section.subsections:
                        issues.append(
                            self._issue(
                                severity="info",
                                category="monolithic_section",
                                message=(
                                    f"Text block '{block.block_id}' in section "
                                    f"'{section.title}' has {len(words)} words "
                                    "with no subsections."
                                ),
                                location=location,
                                context={
                                    "block_id": block.block_id,
                                    "section_title": section.title,
                                    "word_count": len(words),
                                },
                            )
                        )

            if section.subsections:
                self._collect_from_sections(
                    section.subsections, text_blocks, full_text_parts, issues
                )
