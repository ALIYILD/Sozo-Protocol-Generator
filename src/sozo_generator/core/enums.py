from enum import Enum


class Tier(str, Enum):
    FELLOW = "fellow"
    PARTNERS = "partners"
    BOTH = "both"


class DocumentType(str, Enum):
    CLINICAL_EXAM = "clinical_exam"
    PHENOTYPE_CLASSIFICATION = "phenotype_classification"
    RESPONDER_TRACKING = "responder_tracking"
    PSYCH_INTAKE = "psych_intake"
    NETWORK_ASSESSMENT = "network_assessment"  # Partners only
    HANDBOOK = "handbook"
    ALL_IN_ONE_PROTOCOL = "all_in_one_protocol"
    EVIDENCE_BASED_PROTOCOL = "evidence_based_protocol"


class EvidenceLevel(str, Enum):
    HIGHEST = "highest"  # guideline, systematic review, meta-analysis, large RCT
    HIGH = "high"        # RCT, controlled trial
    MEDIUM = "medium"    # cohort, narrative review, consensus
    LOW = "low"          # pilot, feasibility, case series
    VERY_LOW = "very_low"  # case report, expert opinion
    MISSING = "missing"   # no evidence found


class EvidenceType(str, Enum):
    CLINICAL_PRACTICE_GUIDELINE = "clinical_practice_guideline"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    LARGE_RCT = "large_rct"
    RCT = "rct"
    CONTROLLED_TRIAL = "controlled_trial"
    COHORT_STUDY = "cohort_study"
    NARRATIVE_REVIEW = "narrative_review"
    CONSENSUS_STATEMENT = "consensus_statement"
    PILOT_STUDY = "pilot_study"
    FEASIBILITY_STUDY = "feasibility_study"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"
    EXPERT_OPINION = "expert_opinion"
    INDIRECT_EVIDENCE = "indirect_evidence"
    MANUAL_ENTRY = "manual_entry"


class ClaimCategory(str, Enum):
    PATHOPHYSIOLOGY = "pathophysiology"
    BRAIN_REGIONS = "brain_regions"
    NETWORK_INVOLVEMENT = "network_involvement"
    CLINICAL_PHENOTYPES = "clinical_phenotypes"
    ASSESSMENT_TOOLS = "assessment_tools"
    STIMULATION_TARGETS = "stimulation_targets"
    STIMULATION_PARAMETERS = "stimulation_parameters"
    MODALITY_RATIONALE = "modality_rationale"
    SAFETY = "safety"
    CONTRAINDICATIONS = "contraindications"
    RESPONDER_CRITERIA = "responder_criteria"
    INCLUSION_CRITERIA = "inclusion_criteria"
    EXCLUSION_CRITERIA = "exclusion_criteria"


class ConfidenceLabel(str, Enum):
    HIGH = "high_confidence"
    MEDIUM = "medium_confidence"
    LOW = "low_confidence"
    INSUFFICIENT = "insufficient"
    REVIEW_REQUIRED = "review_required"


class ReviewFlag(str, Enum):
    MISSING_PRIMARY_SOURCE = "missing_primary_source"
    CONTRADICTING_SOURCES = "contradicting_sources"
    INDIRECT_EVIDENCE_ONLY = "indirect_evidence_only"
    PILOT_DATA_ONLY = "pilot_data_only"
    OFF_LABEL_NOT_FLAGGED = "off_label_not_flagged"
    TEMPLATE_CARRYOVER = "template_carryover"
    INCOMPLETE_SAFETY = "incomplete_safety"
    NO_VALIDATED_SCALE = "no_validated_scale"
    PLACEHOLDER_TEXT = "placeholder_text"
    MISSING_SECTION = "missing_section"


class Modality(str, Enum):
    TDCS = "tdcs"
    TPS = "tps"
    TAVNS = "tavns"
    CES = "ces"
    TMS = "tms"
    NFB = "nfb"
    MULTIMODAL = "multimodal"


class NetworkKey(str, Enum):
    DMN = "dmn"
    CEN = "cen"
    SN = "sn"
    SMN = "smn"
    LIMBIC = "limbic"
    ATTENTION = "attention"


class NetworkDysfunction(str, Enum):
    HYPO = "hypo"
    NORMAL = "normal"
    HYPER = "hyper"


# ── Phase 2 enums ────────────────────────────────────────────────────


class QASeverity(str, Enum):
    """Severity levels for QA issues. BLOCK prevents export."""
    BLOCK = "block"
    WARNING = "warning"
    INFO = "info"


class ReviewStatus(str, Enum):
    """Lifecycle states for a generated document build."""
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPORTED = "exported"
    FLAGGED = "flagged"


class EvidenceRelation(str, Enum):
    """Relationship of an article to a claim."""
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"
    INDIRECT = "indirect"
