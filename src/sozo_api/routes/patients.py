"""Patient management and assessment API routes.

Provides CRUD for patient profiles, medication tracking, clinical assessments,
treatment history, safety checks, and patient timeline views.

All endpoints use the SQLite database for persistence.
"""
from __future__ import annotations

import json
import logging
import os
import sqlite3
from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/patients", tags=["patients"])


# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------

def _get_db() -> sqlite3.Connection:
    db_url = os.environ.get("DATABASE_URL", "")
    if "sqlite" in db_url:
        path = db_url.split("///")[-1]
    else:
        path = "sozo_dev.db"
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_tables(conn: sqlite3.Connection) -> None:
    """Create patient-related tables if they don't exist."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS patients (
        id TEXT PRIMARY KEY,
        external_id TEXT UNIQUE,
        demographics TEXT DEFAULT '{}',
        conditions TEXT DEFAULT '[]',
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS medications (
        id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        name TEXT NOT NULL,
        drug_class TEXT,
        dose TEXT,
        start_date TEXT,
        end_date TEXT,
        added_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        scale_name TEXT NOT NULL,
        abbreviation TEXT,
        score REAL,
        severity_band TEXT,
        subscale_scores TEXT,
        assessed_at TEXT NOT NULL,
        session_number INTEGER,
        notes TEXT
    );

    CREATE TABLE IF NOT EXISTS treatment_records (
        id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
        modality TEXT NOT NULL,
        condition_slug TEXT,
        target TEXT,
        parameters TEXT DEFAULT '{}',
        sessions_completed INTEGER DEFAULT 0,
        outcome TEXT,
        outcome_measures TEXT DEFAULT '{}',
        adverse_events TEXT DEFAULT '[]',
        start_date TEXT,
        end_date TEXT,
        recorded_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS ix_medications_patient ON medications(patient_id);
    CREATE INDEX IF NOT EXISTS ix_assessments_patient ON assessments(patient_id);
    CREATE INDEX IF NOT EXISTS ix_assessments_patient_scale ON assessments(patient_id, scale_name);
    CREATE INDEX IF NOT EXISTS ix_treatment_records_patient ON treatment_records(patient_id);
    """)
    conn.commit()


# Run table creation once on module load
try:
    _init_conn = _get_db()
    _ensure_tables(_init_conn)
    _init_conn.close()
except Exception as exc:
    logger.warning("Could not initialise patient tables on import: %s", exc)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class Demographics(BaseModel):
    age: int = Field(ge=0, le=120)
    sex: str  # male, female, other
    handedness: str = "right"  # right, left, ambidextrous


class CreatePatientRequest(BaseModel):
    external_id: Optional[str] = None
    demographics: Demographics
    conditions: list[str] = []  # active condition slugs
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    patient_id: UUID
    external_id: Optional[str]
    demographics: Demographics
    conditions: list[str]
    active_protocols: int
    assessments_count: int
    created_at: datetime


class MedicationRequest(BaseModel):
    name: str
    drug_class: str
    dose: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None


class MedicationResponse(BaseModel):
    medication_id: UUID
    name: str
    drug_class: str
    dose: Optional[str]
    start_date: date
    end_date: Optional[date]
    is_active: bool
    added_at: datetime


class AssessmentRequest(BaseModel):
    scale_name: str  # e.g., "PHQ-9"
    score: float
    subscale_scores: Optional[dict[str, float]] = None
    session_number: Optional[int] = None
    notes: Optional[str] = None


class AssessmentResponse(BaseModel):
    assessment_id: UUID
    scale_name: str
    abbreviation: str
    score: float
    severity_band: str
    subscale_scores: Optional[dict[str, float]]
    assessed_at: datetime
    session_number: Optional[int]


class TreatmentRecordRequest(BaseModel):
    modality: str
    condition_slug: str
    target: str
    parameters: dict = {}
    sessions_completed: int
    outcome: str  # responder, partial_responder, non_responder, not_assessed
    outcome_measures: dict = {}
    adverse_events: list[str] = []
    start_date: date
    end_date: Optional[date] = None


