import api from './client';
import type { AuditEventList } from '../types';

// ---------------------------------------------------------------------------
// Types for extended audit endpoints (summary, entity trail, build trace).
// Shapes mirror backend models in src/sozo_api/routes/audit.py.
// ---------------------------------------------------------------------------

/** Matches backend AuditSummary model. */
export type AuditSummary = {
  total_events_24h: number;
  total_events_7d: number;
  events_by_type: Record<string, number>;
  events_by_action: Record<string, number>;
  active_users_24h: number;
  recent_approvals: number;
  recent_rejections: number;
};

/** Matches backend AuditEvent model. */
export type AuditEvent = {
  id: number;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string | null;
  timestamp: string;
  node_name: string | null;
  input_hash: string | null;
  output_hash: string | null;
  details: Record<string, unknown>;
};

/** Response envelope for GET /audit/entity/{entity_type}/{entity_id}. */
export type EntityAuditTrail = {
  entity_type: string;
  entity_id: string;
  total_events: number;
  events: AuditEvent[];
};

/** Matches backend NodeTraceEntry model. */
export type NodeTraceEntry = {
  node_name: string;
  timestamp: string;
  duration_ms: number;
  input_hash: string;
  output_hash: string;
  decision: string | null;
  status: string;
};

/** Matches backend ProtocolBuildTrace model. */
export type ProtocolBuildTrace = {
  protocol_id: string;
  build_id: string;
  started_at: string;
  completed_at: string | null;
  total_duration_ms: number;
  nodes: NodeTraceEntry[];
  errors: Record<string, unknown>[];
  generation_method: string;
};

/** Matches GET /api/audit/events query params (optional strings omitted when empty). */
export type AuditEventFilters = {
  entity_type?: string;
  entity_id?: string;
  action?: string;
  actor?: string;
  /** Graph run id: matches details.thread_id or entity_id. */
  thread_id?: string;
  /** Protocol / LangGraph build id in event details. */
  build_id?: string;
  date_from?: string;
  date_to?: string;
  node_name?: string;
};

/** Build query-string-ready params; empty / whitespace values are omitted. */
export function auditFiltersToQueryParams(
  filters: AuditEventFilters,
): Record<string, string> {
  const out: Record<string, string> = {};
  const entries: [keyof AuditEventFilters, string][] = [
    ['entity_type', 'entity_type'],
    ['entity_id', 'entity_id'],
    ['action', 'action'],
    ['actor', 'actor'],
    ['thread_id', 'thread_id'],
    ['build_id', 'build_id'],
    ['date_from', 'date_from'],
    ['date_to', 'date_to'],
    ['node_name', 'node_name'],
  ];
  for (const [key, param] of entries) {
    const v = filters[key]?.trim();
    if (v) out[param] = v;
  }
  return out;
}

export async function listAuditEvents(
  page = 1,
  pageSize = 25,
  filters: AuditEventFilters = {},
): Promise<AuditEventList> {
  const res = await api.get<AuditEventList>('/audit/events', {
    params: {
      page,
      page_size: pageSize,
      ...auditFiltersToQueryParams(filters),
    },
  });
  return res.data;
}

export async function getAuditEntityTypes(): Promise<string[]> {
  const res = await api.get<{ entity_types: string[] }>('/audit/entity-types');
  return res.data.entity_types;
}

export async function getAuditActions(): Promise<string[]> {
  const res = await api.get<{ actions: string[] }>('/audit/actions');
  return res.data.actions;
}

export async function getAuditSummary(): Promise<AuditSummary> {
  const res = await api.get<AuditSummary>('/audit/summary');
  return res.data;
}

export async function getEntityAuditTrail(
  entity_type: string,
  entity_id: string,
): Promise<AuditEvent[]> {
  const res = await api.get<EntityAuditTrail>(
    `/audit/entity/${encodeURIComponent(entity_type)}/${encodeURIComponent(entity_id)}`,
  );
  return res.data.events;
}

export async function getBuildTrace(build_id: string): Promise<ProtocolBuildTrace> {
  const res = await api.get<ProtocolBuildTrace>(
    `/audit/build-trace/${encodeURIComponent(build_id)}`,
  );
  return res.data;
}

export async function exportAuditEvents(filters: AuditEventFilters): Promise<Blob> {
  const res = await api.get('/audit/export', {
    params: {
      format: 'csv',
      ...auditFiltersToQueryParams(filters),
    },
    responseType: 'blob',
  });
  return res.data as Blob;
}