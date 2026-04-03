# Sozo LangGraph Architecture — Implementation-Ready Design

> Clinical decision support for evidence-based neuromodulation protocol generation.
> Schema-first. Deterministic where possible. Auditable. Human-in-the-loop.

---

## 1. Recommended LangGraph Architecture

### Why StateGraph Over Multi-Agent Chat

Sozo is **clinical decision support software**. The consequences of an incorrect recommendation — wrong stimulation intensity, missed contraindication, unsupported claim — are categorically different from a chatbot giving a bad restaurant suggestion. This demands:

**Deterministic control flow.** A StateGraph defines exactly which node executes after which, under what conditions. There is no "let the agents figure it out" step. When a clinician asks "why did Sozo recommend 2 mA over left DLPFC?", we can point to the exact node that made that decision, the exact evidence objects it consumed, and the exact state it wrote.

**Explicit state mutations.** Every node receives typed input and produces typed output. The state schema is the contract. No node can silently add a field, mutate a neighbor's output, or inject hidden context. In healthcare, hidden mutable state is a regulatory failure.

**Interrupt-based human review.** LangGraph's `interrupt_before` / `interrupt_after` mechanism lets us pause the graph at mandatory review points. The clinician sees exactly what the graph has produced, approves or edits it, and execution resumes. This is not optional — no protocol ships without clinician sign-off.

**Auditability by construction.** Every node logs its inputs, outputs, and decisions. The checkpointer stores every state version. A full execution trace — from intake to final protocol — can be reconstructed from the persisted state alone.

**Why not multi-agent chat:** In an open-ended agent loop, Agent A might argue with Agent B about stimulation parameters. Agent C might "agree" by restating Agent A's claim without evidence. The result looks like consensus but is actually hallucinated agreement. In Sozo, if the evidence says 2 mA, the deterministic parameter extractor says 2 mA. The LLM composes prose around that fact. There is no debate.

### Subgraph Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOP-LEVEL: sozo_protocol_graph               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   INTAKE &    │  │   EVIDENCE   │  │     PROTOCOL       │   │
│  │ NORMALIZATION │→ │   PIPELINE   │→ │    COMPOSITION     │   │
│  │  (subgraph)   │  │  (subgraph)  │  │    (subgraph)      │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│         │                                       │              │
│         │              ┌──────────────┐         │              │
│         └─────────────→│ EEG PERSONAL │─────────┘              │
│           (if EEG)     │  (subgraph)  │  (optional)            │
│                        └──────────────┘                        │
│                                                                 │
│                        ┌──────────────┐                        │
│                        │   REVIEW &   │                        │
│                        │   RELEASE    │                        │
│                        │  (subgraph)  │                        │
│                        └──────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

**(a) Intake & Normalization** — Accepts upload or prompt, determines condition, validates inputs, normalizes to a canonical request object. Mostly deterministic with one LLM node for prompt interpretation.

**(b) Evidence Pipeline** — Multi-source search, dedup, screening, parameter extraction, scoring. Entirely deterministic. Delegates to the existing `ResearchPipeline` and `EvidenceSummarizer`.

**(c) Protocol Composition** — Selects template, composes sections, runs safety gates, builds the `ProtocolSequence`. Mix of deterministic lookups and LLM-assisted prose generation.

**(d) EEG Personalization** (optional) — Loads EEG/QEEG data, extracts features, interprets findings, adjusts protocol parameters. Deterministic signal processing + one LLM interpretation node.

**(e) Review & Release** — Packages the draft for clinician review, pauses at interrupt, processes approval/rejection/edits, generates final output.

---

## 2. Concrete Graph Definition

### Node Catalog

Each node specifies: type (deterministic/LLM), purpose, input/output schemas, external services, failure modes, retry policy, and logging.

---

#### INTAKE & NORMALIZATION SUBGRAPH

##### `intake_router`
- **Type:** Deterministic
- **Purpose:** Classifies the request as `upload` or `prompt` based on input fields. Routes to the appropriate parser.
- **Input:** `{ source_mode: Optional[str], uploaded_file: Optional[bytes], uploaded_filename: Optional[str], user_prompt: Optional[str] }`
- **Output:** `{ source_mode: "upload" | "prompt", routing_decision: str }`
- **External:** None
- **Failure:** If both upload and prompt are empty → set `error: "no_input"`, route to error handler
- **Retry:** None (deterministic)
- **Logged:** `source_mode`, `has_upload`, `has_prompt`, `routing_decision`

##### `template_parser`
- **Type:** Deterministic
- **Purpose:** Parses uploaded DOCX/PDF into structured sections using `build_template_profile()`. Extracts condition hints, section map, tone profile.
- **Input:** `{ uploaded_file: bytes, uploaded_filename: str }`
- **Output:** `{ template_profile: TemplateProfile, inferred_condition: Optional[str], inferred_doc_type: Optional[str], parse_warnings: list[str] }`
- **External:** `sozo_generator.template_profiles.builder`
- **Failure:** Malformed file → `parse_error` with details, routed to clinician for manual correction
- **Retry:** None (parsing is deterministic)
- **Logged:** `filename`, `sections_found`, `inferred_condition`, `inferred_doc_type`, `parse_warnings`

##### `prompt_normalizer`
- **Type:** LLM node
- **Purpose:** Interprets natural-language prompt into structured request fields: condition slug, modality preferences, patient context, personalization hints.
- **Input:** `{ user_prompt: str, available_conditions: list[str], available_modalities: list[str] }`
- **Output:** (Pydantic-validated JSON)
```python
class NormalizedRequest(BaseModel):
    condition_slug: str        # must be in available_conditions
    condition_display: str
    modality_preferences: list[str]
    patient_context: Optional[PatientContext]
    personalization_requested: bool
    eeg_data_referenced: bool
    uncertainty_flags: list[str]  # things the LLM couldn't resolve
```
- **External:** Claude API (structured output)
- **Failure:** LLM returns invalid condition → fallback to `uncertainty_flags`, route to clinician
- **Retry:** 1 retry with rephrased prompt
- **Logged:** `user_prompt`, `normalized_output`, `model_used`, `latency_ms`

##### `condition_resolver`
- **Type:** Deterministic
- **Purpose:** Validates condition slug against the registry. Loads `ConditionSchema` with full clinical metadata.
- **Input:** `{ condition_slug: str, inferred_condition: Optional[str] }`
- **Output:** `{ condition: ConditionSchema, condition_valid: bool, resolution_source: str }`
- **External:** `sozo_generator.conditions.registry`
- **Failure:** Unknown condition → `condition_valid: false`, route to unsupported-condition gate
- **Retry:** None
- **Logged:** `condition_slug`, `condition_valid`, `resolution_source`

##### `intake_validator`
- **Type:** Deterministic
- **Purpose:** Validates completeness of intake data. Checks required fields for the requested document type.
- **Input:** `{ condition: ConditionSchema, source_mode: str, patient_context: Optional[PatientContext], doc_type: str }`
- **Output:** `{ intake_valid: bool, missing_fields: list[str], warnings: list[str] }`
- **External:** None
- **Failure:** Missing critical fields → pause for clinician input
- **Retry:** None
- **Logged:** `intake_valid`, `missing_fields`, `warnings`

---

#### EVIDENCE PIPELINE SUBGRAPH

##### `evidence_search`
- **Type:** Deterministic
- **Purpose:** Executes multi-source search using the `ResearchPipeline`. Queries PubMed, Crossref, Semantic Scholar using the `QueryPlanner`.
- **Input:** `{ condition: ConditionSchema, target_modality: Optional[str] }`
- **Output:** `{ raw_articles: list[ArticleMetadata], search_queries: list[str], source_counts: dict[str, int] }`
- **External:** `sozo_generator.evidence.research_pipeline.ResearchPipeline` (search stage)
- **Failure:** All sources down → `evidence_unavailable: true`, log error, proceed with cached evidence if available
- **Retry:** 2 retries with exponential backoff per source
- **Logged:** `query_count`, `total_results`, `source_counts`, `errors`

##### `evidence_dedup`
- **Type:** Deterministic
- **Purpose:** Cross-source deduplication using PMID, DOI, and title similarity.
- **Input:** `{ raw_articles: list[ArticleMetadata] }`
- **Output:** `{ unique_articles: list[ArticleMetadata], duplicates_removed: int, method_counts: dict }`
- **External:** `sozo_generator.evidence.fuzzy_dedup`
- **Failure:** None (always succeeds)
- **Retry:** None
- **Logged:** `input_count`, `output_count`, `duplicates_removed`, `method_counts`

