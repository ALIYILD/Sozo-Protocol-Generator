"""
Pydantic models for patient records, session records, outcomes, and treatment plans.

These models form the persistence layer for SOZO treatment data.
SessionRecord is designed to be easily created from the existing SessionResult dataclass
in sozo_session.manager.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ── Patient ─────────────────────────────────────────────────────────────


class Patient(BaseModel):
    """A patient registered in the SOZO system."""

    patient_id: str = Field(default_factory=lambda: _new_id("pat"))
    name: str = ""
    date_of_birth: Optional[date] = None
    condition_slugs: list[str] = Field(default_factory=list)
    phenotype_slug: str = ""
    severity: str = ""  # e.g. mild / moderate / severe
    medications: list[str] = Field(default_factory=list)
    contraindications: list[str] = Field(default_factory=list)
    notes: str = ""
    created_at: datetime = Field(default_factory=_utc_now)


# ── Session Record ──────────────────────────────────────────────────────


class SessionRecord(BaseModel):
    """Persistent record of a single treatment session.

    Can be constructed directly from a ``SessionResult`` + ``SessionState``
    returned by ``SessionManager.run_session``.
    """

    session_id: str = Field(default_factory=lambda: _new_id("sess"))
    patient_id: str = ""
    clinician_id: str = ""
    condition_slug: str = ""
    protocol_name: str = ""
    tier: str = ""
    status: str = "scheduled"  # scheduled | in_progress | completed | aborted
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_min: float = 0.0
    steps_completed: int = 0
    steps_total: int = 0
    adverse_events: list[str] = Field(default_factory=list)
    impedance_pre: dict[str, float] = Field(default_factory=dict)
    impedance_post: dict[str, float] = Field(default_factory=dict)
    outcome_scores: dict[str, float] = Field(default_factory=dict)
    notes: str = ""

    @classmethod
    def from_session_result(
        cls,
        result,  # SessionResult (dataclass — no Pydantic import needed)
        *,
        condition_slug: str = "",
        protocol_name: str = "",
        tier: str = "",
        clinician_id: str = "",
    ) -> "SessionRecord":
        """Build a SessionRecord from a manager.SessionResult."""

        def _parse_ts(ts_str: str) -> Optional[datetime]:
            if not ts_str:
                return None
            return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))

        return cls(
            session_id=result.session_id,
            patient_id=result.patient_id,
            clinician_id=clinician_id,
            condition_slug=condition_slug,
            protocol_name=protocol_name,
            tier=tier,
            status=result.status,
            started_at=_parse_ts(result.started_at),
            completed_at=_parse_ts(result.completed_at),
            duration_min=result.duration_min,
            steps_completed=result.steps_completed,
            steps_total=result.steps_total,
            adverse_events=list(result.adverse_events),
            impedance_pre=dict(result.impedance_pre),
            impedance_post=dict(result.impedance_post),
        )


# ── Outcome Record ──────────────────────────────────────────────────────


class OutcomeRecord(BaseModel):
    """A single clinical outcome measurement."""

    outcome_id: str = Field(default_factory=lambda: _new_id("out"))
    patient_id: str = ""
    session_id: str = ""
    assessment_tool: str = ""  # e.g. PHQ-9, GAD-7, MADRS
    score: float = 0.0
    score_max: float = 0.0
    timepoint: str = "baseline"  # baseline | week4 | week8 | endpoint
    recorded_at: datetime = Field(default_factory=_utc_now)
    clinician_id: str = ""
    interpretation: str = ""
    responder_classification: Optional[str] = None  # e.g. responder / non-responder / remitter


# ── Treatment Plan ──────────────────────────────────────────────────────


class TreatmentPlan(BaseModel):
    """A planned course of treatment for a patient."""

    plan_id: str = Field(default_factory=lambda: _new_id("plan"))
    patient_id: str = ""
    condition_slug: str = ""
    tier: str = ""
    protocol_sequence_id: str = ""
    total_sessions: int = 0
    sessions_per_week: int = 0
    start_date: Optional[date] = None
    status: str = "planned"  # planned | active | completed | suspended
    personalization_notes: str = ""
    clinician_id: str = ""
