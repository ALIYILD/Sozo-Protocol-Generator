"""
Pilot instrumentation — operator activity logging and metrics summary.
Tracks review decisions, exports, report downloads, and onboarding actions.
"""
from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class ActivityEvent:
    """A single logged operator activity."""
    timestamp: str = ""
    action: str = ""          # approve, reject, flag, export, download_report, onboard, generate, qa_run
    operator: str = ""
    build_id: str = ""
    condition_slug: str = ""
    document_type: str = ""
    detail: str = ""

@dataclass
class PilotMetrics:
    """Aggregated pilot metrics summary."""
    period_start: str = ""
    period_end: str = ""
    total_events: int = 0
    docs_reviewed: int = 0
    docs_approved: int = 0
    docs_rejected: int = 0
    docs_flagged: int = 0
    docs_exported: int = 0
    reports_downloaded: int = 0
    conditions_onboarded: int = 0
    docs_generated: int = 0
    qa_runs: int = 0
    evidence_gap_count: int = 0
    stale_evidence_count: int = 0
    unique_operators: list[str] = field(default_factory=list)
    avg_review_turnaround_hours: Optional[float] = None
    by_condition: dict[str, int] = field(default_factory=dict)

class ActivityLogger:
    """Logs operator activities to a JSON-lines file."""

    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self.log_dir / "activity_log.jsonl"

    def log(self, action: str, operator: str = "", build_id: str = "",
            condition_slug: str = "", document_type: str = "", detail: str = "") -> None:
        event = ActivityEvent(
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action, operator=operator, build_id=build_id,
            condition_slug=condition_slug, document_type=document_type, detail=detail,
        )
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(asdict(event), default=str) + "\n")
        except Exception as e:
            logger.warning("Failed to log activity: %s", e)

    def get_events(self, since: str = None) -> list[ActivityEvent]:
        """Load all events, optionally filtered to those after `since` timestamp."""
        events = []
        if not self._log_file.exists():
            return events
        with open(self._log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    ev = ActivityEvent(**{k: v for k, v in d.items() if k in ActivityEvent.__dataclass_fields__})
                    if since and ev.timestamp < since:
                        continue
                    events.append(ev)
                except Exception:
                    pass
        return events

    def compute_metrics(self, since: str = None) -> PilotMetrics:
        """Compute aggregated pilot metrics from the activity log."""
        events = self.get_events(since=since)
        m = PilotMetrics(
            period_start=events[0].timestamp if events else "",
            period_end=events[-1].timestamp if events else "",
            total_events=len(events),
        )
        operators = set()
        conditions = {}
        # Track review turnaround: time between first 'needs_review' event and approve/reject
        review_starts = {}  # build_id -> timestamp
        turnarounds = []

        for ev in events:
            operators.add(ev.operator) if ev.operator else None
            if ev.condition_slug:
                conditions[ev.condition_slug] = conditions.get(ev.condition_slug, 0) + 1

            if ev.action == "approve":
                m.docs_approved += 1
                m.docs_reviewed += 1
                if ev.build_id in review_starts:
                    try:
                        start = datetime.fromisoformat(review_starts[ev.build_id])
                        end = datetime.fromisoformat(ev.timestamp)
                        hours = (end - start).total_seconds() / 3600
                        turnarounds.append(hours)
                    except Exception:
                        pass
            elif ev.action == "reject":
                m.docs_rejected += 1
                m.docs_reviewed += 1
            elif ev.action == "flag":
                m.docs_flagged += 1
            elif ev.action == "export":
                m.docs_exported += 1
            elif ev.action == "download_report":
                m.reports_downloaded += 1
            elif ev.action == "onboard":
                m.conditions_onboarded += 1
            elif ev.action == "generate":
                m.docs_generated += 1
            elif ev.action == "qa_run":
                m.qa_runs += 1
            elif ev.action == "submit_review":
                review_starts[ev.build_id] = ev.timestamp

        m.unique_operators = sorted(operators - {""})
        m.by_condition = conditions
        if turnarounds:
            m.avg_review_turnaround_hours = round(sum(turnarounds) / len(turnarounds), 2)
        return m

    def format_metrics_markdown(self, metrics: PilotMetrics) -> str:
        """Format metrics as markdown for display or export."""
        lines = [
            "# Pilot Metrics Summary",
            f"Period: {metrics.period_start[:10] if metrics.period_start else '?'} to {metrics.period_end[:10] if metrics.period_end else '?'}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total events | {metrics.total_events} |",
            f"| Documents reviewed | {metrics.docs_reviewed} |",
            f"| Documents approved | {metrics.docs_approved} |",
            f"| Documents rejected | {metrics.docs_rejected} |",
            f"| Documents flagged | {metrics.docs_flagged} |",
            f"| Documents exported | {metrics.docs_exported} |",
            f"| Documents generated | {metrics.docs_generated} |",
            f"| QA runs | {metrics.qa_runs} |",
            f"| Reports downloaded | {metrics.reports_downloaded} |",
            f"| Conditions onboarded | {metrics.conditions_onboarded} |",
            f"| Unique operators | {len(metrics.unique_operators)} |",
            f"| Avg review turnaround | {metrics.avg_review_turnaround_hours or 'N/A'} hours |",
        ]
        if metrics.by_condition:
            lines.extend(["", "**Activity by condition:**", ""])
            for cond, count in sorted(metrics.by_condition.items(), key=lambda x: -x[1]):
                lines.append(f"- {cond}: {count} events")
        return "\n".join(lines)
