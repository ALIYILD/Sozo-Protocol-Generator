import api from './client';

// ---------------------------------------------------------------------------
// Types — mirror the shapes returned by src/sozo_api/routes/reviews.py
// ---------------------------------------------------------------------------

export type ReviewDecision = 'approve' | 'reject' | 'request_revision';

export type ReviewCommentSeverity =
  | 'comment'
  | 'suggestion'
  | 'required_change'
  | 'blocking';

export interface ReviewComment {
  section_slug?: string | null;
  text: string;
  severity: ReviewCommentSeverity;
}

export interface ReviewQueueItem {
  protocol_id: string;
  version: number;
  condition_name: string;
  modality: string;
  submitted_by: string;
  submitted_at: string;
  evidence_level: string;
  qa_issues_count: number;
  priority: 'normal' | 'high' | string;
}

export interface ReviewQueueResponse {
  items: ReviewQueueItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface ReviewQueueCount {
  pending: number;
  high_priority: number;
}

export interface ReviewRecord {
  review_id: string;
  protocol_id: string;
  protocol_version: number;
  reviewer: string;
  status: string;
  comments: ReviewComment[];
  overall_notes: string | null;
  reviewed_at: string;
  signature_hash: string | null;
}

export interface EvidenceCitation {
  pmid?: string;
  title?: string;
  level?: string;
  [key: string]: unknown;
}

export interface QaIssue {
  id: string;
  severity: string;
  message: string;
  section?: string;
  overridden?: boolean;
  [key: string]: unknown;
}

export interface ReviewViewSection {
  slug: string;
  title: string;
  content: string;
  evidence_citations: EvidenceCitation[];
  qa_status?: string;
  qa_issues?: QaIssue[];
  [key: string]: unknown;
}

export interface ReviewViewBundle {
  protocol_id: string;
  version: number;
  condition: Record<string, unknown>;
  modality: Record<string, unknown>;
  sections: ReviewViewSection[];
  safety: {
    contraindications?: string[];
    warnings?: string[];
    emergency_protocol?: string;
    [key: string]: unknown;
  };
  evidence_summary: {
    total_citations?: number;
    level_I?: number;
    level_II?: number;
    level_III?: number;
    coverage_pct?: number;
    weakest_section?: string;
    [key: string]: unknown;
  };
  qa_report: {
    total_issues?: number;
    by_severity?: Record<string, number>;
    issues?: QaIssue[];
    [key: string]: unknown;
  };
  previous_reviews: ReviewRecord[];
  generation_metadata: Record<string, unknown>;
}

export interface ReviewDiffChange {
  section_slug: string;
  change_type: string;
  summary: string;
  old_snippet?: string;
  new_snippet?: string;
  [key: string]: unknown;
}

export interface ReviewDiff {
  protocol_id: string;
  from_version: number;
  to_version: number;
  changes: ReviewDiffChange[];
}

export interface EvidenceCheckSection {
  slug: string;
  coverage_pct: number;
  citations_count: number;
  low_evidence_claims: Array<{
    claim: string;
    current_level: string;
    note?: string;
    [key: string]: unknown;
  }>;
}

export interface EvidenceCheckReport {
  protocol_id: string;
  sections: EvidenceCheckSection[];
  contradictions: Array<{
    claim_a: string;
    claim_b: string;
    resolution_status: string;
    [key: string]: unknown;
  }>;
  qa_flags: QaIssue[];
}

export interface SignResult {
  protocol_id: string;
  reviewer: string;
  signed_at: string;
  signature_hash: string;
}

export interface QaOverrideResult {
  protocol_id: string;
  issue_id: string;
  overridden: boolean;
  overridden_by: string;
  overridden_at: string;
  justification: string;
}

export interface SubmitReviewPayload {
  decision: ReviewDecision;
  comments: ReviewComment[];
  overall_notes?: string | null;
}

// ---------------------------------------------------------------------------
// Endpoint wrappers — baseURL is `/api`, router prefix is `/reviews`.
// ---------------------------------------------------------------------------

export async function getReviewQueue(
  page = 1,
  pageSize = 20,
  condition?: string,
  priority?: 'normal' | 'high',
): Promise<ReviewQueueResponse> {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (condition) params.condition = condition;
  if (priority) params.priority = priority;
  const res = await api.get<ReviewQueueResponse>('/reviews/queue', { params });
  return res.data;
}

export async function getReviewQueueCount(): Promise<ReviewQueueCount> {
  const res = await api.get<ReviewQueueCount>('/reviews/queue/count');
  return res.data;
}

export async function getReviewView(
  protocolId: string,
  version?: number,
): Promise<ReviewViewBundle> {
  const params: Record<string, unknown> = {};
  if (version !== undefined) params.version = version;
  const res = await api.get<ReviewViewBundle>(
    `/reviews/${protocolId}/review-view`,
    { params },
  );
  return res.data;
}

export async function getReviewDiff(
  protocolId: string,
  fromVersion: number,
  toVersion: number,
): Promise<ReviewDiff> {
  const res = await api.get<ReviewDiff>(`/reviews/${protocolId}/diff`, {
    params: { from_version: fromVersion, to_version: toVersion },
  });
  return res.data;
}

export async function submitReviewDecision(
  protocolId: string,
  payload: SubmitReviewPayload,
): Promise<ReviewRecord> {
  const res = await api.post<ReviewRecord>(
    `/reviews/${protocolId}/review`,
    payload,
  );
  return res.data;
}

export async function listProtocolReviews(
  protocolId: string,
): Promise<{ protocol_id: string; reviews: ReviewRecord[] }> {
  const res = await api.get<{ protocol_id: string; reviews: ReviewRecord[] }>(
    `/reviews/${protocolId}/reviews`,
  );
  return res.data;
}

export async function signProtocol(protocolId: string): Promise<SignResult> {
  const res = await api.post<SignResult>(`/reviews/${protocolId}/sign`);
  return res.data;
}

export async function getEvidenceCheck(
  protocolId: string,
): Promise<EvidenceCheckReport> {
  const res = await api.get<EvidenceCheckReport>(
    `/reviews/${protocolId}/evidence-check`,
  );
  return res.data;
}

export async function overrideQaIssue(
  protocolId: string,
  issueId: string,
  justification: string,
): Promise<QaOverrideResult> {
  const res = await api.post<QaOverrideResult>(
    `/reviews/${protocolId}/override-qa`,
    null,
    { params: { issue_id: issueId, justification } },
  );
  return res.data;
}
