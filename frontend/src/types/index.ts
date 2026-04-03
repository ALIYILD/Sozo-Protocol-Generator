// ── Protocol Types ──────────────────────────────────────────────────

export type ProtocolStatus = 'draft' | 'pending_review' | 'approved' | 'rejected' | 'superseded' | 'archived';

export interface ConditionInfo {
  slug: string;
  display_name: string;
  icd10: string;
  category: string;
}

export interface ConditionAvailable {
  slug: string;
  display_name: string;
  icd10: string;
  evidence_level: string;
  modalities: string[];
}

export interface ModalityInfo {
  name: string;
  type: string;
  parameters: Record<string, unknown>;
  evidence_level: string;
  contraindications: string[];
}

export interface ProtocolVersion {
  version_id: string;
  version: number;
  status: ProtocolStatus;
  created_at: string;
  created_by: string;
  generation_method: string;
}

/** Shape returned by GET /api/protocols/ list endpoint */
export interface ProtocolListItem {
  protocol_id: string;
  version: number;
  status: ProtocolStatus;
  condition_slug: string;
  condition_name: string;
  modality: string;
  evidence_level: string;
  created_at: string;
  created_by: string;
  is_template: boolean;
}

/** Shape returned by GET /api/protocols/{id} detail endpoint */
export interface ProtocolDetail {
  protocol_id: string;
  version_id: string;
  version: number;
  status: ProtocolStatus;
  condition_slug: string;
  condition_name: string;
  modality: string;
  evidence_level: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  is_template: boolean;
  generation_method: string;
  data: Record<string, unknown>;
  evidence: {
    articles_count: number;
    prisma_screened: number;
    prisma_included: number;
    review_flags: string[];
    top_articles: Array<{
      pmid: string;
      title: string;
      year: number;
      evidence_type: string;
      relation: string;
    }>;
  };
}

/** Legacy Protocol type kept for backward compat where needed */
export interface Protocol {
  id: string;
  title: string;
  condition: ConditionInfo;
  status: ProtocolStatus;
  modalities: ModalityInfo[];
  versions: ProtocolVersion[];
  current_version: number;
  created_at: string;
  updated_at: string;
  created_by: string;
  reviewer?: string;
  review_notes?: string;
  tags: string[];
}

export interface ProtocolCreateRequest {
  condition_slug: string;
  modality?: string;
  tier?: string;
  doc_type?: string;
  prompt?: string;
  template_id?: string;
  patient_id?: string;
}

export interface ProtocolCreateResponse {
  protocol_id: string;
  task_id: string;
  status: string;
}

export interface GenerationStatus {
  task_id: string;
  status: string;
  progress: number;
  message: string;
  result: Record<string, unknown> | null;
}

export interface ProtocolUpdateRequest {
  title?: string;
  modalities?: ModalityInfo[];
  tags?: string[];
  change_summary: string;
}

// ── Evidence Types ──────────────────────────────────────────────────

export interface EvidenceArticle {
  id: string;
  pmid?: string;
  doi?: string;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  abstract?: string;
  url?: string;
}

export interface EvidenceClaim {
  id: string;
  article_id: string;
  claim_text: string;
  evidence_level: 'high' | 'moderate' | 'low' | 'very_low';
  confidence: number;
  condition_slug: string;
  modality?: string;
  extracted_at: string;
}

export interface StalenessCondition {
  slug: string;
  name: string;
  freshness: 'fresh' | 'aging' | 'stale' | 'expired';
  days_since_search: number;
  evidence_level: string;
  needs_refresh: boolean;
}

export interface StalenessReport {
  overall_health: string;
  total_conditions: number;
  fresh: number;
  aging: number;
  stale: number;
  expired: number;
  high_priority_refreshes: string[];
  conditions: StalenessCondition[];
}

// ── Safety Types ────────────────────────────────────────────────────

export interface SafetyCheckRequest {
  demographics: {
    age: number;
    sex: string;
  };
  medications: string[];
  medical_history: string[];
  modalities?: string[];
}

export interface SafetyCheckResponse {
  safety_cleared: boolean;
  absolute_contraindications: string[];
  relative_contraindications: string[];
  modality_clearance: Record<string, unknown>;
  warnings: string[];
  medication_summary: string;
}

