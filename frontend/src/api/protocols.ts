import api from './client';
import type {
  ProtocolListItem,
  ProtocolDetail,
  ProtocolCreateRequest,
  ProtocolCreateResponse,
  GenerationStatus,
  PaginatedResponse,
} from '../types';

export async function listProtocols(
  page = 1,
  pageSize = 20,
  status?: string,
  condition?: string,
  modality?: string,
): Promise<PaginatedResponse<ProtocolListItem>> {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (status) params.status = status;
  if (condition) params.condition = condition;
  if (modality) params.modality = modality;
  const res = await api.get<PaginatedResponse<ProtocolListItem>>('/protocols/', { params });
  return res.data;
}

export async function getProtocol(id: string): Promise<ProtocolDetail> {
  const res = await api.get<ProtocolDetail>(`/protocols/${id}`);
  return res.data;
}

export async function createProtocol(data: ProtocolCreateRequest): Promise<ProtocolCreateResponse> {
  const res = await api.post<ProtocolCreateResponse>('/protocols/', data);
  return res.data;
}

export async function getGenerationStatus(taskId: string): Promise<GenerationStatus> {
  const res = await api.get<GenerationStatus>(`/protocols/generation-status/${taskId}`);
  return res.data;
}

export async function updateProtocol(
  id: string,
  data: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const res = await api.put<Record<string, unknown>>(`/protocols/${id}`, data);
  return res.data;
}

export async function submitForReview(id: string, notes?: string): Promise<Record<string, unknown>> {
  const res = await api.post<Record<string, unknown>>(`/protocols/${id}/submit-review`, { notes });
  return res.data;
}

export async function transitionStatus(
  id: string,
  targetStatus: string,
  notes?: string,
): Promise<Record<string, unknown>> {
  const res = await api.post<Record<string, unknown>>(`/protocols/${id}/transition`, {
    target_status: targetStatus,
    notes,
  });
  return res.data;
}

export async function cloneProtocol(id: string): Promise<Record<string, unknown>> {
  const res = await api.post<Record<string, unknown>>(`/protocols/${id}/clone`);
  return res.data;
}

export async function exportProtocol(
  id: string,
  format: 'docx' | 'pdf',
): Promise<Record<string, unknown>> {
  const res = await api.get<Record<string, unknown>>(`/protocols/${id}/export/${format}`);
  return res.data;
}

export async function getProtocolEvidence(id: string): Promise<Record<string, unknown>> {
  const res = await api.get<Record<string, unknown>>(`/protocols/${id}/evidence`);
  return res.data;
}

export async function getProtocolAudit(id: string): Promise<Record<string, unknown>> {
  const res = await api.get<Record<string, unknown>>(`/protocols/${id}/audit`);
  return res.data;
}

export async function listAvailableConditions(): Promise<Record<string, unknown>[]> {
  const res = await api.get<{ conditions: Record<string, unknown>[] }>('/protocols/conditions/available');
  return res.data.conditions;
}
