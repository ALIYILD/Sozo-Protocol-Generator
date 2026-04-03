"""
Regression Comparison — compares legacy vs canonical output for migration safety.

Provides structured semantic comparison between generation paths,
focused on section presence, evidence coverage, and content quality
rather than brittle binary DOCX diffs.

Usage:
    from sozo_generator.knowledge.regression import compare_outputs

    report = compare_outputs("parkinsons", "evidence_based_protocol", "fellow")
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from ..schemas.documents import DocumentSpec

logger = logging.getLogger(__name__)


@dataclass
class ComparisonResult:
    """Structured comparison between legacy and canonical outputs."""

    condition: str
    doc_type: str
    tier: str

    # Section comparison
    legacy_section_count: int = 0
    canonical_section_count: int = 0
    sections_in_both: list[str] = field(default_factory=list)
    sections_only_legacy: list[str] = field(default_factory=list)
    sections_only_canonical: list[str] = field(default_factory=list)

    # Content comparison
    legacy_total_chars: int = 0
    canonical_total_chars: int = 0

    # Evidence comparison
    legacy_ref_count: int = 0
    canonical_ref_count: int = 0

    # Table comparison
    legacy_table_count: int = 0
    canonical_table_count: int = 0

    # Quality
    canonical_readiness: str = ""
    canonical_placeholders: int = 0

    @property
    def parity_score(self) -> float:
        """0-1 score of structural parity between legacy and canonical."""
        if self.legacy_section_count == 0:
            return 0.0
        overlap = len(self.sections_in_both)
        total_unique = len(set(
            self.sections_in_both + self.sections_only_legacy + self.sections_only_canonical
        ))
        return overlap / max(total_unique, 1)

    @property
    def safe_to_route(self) -> bool:
        """Whether canonical can safely replace legacy."""
        return (
            self.canonical_section_count >= self.legacy_section_count * 0.8
            and self.canonical_ref_count >= self.legacy_ref_count * 0.5
            and self.canonical_placeholders <= 2
        )

    def to_text(self) -> str:
        lines = [
            f"=== REGRESSION COMPARISON ===",
            f"Condition: {self.condition} / {self.doc_type} / {self.tier}",
            f"",
            f"Sections: legacy={self.legacy_section_count}, canonical={self.canonical_section_count}",
            f"  In both:         {len(self.sections_in_both)}",
            f"  Only legacy:     {self.sections_only_legacy or '(none)'}",
            f"  Only canonical:  {self.sections_only_canonical or '(none)'}",
            f"",
            f"Content: legacy={self.legacy_total_chars} chars, canonical={self.canonical_total_chars} chars",
            f"References: legacy={self.legacy_ref_count}, canonical={self.canonical_ref_count}",
            f"Tables: legacy={self.legacy_table_count}, canonical={self.canonical_table_count}",
            f"",
            f"Canonical readiness: {self.canonical_readiness}",
            f"Canonical placeholders: {self.canonical_placeholders}",
            f"Parity score: {self.parity_score:.0%}",
            f"Safe to route: {'YES' if self.safe_to_route else 'NO'}",
        ]
        return "\n".join(lines)


def compare_outputs(
    condition: str,
    doc_type: str,
    tier: str,
) -> Optional[ComparisonResult]:
    """Compare legacy and canonical generation for the same condition/doc/tier.

    Returns None if comparison is not possible (e.g., condition not in both systems).
    """
    try:
        from ..conditions.registry import get_registry
        from ..docx.exporter import DocumentExporter
        from ..core.enums import DocumentType, Tier
        from .base import KnowledgeBase
        from .assembler import CanonicalDocumentAssembler

        # Build legacy spec
        registry = get_registry()
        if not registry.exists(condition):
            return None

        schema = registry.get(condition)
        exporter = DocumentExporter()
        try:
            dt_enum = DocumentType(doc_type)
            tier_enum = Tier(tier)
            legacy_spec = exporter._build_spec(schema, dt_enum, tier_enum)
        except Exception:
            return None

        # Build canonical spec
        kb = KnowledgeBase()
        kb.load_all()
        if not kb.get_condition(condition) or not kb.get_blueprint(doc_type):
            return None

        assembler = CanonicalDocumentAssembler(kb)
        canon_spec, provenance = assembler.assemble(condition, doc_type, tier)

        # Compare
        result = ComparisonResult(condition=condition, doc_type=doc_type, tier=tier)

        legacy_ids = {s.section_id for s in legacy_spec.sections}
        canon_ids = {s.section_id for s in canon_spec.sections}

        result.legacy_section_count = len(legacy_spec.sections)
        result.canonical_section_count = len(canon_spec.sections)
        result.sections_in_both = sorted(legacy_ids & canon_ids)
        result.sections_only_legacy = sorted(legacy_ids - canon_ids)
        result.sections_only_canonical = sorted(canon_ids - legacy_ids)

        result.legacy_total_chars = sum(len(s.content) for s in legacy_spec.sections)
        result.canonical_total_chars = sum(len(s.content) for s in canon_spec.sections)

        result.legacy_ref_count = len(legacy_spec.references)
        result.canonical_ref_count = len(canon_spec.references)

        result.legacy_table_count = sum(len(s.tables) for s in legacy_spec.sections)
        result.canonical_table_count = sum(len(s.tables) for s in canon_spec.sections)

        result.canonical_readiness = provenance.readiness
        result.canonical_placeholders = provenance.placeholder_sections

        return result

    except Exception as e:
        logger.warning(f"Comparison failed: {e}")
        return None
