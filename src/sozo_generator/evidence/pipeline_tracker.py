"""
PRISMA pipeline tracker — auditable record of every evidence decision.

Tracks the lifecycle of each study through the PRISMA 2020 stages:
  Identification → Deduplication → Screening → Eligibility → Extraction → Scoring

Every decision is logged with who/what made it, why, and when.
The full log can be used to auto-generate a PRISMA flow diagram.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """PRISMA 2020 pipeline stages."""
    IDENTIFICATION = "identification"
    DEDUPLICATION = "deduplication"
    SCREENING = "screening"
    ELIGIBILITY = "eligibility"
    EXTRACTION = "extraction"
    SCORING = "scoring"
    GROUNDING = "grounding"


class PipelineDecision(str, Enum):
    """Possible decisions at each stage."""
    INCLUDE = "include"
    EXCLUDE = "exclude"
    UNCERTAIN = "uncertain"
    MERGED = "merged"  # dedup stage
    EXTRACTED = "extracted"
    SCORED = "scored"
    GROUNDED = "grounded"
    ERROR = "error"


@dataclass
class PipelineEvent:
    """A single decision event in the evidence pipeline."""

    event_id: str = ""
    study_identifier: str = ""  # PMID, DOI, or title hash
    source: str = ""  # pubmed, crossref, semantic_scholar, manual
    stage: str = ""
    decision: str = ""
    reason: str = ""
    confidence: float = 0.0
    decided_by: str = "system"  # system, llm:{model}, clinician:{user_id}
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
        if not self.event_id:
            self.event_id = f"evt-{self.stage}-{hash(self.study_identifier) % 100000:05d}"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "study_identifier": self.study_identifier,
            "source": self.source,
            "stage": self.stage,
            "decision": self.decision,
            "reason": self.reason,
            "confidence": self.confidence,
            "decided_by": self.decided_by,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class PRISMAFlowCounts:
    """Aggregate counts for PRISMA flow diagram generation."""

    # Identification
    records_identified: int = 0
    records_by_source: dict[str, int] = field(default_factory=dict)

    # Deduplication
    duplicates_removed: int = 0
    records_after_dedup: int = 0

    # Screening
    records_screened: int = 0
    records_excluded_screening: int = 0
    screening_exclusion_reasons: dict[str, int] = field(default_factory=dict)

    # Eligibility
    reports_sought: int = 0
    reports_not_retrieved: int = 0
    reports_assessed: int = 0
    reports_excluded_eligibility: int = 0
    eligibility_exclusion_reasons: dict[str, int] = field(default_factory=dict)

    # Included
    studies_included: int = 0
    studies_extracted: int = 0
    studies_scored: int = 0
    studies_grounded: int = 0


class PipelineTracker:
    """Tracks evidence pipeline decisions for PRISMA audit trail.

    All events are logged in-memory and optionally persisted to disk.
    The tracker can produce PRISMA flow counts at any time.
    """

    def __init__(self, persist_dir: Optional[Path] = None):
        self._events: list[PipelineEvent] = []
        self._persist_dir = Path(persist_dir) if persist_dir else None
        if self._persist_dir:
            self._persist_dir.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        study_identifier: str,
        stage: PipelineStage,
        decision: PipelineDecision,
        reason: str = "",
        confidence: float = 0.0,
        decided_by: str = "system",
        source: str = "",
        metadata: Optional[dict] = None,
    ) -> PipelineEvent:
        """Log a pipeline decision event."""
        event = PipelineEvent(
            study_identifier=study_identifier,
            source=source,
            stage=stage.value,
            decision=decision.value,
            reason=reason,
            confidence=confidence,
            decided_by=decided_by,
            metadata=metadata or {},
        )
        self._events.append(event)
        logger.debug(
            "Pipeline: %s → %s/%s (by %s): %s",
            study_identifier[:30], stage.value, decision.value,
            decided_by, reason[:80],
        )
        return event

    def log_identification(
        self, study_identifier: str, source: str,
    ) -> PipelineEvent:
        """Shortcut: log a study identified from a source."""
        return self.log(
            study_identifier=study_identifier,
            stage=PipelineStage.IDENTIFICATION,
            decision=PipelineDecision.INCLUDE,
            reason=f"Identified from {source} search",
            source=source,
        )

    def log_dedup(
        self,
        study_identifier: str,
        merged_into: str = "",
        is_duplicate: bool = True,
    ) -> PipelineEvent:
        """Shortcut: log a deduplication decision."""
        if is_duplicate:
            return self.log(
                study_identifier=study_identifier,
                stage=PipelineStage.DEDUPLICATION,
                decision=PipelineDecision.MERGED,
                reason=f"Duplicate of {merged_into}",
            )
        return self.log(
            study_identifier=study_identifier,
            stage=PipelineStage.DEDUPLICATION,
            decision=PipelineDecision.INCLUDE,
            reason="Unique record after deduplication",
        )

    def log_screening(
        self,
        study_identifier: str,
        decision: PipelineDecision,
        reason: str,
        confidence: float = 0.0,
        decided_by: str = "system",
    ) -> PipelineEvent:
        """Shortcut: log a screening decision."""
        return self.log(
            study_identifier=study_identifier,
            stage=PipelineStage.SCREENING,
            decision=decision,
            reason=reason,
            confidence=confidence,
            decided_by=decided_by,
        )

    def get_prisma_counts(self) -> PRISMAFlowCounts:
        """Compute PRISMA flow diagram counts from logged events."""
        counts = PRISMAFlowCounts()

        for event in self._events:
            stage = event.stage
            decision = event.decision

            if stage == PipelineStage.IDENTIFICATION.value:
                counts.records_identified += 1
                source = event.source or "unknown"
                counts.records_by_source[source] = (
                    counts.records_by_source.get(source, 0) + 1
                )

            elif stage == PipelineStage.DEDUPLICATION.value:
                if decision == PipelineDecision.MERGED.value:
                    counts.duplicates_removed += 1
                elif decision == PipelineDecision.INCLUDE.value:
                    counts.records_after_dedup += 1

            elif stage == PipelineStage.SCREENING.value:
                counts.records_screened += 1
                if decision == PipelineDecision.EXCLUDE.value:
                    counts.records_excluded_screening += 1
                    reason = event.reason[:50] or "unspecified"
                    counts.screening_exclusion_reasons[reason] = (
                        counts.screening_exclusion_reasons.get(reason, 0) + 1
                    )

            elif stage == PipelineStage.ELIGIBILITY.value:
                counts.reports_assessed += 1
                if decision == PipelineDecision.EXCLUDE.value:
                    counts.reports_excluded_eligibility += 1
                    reason = event.reason[:50] or "unspecified"
                    counts.eligibility_exclusion_reasons[reason] = (
                        counts.eligibility_exclusion_reasons.get(reason, 0) + 1
                    )

            elif stage == PipelineStage.EXTRACTION.value:
                if decision == PipelineDecision.EXTRACTED.value:
                    counts.studies_extracted += 1

            elif stage == PipelineStage.SCORING.value:
                if decision == PipelineDecision.SCORED.value:
                    counts.studies_scored += 1

            elif stage == PipelineStage.GROUNDING.value:
                if decision == PipelineDecision.GROUNDED.value:
                    counts.studies_grounded += 1

        counts.studies_included = counts.studies_extracted
        return counts

    def get_events_for_study(self, study_identifier: str) -> list[PipelineEvent]:
        """Get all events for a specific study."""
        return [e for e in self._events if e.study_identifier == study_identifier]

    def get_events_for_stage(self, stage: PipelineStage) -> list[PipelineEvent]:
        """Get all events for a specific pipeline stage."""
        return [e for e in self._events if e.stage == stage.value]

    @property
    def events(self) -> list[PipelineEvent]:
        return list(self._events)

    @property
    def event_count(self) -> int:
        return len(self._events)

    def persist(self, condition_slug: str) -> Optional[Path]:
        """Save all events to a JSON file."""
        if not self._persist_dir:
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        filename = f"pipeline-{condition_slug}-{timestamp}.json"
        filepath = self._persist_dir / filename

        data = {
            "condition_slug": condition_slug,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "event_count": len(self._events),
            "prisma_counts": self.get_prisma_counts().__dict__,
            "events": [e.to_dict() for e in self._events],
        }

        filepath.write_text(json.dumps(data, indent=2, default=str))
        logger.info("Persisted %d pipeline events to %s", len(self._events), filepath)
        return filepath

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()
