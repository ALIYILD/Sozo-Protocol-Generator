import api from './client';

export interface VisualItem {
  condition: string;
  condition_name: string;
  visual_type: string;
  visual_type_label: string;
  filename: string;
  url: string;
}

export interface VisualsLibraryResponse {
  items: VisualItem[];
  total: number;
}

export async function listVisualsLibrary(
  condition?: string,
  visualType?: string,
): Promise<VisualsLibraryResponse> {
  const params: Record<string, string> = {};
  if (condition) params.condition = condition;
  if (visualType) params.visual_type = visualType;
  const res = await api.get<VisualsLibraryResponse>('/visuals/library', { params });
  return res.data;
}

// ── On-demand render ─────────────────────────────────────────────────

export type VisualType = string;

export interface VisualTypesResponse {
  types: VisualType[];
}

export async function listVisualTypes(): Promise<VisualType[]> {
  const res = await api.get<VisualTypesResponse>('/visuals/types');
  return res.data.types ?? [];
}

export type RenderFormat = 'png' | 'plotly_json' | 'both';

export interface RenderVisualRequest {
  visual_type: VisualType;
  condition_slug?: string;
  tier?: string;
  render_format?: RenderFormat;
  title?: string;
  subtitle?: string;
  [key: string]: unknown;
}

export interface VisualExplanationPayload {
  summary?: string;
  reasoning_chain?: string[];
  eeg_findings?: string[];
  network_interpretation?: string;
  phenotype_link?: string;
  protocol_link?: string;
  confidence_note?: string;
}

export interface VisualEvidencePayload {
  pmid?: string;
  claim?: string;
  relevance?: string;
}

export interface VisualMetadataPayload {
  condition_slug?: string;
  protocol_id?: string;
  modality?: string;
  targets?: string[];
  bands?: string[];
  timepoint?: string;
  comparison_type?: string;
  source_generator?: string;
  generator_version?: string;
}

export interface RenderVisualResponse {
  visual_id: string;
  visual_type: string;
  render_format: string;
  generated_at: string;
  confidence: number;
  success: boolean;
  warnings: string[];
  explanation: VisualExplanationPayload;
  evidence: VisualEvidencePayload[];
  metadata: VisualMetadataPayload;
  image_path?: string;
  plotly_json?: { data?: unknown[]; layout?: unknown; [key: string]: unknown };
}

export async function renderVisual(
  body: RenderVisualRequest,
): Promise<RenderVisualResponse> {
  // Default to "both" so we get a JSON envelope with image_path/plotly_json
  // instead of raw PNG bytes.
  const payload: RenderVisualRequest = {
    render_format: 'both',
    ...body,
  };
  const res = await api.post<RenderVisualResponse>('/visuals/render', payload);
  return res.data;
}
