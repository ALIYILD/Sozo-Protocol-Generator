/**
 * Graph pipeline API — LangGraph-powered protocol generation lifecycle.
 *
 * 1. generateProtocol() → starts pipeline (async), returns thread_id + task_id
 * 2. getGraphStatus(thread_id) → poll for status / review payload
 * 3. submitReview(request) → approve/reject/edit, resumes pipeline
 */
import axios from 'axios';
import api from './client';
import type {
  GraphGenerateRequest,
  GraphGenerateResponse as BaseGraphGenerateResponse,
  GraphStatusResponse,
  GraphReviewRequest,
  GraphReviewResponse,
} from '../types';

/**
 * Extended response shape for the new async /api/graph/generate endpoint.
 *
 * The Celery-backed endpoint returns immediately with `{thread_id, status: "queued", task_id}`.
 * The existing rich fields (evidence_summary, safety, protocol, audit) are kept optional so
 * the frontend can still consume legacy synchronous responses during a rollout.
 */
export type GraphGenerateStatus =
  | 'queued'
  | 'running'
  | 'complete'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | string;

export type GraphGenerateResponse = Omit<
  BaseGraphGenerateResponse,
  'status' | 'evidence_summary' | 'safety' | 'protocol' | 'audit' | 'condition'
> & {
  status: GraphGenerateStatus;
  task_id?: string;
  condition?: BaseGraphGenerateResponse['condition'];
  evidence_summary?: BaseGraphGenerateResponse['evidence_summary'];
  safety?: BaseGraphGenerateResponse['safety'];
  protocol?: BaseGraphGenerateResponse['protocol'];
  audit?: BaseGraphGenerateResponse['audit'];
};

/**
 * Start a protocol generation pipeline.
 * Returns immediately with a thread_id (and task_id for the Celery worker).
 * The pipeline runs asynchronously — use getGraphStatus() to poll.
 */
export async function generateProtocol(
  data: GraphGenerateRequest,
): Promise<GraphGenerateResponse> {
  const res = await api.post<GraphGenerateResponse>('/graph/generate', data);
  return res.data;
}

/**
 * Get the current status of a graph execution.
 * Returns the full review payload when the graph is paused at the
 * clinician review interrupt.
 *
 * Returns `null` on 404 — the race between the HTTP handler returning and
 * Celery creating the first checkpoint can briefly 404. Callers should treat
 * a null result as "not ready yet" and retry.
 */
export async function getGraphStatus(
  threadId: string,
): Promise<GraphStatusResponse | null> {
  try {
    const res = await api.get<GraphStatusResponse>(`/graph/status/${threadId}`);
    return res.data;
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      return null;
    }
    throw err;
  }
}

/**
 * Submit a clinician review decision and resume the graph.
 * - approve: renders output documents and writes audit record
 * - reject: terminates or re-composes (if under max revisions)
 * - edit: applies edits and loops back for re-review
 */
export async function submitReview(
  data: GraphReviewRequest,
): Promise<GraphReviewResponse> {
  const res = await api.post<GraphReviewResponse>('/graph/review', data);
  return res.data;
}
