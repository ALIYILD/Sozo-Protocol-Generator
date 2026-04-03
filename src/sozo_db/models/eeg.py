"""EEG recording model."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, UUIDMixin


class EEGRecord(UUIDMixin, Base):
    __tablename__ = "eeg_records"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False
    )
    recorded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    montage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    band_powers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    asymmetry_indices: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    peak_alpha_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    z_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    connectivity: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_localization: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    source_file_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    processing_params: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="eeg_records")  # noqa: F821

    __table_args__ = (
        Index("ix_eeg_patient", "patient_id"),
        Index("ix_eeg_recorded_at", "recorded_at"),
    )

    def __repr__(self) -> str:
        return f"<EEGRecord {self.id} patient={self.patient_id}>"
