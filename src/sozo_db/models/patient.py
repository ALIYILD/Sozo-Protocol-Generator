"""Patient, Assessment, TreatmentRecord, and Medication models."""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, UUIDMixin, TimestampMixin


class Patient(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "patients"

    external_id: Mapped[str | None] = mapped_column(String(256), nullable=True, unique=True)
    demographics: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )

    # Relationships
    assessments: Mapped[list["Assessment"]] = relationship(
        "Assessment", back_populates="patient", cascade="all, delete-orphan"
    )
    treatment_records: Mapped[list["TreatmentRecord"]] = relationship(
        "TreatmentRecord", back_populates="patient", cascade="all, delete-orphan"
    )
    medications: Mapped[list["Medication"]] = relationship(
        "Medication", back_populates="patient", cascade="all, delete-orphan"
    )
    eeg_records: Mapped[list["EEGRecord"]] = relationship(  # noqa: F821
        "EEGRecord", back_populates="patient", cascade="all, delete-orphan"
    )
    treatment_sessions: Mapped[list["TreatmentSession"]] = relationship(  # noqa: F821
        "TreatmentSession", back_populates="patient"
    )

    def __repr__(self) -> str:
        return f"<Patient {self.id} external={self.external_id}>"


class Assessment(UUIDMixin, Base):
    __tablename__ = "assessments"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    protocol_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("protocols.id"), nullable=True
    )
    scale_name: Mapped[str] = mapped_column(String(256), nullable=False)
    abbreviation: Mapped[str | None] = mapped_column(String(32), nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    subscale_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    severity_band: Mapped[str | None] = mapped_column(String(64), nullable=True)
    assessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assessed_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    session_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="assessments")

    __table_args__ = (
        Index("ix_assessments_patient", "patient_id"),
        Index("ix_assessments_patient_scale", "patient_id", "scale_name"),
        Index("ix_assessments_assessed_at", "assessed_at"),
    )

    def __repr__(self) -> str:
        return f"<Assessment {self.scale_name} score={self.score} patient={self.patient_id}>"


class TreatmentRecord(UUIDMixin, Base):
    __tablename__ = "treatment_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    modality: Mapped[str] = mapped_column(String(64), nullable=False)
    target: Mapped[str | None] = mapped_column(String(128), nullable=True)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    sessions_completed: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    outcome: Mapped[str | None] = mapped_column(String(128), nullable=True)
    outcome_measures: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    adverse_events: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="treatment_records")

    __table_args__ = (
        Index("ix_treatment_records_patient", "patient_id"),
        Index("ix_treatment_records_modality", "modality"),
    )

    def __repr__(self) -> str:
        return f"<TreatmentRecord {self.modality} patient={self.patient_id}>"


class Medication(UUIDMixin, Base):
    __tablename__ = "medications"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    drug_class: Mapped[str | None] = mapped_column(String(128), nullable=True)
    dose: Mapped[str | None] = mapped_column(String(128), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    interaction_flags: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="medications")

    __table_args__ = (
        Index("ix_medications_patient", "patient_id"),
    )

    def __repr__(self) -> str:
        return f"<Medication {self.name} patient={self.patient_id}>"
