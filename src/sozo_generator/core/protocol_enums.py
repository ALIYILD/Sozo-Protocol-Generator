"""Protocol lifecycle and system enums for Sozo Protocol Generator.

Extends the core enums with protocol-specific status, role, and classification types.
These enums cover the full protocol lifecycle from draft through review and approval,
user access control, clinical safety classifications, and audit tracking.
"""

from enum import Enum


class ProtocolStatus(str, Enum):
    """Protocol version lifecycle states.

    Tracks a protocol from initial creation through review, approval,
    and eventual archival or supersession. Enforces a directed state
    machine via ``valid_transitions`` and ``can_transition_to``.
    """

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"

    @classmethod
    def valid_transitions(cls) -> dict:
        """Return the set of allowed next-states for each status.

        Terminal states (SUPERSEDED, ARCHIVED) have no outgoing transitions.
        REJECTED protocols may return to DRAFT for revision.
        """
        return {
            cls.DRAFT: {cls.PENDING_REVIEW, cls.ARCHIVED},
            cls.PENDING_REVIEW: {cls.APPROVED, cls.REJECTED},
            cls.APPROVED: {cls.SUPERSEDED, cls.ARCHIVED},
            cls.REJECTED: {cls.DRAFT},  # Can go back to draft for revision
            cls.SUPERSEDED: set(),  # Terminal
            cls.ARCHIVED: set(),  # Terminal
        }

    def can_transition_to(self, target: "ProtocolStatus") -> bool:
        """Check whether transitioning from the current state to *target* is allowed."""
        return target in self.valid_transitions().get(self, set())


class GenerationMethod(str, Enum):
    """How a protocol was generated.

    Distinguishes between fully automated condition-based generation,
    template extraction, LLM prompt generation, personalised adaptation,
    and manual authoring.
    """

    CONDITION_BASED = "condition_based"
    TEMPLATE_EXTRACTED = "template_extracted"
    PROMPT_GENERATED = "prompt_generated"
    PERSONALIZED = "personalized"
    MANUAL = "manual"


class UserRole(str, Enum):
    """Access-control roles within the Sozo system.

    Ordered roughly by privilege level from clinician (full clinical
    access) down to read-only observers.
    """

    CLINICIAN = "clinician"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    OPERATOR = "operator"
    READONLY = "readonly"


class ReviewStatus(str, Enum):
    """Outcome states for a protocol review cycle.

    Note: This is distinct from ``enums.ReviewStatus`` which tracks
    document build lifecycle. This enum captures *clinical review*
    outcomes specifically.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class Hemisphere(str, Enum):
    """Brain hemisphere targeting for stimulation protocols."""

    LEFT = "left"
    RIGHT = "right"
    BILATERAL = "bilateral"
    MIDLINE = "midline"


class StopSeverity(str, Enum):
    """Severity classification for stop-rule triggers during treatment.

    Determines the clinical response when an adverse event or threshold
    breach occurs mid-session.
    """

    IMMEDIATE_STOP = "immediate_stop"
    PAUSE_AND_REVIEW = "pause_and_review"
    NOTE_AND_CONTINUE = "note_and_continue"


class ContraindicationSeverity(str, Enum):
    """Severity levels for contraindications to neuromodulation.

    ABSOLUTE contraindications prohibit treatment entirely.
    RELATIVE contraindications require risk-benefit analysis.
    PRECAUTION items warrant monitoring but do not prevent treatment.
    """

    ABSOLUTE = "absolute"
    RELATIVE = "relative"
    PRECAUTION = "precaution"


class AssessmentTiming(str, Enum):
    """When clinical assessments should be administered relative to treatment."""

    PRE_TREATMENT = "pre_treatment"
    EACH_SESSION = "each_session"
    WEEKLY = "weekly"
    MID_TREATMENT = "mid_treatment"
    POST_TREATMENT = "post_treatment"
    FOLLOW_UP = "follow_up"


class ScoringDirection(str, Enum):
    """Interpretation direction for clinical outcome measures.

    Determines whether a decrease or increase in score represents
    clinical improvement.
    """

    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class PersonalizationConfidence(str, Enum):
    """Confidence level for personalised protocol recommendations.

    Drives the review pathway: HIGH proceeds with standard review,
    MODERATE triggers enhanced review, LOW requires specialist input,
    and INSUFFICIENT indicates the data is too sparse for a recommendation.
    """

    HIGH = "high"  # >=0.7 -- recommend with standard review
    MODERATE = "moderate"  # 0.4-0.7 -- recommend with enhanced review
    LOW = "low"  # <0.4 -- flag for specialist review
    INSUFFICIENT = "insufficient"  # Not enough data


class EEGBand(str, Enum):
    """Standard EEG frequency bands used in qEEG-guided personalisation."""

    DELTA = "delta"  # 0.5-4 Hz
    THETA = "theta"  # 4-8 Hz
    ALPHA = "alpha"  # 8-13 Hz
    BETA = "beta"  # 13-30 Hz
    HIGH_BETA = "high_beta"  # 30-40 Hz
    GAMMA = "gamma"  # 40-100 Hz


class AuditAction(str, Enum):
    """Actions recorded in the protocol audit trail.

    Every mutation to a protocol or its review state is logged with
    one of these action types for traceability and compliance.
    """

    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    EVIDENCE_REFRESHED = "evidence_refreshed"
    PERSONALIZED = "personalized"
    EXPORTED = "exported"
    ARCHIVED = "archived"


class DrugInteractionSeverity(str, Enum):
    """Severity levels for drug-neuromodulation interactions.

    CONTRAINDICATED means the combination must not be used.
    MAJOR requires protocol modification (e.g. reduced intensity).
    MODERATE requires close monitoring during sessions.
    MINOR is informational only.
    UNKNOWN flags insufficient evidence for classification.
    """

    CONTRAINDICATED = "contraindicated"  # Must not combine
    MAJOR = "major"  # Significant risk, modify protocol
    MODERATE = "moderate"  # Monitor closely
    MINOR = "minor"  # Awareness only
    UNKNOWN = "unknown"  # Insufficient data