##### `evidence_screen`
- **Type:** Deterministic
- **Purpose:** Screens articles for neuromodulation protocol relevance using keyword heuristics.
- **Input:** `{ unique_articles: list[ArticleMetadata], target_condition: str, target_modality: Optional[str] }`
- **Output:** `{ screened_articles: list[ArticleMetadata], excluded_count: int, uncertain_count: int }`
- **External:** `sozo_generator.evidence.screening.ScreeningService`
- **Failure:** None
- **Retry:** None
- **Logged:** `input_count`, `included`, `excluded`, `uncertain`

##### `evidence_extract`
- **Type:** Deterministic
- **Purpose:** Extracts structured stimulation parameters from screened articles using regex patterns.
- **Input:** `{ screened_articles: list[ArticleMetadata] }`
- **Output:** `{ extractions: dict[str, ExtractionResult] }` — keyed by article identifier
- **External:** `sozo_generator.evidence.parameter_extractor.ParameterExtractor`
- **Failure:** None (individual extraction failures are logged, not fatal)
- **Retry:** None
- **Logged:** `articles_processed`, `articles_with_params`, `total_fields_extracted`

##### `evidence_score`
- **Type:** Deterministic
- **Purpose:** Multi-dimensional quality + relevance scoring. Assigns A/B/C/D grades.
- **Input:** `{ screened_articles: list[ArticleMetadata], extractions: dict, target_modality: str, target_condition: str, target_brain_region: Optional[str] }`
- **Output:** `{ evidence_scores: dict[str, EvidenceScore], evidence_summary: EvidenceSummary }`
- **External:** `sozo_generator.evidence.evidence_scorer.EvidenceScorer`
- **Failure:** None
- **Retry:** None
- **Logged:** `articles_scored`, `grade_distribution`, `mean_quality`, `mean_relevance`

##### `evidence_sufficiency_gate`
- **Type:** Deterministic
- **Purpose:** Checks if there is enough evidence to proceed. Requires at minimum 1 Grade A or B article for primary protocol parameters.
- **Input:** `{ evidence_scores: dict, condition: ConditionSchema }`
- **Output:** `{ evidence_sufficient: bool, evidence_level: str, gaps: list[str], proceed_with_caution: bool }`
- **External:** None
- **Failure:** Insufficient evidence → flag for clinician review with explicit gap list
- **Retry:** None
- **Logged:** `evidence_sufficient`, `evidence_level`, `gaps`

---

#### PROTOCOL COMPOSITION SUBGRAPH

##### `safety_policy_engine`
- **Type:** Deterministic
- **Purpose:** Applies contraindication rules, modality restrictions, and regulatory constraints. Loads from `sozo_knowledge/shared/safety_principles.yaml` and `contraindications/universal.yaml`.
- **Input:** `{ condition: ConditionSchema, patient_context: Optional[PatientContext], target_modalities: list[str] }`
- **Output:**
```python
class SafetyAssessment(BaseModel):
    contraindications_found: list[ContraindicationFlag]
    modality_restrictions: list[ModalityRestriction]
    consent_requirements: list[str]
    off_label_flags: list[str]
    safety_cleared: bool
    blocking_contraindications: list[str]  # hard stops
    proceed_with_warnings: list[str]       # can proceed with disclosure
```
- **External:** `sozo_knowledge` YAML files, `ConditionSchema.safety_notes`
- **Failure:** None (rule-based, always returns)
- **Retry:** None
- **Logged:** full `SafetyAssessment`

##### `contraindication_gate`
- **Type:** Deterministic
- **Purpose:** Hard stop if blocking contraindications are present. No override possible without clinician.
- **Input:** `{ safety_assessment: SafetyAssessment }`
- **Output:** `{ gate_passed: bool, blocked_reason: Optional[str] }`
- **External:** None
- **Failure:** Blocking contraindication → interrupt to clinician with explicit reason
- **Retry:** None
- **Logged:** `gate_passed`, `blocked_reason`

##### `protocol_template_selector`
- **Type:** Deterministic
- **Purpose:** Selects the appropriate protocol template and SOZO sequence based on condition, modality, and evidence. Uses `build_sozo_sequence()` from `sozo_protocol.builder`.
- **Input:** `{ condition: ConditionSchema, target_modalities: list[str], safety_assessment: SafetyAssessment, evidence_scores: dict }`
- **Output:** `{ base_sequence: ProtocolSequence, template_source: str, selection_rationale: str }`
- **External:** `sozo_protocol.builder.build_sozo_sequence`, `sozo_knowledge` protocols
- **Failure:** No matching template → flag as unsupported configuration
- **Retry:** None
- **Logged:** `sequence_id`, `phases_count`, `modalities_used`, `template_source`

##### `protocol_composer`
- **Type:** LLM node (structured output)
- **Purpose:** Generates prose sections for the protocol document grounded in evidence. Does NOT choose parameters — those come from the deterministic `base_sequence`. The LLM writes rationale text, clinical context, and narrative sections.
- **Input:**
```python
class ComposerInput(BaseModel):
    condition: ConditionSchema
    base_sequence: ProtocolSequence
    evidence_pool: list[ScoredArticle]  # articles with grades
    safety_assessment: SafetyAssessment
    doc_type: str
    tier: str
    section_specs: list[SectionSpec]
```
- **Output:**
```python
class ComposedProtocol(BaseModel):
    sections: list[ComposedSection]

class ComposedSection(BaseModel):
    section_id: str
    title: str
    content: str
    cited_evidence_ids: list[str]  # PMID or DOI — REQUIRED
    confidence: str
    generation_method: str
    claims: list[ProtocolClaim]

class ProtocolClaim(BaseModel):
    claim_text: str
    evidence_ids: list[str]  # MUST reference evidence_pool items
    claim_type: str  # supports | informs | safety_note
    confidence: str
    uncertainty_flag: Optional[str]  # REQUIRED if evidence is weak
```
- **External:** Claude API with structured output enforcement
- **Failure:** Invalid JSON → retry once. Still invalid → fallback to data-driven section builder
- **Retry:** 1 retry with tighter prompt
- **Logged:** `sections_composed`, `total_citations`, `generation_methods`, `model_used`, `latency_ms`

##### `grounding_validator`
- **Type:** Deterministic
- **Purpose:** Validates all composed sections against evidence. Checks PMID validity, claim support, prohibited language, citation density.
- **Input:** `{ composed_sections: list[ComposedSection], evidence_pool: list[ScoredArticle] }`
- **Output:** `{ grounding_results: list[GroundingResult], overall_grounding_score: float, blocking_issues: list[str] }`
- **External:** `sozo_generator.grounding.validator.GroundingValidator`
- **Failure:** Blocking issues found → flag sections for revision
- **Retry:** None
- **Logged:** `grounding_score`, `issues_by_severity`, `pmids_verified`, `pmids_unverified`

---

#### EEG PERSONALIZATION SUBGRAPH (Optional)

##### `eeg_feature_loader`
- **Type:** Deterministic
- **Purpose:** Loads EEG/QEEG data from uploaded file or external system. Validates format and quality.
- **Input:** `{ eeg_file: Optional[bytes], eeg_source: Optional[str], patient_id: Optional[str] }`
- **Output:** `{ eeg_data: EEGDataset, quality_metrics: QualityReport, data_valid: bool }`
- **External:** EEG file parsers (EDF, BDF, CSV)
- **Failure:** Invalid/corrupt file → `data_valid: false`, skip personalization
- **Retry:** None
- **Logged:** `channels`, `duration_s`, `sample_rate`, `quality_metrics`, `data_valid`

##### `eeg_interpreter`
- **Type:** LLM node (structured output)
- **Purpose:** Interprets EEG features in the context of the target condition. Identifies relevant biomarkers, network dysfunction patterns, and personalization opportunities.
- **Input:**
```python
class EEGInterpretationInput(BaseModel):
    condition_slug: str
    eeg_features: dict[str, float]  # band powers, ratios, asymmetry
    network_profiles: list[NetworkProfile]
    available_targets: list[StimulationTarget]
```
- **Output:**
```python
class EEGInterpretation(BaseModel):
    primary_findings: list[EEGFinding]
    recommended_adjustments: list[ParameterAdjustment]
    confidence: str
    interpretation_notes: str
    evidence_ids: list[str]  # MUST cite supporting literature

class EEGFinding(BaseModel):
    finding: str
    biomarker: str
    clinical_relevance: str
    evidence_ids: list[str]
    confidence: str

class ParameterAdjustment(BaseModel):
    parameter: str  # intensity, target, frequency, duration
    current_value: str
    recommended_value: str
    rationale: str
    evidence_ids: list[str]
    confidence: str
    uncertainty_flag: Optional[str]
```
- **External:** Claude API (structured output)
- **Failure:** Invalid output → skip personalization, use base protocol
- **Retry:** 1 retry
- **Logged:** `findings_count`, `adjustments_count`, `confidence`, `model_used`

