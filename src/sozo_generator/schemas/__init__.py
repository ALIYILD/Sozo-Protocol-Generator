"""SOZO Generator schema models.

Canonical Pydantic models for protocols, conditions, evidence,
patients, EEG, and documents.
"""
# Existing
from sozo_generator.schemas.condition import ConditionSchema
from sozo_generator.schemas.evidence import (
    ArticleMetadata,
    EvidenceClaim,
    EvidenceDossier,
)
from sozo_generator.schemas.documents import (
    DocumentSpec,
    SectionContent,
    SectionClaim,
)

# New
from sozo_generator.schemas.protocol import (
    SozoProtocol,
    ConditionInfo,
    ModalityInfo,
    StimulationParameters,
    Schedule,
    Safety,
    EvidenceReference,
    Personalization,
    AuditMetadata,
)
from sozo_generator.schemas.patient import (
    PatientProfile,
    Demographics,
    SymptomAssessment,
    TreatmentRecord,
    MedicationRecord,
    AssessmentScale,
    VALIDATED_SCALES,
)
from sozo_generator.schemas.eeg import (
    EEGRecording,
    EEGFeatures,
    EEGBand,
    BandPower,
    ChannelData,
    AsymmetryIndex,
    QEEGNormativeComparison,
)