class TreatmentRecordResponse(BaseModel):
    treatment_id: UUID
    modality: str
    condition_slug: str
    target: str
    parameters: dict
    sessions_completed: int
    outcome: str
    outcome_measures: dict
    adverse_events: list[str]
    start_date: date
    end_date: Optional[date]
    recorded_at: datetime


class PatientSafetyCheckResponse(BaseModel):
    patient_id: UUID
    safety_cleared: bool
    absolute_contraindications: list[str]
    relative_contraindications: list[str]
    medication_interactions: list[dict]
    blocked_modalities: list[str]
    warnings: list[str]


class PatientTimelineEntry(BaseModel):
    date: datetime
    event_type: str  # assessment, treatment_session, medication_change, protocol_change
    summary: str
    details: dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_severity_band(scale_name: str, score: float) -> str:
    """Look up the severity band from the VALIDATED_SCALES registry.

    Falls back to a simple tertile classification if the scale is not in the
    registry (keeps the API usable for custom / unregistered scales).
    """
    try:
        from sozo_generator.schemas.patient import VALIDATED_SCALES
        scale = VALIDATED_SCALES.get(scale_name)
        if scale:
            band = scale.classify_severity(score)
            if band:
                return band
    except ImportError:
        pass

    # Fallback heuristic when no registry entry exists
    if score <= 5:
        return "minimal"
    elif score <= 14:
        return "mild"
    elif score <= 20:
        return "moderate"
    return "severe"


def _resolve_abbreviation(scale_name: str) -> str:
    """Return the canonical abbreviation for a scale name."""
    try:
        from sozo_generator.schemas.patient import VALIDATED_SCALES
        scale = VALIDATED_SCALES.get(scale_name)
        if scale:
            return scale.abbreviation
    except ImportError:
        pass
    return scale_name


def _validate_score_range(scale_name: str, score: float) -> None:
    """Raise 422 if the score is outside the scale's valid range."""
    try:
        from sozo_generator.schemas.patient import VALIDATED_SCALES
        scale = VALIDATED_SCALES.get(scale_name)
        if scale and not scale.is_valid_score(score):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Score {score} is outside valid range "
                    f"[{scale.score_range.min}, {scale.score_range.max}] "
                    f"for {scale_name}"
                ),
            )
    except ImportError:
        pass


def _get_patient_or_404(patient_id: UUID) -> dict:
    """Return the patient dict from DB or raise 404."""
    conn = _get_db()
    try:
        row = conn.execute("SELECT * FROM patients WHERE id = ?", (str(patient_id),)).fetchone()
    finally:
        conn.close()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found",
        )
    return _row_to_patient(row)


def _row_to_patient(row: sqlite3.Row) -> dict:
    """Convert a patients DB row to dict with parsed JSON fields."""
    d = dict(row)
    d["patient_id"] = d.pop("id")
    d["demographics"] = json.loads(d.get("demographics") or "{}")
    d["conditions"] = json.loads(d.get("conditions") or "[]")
    return d


def _patient_response(patient: dict) -> PatientResponse:
    """Build a PatientResponse from the internal dict."""
    pid = patient["patient_id"]
    conn = _get_db()
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM assessments WHERE patient_id = ?", (str(pid),)
        ).fetchone()[0]
    finally:
        conn.close()
    return PatientResponse(
        patient_id=pid,
        external_id=patient.get("external_id"),
        demographics=Demographics(**patient["demographics"]),
        conditions=patient.get("conditions", []),
        active_protocols=0,  # stub — no protocol engine wired yet
        assessments_count=count,
        created_at=patient["created_at"],
    )


