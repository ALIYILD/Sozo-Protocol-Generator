"""
sozo_db — SQLAlchemy database layer for the Sozo Protocol Generator.

Exports all models, engine utilities, base classes, and repositories.
"""
from .base import Base, UUIDMixin, TimestampMixin
from .engine import (
    build_engine,
    get_engine,
    get_session,
    get_session_factory,
    dispose_engine,
)
from .repository import BaseRepository
from .models import (
    User,
    Protocol,
    ProtocolVersion,
    EvidenceArticle,
    ProtocolEvidence,
    Patient,
    Assessment,
    TreatmentRecord,
    Medication,
    EEGRecord,
    Review,
    AuditEvent,
    TreatmentSession,
)
from .repositories import (
    ProtocolRepository,
    EvidenceRepository,
    PatientRepository,
    AuditRepository,
)

__all__ = [
    # Base
    "Base",
    "UUIDMixin",
    "TimestampMixin",
    # Engine
    "build_engine",
    "get_engine",
    "get_session",
    "get_session_factory",
    "dispose_engine",
    # Models
    "User",
    "Protocol",
    "ProtocolVersion",
    "EvidenceArticle",
    "ProtocolEvidence",
    "Patient",
    "Assessment",
    "TreatmentRecord",
    "Medication",
    "EEGRecord",
    "Review",
    "AuditEvent",
    "TreatmentSession",
    # Repositories
    "BaseRepository",
    "ProtocolRepository",
    "EvidenceRepository",
    "PatientRepository",
    "AuditRepository",
]
