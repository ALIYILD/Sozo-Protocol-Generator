"""
JSON-file-backed persistence stores for patients, sessions, and outcomes.

Each entity is stored as a single JSON file under ``outputs/``:
    outputs/patients/{patient_id}.json
    outputs/sessions/{session_id}.json
    outputs/outcomes/{outcome_id}.json

No database dependency — just the filesystem.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from .models import Patient, SessionRecord, OutcomeRecord

logger = logging.getLogger(__name__)

# Resolve project root (two levels up from this file → src/sozo_session/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_OUTPUTS = _PROJECT_ROOT / "outputs"


# ── helpers ─────────────────────────────────────────────────────────────


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, data: dict) -> None:
    _ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ── Patient Store ───────────────────────────────────────────────────────


class PatientStore:
    """CRUD store for Patient records."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = _ensure_dir(base_dir or _OUTPUTS / "patients")

    def _path(self, patient_id: str) -> Path:
        return self.base_dir / f"{patient_id}.json"

    def save(self, patient: Patient) -> Path:
        path = self._path(patient.patient_id)
        _write_json(path, patient.model_dump(mode="json"))
        logger.info("Saved patient %s → %s", patient.patient_id, path)
        return path

    def load(self, patient_id: str) -> Patient:
        path = self._path(patient_id)
        return Patient.model_validate(_read_json(path))

    def exists(self, patient_id: str) -> bool:
        return self._path(patient_id).is_file()

    def list(self) -> list[Patient]:
        patients: list[Patient] = []
        for f in sorted(self.base_dir.glob("*.json")):
            try:
                patients.append(Patient.model_validate(_read_json(f)))
            except Exception as exc:
                logger.warning("Skipping invalid patient file %s: %s", f, exc)
        return patients

    def search_by_condition(self, condition_slug: str) -> list[Patient]:
        return [p for p in self.list() if condition_slug in p.condition_slugs]


# ── Session Store ───────────────────────────────────────────────────────


class SessionStore:
    """CRUD store for SessionRecord entries."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = _ensure_dir(base_dir or _OUTPUTS / "sessions")

    def _path(self, session_id: str) -> Path:
        return self.base_dir / f"{session_id}.json"

    def save(self, record: SessionRecord) -> Path:
        path = self._path(record.session_id)
        _write_json(path, record.model_dump(mode="json"))
        logger.info("Saved session %s → %s", record.session_id, path)
        return path

    def load(self, session_id: str) -> SessionRecord:
        path = self._path(session_id)
        return SessionRecord.model_validate(_read_json(path))

    def list_for_patient(self, patient_id: str) -> list[SessionRecord]:
        records: list[SessionRecord] = []
        for f in sorted(self.base_dir.glob("*.json")):
            try:
                rec = SessionRecord.model_validate(_read_json(f))
                if rec.patient_id == patient_id:
                    records.append(rec)
            except Exception as exc:
                logger.warning("Skipping invalid session file %s: %s", f, exc)
        return records

    def list_recent(self, limit: int = 20) -> list[SessionRecord]:
        """Return the most recent sessions, sorted by started_at descending."""
        records: list[SessionRecord] = []
        for f in sorted(self.base_dir.glob("*.json"), reverse=True):
            try:
                records.append(SessionRecord.model_validate(_read_json(f)))
            except Exception as exc:
                logger.warning("Skipping invalid session file %s: %s", f, exc)
        # Sort by started_at (None sorts last)
        records.sort(key=lambda r: r.started_at or "", reverse=True)
        return records[:limit]


# ── Outcome Store ───────────────────────────────────────────────────────


class OutcomeStore:
    """CRUD store for OutcomeRecord entries."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = _ensure_dir(base_dir or _OUTPUTS / "outcomes")

    def _path(self, outcome_id: str) -> Path:
        return self.base_dir / f"{outcome_id}.json"

    def save(self, record: OutcomeRecord) -> Path:
        path = self._path(record.outcome_id)
        _write_json(path, record.model_dump(mode="json"))
        logger.info("Saved outcome %s → %s", record.outcome_id, path)
        return path

    def load(self, outcome_id: str) -> OutcomeRecord:
        path = self._path(outcome_id)
        return OutcomeRecord.model_validate(_read_json(path))

    def list_for_patient(self, patient_id: str) -> list[OutcomeRecord]:
        records: list[OutcomeRecord] = []
        for f in sorted(self.base_dir.glob("*.json")):
            try:
                rec = OutcomeRecord.model_validate(_read_json(f))
                if rec.patient_id == patient_id:
                    records.append(rec)
            except Exception as exc:
                logger.warning("Skipping invalid outcome file %s: %s", f, exc)
        return records

    def list_for_session(self, session_id: str) -> list[OutcomeRecord]:
        records: list[OutcomeRecord] = []
        for f in sorted(self.base_dir.glob("*.json")):
            try:
                rec = OutcomeRecord.model_validate(_read_json(f))
                if rec.session_id == session_id:
                    records.append(rec)
            except Exception as exc:
                logger.warning("Skipping invalid outcome file %s: %s", f, exc)
        return records