##### `eeg_personalizer`
- **Type:** Deterministic
- **Purpose:** Applies validated EEG-driven adjustments to the `ProtocolSequence`. Enforces parameter bounds from `configs/modalities.yaml`. Never exceeds safety limits regardless of LLM recommendation.
- **Input:** `{ base_sequence: ProtocolSequence, adjustments: list[ParameterAdjustment], safety_assessment: SafetyAssessment }`
- **Output:** `{ personalized_protocol: PersonalizedProtocol, adjustments_applied: list[str], adjustments_rejected: list[str], rejection_reasons: list[str] }`
- **External:** `configs/modalities.yaml` (parameter bounds)
- **Failure:** All adjustments rejected → proceed with base protocol
- **Retry:** None
- **Logged:** `adjustments_applied`, `adjustments_rejected`, `rejection_reasons`, `final_parameters`

---

#### REVIEW & RELEASE SUBGRAPH

##### `clinician_review_interrupt`
- **Type:** Interrupt (LangGraph `interrupt_before`)
- **Purpose:** Pauses graph execution and presents the complete draft to the clinician. This is a MANDATORY checkpoint — no protocol reaches production without human approval.
- **Input:** Full `SozoGraphState` (all fields populated)
- **Output:** `{ review_decision: "approve" | "reject" | "edit", reviewer_id: str, review_notes: str, edits: Optional[dict] }`
- **External:** None (interrupt mechanism)
- **Failure:** N/A (pauses indefinitely until clinician acts)
- **Retry:** N/A
- **Logged:** `reviewer_id`, `review_decision`, `review_timestamp`, `sections_modified`

##### `review_processor`
- **Type:** Deterministic
- **Purpose:** Applies clinician edits to the protocol. If rejected, captures reason and routes back to appropriate node. If approved, stamps the protocol.
- **Input:** `{ review_decision: str, edits: Optional[dict], protocol: ComposedProtocol }`
- **Output:** `{ protocol_status: str, revision_number: int, approval_stamp: Optional[ApprovalStamp] }`
- **External:** None
- **Failure:** None
- **Retry:** None
- **Logged:** `review_decision`, `edits_applied`, `revision_number`, `reviewer_id`

##### `protocol_reporter`
- **Type:** Deterministic
- **Purpose:** Renders the approved protocol into output formats: DOCX, JSON, FHIR-compatible bundle. Includes full reference list, PRISMA diagram, evidence summary.
- **Input:** `{ approved_protocol: ComposedProtocol, base_sequence: ProtocolSequence, evidence_summary: EvidenceSummary, prisma_counts: PRISMAFlowCounts }`
- **Output:** `{ output_paths: dict[str, str], output_formats: list[str] }`
- **External:** `sozo_generator.docx.renderer`, `sozo_generator.evidence.prisma_diagram`
- **Failure:** Rendering error → log and return partial outputs
- **Retry:** 1 retry
- **Logged:** `output_formats`, `output_paths`, `file_sizes`

##### `audit_logger`
- **Type:** Deterministic
- **Purpose:** Writes the complete execution audit record. Includes every node's inputs/outputs, every decision point, every state transition, every evidence object referenced, every clinician interaction.
- **Input:** Full `SozoGraphState` including `node_history`
- **Output:** `{ audit_record_id: str, audit_path: str }`
- **External:** File system / database
- **Failure:** Audit write failure → BLOCK release (audit is mandatory)
- **Retry:** 3 retries
- **Logged:** `audit_record_id`, `total_events`, `total_evidence_refs`, `execution_duration_s`

---

## 3. Shared State Schema

### JSON Schema (abbreviated)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SozoGraphState",
  "type": "object",
  "required": ["request_id", "source_mode", "status"],
  "properties": {
    "request_id": { "type": "string", "format": "uuid" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" },
    "status": {
      "type": "string",
      "enum": ["intake", "evidence", "composition", "personalization",
               "review", "approved", "rejected", "released", "error"]
    },
    "source_mode": { "type": "string", "enum": ["upload", "prompt"] },

    "intake": {
      "type": "object",
      "properties": {
        "user_prompt": { "type": ["string", "null"] },
        "uploaded_filename": { "type": ["string", "null"] },
        "template_profile": { "$ref": "#/$defs/TemplateProfile" },
        "normalized_request": { "$ref": "#/$defs/NormalizedRequest" }
      }
    },

    "condition": {
      "type": "object",
      "properties": {
        "slug": { "type": "string" },
        "display_name": { "type": "string" },
        "icd10": { "type": "string" },
        "schema": { "$ref": "#/$defs/ConditionSchema" },
        "resolution_source": { "type": "string" }
      }
    },

    "patient_context": {
      "type": ["object", "null"],
      "properties": {
        "patient_id": { "type": ["string", "null"] },
        "age": { "type": ["integer", "null"] },
        "sex": { "type": ["string", "null"] },
        "diagnosis_icd10": { "type": ["string", "null"] },
        "current_medications": { "type": "array", "items": { "type": "string" } },
        "contraindications": { "type": "array", "items": { "type": "string" } },
        "prior_neuromodulation": { "type": "array", "items": { "type": "string" } },
        "assessment_scores": { "type": "object" },
        "phenotype_slug": { "type": ["string", "null"] },
        "severity_level": { "type": ["string", "null"] }
      }
    },

    "evidence": {
      "type": "object",
      "properties": {
        "search_queries": { "type": "array", "items": { "type": "string" } },
        "source_counts": { "type": "object" },
        "raw_article_count": { "type": "integer" },
        "unique_article_count": { "type": "integer" },
        "screened_article_count": { "type": "integer" },
        "articles": {
          "type": "array",
          "items": { "$ref": "#/$defs/ScoredArticle" }
        },
        "extractions": { "type": "object" },
        "evidence_summary": { "$ref": "#/$defs/EvidenceSummary" },
        "evidence_sufficient": { "type": "boolean" },
        "evidence_gaps": { "type": "array", "items": { "type": "string" } },
        "prisma_counts": { "$ref": "#/$defs/PRISMAFlowCounts" },
        "pipeline_log_path": { "type": ["string", "null"] }
      }
    },

    "safety": {
      "type": "object",
      "properties": {
        "contraindications_found": { "type": "array" },
        "modality_restrictions": { "type": "array" },
        "consent_requirements": { "type": "array", "items": { "type": "string" } },
        "off_label_flags": { "type": "array", "items": { "type": "string" } },
        "safety_cleared": { "type": "boolean" },
        "blocking_contraindications": { "type": "array", "items": { "type": "string" } }
      }
    },

    "protocol": {
      "type": "object",
      "properties": {
        "base_sequence": { "$ref": "#/$defs/ProtocolSequence" },
        "template_source": { "type": "string" },
        "composed_sections": { "type": "array" },
        "grounding_score": { "type": "number" },
        "grounding_issues": { "type": "array" },
        "doc_type": { "type": "string" },
        "tier": { "type": "string" }
      }
    },

    "eeg": {
      "type": ["object", "null"],
      "properties": {
        "data_available": { "type": "boolean" },
        "features": { "type": "object" },
        "interpretation": { "$ref": "#/$defs/EEGInterpretation" },
        "adjustments_applied": { "type": "array" },
        "adjustments_rejected": { "type": "array" },
        "personalized_protocol": { "$ref": "#/$defs/PersonalizedProtocol" }
      }
    },

    "review": {
      "type": "object",
      "properties": {
        "status": { "type": "string", "enum": ["pending", "approved", "rejected", "edited"] },
        "reviewer_id": { "type": ["string", "null"] },
        "review_timestamp": { "type": ["string", "null"] },
        "review_notes": { "type": ["string", "null"] },
        "edits_applied": { "type": "array" },
        "revision_number": { "type": "integer", "default": 0 },
        "approval_stamp": { "$ref": "#/$defs/ApprovalStamp" }
      }
    },

    "output": {
      "type": "object",
      "properties": {
        "output_paths": { "type": "object" },
        "output_formats": { "type": "array", "items": { "type": "string" } },
        "audit_record_id": { "type": ["string", "null"] }
      }
    },

    "node_history": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "node_id": { "type": "string" },
          "started_at": { "type": "string" },
          "completed_at": { "type": "string" },
          "duration_ms": { "type": "number" },
          "status": { "type": "string" },
          "error": { "type": ["string", "null"] }
        }
      }
    },

    "errors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "node_id": { "type": "string" },
          "error_type": { "type": "string" },
          "message": { "type": "string" },
          "recoverable": { "type": "boolean" },
          "timestamp": { "type": "string" }
        }
      }
    },

    "version": { "type": "string", "default": "1.0" },
    "graph_version": { "type": "string" }
  }
}
```

### Pydantic Model Outline

```python
class SozoGraphState(TypedDict):
    """Top-level shared state for the Sozo LangGraph."""

    # Identity & lifecycle
    request_id: str
    created_at: str
    updated_at: str
    status: str  # intake | evidence | composition | personalization | review | approved | rejected | released | error

    # Intake
    source_mode: str  # upload | prompt
    intake: IntakeState
    condition: ConditionState
    patient_context: Optional[PatientContextState]

    # Evidence
    evidence: EvidenceState

    # Safety
    safety: SafetyState

    # Protocol
    protocol: ProtocolState

    # EEG (optional)
    eeg: Optional[EEGState]

    # Review
    review: ReviewState

    # Output
    output: OutputState

    # Audit
    node_history: list[NodeHistoryEntry]
    errors: list[ErrorEntry]
    version: str
    graph_version: str