// ── Personalization Types ───────────────────────────────────────────

export interface PersonalizationRequest {
  condition_slug: string;
  demographics: {
    age: number;
    sex: string;
  };
  symptoms: Array<{ name: string; score: number }>;
  medications: string[];
  treatment_history: Array<Record<string, unknown>>;
  medical_history: string[];
  modalities?: string[];
}

export interface PersonalizationResponse {
  safety_cleared: boolean;
  matched_phenotype: string | null;
  confidence_score: number;
  confidence_band: string;
  recommended_protocol: {
    modality: string;
    target: string;
    parameters: Record<string, unknown>;
    evidence_level: string;
    score: number;
    rationale: string;
  } | null;
  ranked_protocols_count: number;
  blocked_modalities: string[];
  warnings: string[];
  explanation: string;
}

// ── User / Auth Types ───────────────────────────────────────────────

export type UserRole = 'admin' | 'clinician' | 'researcher' | 'viewer';

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  created_at: string;
  is_active: boolean;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role?: UserRole;
}

// ── Graph Pipeline Types ────────────────────────────────────────────

export interface GraphGenerateRequest {
  condition_slug: string;
  modality?: string;
  tier?: string;
  doc_type?: string;
  prompt?: string;
  patient_context?: {
    age?: number;
    sex?: string;
    current_medications?: string[];
    contraindications?: string[];
  };
}

export interface GraphGenerateResponse {
  success: boolean;
  thread_id: string;
  status: string;
  condition: {
    slug: string;
    display_name: string;
    valid: boolean;
  };
  evidence_summary: {
    total_articles: number;
    sufficient: boolean;
    grade_distribution: Record<string, number>;
  };
  safety: {
    cleared: boolean;
    blocking: string[];
    off_label: string[];
  };
  protocol: {
    sections_count: number;
    grounding_score: number | null;
    qa_passed: boolean | null;
  };
  audit: {
    nodes_executed: number;
    errors: number;
  };
}

export interface GraphStatusResponse {
  thread_id: string;
  status: string;
  review_status: string;
  revision_number: number;
  condition: {
    slug: string;
    display_name: string;
  };
  evidence: {
    sufficient: boolean;
    article_count: number;
    grade_distribution: Record<string, number>;
    gaps: string[];
  };
  safety: {
    cleared: boolean;
    blocking: string[];
    off_label: string[];
    consent: string[];
  };
  protocol: {
    sections: Array<{
      section_id: string;
      title: string;
      content: string;
      cited_evidence_ids: string[];
      confidence: string;
    }>;
    grounding_score: number | null;
    grounding_issues: Array<{
      severity: string;
      section_id: string;
      message: string;
    }>;
  };
  evidence_articles: Array<{
    pmid: string;
    doi: string;
    title: string;
    year: number;
    grade: string;
    authors: string[];
  }>;
  node_history: Array<{
    node_id: string;
    duration_ms: number;
    status: string;
  }>;
  output: Record<string, unknown>;
}

export interface GraphReviewRequest {
  thread_id: string;
  decision: 'approve' | 'reject' | 'edit';
  reviewer_id: string;
  reviewer_credentials?: string;
  review_notes?: string;
  section_edits?: Array<{
    section_id: string;
    field: string;
    new_value: string;
    edit_reason: string;
  }>;
  parameter_overrides?: Array<{
    parameter: string;
    old_value: string;
    new_value: string;
    override_reason: string;
  }>;
}

export interface GraphReviewResponse {
  success: boolean;
  thread_id: string;
  decision: string;
  status: string;
  revision_number: number;
  output: Record<string, unknown>;
  audit_record_id: string | null;
}

// ── Generic Types ───────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// ── Cockpit Types ───────────────────────────────────────────────────

export interface CockpitOverview {
  total_conditions: number;
  total_protocols: number;
  pending_reviews: number;
  evidence_freshness: string;
  last_updated: string;
}

export interface ConditionSummary {
  slug: string;
  display_name: string;
  protocol_count: number;
  evidence_count: number;
  coverage_score: number;
}
