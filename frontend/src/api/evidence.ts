import api from './client';
import type {
  EvidenceArticle,
  EvidenceClaim,
  PaginatedResponse,
  ConditionInfo,
  StalenessReport,
  CockpitOverview,
  ConditionSummary,
  SafetyCheckRequest,
  SafetyCheckResponse,
  PersonalizationRequest,
  PersonalizationResponse,
} from '../types';

export async function listArticles(
  page = 1,
  pageSize = 20,
  conditionSlug?: string,
): Promise<PaginatedResponse<EvidenceArticle>> {
  const params: Record<string, unknown> = { page, page_size: pageSize };
  if (conditionSlug) params.condition = conditionSlug;
  const res = await api.get<PaginatedResponse<EvidenceArticle>>('/evidence/articles', { params });
  return res.data;
}

export async function getArticle(id: string): Promise<EvidenceArticle> {
  const res = await api.get<EvidenceArticle>(`/evidence/articles/${id}`);
  return res.data;
}

export async function listClaims(
  articleId?: string,
  conditionSlug?: string,
): Promise<EvidenceClaim[]> {
  const params: Record<string, unknown> = {};
  if (articleId) params.article_id = articleId;
  if (conditionSlug) params.condition = conditionSlug;
  const res = await api.get<EvidenceClaim[]>('/evidence/claims', { params });
  return res.data;
}

export async function listConditions(): Promise<ConditionInfo[]> {
  const res = await api.get<{ conditions: ConditionInfo[] }>('/knowledge/conditions');
  return res.data.conditions;
}

export async function getCondition(slug: string): Promise<Record<string, unknown>> {
  const res = await api.get<{ condition: Record<string, unknown> }>(
    `/knowledge/conditions/${slug}`,
  );
  return res.data.condition;
}

export async function getStalenessReport(): Promise<StalenessReport> {
  const res = await api.get<StalenessReport>('/evidence/staleness');
  return res.data;
}

export async function getCockpitOverview(): Promise<CockpitOverview> {
  const res = await api.get<{ overview: CockpitOverview }>('/cockpit/overview');
  return res.data.overview;
}

export async function getCockpitConditions(): Promise<ConditionSummary[]> {
  const res = await api.get<{ conditions: ConditionSummary[] }>('/cockpit/conditions');
  return res.data.conditions;
}

export async function runSafetyCheck(data: SafetyCheckRequest): Promise<SafetyCheckResponse> {
  const res = await api.post<SafetyCheckResponse>('/safety/check', data);
  return res.data;
}

export async function runPersonalization(data: PersonalizationRequest): Promise<PersonalizationResponse> {
  const res = await api.post<PersonalizationResponse>('/personalization/run', data);
  return res.data;
}