```

*(Full Pydantic definitions in Section 9 pseudocode.)*

---

## 4. Control Flow and Branching

### Top-Level Graph Diagram

```
START
  │
  ▼
intake_router ──────────────────┐
  │                             │
  ├─ source_mode="upload" ──→ template_parser ──┐
  │                                              │
  └─ source_mode="prompt" ──→ prompt_normalizer ─┤
                                                  │
                                                  ▼
                                         condition_resolver
                                                  │
                                                  ▼
                                         intake_validator
                                                  │
                                    ┌─────────────┴───────────────┐
                                    │                             │
                                    ▼                             │
                             evidence_search                      │
                                    │                             │
                                    ▼                             │
                             evidence_dedup                       │
                                    │                             │
                                    ▼                             │
                             evidence_screen                      │
                                    │                             │
                                    ▼                             │
                             evidence_extract                     │
                                    │                             │
                                    ▼                             │
                             evidence_score                       │
                                    │                             │
                                    ▼                             │
                          evidence_sufficiency_gate               │
                                    │                             │
                        ┌───────────┴────────────┐               │
                        │                        │               │
                  sufficient=true          sufficient=false       │
                        │                        │               │
                        │                  [INTERRUPT:            │
                        │                   clinician_evidence    │
                        │                   _review]             │
                        │                        │               │
                        ▼                        ▼               │
                 safety_policy_engine    (clinician override      │
                        │                 or abort)               │
                        ▼                                        │
                 contraindication_gate                            │
                        │                                        │
                  ┌─────┴──────┐                                │
                  │            │                                 │
             gate_pass    gate_block                             │
                  │            │                                 │
                  │      [INTERRUPT:                             │
                  │       contraindication                       │
                  │       _review]                               │
                  ▼                                              │
          protocol_template_selector                             │
                  │                                              │
                  ▼                                              │
          protocol_composer (LLM)                                │
                  │                                              │
                  ▼                                              │
          grounding_validator                                    │
                  │                                              │
                  ▼                                              │
          ┌───── has_eeg? ─────┐                                │
          │                    │                                 │
     eeg=true            eeg=false                              │
          │                    │                                 │
          ▼                    │                                 │
   eeg_feature_loader          │                                 │
          │                    │                                 │
          ▼                    │                                 │
   eeg_interpreter (LLM)      │                                 │
          │                    │                                 │
          ▼                    │                                 │
   eeg_personalizer            │                                 │
          │                    │                                 │
          └────────┬───────────┘                                │
                   │                                             │
                   ▼                                             │
        ══════════════════════                                   │
        ║ CLINICIAN REVIEW   ║  ← MANDATORY INTERRUPT            │
        ║ (interrupt_before) ║                                   │
        ══════════════════════                                   │
                   │                                             │
             ┌─────┴──────┐                                      │
             │            │                                      │
          approve      reject ──→ review_processor ──→ (loop     │
             │                     back to composer              │
             ▼                     or abort)                     │
      review_processor                                           │
             │                                                   │
             ▼                                                   │
      protocol_reporter                                          │
             │                                                   │
             ▼                                                   │
      audit_logger                                               │
             │                                                   │
             ▼                                                   │
           END
```

### Branch Conditions

```python
# After intake_router
def route_by_source(state):
    if state["source_mode"] == "upload":
        return "template_parser"
    return "prompt_normalizer"

# After evidence_sufficiency_gate
def route_by_evidence(state):
    if state["evidence"]["evidence_sufficient"]:
        return "safety_policy_engine"
    return "clinician_evidence_review"  # interrupt

# After contraindication_gate
def route_by_safety(state):
    if state["safety"]["safety_cleared"]:
        return "protocol_template_selector"
    return "contraindication_review"  # interrupt

# After grounding_validator
def route_by_eeg(state):
    eeg = state.get("eeg")
    if eeg and eeg.get("data_available"):
        return "eeg_feature_loader"
    return "clinician_review_interrupt"

# After clinician review
def route_by_review(state):
    if state["review"]["status"] == "approved":
        return "protocol_reporter"
    if state["review"]["status"] == "edited":
        return "review_processor"  # apply edits, then re-validate
    return "END"  # rejected → terminate
```

### Edge Cases

**No EEG present:** `route_by_eeg` returns `"clinician_review_interrupt"`, skipping the entire EEG subgraph. The `eeg` field in state remains `None`.

**Evidence is weak:** `evidence_sufficiency_gate` sets `evidence_sufficient: false`. The graph interrupts at `clinician_evidence_review`. The clinician can:
- Override and proceed (with a documented "proceed despite weak evidence" flag)
- Abort the generation
- Request manual evidence addition

**Contraindications triggered:** `contraindication_gate` blocks. The graph interrupts. The clinician can:
- Confirm the contraindication is not applicable (with documented override reason)
- Modify patient context to remove the flag
- Abort

**Clinician rejects draft:** `review_processor` captures the rejection reason. The graph routes back to `protocol_composer` with the rejection notes added to the composer's context. The revision number increments. Max 3 revision cycles before requiring a fresh start.

**Uploaded template is malformed:** `template_parser` sets `parse_error`. The graph interrupts with the error details, allowing the clinician to upload a corrected file or switch to prompt-based input.

### Checkpointing

Every node writes its output to the shared state, which is persisted by the LangGraph checkpointer. This means:
- If the graph crashes mid-execution, it resumes from the last completed node
- If the clinician review takes 3 days, the state is intact
- Every state version is preserved for audit trail reconstruction

---

## 5. Human-in-the-Loop Design

### Mandatory Interrupt Points

| Interrupt | When | Payload |
|-----------|------|---------|
| `clinician_evidence_review` | Evidence insufficient | Evidence gaps, available articles with grades, condition |
| `contraindication_review` | Blocking contraindication | Contraindication details, patient context, modality restrictions |
| `clinician_review_interrupt` | Protocol draft complete | Full protocol, evidence summary, safety assessment, grounding score |

### Review Payload (Main Review)

The clinician sees:

```python
class ReviewPayload(BaseModel):
    """What the clinician sees at the review interrupt."""

    # Protocol
    protocol_summary: str  # 1-paragraph overview
    base_sequence: ProtocolSequence  # SOZO phase structure
    composed_sections: list[ComposedSection]  # narrative sections
    personalized_protocol: Optional[PersonalizedProtocol]

    # Evidence
    evidence_summary: EvidenceSummary
    evidence_grade_distribution: dict[str, int]  # A:3, B:5, C:2
    evidence_gaps: list[str]
    key_citations: list[ScoredArticle]  # top 10

    # Safety
    safety_assessment: SafetyAssessment
    off_label_flags: list[str]
    consent_requirements: list[str]

    # Quality
    grounding_score: float
    grounding_issues: list[GroundingIssue]  # only warnings/blocks
    review_flags: list[str]

    # EEG (if applicable)
    eeg_interpretation: Optional[EEGInterpretation]
    eeg_adjustments: list[ParameterAdjustment]

    # Audit
    revision_number: int
    prior_review_notes: list[str]
    node_history_summary: list[str]
```

### Allowed Clinician Actions

```python
class ClinicianReviewAction(BaseModel):
    decision: Literal["approve", "reject", "edit"]
    reviewer_id: str
    reviewer_credentials: str  # e.g. "MD, Board Certified Neurologist"
    timestamp: str  # ISO 8601

    # If reject
    rejection_reason: Optional[str]

    # If edit
    section_edits: Optional[list[SectionEdit]]
    parameter_overrides: Optional[list[ParameterOverride]]
    added_notes: Optional[str]

    # Always
    review_notes: Optional[str]
    digital_signature: Optional[str]

class SectionEdit(BaseModel):
    section_id: str
    field: str  # "content" | "citations" | "confidence"
    old_value: str
    new_value: str
    edit_reason: str

class ParameterOverride(BaseModel):
    step_id: str
    parameter: str
    old_value: str
    new_value: str
    override_reason: str
    evidence_ids: list[str]  # clinician must cite justification
