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
# Long-document pipeline — canonical models
from sozo_generator.schemas.canonical import (
    # Literal type aliases
    AssemblyStatus,
    AssetStatus,
    AssetType,
    BlockType,
    SectionVariant,
    ValidationSeverity,
    # Planning-time specs
    ContentBlockSpec,
    SubsectionSpec,
    SectionSpec,
    DocumentBlueprint,
    # Asset tracking
    AssetRecord,
    # Resolved content models
    CanonicalBlock,
    CanonicalSection,
    # Standalone asset content models
    CanonicalChart,
    CanonicalFigure,
    CanonicalImage,
    CanonicalTable,
    # Citations
    CanonicalCitation,
    # QA
    DocumentQAReport,
    QAValidationIssue,
    QAValidationResult,
    # Provenance
    AssemblyProvenance,
    # Root document model
    CanonicalDocument,
)
