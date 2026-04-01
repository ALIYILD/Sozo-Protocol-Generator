"""
Pattern extractor — analyzes ingested document fingerprints to extract:
- Master template structure (shared across all conditions)
- Boilerplate blocks (identical text)
- Table layout patterns (reusable column structures)
- Section ordering rules
- Document variant structures (per doc type)
- Condition-variable vs invariant sections
"""
from __future__ import annotations

import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from .document_ingester import DocumentFingerprint, TableFingerprint, SectionFingerprint

logger = logging.getLogger(__name__)


@dataclass
class TablePattern:
    """A reusable table layout pattern learned from existing documents."""
    pattern_id: str = ""
    headers: list[str] = field(default_factory=list)
    col_count: int = 0
    typical_row_count: int = 0
    found_in_doc_types: list[str] = field(default_factory=list)
    found_in_sections: list[str] = field(default_factory=list)
    occurrence_count: int = 0


@dataclass
class BoilerplateBlock:
    """A block of text that is identical across conditions."""
    block_id: str = ""
    content_hash: str = ""
    section_title: str = ""
    found_in: list[str] = field(default_factory=list)  # condition slugs
    is_universal: bool = False  # appears in ALL conditions


@dataclass
class SectionPattern:
    """A section that appears in a specific position across documents."""
    section_id: str = ""
    typical_title: str = ""
    typical_position: int = 0  # 0-indexed order
    typical_word_count: int = 0
    is_boilerplate: bool = False
    is_variable: bool = False  # content changes per condition
    found_in_doc_types: list[str] = field(default_factory=list)
    occurrence_count: int = 0


@dataclass
class DocumentTypePattern:
    """The structural pattern for one document type (e.g., Evidence-Based Protocol)."""
    doc_type: str = ""
    typical_section_order: list[str] = field(default_factory=list)
    typical_section_count: int = 0
    typical_table_count: int = 0
    typical_word_count: int = 0
    typical_paragraph_count: int = 0
    table_patterns: list[TablePattern] = field(default_factory=list)
    title_template: str = ""  # e.g., "SOZO Evidence-Based Protocol — {condition}"
    conditions_analyzed: int = 0


@dataclass
class MasterTemplateProfile:
    """The learned master template profile across all documents."""
    # Title block pattern
    title_block_pattern: list[str] = field(default_factory=list)
    # Shared formatting
    primary_font: str = "Calibri"
    heading_sizes: dict[int, float] = field(default_factory=dict)
    body_font_size: float = 11.0
    # Document type patterns
    doc_type_patterns: dict[str, DocumentTypePattern] = field(default_factory=dict)
    # Shared patterns
    boilerplate_blocks: list[BoilerplateBlock] = field(default_factory=list)
    table_patterns: list[TablePattern] = field(default_factory=list)
    section_patterns: list[SectionPattern] = field(default_factory=list)
    # Stats
    total_documents_analyzed: int = 0
    conditions_analyzed: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)


