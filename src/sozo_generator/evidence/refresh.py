"""
Evidence refresh -- re-evaluates evidence for a condition, marks stale
evidence, triggers QA re-run, and supports recency controls.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..schemas.condition import ConditionSchema
from ..schemas.contracts import EvidenceBundle, QAReport
from ..evidence.section_evidence_mapper import SectionEvidenceMapper, DocumentEvidenceProfile
from ..evidence.confidence import assign_confidence, get_clinical_language
from ..core.enums import EvidenceLevel, ConfidenceLabel

logger = logging.getLogger(__name__)

@dataclass
class EvidenceRefreshResult:
    """Result of an evidence refresh operation."""
    condition_slug: str = ""
    refreshed_at: str = ""
    total_items: int = 0
    stale_items: int = 0  # older than recency window
    fresh_items: int = 0
    stale_sections: list[str] = field(default_factory=list)
    confidence_changes: list[dict] = field(default_factory=list)  # {section, old, new}
    qa_rerun_needed: bool = False
    qa_report: Optional[QAReport] = None

class EvidenceRefresher:
    """Manages evidence refresh operations."""

    def __init__(self, recency_years: int = 5):
        self.recency_years = recency_years
        self.mapper = SectionEvidenceMapper(recency_years=recency_years)

    def assess_staleness(self, condition: ConditionSchema) -> EvidenceRefreshResult:
        """Check how stale the evidence is for a condition WITHOUT re-fetching.
        Uses existing references and assessment tools."""
        result = EvidenceRefreshResult(
            condition_slug=condition.slug,
            refreshed_at=datetime.now().isoformat(),
        )

        items = self.mapper.build_evidence_items_from_condition(condition)
        result.total_items = len(items)

        current_year = datetime.now().year
        cutoff = current_year - self.recency_years

        for item in items:
            if item.year and item.year < cutoff:
                result.stale_items += 1
            elif item.year:
                result.fresh_items += 1
            # Items without year are not counted either way

        # Determine stale sections by mapping
        from ..schemas.documents import DocumentSpec, SectionContent
        from ..core.enums import DocumentType, Tier
        from ..content.assembler import ContentAssembler

        assembler = ContentAssembler()
        try:
            sections = assembler.assemble(condition, DocumentType.EVIDENCE_BASED_PROTOCOL, Tier.FELLOW)
            spec = DocumentSpec(
                document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
                tier=Tier.FELLOW,
                condition_slug=condition.slug,
                condition_name=condition.display_name,
                title="Evidence Refresh Check",
                sections=sections,
            )
            profile = self.mapper.map_to_sections(spec, items)
            result.stale_sections = profile.outdated_sections
        except Exception as e:
            logger.warning("Could not map sections for staleness: %s", e)

        result.qa_rerun_needed = result.stale_items > result.total_items * 0.5
        return result

    def refresh_and_rerun_qa(self, condition: ConditionSchema) -> EvidenceRefreshResult:
        """Assess staleness and re-run QA if needed."""
        result = self.assess_staleness(condition)

        if result.qa_rerun_needed:
            try:
                from ..qa.engine import QAEngine
                engine = QAEngine()
                qa_report = engine.run_condition_qa(condition)
                qa_report.compute_counts()
                result.qa_report = qa_report
            except Exception as e:
                logger.warning("QA re-run failed: %s", e)

        return result

    def set_recency(self, years: int) -> None:
        """Update the recency window."""
        self.recency_years = years
        self.mapper = SectionEvidenceMapper(recency_years=years)
