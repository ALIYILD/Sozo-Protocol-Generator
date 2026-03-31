class SozoGeneratorError(Exception):
    """Base exception for sozo_generator."""


class TemplateExtractionError(SozoGeneratorError):
    """Raised when template extraction fails."""


class EvidenceIngestionError(SozoGeneratorError):
    """Raised when evidence ingestion fails."""


class ConditionNotFoundError(SozoGeneratorError):
    """Raised when a condition slug is not registered."""


class SchemaValidationError(SozoGeneratorError):
    """Raised when a Pydantic schema validation fails."""


class DocumentGenerationError(SozoGeneratorError):
    """Raised when document generation fails."""


class VisualGenerationError(SozoGeneratorError):
    """Raised when visual/diagram generation fails."""


class InsufficientEvidenceError(SozoGeneratorError):
    """Raised in strict mode when evidence is below threshold."""


class ReviewRequiredError(SozoGeneratorError):
    """Raised when content requires clinical review and strict mode is enabled."""
