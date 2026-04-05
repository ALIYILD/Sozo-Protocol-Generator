import api from './client';

// ── Types ────────────────────────────────────────────────────────────────────

export interface Demographics {
  age: number;
  sex: string;
  handedness: string;
}

export interface PatientListItem {
  patient_id: string;
  external_id: string | null;
  demographics: Demographics;
  conditions: string[];
  active_protocols: number;
  assessments_count: number;
  created_at: string;
}

export interface PatientListResponse {
  patients: PatientListItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface AssessmentRecord {
  assessment_id: string;
  scale_name: string;
  abbreviation: string;
  score: number;
  severity_band: string;
  subscale_scores: Record<string, number> | null;
  assessed_at: string;
  session_number: number | null;
}

export interface TreatmentRecord {
  treatment_id: string;
  modality: string;
  condition_slug: string;
  target: string;
  parameters: Record<string, unknown>;
  sessions_completed: number;
  outcome: string;
  outcome_measures: Record<string, unknown>;
  adverse_events: string[];
  start_date: string | null;
  end_date: string | null;
  recorded_at: string;
}

export interface MedicationRecord {
  medication_id: string;
  name: string;
  drug_class: string;
  dose: string | null;
  start_date: string;
  end_date: string | null;
  is_active: boolean;
  added_at: string;
}

export interface PatientSafetyCheck {
  patient_id: string;
  safety_cleared: boolean;
  absolute_contraindications: string[];
  relative_contraindications: string[];
  medication_interactions: Array<Record<string, unknown>>;
  blocked_modalities: string[];
  warnings: string[];
}

export interface TimelineEntry {
  date: string;
  event_type: string;
  summary: string;
  details: Record<string, unknown>;
}

export interface CreatePatientRequest {
  external_id?: string;
  demographics: {
    age: number;
    sex: string;
    handedness?: string;
  };
  conditions?: string[];
  notes?: string;
}

// ── API functions ─────────────────────────────────────────────────────────────

export async function listPatients(params?: {
  page?: number;
  page_size?: number;
  search?: string;
  condition?: string;
}): Promise<PatientListResponse> {
  const res = await api.get<PatientListResponse>('/patients/', { params });
  return res.data;
}

export async function getPatient(id: string): Promise<PatientListItem> {
  const res = await api.get<PatientListItem>(`/patients/${id}`);
  return res.data;
}

export async function createPatient(data: CreatePatientRequest): Promise<PatientListItem> {
  const res = await api.post<PatientListItem>('/patients/', data);
  return res.data;
}

export async function getPatientAssessments(
  id: string,
  scale?: string,
): Promise<AssessmentRecord[]> {
  const res = await api.get<AssessmentRecord[]>(`/patients/${id}/assessments`, {
    params: scale ? { scale } : undefined,
  });
  return res.data;
}

export async function getPatientTreatments(id: string): Promise<TreatmentRecord[]> {
  const res = await api.get<TreatmentRecord[]>(`/patients/${id}/treatments`);
  return res.data;
}

export async function getPatientMedications(
  id: string,
  activeOnly = true,
): Promise<MedicationRecord[]> {
  const res = await api.get<MedicationRecord[]>(`/patients/${id}/medications`, {
    params: { active_only: activeOnly },
  });
  return res.data;
}

export async function getPatientSafetyCheck(
  id: string,
  modalities?: string,
): Promise<PatientSafetyCheck> {
  const res = await api.get<PatientSafetyCheck>(`/patients/${id}/safety-check`, {
    params: modalities ? { modalities } : undefined,
  });
  return res.data;
}

export async function getPatientTimeline(id: string, limit = 50): Promise<TimelineEntry[]> {
  const res = await api.get<TimelineEntry[]>(`/patients/${id}/timeline`, {
    params: { limit },
  });
  return res.data;
}

// EEG is not yet a backend endpoint; this stub returns an empty list so the
// EEG page can render its empty state gracefully.
export async function getPatientEEG(_id: string): Promise<[]> {
  return [];
}
