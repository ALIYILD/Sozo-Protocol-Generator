"""Patient repository."""
from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..repository import BaseRepository
from ..models.patient import Patient, Assessment, TreatmentRecord, Medication


class PatientRepository(BaseRepository[Patient]):
    model = Patient

    async def get_by_external_id(self, external_id: str) -> Patient | None:
        stmt = select(Patient).where(Patient.external_id == external_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_assessments(self, patient_id: uuid.UUID) -> Patient | None:
        stmt = (
            select(Patient)
            .options(selectinload(Patient.assessments))
            .where(Patient.id == patient_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_full_profile(self, patient_id: uuid.UUID) -> Patient | None:
        """Load patient with all related records eagerly."""
        stmt = (
            select(Patient)
            .options(
                selectinload(Patient.assessments),
                selectinload(Patient.treatment_records),
                selectinload(Patient.medications),
                selectinload(Patient.eeg_records),
                selectinload(Patient.treatment_sessions),
            )
            .where(Patient.id == patient_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(
        self, organization_id: uuid.UUID, *, offset: int = 0, limit: int = 100
    ) -> Sequence[Patient]:
        stmt = (
            select(Patient)
            .where(Patient.organization_id == organization_id)
            .order_by(Patient.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ── Assessment helpers ────────────────────────────────────────────

    async def add_assessment(self, assessment: Assessment) -> Assessment:
        self.session.add(assessment)
        await self.session.flush()
        return assessment

    async def list_assessments(
        self,
        patient_id: uuid.UUID,
        *,
        scale_name: str | None = None,
        limit: int = 50,
    ) -> Sequence[Assessment]:
        stmt = select(Assessment).where(Assessment.patient_id == patient_id)
        if scale_name:
            stmt = stmt.where(Assessment.scale_name == scale_name)
        stmt = stmt.order_by(Assessment.assessed_at.desc().nullslast()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ── Treatment record helpers ──────────────────────────────────────

    async def add_treatment_record(self, record: TreatmentRecord) -> TreatmentRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    # ── Medication helpers ────────────────────────────────────────────

    async def add_medication(self, medication: Medication) -> Medication:
        self.session.add(medication)
        await self.session.flush()
        return medication

    async def list_active_medications(self, patient_id: uuid.UUID) -> Sequence[Medication]:
        stmt = (
            select(Medication)
            .where(
                Medication.patient_id == patient_id,
                Medication.end_date.is_(None),
            )
            .order_by(Medication.start_date.desc().nullslast())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