# ---------------------------------------------------------------------------
# Patient CRUD
# ---------------------------------------------------------------------------

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PatientResponse,
    summary="Create a new patient",
)
async def create_patient(request: CreatePatientRequest):
    """Create a new patient record.

    Accepts demographics, active conditions, and optional notes.
    Returns the full patient object with a generated UUID.
    """
    pid = str(uuid4())
    now = datetime.utcnow().isoformat()
    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO patients (id, external_id, demographics, conditions, notes, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                pid,
                request.external_id,
                json.dumps(request.demographics.model_dump()),
                json.dumps(request.conditions),
                request.notes,
                now,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Created patient %s", pid)
    patient = _get_patient_or_404(UUID(pid))
    return _patient_response(patient)


@router.get(
    "/",
    response_model=dict,
    summary="List patients",
)
async def list_patients(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    condition: Optional[str] = None,
):
    """List patients with pagination and optional filtering.

    - **search**: partial match against external_id or notes.
    - **condition**: filter to patients with this condition slug active.
    """
    conn = _get_db()
    try:
        rows = conn.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
    finally:
        conn.close()

    patients = [_row_to_patient(r) for r in rows]

    # Filtering
    if condition:
        patients = [p for p in patients if condition in p.get("conditions", [])]
    if search:
        _q = search.lower()
        patients = [
            p for p in patients
            if (_q in (p.get("external_id") or "").lower())
            or (_q in (p.get("notes") or "").lower())
        ]

    total = len(patients)
    start = (page - 1) * page_size
    end = start + page_size
    page_items = patients[start:end]

    return {
        "patients": [_patient_response(p).model_dump() for p in page_items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, -(-total // page_size)),  # ceil division
    }


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Get patient details",
)
async def get_patient(patient_id: UUID):
    """Retrieve full details for a single patient."""
    patient = _get_patient_or_404(patient_id)
    return _patient_response(patient)


@router.put(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="Update patient",
)
async def update_patient(patient_id: UUID, request: CreatePatientRequest):
    """Update patient demographics, conditions, and notes.

    Replaces the existing values wholesale (PUT semantics).
    """
    _get_patient_or_404(patient_id)
    now = datetime.utcnow().isoformat()
    conn = _get_db()
    try:
        conn.execute(
            "UPDATE patients SET external_id = ?, demographics = ?, conditions = ?, notes = ?, updated_at = ? "
            "WHERE id = ?",
            (
                request.external_id,
                json.dumps(request.demographics.model_dump()),
                json.dumps(request.conditions),
                request.notes,
                now,
                str(patient_id),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Updated patient %s", patient_id)
    patient = _get_patient_or_404(patient_id)
    return _patient_response(patient)


# ---------------------------------------------------------------------------
# Medications
# ---------------------------------------------------------------------------

@router.post(
    "/{patient_id}/medications",
    status_code=status.HTTP_201_CREATED,
    response_model=MedicationResponse,
    summary="Add medication",
)
async def add_medication(patient_id: UUID, request: MedicationRequest):
    """Add a medication to the patient's profile.

    Records the drug name, class, dose, and date range.
    """
    _get_patient_or_404(patient_id)
    med_id = str(uuid4())
    now = datetime.utcnow().isoformat()
    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO medications (id, patient_id, name, drug_class, dose, start_date, end_date, added_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                med_id,
                str(patient_id),
                request.name,
                request.drug_class,
                request.dose,
                request.start_date.isoformat() if request.start_date else None,
                request.end_date.isoformat() if request.end_date else None,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Added medication %s to patient %s", med_id, patient_id)
    return MedicationResponse(
        medication_id=med_id,
        name=request.name,
        drug_class=request.drug_class,
        dose=request.dose,
        start_date=request.start_date,
        end_date=request.end_date,
        is_active=request.end_date is None,
        added_at=now,
    )


@router.get(
    "/{patient_id}/medications",
    response_model=list[MedicationResponse],
    summary="List medications",
)
async def list_medications(patient_id: UUID, active_only: bool = True):
    """List patient medications.

    By default returns only active medications (no end_date). Pass
    ``active_only=false`` to include discontinued medications.
    """
    _get_patient_or_404(patient_id)
    conn = _get_db()
    try:
        if active_only:
            rows = conn.execute(
                "SELECT * FROM medications WHERE patient_id = ? AND end_date IS NULL ORDER BY added_at DESC",
                (str(patient_id),),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM medications WHERE patient_id = ? ORDER BY added_at DESC",
                (str(patient_id),),
            ).fetchall()
    finally:
        conn.close()

    results = []
    for r in rows:
        d = dict(r)
        results.append(MedicationResponse(
            medication_id=d["id"],
            name=d["name"],
            drug_class=d["drug_class"],
            dose=d["dose"],
            start_date=d["start_date"],
            end_date=d["end_date"],
            is_active=d["end_date"] is None,
            added_at=d["added_at"],
        ))
    return results


@router.delete(
    "/{patient_id}/medications/{medication_id}",
    status_code=status.HTTP_200_OK,
    summary="Discontinue medication",
)
async def remove_medication(patient_id: UUID, medication_id: UUID):
    """Discontinue a medication by setting its end_date to today.

    Does not physically delete the record — treatment history is preserved.
    """
    _get_patient_or_404(patient_id)
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT * FROM medications WHERE id = ? AND patient_id = ?",
            (str(medication_id), str(patient_id)),
        ).fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Medication {medication_id} not found for patient {patient_id}",
            )
        conn.execute(
            "UPDATE medications SET end_date = ? WHERE id = ?",
            (date.today().isoformat(), str(medication_id)),
        )
        conn.commit()
    finally:
        conn.close()
    logger.info("Discontinued medication %s for patient %s", medication_id, patient_id)
    return {"status": "discontinued", "medication_id": str(medication_id)}


# ---------------------------------------------------------------------------
# Assessments
# ---------------------------------------------------------------------------

@router.post(
    "/{patient_id}/assessments",
    status_code=status.HTTP_201_CREATED,
    response_model=AssessmentResponse,
    summary="Record assessment",
)
async def record_assessment(patient_id: UUID, request: AssessmentRequest):
    """Record a new assessment score for a patient.

    Automatically resolves the severity band from the SOZO validated scales
    registry. Returns 422 if the score is outside the scale's valid range.
    """
    _get_patient_or_404(patient_id)
    _validate_score_range(request.scale_name, request.score)

    aid = str(uuid4())
    now = datetime.utcnow().isoformat()
    severity = _resolve_severity_band(request.scale_name, request.score)
    abbreviation = _resolve_abbreviation(request.scale_name)

    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO assessments "
            "(id, patient_id, scale_name, abbreviation, score, severity_band, subscale_scores, assessed_at, session_number, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                aid,
                str(patient_id),
                request.scale_name,
                abbreviation,
                request.score,
                severity,
                json.dumps(request.subscale_scores) if request.subscale_scores else None,
                now,
                request.session_number,
                request.notes,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info(
        "Recorded %s assessment (score=%.1f, band=%s) for patient %s",
        request.scale_name, request.score, severity, patient_id,
    )
    return AssessmentResponse(
        assessment_id=aid,
        scale_name=request.scale_name,
        abbreviation=abbreviation,
        score=request.score,
        severity_band=severity,
        subscale_scores=request.subscale_scores,
        assessed_at=now,
        session_number=request.session_number,
    )


@router.get(
    "/{patient_id}/assessments",
    response_model=list[AssessmentResponse],
    summary="List assessments",
)
async def list_assessments(
    patient_id: UUID,
    scale: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """List assessments for a patient.

    Optionally filter by ``scale`` name. Results are ordered most-recent-first.
    """
    _get_patient_or_404(patient_id)
    conn = _get_db()
    try:
        if scale:
            rows = conn.execute(
                "SELECT * FROM assessments WHERE patient_id = ? AND scale_name = ? "
                "ORDER BY assessed_at DESC LIMIT ?",
                (str(patient_id), scale, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM assessments WHERE patient_id = ? ORDER BY assessed_at DESC LIMIT ?",
                (str(patient_id), limit),
            ).fetchall()
    finally:
        conn.close()

    results = []
    for r in rows:
        d = dict(r)
        results.append(AssessmentResponse(
            assessment_id=d["id"],
            scale_name=d["scale_name"],
            abbreviation=d["abbreviation"] or d["scale_name"],
            score=d["score"],
            severity_band=d["severity_band"] or "unknown",
            subscale_scores=json.loads(d["subscale_scores"]) if d["subscale_scores"] else None,
            assessed_at=d["assessed_at"],
            session_number=d["session_number"],
        ))
    return results


@router.get(
    "/{patient_id}/assessments/trajectory",
    summary="Assessment score trajectory",
)
async def get_assessment_trajectory(patient_id: UUID, scale_name: str):
    """Get score trajectory over time for a specific assessment scale.

    Returns an ordered list of ``{date, score, severity_band, session_number}``
    entries suitable for line chart rendering.
    """
    _get_patient_or_404(patient_id)
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM assessments WHERE patient_id = ? AND scale_name = ? ORDER BY assessed_at ASC",
            (str(patient_id), scale_name),
        ).fetchall()
    finally:
        conn.close()

    points = []
    for r in rows:
        d = dict(r)
        points.append({
            "date": d["assessed_at"],
            "score": d["score"],
            "severity_band": d["severity_band"] or "unknown",
            "session_number": d["session_number"],
        })

    # Compute basic trend info
    scores = [p["score"] for p in points]
    trend = "stable"
    if len(scores) >= 2:
        delta = scores[-1] - scores[0]
        if delta < -1:
            trend = "improving"
        elif delta > 1:
            trend = "worsening"

    return {
        "patient_id": str(patient_id),
        "scale_name": scale_name,
        "abbreviation": _resolve_abbreviation(scale_name),
        "data_points": points,
        "summary": {
            "total_assessments": len(points),
            "first_score": scores[0] if scores else None,
            "latest_score": scores[-1] if scores else None,
            "min_score": min(scores) if scores else None,
            "max_score": max(scores) if scores else None,
            "trend": trend,
        },
    }


# ---------------------------------------------------------------------------
# Treatment History
# ---------------------------------------------------------------------------

@router.post(
    "/{patient_id}/treatments",
    status_code=status.HTTP_201_CREATED,
    response_model=TreatmentRecordResponse,
    summary="Record treatment",
)
async def add_treatment_record(patient_id: UUID, request: TreatmentRecordRequest):
    """Record a prior or ongoing neuromodulation treatment course."""
    _get_patient_or_404(patient_id)

    valid_outcomes = {"responder", "partial_responder", "non_responder", "not_assessed"}
    if request.outcome not in valid_outcomes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid outcome '{request.outcome}'. Must be one of: {sorted(valid_outcomes)}",
        )
    if request.end_date and request.start_date and request.end_date < request.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date cannot precede start_date",
        )

    tid = str(uuid4())
    now = datetime.utcnow().isoformat()
    conn = _get_db()
    try:
        conn.execute(
            "INSERT INTO treatment_records "
            "(id, patient_id, modality, condition_slug, target, parameters, sessions_completed, "
            "outcome, outcome_measures, adverse_events, start_date, end_date, recorded_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                tid,
                str(patient_id),
                request.modality,
                request.condition_slug,
                request.target,
                json.dumps(request.parameters),
                request.sessions_completed,
                request.outcome,
                json.dumps(request.outcome_measures),
                json.dumps(request.adverse_events),
                request.start_date.isoformat() if request.start_date else None,
                request.end_date.isoformat() if request.end_date else None,
                now,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info("Recorded treatment %s for patient %s", tid, patient_id)
    return TreatmentRecordResponse(
        treatment_id=tid,
        modality=request.modality,
        condition_slug=request.condition_slug,
        target=request.target,
        parameters=request.parameters,
        sessions_completed=request.sessions_completed,
        outcome=request.outcome,
        outcome_measures=request.outcome_measures,
        adverse_events=request.adverse_events,
        start_date=request.start_date,
        end_date=request.end_date,
        recorded_at=now,
    )


@router.get(
    "/{patient_id}/treatments",
    response_model=list[TreatmentRecordResponse],
    summary="List treatment history",
)
async def list_treatment_history(patient_id: UUID):
    """List all treatment records for a patient, ordered most-recent-first."""
    _get_patient_or_404(patient_id)
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT * FROM treatment_records WHERE patient_id = ? ORDER BY recorded_at DESC",
            (str(patient_id),),
        ).fetchall()
    finally:
        conn.close()

    results = []
    for r in rows:
        d = dict(r)
        results.append(TreatmentRecordResponse(
            treatment_id=d["id"],
            modality=d["modality"],
            condition_slug=d["condition_slug"] or "",
            target=d["target"] or "",
            parameters=json.loads(d["parameters"]) if d["parameters"] else {},
            sessions_completed=d["sessions_completed"] or 0,
            outcome=d["outcome"] or "not_assessed",
            outcome_measures=json.loads(d["outcome_measures"]) if d["outcome_measures"] else {},
            adverse_events=json.loads(d["adverse_events"]) if d["adverse_events"] else [],
            start_date=d["start_date"],
            end_date=d["end_date"],
            recorded_at=d["recorded_at"],
        ))
    return results


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------

# Medication interaction rules (simplified).
# In production this would use sozo_generator.safety.interaction_checker.
_MEDICATION_INTERACTION_RULES: list[dict] = [
    {
        "drug_class": "SSRI",
        "modality": "tms",
        "severity": "caution",
        "note": "SSRIs may lower seizure threshold; monitor closely with TMS.",
    },
    {
        "drug_class": "MAOI",
        "modality": "tms",
        "severity": "warning",
        "note": "MAOIs combined with TMS may potentiate effects; consider dose timing.",
    },
    {
        "drug_class": "benzodiazepine",
        "modality": "tdcs",
        "severity": "caution",
        "note": "Benzodiazepines may attenuate tDCS neuroplastic effects.",
    },
    {
        "drug_class": "anticonvulsant",
        "modality": "tms",
        "severity": "relative_contraindication",
        "note": "Anticonvulsants raise seizure threshold; may reduce TMS efficacy.",
    },
    {
        "drug_class": "stimulant",
        "modality": "tms",
        "severity": "caution",
        "note": "Stimulants may lower seizure threshold; use conservative TMS parameters.",
    },
]

# Absolute contraindications by modality (simplified).
_ABSOLUTE_CONTRAINDICATIONS: dict[str, list[str]] = {
    "tms": [
        "cochlear_implant",
        "metallic_implant_near_coil",
        "implanted_cardiac_defibrillator",
        "deep_brain_stimulator",
    ],
    "tdcs": [
        "open_skull_wound",
        "metallic_implant_at_electrode_site",
    ],
    "tps": [
        "skull_defect_at_target",
    ],
}

_RELATIVE_CONTRAINDICATIONS: dict[str, list[str]] = {
    "tms": [
        "epilepsy",
        "history_of_seizures",
        "pregnancy",
        "raised_intracranial_pressure",
    ],
    "tdcs": [
        "eczema_at_electrode_site",
        "pregnancy",
    ],
}


@router.get(
    "/{patient_id}/safety-check",
    response_model=PatientSafetyCheckResponse,
    summary="Run patient safety check",
)
async def check_patient_safety(
    patient_id: UUID,
    modalities: Optional[str] = Query(
        None,
        description="Comma-separated modality list, e.g. 'tms,tdcs'. Defaults to all.",
    ),
):
    """Run safety check for a patient against target modalities.

    Evaluates:
    - Absolute contraindications (blocks treatment)
    - Relative contraindications (requires clinician review)
    - Medication interaction screening
    - Age-based considerations

    Returns clearance status and itemised findings.
    """
    patient = _get_patient_or_404(patient_id)
    demographics = patient["demographics"]
    conditions = patient.get("conditions", [])

    # Load active medications from DB
    conn = _get_db()
    try:
        med_rows = conn.execute(
            "SELECT * FROM medications WHERE patient_id = ? AND end_date IS NULL",
            (str(patient_id),),
        ).fetchall()
    finally:
        conn.close()
    active_meds = [dict(r) for r in med_rows]

    # Try the real safety engine first
    try:
        from sozo_generator.safety.contraindication_engine import evaluate_patient_safety

        profile = evaluate_patient_safety(
            patient_demographics=demographics,
            medications=[{"name": m["name"], "drug_class": m["drug_class"], "dose": m["dose"]} for m in active_meds],
            medical_history=conditions,
            target_modalities=(
                [m.strip().lower() for m in modalities.split(",")]
                if modalities
                else None
            ),
        )
        return PatientSafetyCheckResponse(
            patient_id=patient_id,
            safety_cleared=profile.is_cleared,
            absolute_contraindications=profile.absolute_contraindications,
            relative_contraindications=profile.relative_contraindications,
            medication_interactions=[vars(i) if hasattr(i, '__dict__') else i for i in profile.medication_interactions],
            blocked_modalities=profile.blocked_modalities,
            warnings=profile.warnings,
        )
    except (ImportError, AttributeError, Exception) as exc:
        logger.debug("Safety engine unavailable (%s), using built-in rules", exc)

    # Fallback: built-in safety rules
    target_modalities = (
        [m.strip().lower() for m in modalities.split(",")]
        if modalities
        else ["tms", "tdcs", "tps", "tavns"]
    )

    absolute: list[str] = []
    relative: list[str] = []
    interactions: list[dict] = []
    blocked: list[str] = []
    warnings: list[str] = []

    # Check absolute contraindications
    for mod in target_modalities:
        for contra in _ABSOLUTE_CONTRAINDICATIONS.get(mod, []):
            if contra in conditions:
                absolute.append(f"{mod}: {contra}")
                if mod not in blocked:
                    blocked.append(mod)

    # Check relative contraindications
    for mod in target_modalities:
        for contra in _RELATIVE_CONTRAINDICATIONS.get(mod, []):
            if contra in conditions:
                relative.append(f"{mod}: {contra}")

    # Medication interaction screening
    for med in active_meds:
        drug_class = med.get("drug_class", "")
        for rule in _MEDICATION_INTERACTION_RULES:
            if (
                rule["drug_class"].lower() == (drug_class or "").lower()
                and rule["modality"] in target_modalities
            ):
                interactions.append({
                    "medication": med["name"],
                    "drug_class": drug_class,
                    "modality": rule["modality"],
                    "severity": rule["severity"],
                    "note": rule["note"],
                })
                if rule["severity"] == "relative_contraindication" and rule["modality"] not in blocked:
                    blocked.append(rule["modality"])

    # Age considerations
    age = demographics.get("age", 30)
    if age < 18:
        warnings.append(
            "Paediatric patient (age < 18): additional consent and protocol "
            "adjustments required for all neuromodulation modalities."
        )
    if age > 80:
        warnings.append(
            "Elderly patient (age > 80): consider reduced stimulation intensity "
            "and closer monitoring for adverse events."
        )

    safety_cleared = len(absolute) == 0 and len(blocked) == 0

    return PatientSafetyCheckResponse(
        patient_id=patient_id,
        safety_cleared=safety_cleared,
        absolute_contraindications=absolute,
        relative_contraindications=relative,
        medication_interactions=interactions,
        blocked_modalities=blocked,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Timeline
# ---------------------------------------------------------------------------

@router.get(
    "/{patient_id}/timeline",
    response_model=list[PatientTimelineEntry],
    summary="Patient event timeline",
)
async def get_patient_timeline(patient_id: UUID, limit: int = Query(50, ge=1, le=500)):
    """Get chronological timeline of all patient events.

    Merges assessments, treatments, and medication changes into a single
    ordered stream for display in a timeline component.
    """
    _get_patient_or_404(patient_id)
    pid_str = str(patient_id)
    entries: list[dict] = []

    conn = _get_db()
    try:
        # Assessments
        a_rows = conn.execute(
            "SELECT * FROM assessments WHERE patient_id = ?", (pid_str,)
        ).fetchall()
        for r in a_rows:
            a = dict(r)
            abbr = a["abbreviation"] or a["scale_name"]
            entries.append({
                "date": a["assessed_at"],
                "event_type": "assessment",
                "summary": f"{abbr} score: {a['score']} ({a['severity_band']})",
                "details": {
                    "assessment_id": a["id"],
                    "scale_name": a["scale_name"],
                    "score": a["score"],
                    "severity_band": a["severity_band"],
                    "session_number": a["session_number"],
                },
            })

        # Treatment records
        t_rows = conn.execute(
            "SELECT * FROM treatment_records WHERE patient_id = ?", (pid_str,)
        ).fetchall()
        for r in t_rows:
            t = dict(r)
            entries.append({
                "date": t["recorded_at"],
                "event_type": "treatment_session",
                "summary": (
                    f"{(t['modality'] or '').upper()} targeting {t['target'] or 'N/A'} "
                    f"for {t['condition_slug'] or 'N/A'} — {t['sessions_completed'] or 0} sessions, "
                    f"outcome: {t['outcome'] or 'not_assessed'}"
                ),
                "details": {
                    "treatment_id": t["id"],
                    "modality": t["modality"],
                    "target": t["target"],
                    "outcome": t["outcome"],
                    "sessions_completed": t["sessions_completed"],
                },
            })

        # Medication additions
        m_rows = conn.execute(
            "SELECT * FROM medications WHERE patient_id = ?", (pid_str,)
        ).fetchall()
        for r in m_rows:
            m = dict(r)
            entries.append({
                "date": m["added_at"],
                "event_type": "medication_change",
                "summary": f"Added {m['name']} ({m['drug_class']}) {m.get('dose') or ''}".strip(),
                "details": {
                    "medication_id": m["id"],
                    "name": m["name"],
                    "drug_class": m["drug_class"],
                    "dose": m.get("dose"),
                    "is_active": m["end_date"] is None,
                },
            })
    finally:
        conn.close()

    # Sort by date descending and limit
    entries.sort(key=lambda e: e["date"], reverse=True)
    entries = entries[:limit]

    return [PatientTimelineEntry(**e) for e in entries]


# ---------------------------------------------------------------------------
# Available Scales (not patient-specific, but lives here for convenience)
# ---------------------------------------------------------------------------

@router.get(
    "/scales/available",
    summary="List available assessment scales",
)
async def list_available_scales(condition: Optional[str] = None):
    """List validated clinical assessment scales.

    Optionally filter by condition slug to see only scales validated for
    that condition. Returns scale definitions including severity bands.
    """
    try:
        from sozo_generator.schemas.patient import VALIDATED_SCALES
        scales = list(VALIDATED_SCALES.values())
    except ImportError:
        # Fallback minimal set if the schemas package is unavailable
        return {
            "scales": [
                {
                    "abbreviation": "PHQ-9",
                    "full_name": "Patient Health Questionnaire-9",
                    "score_range": {"min": 0, "max": 27},
                    "validated_for": ["depression"],
                },
                {
                    "abbreviation": "GAD-7",
                    "full_name": "Generalised Anxiety Disorder-7",
                    "score_range": {"min": 0, "max": 21},
                    "validated_for": ["anxiety", "depression"],
                },
            ],
            "total": 2,
            "note": "Fallback — sozo_generator.schemas.patient not importable",
        }

    if condition:
        scales = [s for s in scales if condition in s.validated_for]

    return {
        "scales": [
            {
                "scale_name": s.scale_name,
                "abbreviation": s.abbreviation,
                "full_name": s.full_name,
                "domains": s.domains,
                "score_range": {"min": s.score_range.min, "max": s.score_range.max},
                "severity_bands": {
                    label: {"min": band.min, "max": band.max}
                    for label, band in s.severity_bands.items()
                },
                "scoring_direction": s.scoring_direction.value,
                "administration_time_minutes": s.administration_time_minutes,
                "validated_for": s.validated_for,
            }
            for s in scales
        ],
        "total": len(scales),
    }