class PatternExtractor:
    """Analyzes a collection of document fingerprints to extract the master
    template profile and reusable patterns."""

    def __init__(self, fingerprints: list[DocumentFingerprint]):
        self.fingerprints = fingerprints

    def extract_master_profile(self) -> MasterTemplateProfile:
        """Extract the complete master template profile."""
        profile = MasterTemplateProfile()
        profile.total_documents_analyzed = len(self.fingerprints)
        profile.conditions_analyzed = sorted(set(
            fp.condition_slug for fp in self.fingerprints if fp.condition_slug != "unknown"
        ))

        # ── Title block pattern ──
        profile.title_block_pattern = self._extract_title_block_pattern()

        # ── Formatting ──
        profile.primary_font, profile.body_font_size, profile.heading_sizes = (
            self._extract_formatting_patterns()
        )

        # ── Document type patterns ──
        profile.doc_type_patterns = self._extract_doc_type_patterns()

        # ── Boilerplate blocks ──
        profile.boilerplate_blocks = self._extract_boilerplate_blocks()

        # ── Table patterns ──
        profile.table_patterns = self._extract_table_patterns()

        # ── Section patterns ──
        profile.section_patterns = self._extract_section_patterns()

        logger.info(
            "Extracted master profile: %d doc types, %d boilerplate blocks, "
            "%d table patterns, %d section patterns",
            len(profile.doc_type_patterns),
            len(profile.boilerplate_blocks),
            len(profile.table_patterns),
            len(profile.section_patterns),
        )
        return profile

    def _extract_title_block_pattern(self) -> list[str]:
        """Extract the common title block pattern."""
        # The title block is the first few lines, with condition name replaced by {condition}
        if not self.fingerprints:
            return []

        # Take the first document and generalize its title block
        first = self.fingerprints[0]
        pattern = []
        for line in first.title_block:
            # Replace condition-specific text with placeholder
            generalized = line
            if first.condition_slug and first.condition_slug != "unknown":
                # Try to find and replace the condition name
                for fp in self.fingerprints[:5]:
                    if fp.title and "—" in fp.title:
                        cond_part = fp.title.split("—")[-1].strip()
                        if cond_part in generalized:
                            generalized = generalized.replace(cond_part, "{condition_name}")
                            break
            pattern.append(generalized)
        return pattern

    def _extract_formatting_patterns(self) -> tuple[str, float, dict]:
        """Extract shared formatting: font, body size, heading sizes."""
        font_counter = Counter()
        size_counter = Counter()

        for fp in self.fingerprints:
            for f in fp.fonts_used:
                font_counter[f] += 1
            for s in fp.font_sizes:
                size_counter[s] += 1

        primary_font = font_counter.most_common(1)[0][0] if font_counter else "Calibri"

        # Body text is typically 11pt
        body_size = 11.0
        if size_counter:
            body_size = size_counter.most_common(1)[0][0]

        # Heading sizes by convention
        heading_sizes = {1: 16.0, 2: 14.0, 3: 12.0}
        all_sizes = sorted(size_counter.keys(), reverse=True)
        if len(all_sizes) >= 3:
            heading_sizes = {1: all_sizes[0], 2: all_sizes[1], 3: all_sizes[2]}

        return primary_font, body_size, heading_sizes

    def _extract_doc_type_patterns(self) -> dict[str, DocumentTypePattern]:
        """Extract structural pattern for each document type."""
        by_doc_type = defaultdict(list)
        for fp in self.fingerprints:
            if fp.doc_type != "unknown":
                by_doc_type[fp.doc_type].append(fp)

        patterns = {}
        for doc_type, fps in by_doc_type.items():
            dtp = DocumentTypePattern(doc_type=doc_type)
            dtp.conditions_analyzed = len(fps)

            # Average metrics
            dtp.typical_section_count = round(sum(len(fp.sections) for fp in fps) / len(fps))
            dtp.typical_table_count = round(sum(fp.total_tables for fp in fps) / len(fps))
            dtp.typical_word_count = round(sum(fp.total_words for fp in fps) / len(fps))
            dtp.typical_paragraph_count = round(sum(fp.total_paragraphs for fp in fps) / len(fps))

            # Most common section order (from first document as reference)
            if fps:
                dtp.typical_section_order = [s.section_id for s in fps[0].sections]

            # Title template
            titles = [fp.title for fp in fps if fp.title]
            if titles:
                # Find the common prefix/suffix pattern
                dtp.title_template = _generalize_title(titles)

            # Table patterns for this doc type
            for fp in fps:
                for tf in fp.tables:
                    tp = TablePattern(
                        pattern_id=f"{doc_type}_table_{tf.index}",
                        headers=tf.headers,
                        col_count=tf.col_count,
                        typical_row_count=tf.row_count,
                        found_in_doc_types=[doc_type],
                    )
                    dtp.table_patterns.append(tp)

            patterns[doc_type] = dtp

        return patterns

    def _extract_boilerplate_blocks(self) -> list[BoilerplateBlock]:
        """Find sections with identical content across conditions."""
        # Group sections by content_hash
        hash_to_sections = defaultdict(list)
        for fp in self.fingerprints:
            for s in fp.sections:
                if s.content_hash and s.is_boilerplate:
                    hash_to_sections[s.content_hash].append((fp.condition_slug, s))

        blocks = []
        for content_hash, items in hash_to_sections.items():
            conditions = list(set(cond for cond, _ in items))
            if len(conditions) >= 2:  # appears in at least 2 conditions
                _, section = items[0]
                block = BoilerplateBlock(
                    block_id=f"bp_{section.section_id}",
                    content_hash=content_hash,
                    section_title=section.title,
                    found_in=conditions,
                    is_universal=len(conditions) >= len(set(
                        fp.condition_slug for fp in self.fingerprints
                        if fp.condition_slug != "unknown"
                    )) * 0.8,
                )
                blocks.append(block)

        return blocks

    def _extract_table_patterns(self) -> list[TablePattern]:
        """Extract reusable table column patterns."""
        # Group by header tuple
        header_groups = defaultdict(list)
        for fp in self.fingerprints:
            for tf in fp.tables:
                key = tuple(tf.headers)
                header_groups[key].append((fp.doc_type, fp.condition_slug, tf))

        patterns = []
        for headers, items in header_groups.items():
            if not headers:
                continue
            doc_types = list(set(dt for dt, _, _ in items))
            tp = TablePattern(
                pattern_id=f"table_{'_'.join(h[:10].lower().replace(' ', '') for h in headers[:3])}",
                headers=list(headers),
                col_count=len(headers),
                typical_row_count=round(sum(tf.row_count for _, _, tf in items) / len(items)),
                found_in_doc_types=doc_types,
                occurrence_count=len(items),
            )
            patterns.append(tp)

        # Sort by frequency
        patterns.sort(key=lambda p: p.occurrence_count, reverse=True)
        return patterns

    def _extract_section_patterns(self) -> list[SectionPattern]:
        """Extract section ordering and classification patterns."""
        section_stats = defaultdict(lambda: {
            "positions": [], "word_counts": [], "doc_types": set(),
            "boilerplate_count": 0, "total_count": 0, "title": "",
        })

        for fp in self.fingerprints:
            for i, s in enumerate(fp.sections):
                stats = section_stats[s.section_id]
                stats["positions"].append(i)
                stats["word_counts"].append(s.word_count)
                stats["doc_types"].add(fp.doc_type)
                stats["total_count"] += 1
                if s.is_boilerplate:
                    stats["boilerplate_count"] += 1
                if not stats["title"]:
                    stats["title"] = s.title

        patterns = []
        for section_id, stats in section_stats.items():
            sp = SectionPattern(
                section_id=section_id,
                typical_title=stats["title"],
                typical_position=round(sum(stats["positions"]) / len(stats["positions"])),
                typical_word_count=round(sum(stats["word_counts"]) / len(stats["word_counts"])),
                is_boilerplate=stats["boilerplate_count"] > stats["total_count"] * 0.7,
                is_variable=stats["boilerplate_count"] < stats["total_count"] * 0.3,
                found_in_doc_types=sorted(stats["doc_types"]),
                occurrence_count=stats["total_count"],
            )
            patterns.append(sp)

        patterns.sort(key=lambda p: p.occurrence_count, reverse=True)
        return patterns


def save_profile(profile: MasterTemplateProfile, output_path: Path) -> None:
    """Save master profile to JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(profile.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )
    logger.info("Saved master profile to %s", output_path)


def load_profile(input_path: Path) -> dict:
    """Load master profile from JSON (returns raw dict)."""
    return json.loads(Path(input_path).read_text(encoding="utf-8"))


# ── Helpers ──────────────────────────────────────────────────────────────

def _generalize_title(titles: list[str]) -> str:
    """Find the common title pattern, replacing condition names with {condition_name}."""
    if not titles:
        return ""
    # Split by — and take the prefix
    prefixes = []
    for t in titles:
        if "—" in t:
            prefixes.append(t.split("—")[0].strip())
        elif "–" in t:
            prefixes.append(t.split("–")[0].strip())
    if prefixes:
        # Most common prefix
        common = Counter(prefixes).most_common(1)[0][0]
        return f"{common} — {{condition_name}}"
    return titles[0]
