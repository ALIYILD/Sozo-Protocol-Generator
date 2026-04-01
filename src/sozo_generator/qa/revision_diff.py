"""
Diff generator for document revisions.

Compares an original and revised DocumentSpec section-by-section
to produce a structured DocumentDiff with change summaries.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from ..schemas.documents import DocumentSpec, SectionContent

logger = logging.getLogger(__name__)


@dataclass
class SectionDiff:
    """Diff for a single section between original and revised."""

    section_id: str = ""
    title: str = ""
    change_type: str = ""  # "modified", "added", "removed", "unchanged"
    original_word_count: int = 0
    revised_word_count: int = 0
    content_changed: bool = False
    tables_changed: bool = False
    detail: str = ""


@dataclass
class DocumentDiff:
    """Full diff between original and revised DocumentSpec."""

    original_title: str = ""
    revised_title: str = ""
    section_diffs: list[SectionDiff] = field(default_factory=list)
    total_modified: int = 0
    total_added: int = 0
    total_removed: int = 0
    total_unchanged: int = 0
    summary: str = ""


class RevisionDiffGenerator:
    """Compares original and revised DocumentSpec objects."""

    def generate_diff(
        self, original: DocumentSpec, revised: DocumentSpec
    ) -> DocumentDiff:
        """Compare original and revised DocumentSpec section by section."""
        diff = DocumentDiff(
            original_title=original.title,
            revised_title=revised.title,
        )

        original_map = self._build_section_map(original.sections)
        revised_map = self._build_section_map(revised.sections)

        all_ids = list(dict.fromkeys(
            list(original_map.keys()) + list(revised_map.keys())
        ))

        for sid in all_ids:
            orig_section = original_map.get(sid)
            rev_section = revised_map.get(sid)

            if orig_section and rev_section:
                # Section exists in both — check for modifications
                section_diff = self._compare_sections(orig_section, rev_section)
                diff.section_diffs.append(section_diff)
                if section_diff.change_type == "modified":
                    diff.total_modified += 1
                else:
                    diff.total_unchanged += 1

            elif orig_section and not rev_section:
                # Section was removed
                wc = self._word_count(orig_section.content)
                diff.section_diffs.append(
                    SectionDiff(
                        section_id=sid,
                        title=orig_section.title,
                        change_type="removed",
                        original_word_count=wc,
                        revised_word_count=0,
                        content_changed=True,
                        detail=f"Section removed ({wc} words)",
                    )
                )
                diff.total_removed += 1

            elif rev_section and not orig_section:
                # Section was added
                wc = self._word_count(rev_section.content)
                diff.section_diffs.append(
                    SectionDiff(
                        section_id=sid,
                        title=rev_section.title,
                        change_type="added",
                        original_word_count=0,
                        revised_word_count=wc,
                        content_changed=True,
                        detail=f"New section added ({wc} words)",
                    )
                )
                diff.total_added += 1

        diff.summary = (
            f"{diff.total_modified} modified, {diff.total_added} added, "
            f"{diff.total_removed} removed, {diff.total_unchanged} unchanged"
        )
        logger.info("Diff summary: %s", diff.summary)
        return diff

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_section_map(
        self, sections: list[SectionContent]
    ) -> dict[str, SectionContent]:
        """Flatten section tree into {section_id: SectionContent} map."""
        result: dict[str, SectionContent] = {}
        for section in sections:
            self._walk(section, result)
        return result

    def _walk(
        self, section: SectionContent, out: dict[str, SectionContent]
    ) -> None:
        """Recursively collect sections."""
        out[section.section_id] = section
        for sub in section.subsections:
            self._walk(sub, out)

    def _compare_sections(
        self, original: SectionContent, revised: SectionContent
    ) -> SectionDiff:
        """Compare two versions of the same section."""
        orig_wc = self._word_count(original.content)
        rev_wc = self._word_count(revised.content)

        content_changed = original.content.strip() != revised.content.strip()
        tables_changed = self._tables_differ(original.tables, revised.tables)

        # Also check title changes
        title_changed = original.title != revised.title

        any_change = content_changed or tables_changed or title_changed

        details: list[str] = []
        if content_changed:
            delta = rev_wc - orig_wc
            sign = "+" if delta >= 0 else ""
            details.append(f"Content changed ({sign}{delta} words)")
        if tables_changed:
            details.append(
                f"Tables changed ({len(original.tables)} -> {len(revised.tables)})"
            )
        if title_changed:
            details.append(f"Title: '{original.title}' -> '{revised.title}'")

        return SectionDiff(
            section_id=original.section_id,
            title=revised.title,
            change_type="modified" if any_change else "unchanged",
            original_word_count=orig_wc,
            revised_word_count=rev_wc,
            content_changed=content_changed,
            tables_changed=tables_changed,
            detail="; ".join(details) if details else "No changes",
        )

    def _tables_differ(
        self, original: list[dict], revised: list[dict]
    ) -> bool:
        """Check whether table lists differ."""
        if len(original) != len(revised):
            return True
        for orig_t, rev_t in zip(original, revised):
            if orig_t != rev_t:
                return True
        return False

    def _word_count(self, text: str) -> int:
        """Count words in a string."""
        return len(text.split()) if text else 0
