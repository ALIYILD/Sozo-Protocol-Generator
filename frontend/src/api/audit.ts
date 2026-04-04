import api from './client';
import type { AuditEventList } from '../types';

/** Matches GET /api/audit/events query params (optional strings omitted when empty). */
export type AuditEventFilters = {
  entity_type?: string;
  entity_id?: string;
  action?: string;
  actor?: string;
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