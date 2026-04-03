"""Treatment session model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, UUIDMixin


class TreatmentSession(UUIDMixin, Base):
    __tablename__ = "treatment_sessions"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    protocol_version_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("protocol_versions.id"),
        nullable=False,
    )
    session_number: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    parameters_used: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    side_effects: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    clinician_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome_measures: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    conducted_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="treatment_sessions")  # noqa: F821
    protocol_version: Mapped["ProtocolVersion"] = relationship(  # noqa: F821
        "ProtocolVersion", back_populates="sessions"
    )

    __table_args__ = (
        Index("ix_sessions_patient", "patient_id"),
        Index("ix_sessions_protocol_version", "protocol_version_id"),
        Index("ix_sessions_scheduled", "scheduled_at"),
        Index("ix_sessions_patient_number", "patient_id", "protocol_version_id", "session_number", unique=True),
    )

    def __repr__(self) -> str:
        return f"<TreatmentSession {self.id} session={self.session_number}>"
