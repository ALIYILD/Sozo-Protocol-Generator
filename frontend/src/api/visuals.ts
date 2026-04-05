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