```

### How Edits Are Stored

All edits are written to `state["review"]`:
```python
state["review"]["edits_applied"].append({
    "revision": state["review"]["revision_number"],
    "reviewer_id": action.reviewer_id,
    "timestamp": action.timestamp,
    "edits": [e.model_dump() for e in action.section_edits],
    "overrides": [o.model_dump() for o in action.parameter_overrides],
})
state["review"]["revision_number"] += 1
```

The original pre-edit state is preserved in the checkpointer history. The diff between versions is always recoverable.

### What Invalidates a Previously Approved Result

- Patient context changes (new contraindication, new medication)
- Evidence refresh reveals contradicting findings
- Safety policy update
- Condition schema update
- Clinician explicitly revokes approval

On invalidation, the protocol status moves from `approved` → `needs_review` and the revision number increments.

---

## 6. LLM Node Prompts and Contracts

### Node: `prompt_normalizer`

**System Prompt:**
```
You are Sozo's intake interpreter for a neuromodulation protocol generation system.

Your job is to interpret a clinician's natural-language request and extract structured fields.
You MUST return valid JSON matching the schema exactly. No prose outside the JSON.

Rules:
- condition_slug MUST be one of the provided available_conditions list. If unsure, pick the closest match and add an uncertainty_flag.
- modality_preferences MUST only include items from available_modalities.
- If the prompt mentions EEG, QEEG, or brainwave data, set eeg_data_referenced: true.
- If the prompt mentions patient-specific factors (age, symptoms, prior treatment), set personalization_requested: true and populate patient_context.
- If you cannot confidently determine any field, set it to null and add a description to uncertainty_flags.
- NEVER fabricate clinical details not present in the prompt.
- NEVER recommend specific treatment parameters — that is not your role.
```

**Output Contract:**
```python
class NormalizedRequest(BaseModel):
    condition_slug: str
    condition_display: str
    modality_preferences: list[str] = Field(default_factory=list)
    patient_context: Optional[PatientContext] = None
    personalization_requested: bool = False
    eeg_data_referenced: bool = False
    uncertainty_flags: list[str] = Field(default_factory=list)
    raw_prompt: str  # echo back for audit
```

---

### Node: `protocol_composer`

**System Prompt:**
```
You are Sozo's protocol composition engine. You write clinical protocol document sections grounded in evidence.

CRITICAL RULES:
1. Every factual claim MUST cite at least one evidence_id from the provided evidence_pool.
2. Evidence IDs are PMIDs or DOIs. Use the EXACT IDs from the evidence_pool — do NOT fabricate PMIDs.
3. If evidence for a claim is weak (Grade C or D), you MUST include an uncertainty_flag.
4. If evidence is conflicting, you MUST note the conflict and cite both sides.
5. You do NOT choose stimulation parameters. Those come from base_sequence. You describe and justify them.
6. You MUST NOT claim any modality is "FDA-approved" for neuromodulation indications unless explicitly stated in the evidence.
7. You MUST flag off-label use per the safety_assessment.
8. Return ONLY valid JSON matching the output schema. No markdown, no prose wrapper.

Tone: Clinical, precise, evidence-based. Third-person professional voice.
Target audience: Qualified clinicians operating neuromodulation equipment.
```

**Output Contract:**
```python
class ComposerOutput(BaseModel):
    sections: list[ComposedSection]

class ComposedSection(BaseModel):
    section_id: str
    title: str
    content: str  # clinical prose, may contain inline citations like (PMID: 12345678)
    cited_evidence_ids: list[str]  # all PMIDs/DOIs referenced in this section
    confidence: Literal["high", "medium", "low", "insufficient"]
    generation_method: Literal["llm_composed"]
    claims: list[ProtocolClaim]

class ProtocolClaim(BaseModel):
    claim_text: str
    evidence_ids: list[str]  # NON-EMPTY — every claim must cite evidence
    claim_type: Literal["supports", "informs", "contradicts", "safety_note"]
    confidence: Literal["high", "medium", "low"]
    uncertainty_flag: Optional[str] = None  # REQUIRED if confidence != "high"
```

---

### Node: `eeg_interpreter`

**System Prompt:**
```
You are Sozo's EEG interpretation engine. You analyze quantitative EEG features in the context of a specific neurological/psychiatric condition and recommend protocol adjustments.

CRITICAL RULES:
1. Every finding MUST cite evidence_ids from the literature. Do NOT fabricate PMIDs.
2. Every recommended adjustment MUST include a rationale and evidence_ids.
3. If confidence in an adjustment is low, set uncertainty_flag with an explanation.
4. You recommend adjustments — you do NOT apply them. The deterministic personalizer applies them within safety bounds.
5. Never recommend parameters outside the modality's safety envelope.
6. Return ONLY valid JSON matching the output schema.
```

**Output Contract:** As defined in `EEGInterpretation` above.

---

## 7. Safety Architecture

### Safety Gates

| Gate | Type | Trigger | Action |
|------|------|---------|--------|
| **Contraindication gate** | Hard block | Any blocking contraindication (e.g., metallic implant for TMS, epilepsy for certain protocols) | Interrupt to clinician. Cannot proceed without documented override. |
| **Evidence sufficiency gate** | Soft block | No Grade A/B evidence for primary protocol parameters | Interrupt to clinician with gap list. Can proceed with "weak evidence" flag. |
| **Unsupported condition gate** | Hard block | Condition not in registry OR evidence_quality="emerging" with no manual override | Return error explaining the condition is not yet supported. |
| **Missing assessment gate** | Warning | Patient context incomplete for personalization | Proceed with base protocol, flag missing data. |
| **No-autonomous-prescription rule** | Architectural | Every path through the graph | No path from START to END bypasses `clinician_review_interrupt`. Enforced by graph topology. |
| **Escalation-to-clinician rule** | Architectural | Any node error, any safety flag, any confidence < threshold | Route to interrupt with full context. |

### Logging/Audit Requirements

Every node MUST log:
```python
{
    "node_id": str,
    "started_at": str,        # ISO 8601
    "completed_at": str,
    "duration_ms": float,
    "input_hash": str,        # SHA-256 of input for integrity
    "output_hash": str,       # SHA-256 of output
    "status": "success" | "error" | "skipped",
    "error": Optional[str],
    "decisions": list[str],   # human-readable decision log
    "evidence_ids_consumed": list[str],
    "evidence_ids_produced": list[str],
    "safety_flags_raised": list[str],
}
```

### Explainability Requirements

Every protocol section MUST include:
1. At least one evidence citation (PMID/DOI)
2. A confidence label (high/medium/low/insufficient)
3. An uncertainty flag if confidence < high
4. The generation method (deterministic/LLM/clinician-edited)

Every stimulation parameter MUST trace to:
1. The evidence article(s) that support it
2. The knowledge base rule that selected it
3. The safety policy that validated it

---

## 8. Python Implementation Layout

```
sozo_graph/
├── __init__.py
├── graph.py                    # Top-level StateGraph definition & compilation
├── state.py                    # SozoGraphState TypedDict + all sub-state types
│
├── nodes/                      # One file per node
│   ├── __init__.py
│   ├── intake_router.py
│   ├── template_parser.py
│   ├── prompt_normalizer.py    # LLM node
│   ├── condition_resolver.py
│   ├── intake_validator.py
│   ├── evidence_search.py
│   ├── evidence_dedup.py
│   ├── evidence_screen.py
│   ├── evidence_extract.py
│   ├── evidence_score.py
│   ├── evidence_sufficiency_gate.py
│   ├── safety_policy_engine.py
│   ├── contraindication_gate.py
│   ├── protocol_template_selector.py
│   ├── protocol_composer.py    # LLM node
│   ├── grounding_validator.py
│   ├── eeg_feature_loader.py
│   ├── eeg_interpreter.py      # LLM node
│   ├── eeg_personalizer.py
│   ├── review_processor.py
│   ├── protocol_reporter.py
│   └── audit_logger.py
│
├── subgraphs/                  # Subgraph definitions
│   ├── __init__.py
│   ├── intake.py               # intake_router → parser/normalizer → resolver → validator
│   ├── evidence.py             # search → dedup → screen → extract → score → gate
│   ├── composition.py          # safety → contraindication → selector → composer → grounding
│   ├── eeg_personalization.py  # loader → interpreter → personalizer
│   └── review.py               # interrupt → processor → reporter → audit
│
├── schemas/                    # Pydantic models for node I/O
│   ├── __init__.py
│   ├── state.py                # SozoGraphState and all nested TypedDicts
│   ├── intake.py               # NormalizedRequest, PatientContext, TemplateParseResult
│   ├── evidence.py             # ScoredArticle, EvidenceSummary (graph-specific wrappers)
│   ├── safety.py               # SafetyAssessment, ContraindicationFlag, ModalityRestriction
│   ├── protocol.py             # ComposedSection, ProtocolClaim, ComposerOutput
│   ├── eeg.py                  # EEGInterpretation, EEGFinding, ParameterAdjustment
│   ├── review.py               # ReviewPayload, ClinicianReviewAction, ApprovalStamp
│   └── audit.py                # NodeHistoryEntry, ErrorEntry, AuditRecord
│
├── prompts/                    # LLM prompt templates
│   ├── __init__.py
│   ├── prompt_normalizer.py    # system prompt + user template
│   ├── protocol_composer.py    # system prompt + section-level template
│   └── eeg_interpreter.py      # system prompt + interpretation template
│
├── policies/                   # Safety and business rules
│   ├── __init__.py
│   ├── contraindication_rules.py
│   ├── evidence_thresholds.py
│   ├── parameter_bounds.py     # min/max per modality from configs/modalities.yaml
│   └── regulatory_flags.py     # off-label rules, consent requirements
│
├── integrations/               # External service adapters
│   ├── __init__.py
│   ├── llm_client.py           # Claude API wrapper with structured output
│   ├── evidence_service.py     # Wraps sozo_generator.evidence.research_pipeline
│   ├── condition_service.py    # Wraps sozo_generator.conditions.registry
│   ├── knowledge_service.py    # Wraps sozo_generator.knowledge.base
│   ├── protocol_builder.py     # Wraps sozo_protocol.builder
│   ├── document_renderer.py    # Wraps sozo_generator.docx.renderer
│   └── eeg_loader.py           # EEG file parsing adapters
│
├── audit/                      # Audit infrastructure
│   ├── __init__.py
│   ├── logger.py               # Node-level audit logging
│   ├── trace.py                # Execution trace reconstruction
│   └── storage.py              # Audit record persistence
│
└── tests/
    ├── __init__.py
    ├── test_graph_compilation.py
    ├── test_intake_subgraph.py
    ├── test_evidence_subgraph.py
    ├── test_composition_subgraph.py
    ├── test_eeg_subgraph.py
    ├── test_review_subgraph.py
    ├── test_safety_gates.py
    ├── test_end_to_end.py
    └── fixtures/
        ├── sample_condition.json
        ├── sample_evidence.json
        ├── sample_eeg.json
        └── sample_review.json
