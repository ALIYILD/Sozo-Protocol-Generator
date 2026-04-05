/**
 * Health / readiness API.
 *
 * GET /api/health is unauthenticated and reports overall backend status
 * plus a `checks` bag that the frontend probes defensively. The exact
 * shape depends on what the backend has been extended with, so the
 * return type is intentionally loose — consumers use optional chaining
 * to probe individual fields.
 *
 * Expected (eventual) shape:
 *   {
 *     status: "ok" | "degraded",
 *     checks: {
 *       anthropic_key_configured: boolean,
 *       semantic_scholar_key_configured: boolean,
 *       ...
 *     }
 *   }
 */
import api from './client';

export async function getHealth(): Promise<Record<string, unknown>> {
  const res = await api.get<Record<string, unknown>>('/health');
  return res.data;
}
