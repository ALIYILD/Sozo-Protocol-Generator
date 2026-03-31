"""
Template content extractor — extracts specific content blocks from parsed templates.
Used to pull Gold Standard content for comparison and gap analysis.
"""
import logging
import re
from pathlib import Path
from typing import Optional

from .parser import TemplateParser, ParsedSection

logger = logging.getLogger(__name__)


class ContentBlock:
    """A named block of extracted content from a template."""

    def __init__(
        self,
        block_id: str,
        source_section: str,
        content: str,
        content_type: str = "text",  # text | table | list | mixed
        is_placeholder: bool = False,
        word_count: int = 0,
    ):
        self.block_id = block_id
        self.source_section = source_section
        self.content = content
        self.content_type = content_type
        self.is_placeholder = is_placeholder
        self.word_count = word_count or len(content.split())

    def __repr__(self) -> str:
        return f"ContentBlock(id={self.block_id!r}, type={self.content_type!r}, words={self.word_count})"


class TemplateExtractor:
    """
    Extracts typed content blocks from a parsed template.
    Supports extraction of:
    - Protocol parameters
    - Clinical overview text
    - Phenotype descriptions
    - Assessment scale references
    - Safety notes
    """

    def __init__(self, parser: TemplateParser):
        self.parser = parser
        self._blocks: list[ContentBlock] = []

    def extract_all(self) -> list[ContentBlock]:
        """Extract all content blocks from all parsed sections."""
        blocks = []
        for section in self.parser.sections:
            block = self._extract_section_block(section)
            if block:
                blocks.append(block)
        self._blocks = blocks
        logger.info(f"Extracted {len(blocks)} content blocks")
        return blocks

    def _extract_section_block(self, section: ParsedSection) -> Optional[ContentBlock]:
        """Extract a content block from a single section."""
        if not section.raw_content.strip():
            return None

        content_type = self._infer_content_type(section.raw_content)
        is_placeholder = section.placeholder_count > 0

        return ContentBlock(
            block_id=section.section_id,
            source_section=section.title,
            content=section.raw_content,
            content_type=content_type,
            is_placeholder=is_placeholder,
        )

    def _infer_content_type(self, text: str) -> str:
        """Infer content type from text structure."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        if not lines:
            return "text"

        # Check for list patterns
        bullet_count = sum(1 for l in lines if l.startswith(("•", "-", "*", "–")) or re.match(r"^\d+[\.\)]\s", l))
        if bullet_count > len(lines) * 0.5:
            return "list"

        # Check for table-like patterns (pipe-separated or tab-separated)
        table_count = sum(1 for l in lines if "|" in l or "\t" in l)
        if table_count > len(lines) * 0.3:
            return "table"

        return "text"

    def get_block(self, block_id: str) -> Optional[ContentBlock]:
        """Get a content block by ID."""
        for block in self._blocks:
            if block.block_id == block_id:
                return block
        return None

    def get_blocks_by_type(self, content_type: str) -> list[ContentBlock]:
        """Get all blocks of a specific type."""
        return [b for b in self._blocks if b.content_type == content_type]

    def get_placeholder_blocks(self) -> list[ContentBlock]:
        """Get all blocks containing placeholders."""
        return [b for b in self._blocks if b.is_placeholder]

    def extract_protocol_parameters(self) -> dict[str, dict]:
        """
        Extract protocol parameter tables from template sections.
        Returns dict keyed by protocol_id.
        """
        protocols = {}
        for section in self.parser.sections:
            if any(kw in section.section_id for kw in ["protocol", "tdcs", "tps", "tavns", "ces"]):
                params = self._parse_parameter_table(section.raw_content)
                if params:
                    protocols[section.section_id] = params
        return protocols

    def _parse_parameter_table(self, text: str) -> dict:
        """Parse key:value parameter pairs from text."""
        params = {}
        for line in text.split("\n"):
            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(" ", "_")
                    value = parts[1].strip()
                    if key and value and len(key) < 50:
                        params[key] = value
        return params

    def compare_with_generated(
        self,
        generated_section_ids: list[str],
    ) -> dict[str, list[str]]:
        """
        Compare template section IDs with generated section IDs.
        Returns dict with 'missing', 'extra', and 'matched' lists.
        """
        template_ids = set(self.parser.get_section_ids())
        generated_ids = set(generated_section_ids)

        return {
            "missing": sorted(template_ids - generated_ids),
            "extra": sorted(generated_ids - template_ids),
            "matched": sorted(template_ids & generated_ids),
        }

    @property
    def blocks(self) -> list[ContentBlock]:
        return self._blocks

    @property
    def total_word_count(self) -> int:
        return sum(b.word_count for b in self._blocks)