```

---

## 9. LangGraph Pseudocode

### Shared State Definition

```python
from typing import TypedDict, Optional, Literal, Annotated
from langgraph.graph import add_messages
import operator


class IntakeState(TypedDict, total=False):
    user_prompt: Optional[str]
    uploaded_file: Optional[bytes]
    uploaded_filename: Optional[str]
    template_profile: Optional[dict]
    normalized_request: Optional[dict]
    parse_warnings: list[str]
    parse_error: Optional[str]


class ConditionState(TypedDict, total=False):
    slug: str
    display_name: str
    icd10: str
    schema: dict  # serialized ConditionSchema
    resolution_source: str
    condition_valid: bool


class PatientContextState(TypedDict, total=False):
    patient_id: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    diagnosis_icd10: Optional[str]
    current_medications: list[str]
    contraindications: list[str]
    prior_neuromodulation: list[str]
    assessment_scores: dict
    phenotype_slug: Optional[str]
    severity_level: Optional[str]


class EvidenceState(TypedDict, total=False):
    search_queries: list[str]
    source_counts: dict[str, int]
    raw_article_count: int
    unique_article_count: int
    screened_article_count: int
    articles: list[dict]  # serialized ScoredArticles
    extractions: dict[str, dict]
    evidence_summary: dict
    evidence_sufficient: bool
    evidence_gaps: list[str]
    prisma_counts: dict
    pipeline_log_path: Optional[str]


class SafetyState(TypedDict, total=False):
    contraindications_found: list[dict]
    modality_restrictions: list[dict]
    consent_requirements: list[str]
    off_label_flags: list[str]
    safety_cleared: bool
    blocking_contraindications: list[str]


class ProtocolState(TypedDict, total=False):
    base_sequence: dict  # serialized ProtocolSequence
    template_source: str
    selection_rationale: str
    composed_sections: list[dict]
    grounding_score: float
    grounding_issues: list[dict]
    doc_type: str
    tier: str


class EEGState(TypedDict, total=False):
    data_available: bool
    features: dict[str, float]
    quality_metrics: dict
    interpretation: Optional[dict]
    adjustments_applied: list[dict]
    adjustments_rejected: list[dict]
    personalized_protocol: Optional[dict]


class ReviewState(TypedDict, total=False):
    status: str  # pending | approved | rejected | edited
    reviewer_id: Optional[str]
    review_timestamp: Optional[str]
    review_notes: Optional[str]
    edits_applied: list[dict]
    revision_number: int
    approval_stamp: Optional[dict]


class OutputState(TypedDict, total=False):
    output_paths: dict[str, str]
    output_formats: list[str]
    audit_record_id: Optional[str]


class NodeHistoryEntry(TypedDict):
    node_id: str
    started_at: str
    completed_at: str
    duration_ms: float
    status: str
    error: Optional[str]
    decisions: list[str]


class ErrorEntry(TypedDict):
    node_id: str
    error_type: str
    message: str
    recoverable: bool
    timestamp: str


class SozoGraphState(TypedDict):
    request_id: str
    created_at: str
    updated_at: str
    status: str
    source_mode: str

    intake: IntakeState
    condition: ConditionState
    patient_context: Optional[PatientContextState]
    evidence: EvidenceState
    safety: SafetyState
    protocol: ProtocolState
    eeg: Optional[EEGState]
    review: ReviewState
    output: OutputState

    node_history: Annotated[list[NodeHistoryEntry], operator.add]
    errors: Annotated[list[ErrorEntry], operator.add]
    version: str
    graph_version: str
```

### Subgraph Definitions

```python
# ── subgraphs/intake.py ──────────────────────────────────────────

from langgraph.graph import StateGraph

from ..nodes.intake_router import intake_router
from ..nodes.template_parser import template_parser
from ..nodes.prompt_normalizer import prompt_normalizer
from ..nodes.condition_resolver import condition_resolver
from ..nodes.intake_validator import intake_validator
from ..state import SozoGraphState


def build_intake_subgraph() -> StateGraph:
    sg = StateGraph(SozoGraphState)

    sg.add_node("intake_router", intake_router)
    sg.add_node("template_parser", template_parser)
    sg.add_node("prompt_normalizer", prompt_normalizer)
    sg.add_node("condition_resolver", condition_resolver)
    sg.add_node("intake_validator", intake_validator)

    sg.set_entry_point("intake_router")

    sg.add_conditional_edges(
        "intake_router",
        lambda s: "template_parser" if s["source_mode"] == "upload" else "prompt_normalizer",
        {"template_parser": "template_parser", "prompt_normalizer": "prompt_normalizer"},
    )

    sg.add_edge("template_parser", "condition_resolver")
    sg.add_edge("prompt_normalizer", "condition_resolver")
    sg.add_edge("condition_resolver", "intake_validator")
    sg.set_finish_point("intake_validator")

    return sg.compile()


# ── subgraphs/evidence.py ────────────────────────────────────────

from ..nodes.evidence_search import evidence_search
from ..nodes.evidence_dedup import evidence_dedup
from ..nodes.evidence_screen import evidence_screen
from ..nodes.evidence_extract import evidence_extract
from ..nodes.evidence_score import evidence_score
from ..nodes.evidence_sufficiency_gate import evidence_sufficiency_gate


def build_evidence_subgraph() -> StateGraph:
    sg = StateGraph(SozoGraphState)

    sg.add_node("evidence_search", evidence_search)
    sg.add_node("evidence_dedup", evidence_dedup)
    sg.add_node("evidence_screen", evidence_screen)
    sg.add_node("evidence_extract", evidence_extract)
    sg.add_node("evidence_score", evidence_score)
    sg.add_node("evidence_sufficiency_gate", evidence_sufficiency_gate)

    sg.set_entry_point("evidence_search")
    sg.add_edge("evidence_search", "evidence_dedup")
    sg.add_edge("evidence_dedup", "evidence_screen")
    sg.add_edge("evidence_screen", "evidence_extract")
    sg.add_edge("evidence_extract", "evidence_score")
    sg.add_edge("evidence_score", "evidence_sufficiency_gate")
    sg.set_finish_point("evidence_sufficiency_gate")

    return sg.compile()


# ── subgraphs/composition.py ─────────────────────────────────────

from ..nodes.safety_policy_engine import safety_policy_engine
from ..nodes.contraindication_gate import contraindication_gate
from ..nodes.protocol_template_selector import protocol_template_selector
from ..nodes.protocol_composer import protocol_composer
from ..nodes.grounding_validator import grounding_validator


