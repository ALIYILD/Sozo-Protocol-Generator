/**
 * Graph pipeline API — LangGraph-powered protocol generation lifecycle.
 *
 * 1. generateProtocol() → starts pipeline, returns thread_id
 * 2. getGraphStatus(thread_id) → poll for status / review payload
 * 3. submitReview(request) → approve/reject/edit, resumes pipeline
 */
import api from './client';
import type {
  GraphGenerateRequest,
  GraphGenerateResponse,
  GraphStatusResponse,
  GraphReviewRequest,
  GraphReviewResponse,
} from '../types';

/**
 * Start a protocol generation pipeline.
 * Returns immediately with a thread_id. The pipeline runs asynchronously
 * and pauses at the clinician review interrupt.
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
 */
export async function getGraphStatus(
  threadId: string,
): Promise<GraphStatusResponse> {
  const res = await api.get<GraphStatusResponse>(`/graph/status/${threadId}`);
  return res.data;
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