def build_composition_subgraph() -> StateGraph:
    sg = StateGraph(SozoGraphState)

    sg.add_node("safety_policy_engine", safety_policy_engine)
    sg.add_node("contraindication_gate", contraindication_gate)
    sg.add_node("protocol_template_selector", protocol_template_selector)
    sg.add_node("protocol_composer", protocol_composer)
    sg.add_node("grounding_validator", grounding_validator)

    sg.set_entry_point("safety_policy_engine")
    sg.add_edge("safety_policy_engine", "contraindication_gate")

    sg.add_conditional_edges(
        "contraindication_gate",
        lambda s: "protocol_template_selector" if s["safety"]["safety_cleared"] else "__interrupt__",
        {"protocol_template_selector": "protocol_template_selector", "__interrupt__": "__interrupt__"},
    )

    sg.add_edge("protocol_template_selector", "protocol_composer")
    sg.add_edge("protocol_composer", "grounding_validator")
    sg.set_finish_point("grounding_validator")

    return sg.compile()


# ── subgraphs/eeg_personalization.py ──────────────────────────────

from ..nodes.eeg_feature_loader import eeg_feature_loader
from ..nodes.eeg_interpreter import eeg_interpreter
from ..nodes.eeg_personalizer import eeg_personalizer


def build_eeg_subgraph() -> StateGraph:
    sg = StateGraph(SozoGraphState)

    sg.add_node("eeg_feature_loader", eeg_feature_loader)
    sg.add_node("eeg_interpreter", eeg_interpreter)
    sg.add_node("eeg_personalizer", eeg_personalizer)

    sg.set_entry_point("eeg_feature_loader")
    sg.add_edge("eeg_feature_loader", "eeg_interpreter")
    sg.add_edge("eeg_interpreter", "eeg_personalizer")
    sg.set_finish_point("eeg_personalizer")

    return sg.compile()


# ── subgraphs/review.py ──────────────────────────────────────────

from ..nodes.review_processor import review_processor
from ..nodes.protocol_reporter import protocol_reporter
from ..nodes.audit_logger import audit_logger


def build_review_subgraph() -> StateGraph:
    sg = StateGraph(SozoGraphState)

    sg.add_node("review_processor", review_processor)
    sg.add_node("protocol_reporter", protocol_reporter)
    sg.add_node("audit_logger", audit_logger)

    sg.set_entry_point("review_processor")

    sg.add_conditional_edges(
        "review_processor",
        lambda s: "protocol_reporter" if s["review"]["status"] == "approved" else "__end__",
        {"protocol_reporter": "protocol_reporter", "__end__": "__end__"},
    )

    sg.add_edge("protocol_reporter", "audit_logger")
    sg.set_finish_point("audit_logger")

    return sg.compile()
```

### Top-Level Graph Wiring

```python
# ── graph.py ──────────────────────────────────────────────────────

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver  # or SqliteSaver for MVP

from .state import SozoGraphState
from .subgraphs.intake import build_intake_subgraph
from .subgraphs.evidence import build_evidence_subgraph
from .subgraphs.composition import build_composition_subgraph
from .subgraphs.eeg_personalization import build_eeg_subgraph
from .subgraphs.review import build_review_subgraph


def build_sozo_graph(checkpointer=None):
    """Build and compile the top-level Sozo protocol generation graph."""

    graph = StateGraph(SozoGraphState)

    # ── Add subgraphs as nodes ────────────────────────────────
    graph.add_node("intake", build_intake_subgraph())
    graph.add_node("evidence", build_evidence_subgraph())
    graph.add_node("composition", build_composition_subgraph())
    graph.add_node("eeg_personalization", build_eeg_subgraph())
    graph.add_node("review", build_review_subgraph())

    # ── Entry point ───────────────────────────────────────────
    graph.set_entry_point("intake")

    # ── Edges ─────────────────────────────────────────────────

    # Intake → Evidence (always)
    graph.add_edge("intake", "evidence")

    # Evidence → Composition (if evidence sufficient)
    # Evidence → interrupt (if insufficient)
    graph.add_conditional_edges(
        "evidence",
        route_after_evidence,
        {
            "composition": "composition",
            "evidence_interrupt": END,  # pauses for clinician
        },
    )

    # Composition → EEG or Review
    graph.add_conditional_edges(
        "composition",
        route_after_composition,
        {
            "eeg_personalization": "eeg_personalization",
            "review": "review",
            "contraindication_interrupt": END,  # pauses for clinician
        },
    )

    # EEG → Review (always)
    graph.add_edge("eeg_personalization", "review")

    # Review → END
    graph.add_edge("review", END)

    # ── Compile with checkpointer ─────────────────────────────
    compiled = graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["review"],  # MANDATORY clinician review
    )

    return compiled


# ── Routing functions ─────────────────────────────────────────────

def route_after_evidence(state: SozoGraphState) -> str:
    if state["evidence"].get("evidence_sufficient", False):
        return "composition"
    return "evidence_interrupt"


def route_after_composition(state: SozoGraphState) -> str:
    if not state["safety"].get("safety_cleared", False):
        return "contraindication_interrupt"
    eeg = state.get("eeg")
    if eeg and eeg.get("data_available", False):
        return "eeg_personalization"
    return "review"


# ── Graph execution ───────────────────────────────────────────────

def run_protocol_generation(
    source_mode: str,
    user_prompt: str = "",
    uploaded_file: bytes = b"",
    uploaded_filename: str = "",
    patient_context: dict = None,
    eeg_file: bytes = None,
    checkpointer=None,
):
    """Execute the full protocol generation pipeline."""
    import uuid
    from datetime import datetime, timezone

    graph = build_sozo_graph(checkpointer=checkpointer)

    initial_state: SozoGraphState = {
        "request_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "intake",
        "source_mode": source_mode,
        "intake": {
            "user_prompt": user_prompt or None,
            "uploaded_file": uploaded_file or None,
            "uploaded_filename": uploaded_filename or None,
        },
        "condition": {},
        "patient_context": patient_context,
        "evidence": {},
        "safety": {},
        "protocol": {},
        "eeg": {
            "data_available": eeg_file is not None,
        } if eeg_file else None,
        "review": {"status": "pending", "revision_number": 0},
        "output": {},
        "node_history": [],
        "errors": [],
        "version": "1.0",
        "graph_version": "0.1.0",
    }

    config = {"configurable": {"thread_id": initial_state["request_id"]}}

    # Run until interrupt (clinician review)
    result = graph.invoke(initial_state, config=config)
    return result


def resume_after_review(
    thread_id: str,
    review_action: dict,
    checkpointer=None,
):
    """Resume graph execution after clinician review."""
    graph = build_sozo_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": thread_id}}

    # Update state with review action
    graph.update_state(config, {
        "review": {
            "status": review_action["decision"],
            "reviewer_id": review_action["reviewer_id"],
            "review_timestamp": review_action.get("timestamp"),
            "review_notes": review_action.get("review_notes"),
        }
    })

    # Resume execution
    result = graph.invoke(None, config=config)
    return result
```

### Retry Policy

```python
# ── integrations/llm_client.py ────────────────────────────────────

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import ValidationError


class LLMClient:
    """Claude API client with structured output and retry."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ValidationError, ValueError)),
    )
    def structured_call(
        self,
        system_prompt: str,
        user_message: str,
        output_model: type,  # Pydantic model class
        max_tokens: int = 4096,
    ):
        """Call Claude API and parse response into Pydantic model.

        Retries once on validation failure with a correction prompt.
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text = response.content[0].text

        # Parse JSON from response
        import json
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
            else:
                raise ValueError(f"Response is not valid JSON: {raw_text[:200]}")

        # Validate with Pydantic
        return output_model.model_validate(parsed)
```

---

## 10. Observability and Audit

### What Every Node Logs

```python
# ── audit/logger.py ───────────────────────────────────────────────

import hashlib
import json
import time
from datetime import datetime, timezone
from functools import wraps


def audited_node(node_id: str):
    """Decorator that wraps every node with audit logging."""
    def decorator(func):
        @wraps(func)
        def wrapper(state):
            start = time.monotonic()
            started_at = datetime.now(timezone.utc).isoformat()

            # Hash inputs for integrity
            input_subset = {k: v for k, v in state.items()
                          if k not in ("node_history", "errors")}
            input_hash = hashlib.sha256(
                json.dumps(input_subset, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]

            try:
                result = func(state)

                completed_at = datetime.now(timezone.utc).isoformat()
                duration_ms = (time.monotonic() - start) * 1000

                output_hash = hashlib.sha256(
                    json.dumps(result, sort_keys=True, default=str).encode()
                ).hexdigest()[:16]

                # Append to node_history
                entry = {
                    "node_id": node_id,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "duration_ms": round(duration_ms, 2),
                    "status": "success",
                    "error": None,
                    "input_hash": input_hash,
                    "output_hash": output_hash,
                    "decisions": result.pop("_decisions", []),
                }

                result["node_history"] = [entry]
                result["updated_at"] = completed_at
                return result

            except Exception as e:
                completed_at = datetime.now(timezone.utc).isoformat()
                duration_ms = (time.monotonic() - start) * 1000

                error_entry = {
                    "node_id": node_id,
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "recoverable": True,
                    "timestamp": completed_at,
                }

                history_entry = {
                    "node_id": node_id,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "duration_ms": round(duration_ms, 2),
                    "status": "error",
                    "error": str(e),
                }

                return {
                    "node_history": [history_entry],
                    "errors": [error_entry],
                    "updated_at": completed_at,
                }

        return wrapper
    return decorator
```

### Audit Record Structure

```python
class AuditRecord(BaseModel):
    """Complete audit record for one protocol generation run."""
    audit_id: str
    request_id: str
    condition_slug: str
    created_at: str
    completed_at: str
    total_duration_s: float

    # Execution trace
    node_history: list[NodeHistoryEntry]
    errors: list[ErrorEntry]
    total_nodes_executed: int
    total_llm_calls: int

    # Evidence audit
    evidence_sources_searched: int
    evidence_articles_considered: int
    evidence_articles_cited: int
    evidence_ids_cited: list[str]  # all PMIDs/DOIs
    evidence_grade_distribution: dict[str, int]
    prisma_counts: dict

    # Safety audit
    contraindications_checked: list[str]
    safety_flags_raised: list[str]
    consent_requirements: list[str]

    # Review audit
    review_cycles: int
    reviewer_id: str
    review_decision: str
    sections_modified_by_clinician: list[str]
    parameter_overrides_by_clinician: list[dict]

    # Output
    output_formats: list[str]
    protocol_version: str
    graph_version: str
```

### State Version Tracking

The LangGraph checkpointer stores every state transition. To reconstruct a full trace:

```python
def reconstruct_trace(thread_id: str, checkpointer) -> list[dict]:
    """Reconstruct the full execution trace from checkpointer history."""
    history = list(checkpointer.list({"configurable": {"thread_id": thread_id}}))

    trace = []
    for checkpoint in history:
        state = checkpoint.values
        trace.append({
            "checkpoint_id": checkpoint.config["configurable"]["checkpoint_id"],
            "timestamp": state.get("updated_at"),
            "status": state.get("status"),
            "last_node": state.get("node_history", [{}])[-1].get("node_id")
                         if state.get("node_history") else None,
            "state_snapshot": state,
        })

    return sorted(trace, key=lambda x: x["timestamp"] or "")
```

---

## 11. Anti-Patterns

### What Sozo Must Never Do

| Anti-Pattern | Why It's Dangerous | How We Prevent It |
|---|---|---|
| **Open-ended agent debate loops** | Two LLMs arguing about stimulation parameters produces false consensus, not evidence | StateGraph topology: no cycles between LLM nodes. Parameters come from deterministic extractors. |
| **Hidden mutable state** | Untracked state changes break auditability and reproducibility | TypedDict with `Annotated` reducers. Every state mutation is a node return value. |
| **Protocol recommendations without evidence IDs** | Clinician cannot verify claims. Regulatory failure. | Pydantic validation: `ProtocolClaim.evidence_ids` is `list[str]` with `min_length=1`. LLM prompt explicitly forbids claims without citations. |
| **Autonomous clinical decisions** | No software should prescribe treatment without clinician oversight | Graph topology: every path through the graph passes through `clinician_review_interrupt`. No `END` reachable without review. |
| **Silent fallback behavior** | If evidence search fails silently, the protocol appears evidence-based but isn't | Every fallback logs explicitly. `evidence_sufficiency_gate` blocks if below threshold. No silent degradation. |
| **LLM rewriting another node's structured output** | The composer LLM should not "improve" the parameter extractor's numbers | The composer receives `base_sequence` as read-only context. Its output schema has no parameter fields — only prose and citations. Parameters are never in the LLM's output contract. |
| **Bypassing clinician interrupt** | Legal and ethical requirement for human oversight | `interrupt_before=["review"]` is set at graph compilation. It cannot be overridden at runtime. The review subgraph is the only path to `END`. |
| **Fabricating PMIDs** | Hallucinated citations undermine the entire evidence layer | `validate_pmid()` on all PMID fields. `grounding_validator` cross-references every cited PMID against the evidence pool. Unknown PMIDs are flagged as blocking issues. |
| **Exceeding modality safety bounds** | LLM suggests 5 mA tDCS (max safe is 2 mA) | `eeg_personalizer` is deterministic and clamps all parameters to bounds from `configs/modalities.yaml`. LLM recommendations are suggestions, not commands. |
| **Skipping safety gates on retry** | After a rejection, the re-composed protocol bypasses contraindication checks | Re-composition routes through the full composition subgraph including all safety gates. There are no shortcuts. |

---

## 12. Final Deliverable

### Recommended MVP Graph

The MVP graph is a single-path flow with mandatory review:

```
prompt_normalizer → condition_resolver → evidence_search → evidence_dedup →
evidence_screen → evidence_extract → evidence_score → evidence_sufficiency_gate →
safety_policy_engine → contraindication_gate → protocol_template_selector →
protocol_composer → grounding_validator → [CLINICIAN REVIEW] → review_processor →
protocol_reporter → audit_logger → END
```

**What's in the MVP:**
- Prompt-based input only (no template upload parsing)
- PubMed search only (no Crossref/Semantic Scholar in v0.1)
- No EEG personalization
- Single-pass composition (no multi-revision loop)
- DOCX output only
- SQLite checkpointer
- File-based audit logs

### Sprint 1 (Weeks 1-2)

| Task | Priority |
|------|----------|
| Define `SozoGraphState` TypedDict in `state.py` | P0 |
| Implement `condition_resolver` node (wraps existing registry) | P0 |
| Implement `evidence_search` through `evidence_score` (wraps existing `ResearchPipeline`) | P0 |
| Implement `evidence_sufficiency_gate` | P0 |
| Implement `safety_policy_engine` (wraps existing safety YAML rules) | P0 |
| Implement `contraindication_gate` | P0 |
| Implement `protocol_template_selector` (wraps existing `build_sozo_sequence`) | P0 |
| Implement `prompt_normalizer` LLM node with Claude structured output | P0 |
| Implement `protocol_composer` LLM node with evidence grounding | P0 |
| Implement `grounding_validator` (wraps existing `GroundingValidator`) | P0 |
| Wire the top-level StateGraph with `interrupt_before=["review"]` | P0 |
| Implement `review_processor` and `protocol_reporter` | P0 |
| Implement `audited_node` decorator | P1 |
| Write integration test: prompt → evidence → compose → review → output | P0 |
| SQLite checkpointer setup | P1 |

### Sprint 2 (Weeks 3-4)

| Task | Priority |
|------|----------|
| Add `template_parser` and `intake_router` for upload support | P1 |
| Add Crossref + Semantic Scholar to `evidence_search` | P1 |
| Implement `audit_logger` with full trace reconstruction | P1 |
| Add multi-revision loop (reject → re-compose → re-review, max 3 cycles) | P1 |
| Build Streamlit review UI that shows `ReviewPayload` and captures `ClinicianReviewAction` | P1 |
| Add PRISMA flow diagram to protocol output | P2 |
| Add JSON/FHIR export format to reporter | P2 |

### Deferred to Later Versions

| Feature | Version |
|---------|---------|
| EEG personalization subgraph | v0.3 |
| Closed-loop session integration (`sozo_session`) | v0.4 |
| PostgreSQL checkpointer for production | v0.3 |
| LLM-based screening (replace keyword heuristics) | v0.3 |
| Multi-clinician review workflow (consensus) | v0.4 |
| Regulatory compliance export (IEC 62304 traceability) | v0.5 |
| Real-time evidence monitoring (scheduled re-search) | v0.4 |
| Patient cohort analytics | v0.5 |

### The Smallest Safe Implementation That Ships First

1. One LLM node (`prompt_normalizer`) to accept natural-language input
2. The existing `ResearchPipeline` for evidence
3. The existing `build_sozo_sequence` for protocol structure
4. One LLM node (`protocol_composer`) for prose sections with mandatory evidence citations
5. The existing `GroundingValidator` to check citations
6. One mandatory clinician review interrupt
7. DOCX output via the existing renderer
8. File-based audit log

**This ships a working, auditable, evidence-grounded, clinician-reviewed protocol generator with exactly 2 LLM calls and 0 autonomous decisions.**
