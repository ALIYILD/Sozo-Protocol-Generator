import { useState, type FormEvent } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  ShieldCheck,
  Sliders,
  Activity,
  AlertTriangle,
  CheckCircle,
  Pencil,
  Trash2,
} from 'lucide-react';
import {
  addPatientAssessment,
  addPatientMedication,
  addPatientTreatment,
  getAssessmentTrajectory,
  getPatient,
  getPatientAssessments,
  getPatientTreatments,
  getPatientMedications,
  listAvailableScales,
  removePatientMedication,
  updatePatient,
  type AddAssessmentRequest,
  type AddMedicationRequest,
  type AddTreatmentRequest,
  type ScaleDefinition,
  type TrajectoryPoint,
  type UpdatePatientRequest,
} from '../api/patients';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import type { TreatmentRecord, AssessmentRecord, MedicationRecord } from '../api/patients';
import { format, parseISO } from 'date-fns';

// ── Severity band → badge status mapping ──────────────────────────────────────

function severityStatus(band: string): string {
  const map: Record<string, string> = {
    minimal: 'approved',
    mild: 'low',
    moderate: 'pending_review',
    severe: 'rejected',
    unknown: 'draft',
  };
  return map[band] ?? 'draft';
}

function outcomeStatus(outcome: string): string {
  const map: Record<string, string> = {
    responder: 'approved',
    partial_responder: 'low',
    non_responder: 'rejected',
    not_assessed: 'draft',
  };
  return map[outcome] ?? 'draft';
}

// ── Page ──────────────────────────────────────────────────────────────────────

const TREATMENT_OUTCOMES = [
  { value: 'responder', label: 'Responder' },
  { value: 'partial_responder', label: 'Partial responder' },
  { value: 'non_responder', label: 'Non-responder' },
  { value: 'not_assessed', label: 'Not assessed' },
] as const;

interface DemographicsForm {
  external_id: string;
  age: string;
  sex: string;
  handedness: string;
}

interface MedicationForm {
  name: string;
  drug_class: string;
  dose: string;
  start_date: string;
}

interface AssessmentForm {
  scale_name: string;
  score: string;
  session_number: string;
  notes: string;
}

interface TreatmentForm {
  modality: string;
  condition_slug: string;
  target: string;
  parameters_summary: string;
  sessions_completed: string;
  outcome: string;
  start_date: string;
  end_date: string;
}

const emptyMedicationForm: MedicationForm = {
  name: '',
  drug_class: '',
  dose: '',
  start_date: new Date().toISOString().slice(0, 10),
};

const emptyAssessmentForm: AssessmentForm = {
  scale_name: 'PHQ-9',
  score: '',
  session_number: '',
  notes: '',
};

const emptyTreatmentForm: TreatmentForm = {
  modality: '',
  condition_slug: '',
  target: '',
  parameters_summary: '',
  sessions_completed: '0',
  outcome: 'not_assessed',
  start_date: new Date().toISOString().slice(0, 10),
  end_date: '',
};

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const {
    data: patient,
    isLoading: patientLoading,
    error: patientError,
  } = useQuery({
    queryKey: ['patient', id],
    queryFn: () => getPatient(id!),
    enabled: !!id,
  });

  // ── Write-state: edit mode + form values ──────────────────────────────
  const [editingDemographics, setEditingDemographics] = useState(false);
  const [demoForm, setDemoForm] = useState<DemographicsForm>({
    external_id: '',
    age: '',
    sex: 'male',
    handedness: 'right',
  });
  const [medForm, setMedForm] = useState<MedicationForm>(emptyMedicationForm);
  const [assessForm, setAssessForm] = useState<AssessmentForm>(emptyAssessmentForm);
  const [treatForm, setTreatForm] = useState<TreatmentForm>(emptyTreatmentForm);
  const [trajectoryScale, setTrajectoryScale] = useState<string>('');

  const invalidatePatient = () => {
    queryClient.invalidateQueries({ queryKey: ['patient', id] });
  };
  const invalidateMeds = () => {
    queryClient.invalidateQueries({ queryKey: ['patient-medications', id] });
  };
  const invalidateAssessments = () => {
    queryClient.invalidateQueries({ queryKey: ['patient-assessments', id] });
  };
  const invalidateTreatments = () => {
    queryClient.invalidateQueries({ queryKey: ['patient-treatments', id] });
  };

  const updatePatientMutation = useMutation({
    mutationFn: (data: UpdatePatientRequest) => updatePatient(id!, data),
    onSuccess: () => {
      invalidatePatient();
      setEditingDemographics(false);
    },
  });

  const addMedicationMutation = useMutation({
    mutationFn: (data: AddMedicationRequest) => addPatientMedication(id!, data),
    onSuccess: () => {
      invalidateMeds();
      setMedForm(emptyMedicationForm);
    },
  });

  const removeMedicationMutation = useMutation({
    mutationFn: (medicationId: string) => removePatientMedication(id!, medicationId),
    onSuccess: () => invalidateMeds(),
  });

  const addAssessmentMutation = useMutation({
    mutationFn: (data: AddAssessmentRequest) => addPatientAssessment(id!, data),
    onSuccess: () => {
      invalidateAssessments();
      invalidatePatient();
      setAssessForm(emptyAssessmentForm);
    },
  });

  const addTreatmentMutation = useMutation({
    mutationFn: (data: AddTreatmentRequest) => addPatientTreatment(id!, data),
    onSuccess: () => {
      invalidateTreatments();
      setTreatForm(emptyTreatmentForm);
    },
  });

  const beginEditDemographics = () => {
    if (!patient) return;
    setDemoForm({
      external_id: patient.external_id ?? '',
      age: String(patient.demographics.age),
      sex: patient.demographics.sex,
      handedness: patient.demographics.handedness,
    });
    setEditingDemographics(true);
  };

  const submitDemographics = (e: FormEvent) => {
    e.preventDefault();
    if (!patient) return;
    const ageNum = Number(demoForm.age);
    if (!Number.isFinite(ageNum) || ageNum < 0) return;
    updatePatientMutation.mutate({
      external_id: demoForm.external_id.trim() || null,
      demographics: {
        age: ageNum,
        sex: demoForm.sex,
        handedness: demoForm.handedness,
      },
      conditions: patient.conditions,
    });
  };

  const submitMedication = (e: FormEvent) => {
    e.preventDefault();
    if (!medForm.name.trim() || !medForm.drug_class.trim() || !medForm.start_date) return;
    addMedicationMutation.mutate({
      name: medForm.name.trim(),
      drug_class: medForm.drug_class.trim(),
      dose: medForm.dose.trim() || null,
      start_date: medForm.start_date,
    });
  };

  const handleRemoveMedication = (medId: string, name: string) => {
    if (window.confirm(`Remove ${name}? This will mark it as discontinued.`)) {
      removeMedicationMutation.mutate(medId);
    }
  };

  const submitAssessment = (e: FormEvent) => {
    e.preventDefault();
    const scoreNum = Number(assessForm.score);
    if (!assessForm.scale_name.trim() || !Number.isFinite(scoreNum)) return;
    const sessionNum = assessForm.session_number
      ? Number(assessForm.session_number)
      : null;
    addAssessmentMutation.mutate({
      scale_name: assessForm.scale_name.trim(),
      score: scoreNum,
      session_number:
        sessionNum !== null && Number.isFinite(sessionNum) ? sessionNum : null,
      notes: assessForm.notes.trim() || null,
    });
  };

  const submitTreatment = (e: FormEvent) => {
    e.preventDefault();
    if (
      !treatForm.modality.trim() ||
      !treatForm.condition_slug.trim() ||
      !treatForm.target.trim() ||
      !treatForm.start_date
    ) {
      return;
    }
    const sessionsNum = Number(treatForm.sessions_completed);
    addTreatmentMutation.mutate({
      modality: treatForm.modality.trim(),
      condition_slug: treatForm.condition_slug.trim(),
      target: treatForm.target.trim(),
      parameters: treatForm.parameters_summary.trim()
        ? { summary: treatForm.parameters_summary.trim() }
        : {},
      sessions_completed: Number.isFinite(sessionsNum) ? sessionsNum : 0,
      outcome: treatForm.outcome,
      start_date: treatForm.start_date,
      end_date: treatForm.end_date || null,
    });
  };

  const { data: assessments = [], isLoading: assessmentsLoading } = useQuery({
    queryKey: ['patient-assessments', id],
    queryFn: () => getPatientAssessments(id!),
    enabled: !!id,
  });

  const { data: treatments = [], isLoading: treatmentsLoading } = useQuery({
    queryKey: ['patient-treatments', id],
    queryFn: () => getPatientTreatments(id!),
    enabled: !!id,
  });

  const { data: medications = [] } = useQuery({
    queryKey: ['patient-medications', id],
    queryFn: () => getPatientMedications(id!, true),
    enabled: !!id,
  });

  const {
    data: availableScales = [],
    isError: scalesError,
  } = useQuery<ScaleDefinition[]>({
    queryKey: ['available-scales'],
    queryFn: listAvailableScales,
  });

  const { data: trajectoryPoints = [], isLoading: trajectoryLoading } = useQuery<
    TrajectoryPoint[]
  >({
    queryKey: ['assessment-trajectory', id, trajectoryScale],
    queryFn: () => getAssessmentTrajectory(id!, trajectoryScale),
    enabled: !!id && !!trajectoryScale,
  });

  const scalesUnavailable = scalesError || availableScales.length === 0;

  if (patientLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  if (patientError || !patient) {
    return (
      <div className="mt-20 text-center">
        <p className="text-gray-500">Patient not found.</p>
        <Button variant="ghost" className="mt-4" onClick={() => navigate('/patients')}>
          Back to Patients
        </Button>
      </div>
    );
  }

  const demo = patient.demographics;
  const label =
    patient.external_id ?? (patient.patient_id as string).slice(0, 8).toUpperCase();

  // Assessment columns
  const assessmentCols: Column<AssessmentRecord & Record<string, unknown>>[] = [
    { key: 'abbreviation', header: 'Scale', sortable: true },
    {
      key: 'score',
      header: 'Score',
      render: (row) => <span className="font-semibold">{row.score as number}</span>,
    },
    {
      key: 'severity_band',
      header: 'Severity',
      render: (row) => <Badge status={severityStatus(row.severity_band as string)} />,
    },
    {
      key: 'session_number',
      header: 'Session',
      render: (row) =>
        row.session_number != null ? (
          <span className="text-sm text-gray-600">#{row.session_number as number}</span>
        ) : (
          <span className="text-gray-400">—</span>
        ),
    },
    {
      key: 'assessed_at',
      header: 'Date',
      sortable: true,
      render: (row) => format(new Date(row.assessed_at as string), 'dd MMM yyyy'),
    },
  ];

  // Treatment columns
  const treatmentCols: Column<TreatmentRecord & Record<string, unknown>>[] = [
    {
      key: 'modality',
      header: 'Modality',
      render: (row) => (
        <span className="font-medium uppercase text-sozo-text">
          {row.modality as string}
        </span>
      ),
    },
    { key: 'condition_slug', header: 'Condition', sortable: true },
    { key: 'target', header: 'Target' },
    {
      key: 'sessions_completed',
      header: 'Sessions',
      render: (row) => (
        <span className="text-sm text-gray-700">{row.sessions_completed as number}</span>
      ),
    },
    {
      key: 'outcome',
      header: 'Outcome',
      render: (row) => <Badge status={outcomeStatus(row.outcome as string)} />,
    },
    {
      key: 'start_date',
      header: 'Start',
      sortable: true,
      render: (row) =>
        row.start_date ? format(new Date(row.start_date as string), 'dd MMM yyyy') : '—',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/patients')}
          className="rounded-md p-2 hover:bg-gray-100"
        >
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-sozo-text">Patient {label}</h1>
          <p className="text-sm text-gray-500">
            {demo.age}y &middot; {demo.sex} &middot; {demo.handedness}-handed
            {patient.conditions.length > 0 && (
              <> &middot; {patient.conditions.join(', ')}</>
            )}
          </p>
        </div>
        {patient.conditions.slice(0, 2).map((c) => (
          <Badge key={c} status={c} className="capitalize" />
        ))}
        {!editingDemographics && (
          <Button variant="secondary" size="sm" onClick={beginEditDemographics}>
            <Pencil className="mr-2 h-4 w-4" />
            Edit
          </Button>
        )}
      </div>

      {/* Inline edit demographics form */}
      {editingDemographics && (
        <Card title="Edit Demographics">
          <form onSubmit={submitDemographics} className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <label className="block text-sm">
                <span className="mb-1 block font-medium text-gray-700">
                  External ID
                </span>
                <input
                  type="text"
                  value={demoForm.external_id}
                  onChange={(e) =>
                    setDemoForm({ ...demoForm, external_id: e.target.value })
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  placeholder="Optional identifier"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block font-medium text-gray-700">Age *</span>
                <input
                  type="number"
                  required
                  min={0}
                  max={120}
                  value={demoForm.age}
                  onChange={(e) => setDemoForm({ ...demoForm, age: e.target.value })}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                />
              </label>
              <label className="block text-sm">
                <span className="mb-1 block font-medium text-gray-700">Sex *</span>
                <select
                  required
                  value={demoForm.sex}
                  onChange={(e) => setDemoForm({ ...demoForm, sex: e.target.value })}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </label>
              <label className="block text-sm">
                <span className="mb-1 block font-medium text-gray-700">
                  Handedness
                </span>
                <select
                  value={demoForm.handedness}
                  onChange={(e) =>
                    setDemoForm({ ...demoForm, handedness: e.target.value })
                  }
                  className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                >
                  <option value="right">Right</option>
                  <option value="left">Left</option>
                  <option value="ambidextrous">Ambidextrous</option>
                </select>
              </label>
            </div>
            {updatePatientMutation.isError && (
              <p className="text-sm text-sozo-danger">
                Failed to update patient. Please try again.
              </p>
            )}
            {updatePatientMutation.isSuccess && (
              <p className="text-sm text-green-600">Patient updated.</p>
            )}
            <div className="flex gap-2">
              <Button
                type="submit"
                variant="primary"
                isLoading={updatePatientMutation.isPending}
                disabled={updatePatientMutation.isPending}
              >
                Save
              </Button>
              <Button
                type="button"
                variant="ghost"
                onClick={() => setEditingDemographics(false)}
                disabled={updatePatientMutation.isPending}
              >
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* ── Main content ─────────────────────────────────────── */}
        <div className="space-y-6 lg:col-span-2">
          {/* Assessment scores */}
          <Card title="Assessment Scores">
            {assessmentsLoading ? (
              <LoadingSpinner size="sm" className="py-4" />
            ) : assessments.length === 0 ? (
              <p className="py-4 text-center text-sm text-gray-400">
                No assessments recorded yet.
              </p>
            ) : (
              <Table
                columns={assessmentCols}
                data={assessments as (AssessmentRecord & Record<string, unknown>)[]}
                keyExtractor={(row) => row.assessment_id as string}
                emptyMessage="No assessments recorded."
              />
            )}

            {/* Add assessment form */}
            <form
              onSubmit={submitAssessment}
              className="mt-4 space-y-3 border-t border-gray-100 pt-4"
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Record assessment
              </p>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Scale *</span>
                  {scalesUnavailable ? (
                    <input
                      type="text"
                      required
                      placeholder="e.g. PHQ-9"
                      value={assessForm.scale_name}
                      onChange={(e) =>
                        setAssessForm({ ...assessForm, scale_name: e.target.value })
                      }
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                    />
                  ) : (
                    <select
                      required
                      value={assessForm.scale_name}
                      onChange={(e) =>
                        setAssessForm({ ...assessForm, scale_name: e.target.value })
                      }
                      className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                    >
                      {availableScales.map((s) => (
                        <option key={s.scale_name} value={s.scale_name}>
                          {s.abbreviation} — {s.full_name}
                        </option>
                      ))}
                    </select>
                  )}
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Score *</span>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={assessForm.score}
                    onChange={(e) =>
                      setAssessForm({ ...assessForm, score: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Session #</span>
                  <input
                    type="number"
                    min={0}
                    value={assessForm.session_number}
                    onChange={(e) =>
                      setAssessForm({
                        ...assessForm,
                        session_number: e.target.value,
                      })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm md:col-span-2">
                  <span className="mb-1 block text-xs text-gray-600">Notes</span>
                  <input
                    type="text"
                    value={assessForm.notes}
                    onChange={(e) =>
                      setAssessForm({ ...assessForm, notes: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
              </div>
              {addAssessmentMutation.isError && (
                <p className="text-xs text-sozo-danger">
                  Failed to record assessment. Please verify the scale and score range.
                </p>
              )}
              {addAssessmentMutation.isSuccess && (
                <p className="text-xs text-green-600">Assessment recorded.</p>
              )}
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={addAssessmentMutation.isPending}
                disabled={addAssessmentMutation.isPending}
              >
                Record assessment
              </Button>
            </form>
          </Card>

          {/* Score trajectory */}
          <Card title="Score Trajectory">
            <div className="space-y-4">
              <label className="block text-sm">
                <span className="mb-1 block text-xs text-gray-600">Scale</span>
                {scalesUnavailable ? (
                  <input
                    type="text"
                    placeholder="Enter scale name (e.g. PHQ-9)"
                    value={trajectoryScale}
                    onChange={(e) => setTrajectoryScale(e.target.value)}
                    className="w-full max-w-xs rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                ) : (
                  <select
                    value={trajectoryScale}
                    onChange={(e) => setTrajectoryScale(e.target.value)}
                    className="w-full max-w-xs rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  >
                    <option value="">Select a scale…</option>
                    {availableScales.map((s) => (
                      <option key={s.scale_name} value={s.scale_name}>
                        {s.abbreviation} — {s.full_name}
                      </option>
                    ))}
                  </select>
                )}
              </label>

              {!trajectoryScale ? (
                <p className="py-6 text-center text-sm text-gray-400">
                  Select a scale to view its trajectory.
                </p>
              ) : trajectoryLoading ? (
                <LoadingSpinner size="sm" className="py-6" />
              ) : trajectoryPoints.length === 0 ? (
                <p className="py-6 text-center text-sm text-gray-400">
                  No data yet for this scale.
                </p>
              ) : (
                <TrajectoryChart
                  points={trajectoryPoints}
                  scaleName={trajectoryScale}
                />
              )}
            </div>
          </Card>

          {/* Active medications */}
          <Card title="Active Medications">
            {medications.length === 0 ? (
              <p className="py-2 text-sm text-gray-400">No active medications on file.</p>
            ) : (
              <div className="divide-y divide-gray-100">
                {(medications as MedicationRecord[]).map((med) => (
                  <div
                    key={med.medication_id}
                    className="flex items-start justify-between gap-3 py-3"
                  >
                    <div className="flex-1">
                      <p className="text-sm font-medium text-sozo-text">{med.name}</p>
                      <p className="text-xs text-gray-500">
                        {med.drug_class}
                        {med.dose ? ` · ${med.dose}` : ''}
                      </p>
                    </div>
                    <span className="text-xs text-gray-400">
                      since {format(new Date(med.start_date), 'dd MMM yyyy')}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveMedication(med.medication_id, med.name)}
                      isLoading={
                        removeMedicationMutation.isPending &&
                        removeMedicationMutation.variables === med.medication_id
                      }
                      disabled={removeMedicationMutation.isPending}
                    >
                      <Trash2 className="mr-1 h-3.5 w-3.5" />
                      Remove
                    </Button>
                  </div>
                ))}
              </div>
            )}

            {/* Add medication form */}
            <form
              onSubmit={submitMedication}
              className="mt-4 space-y-3 border-t border-gray-100 pt-4"
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Add medication
              </p>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                <input
                  type="text"
                  required
                  placeholder="Name *"
                  value={medForm.name}
                  onChange={(e) => setMedForm({ ...medForm, name: e.target.value })}
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                />
                <input
                  type="text"
                  required
                  placeholder="Drug class *"
                  value={medForm.drug_class}
                  onChange={(e) =>
                    setMedForm({ ...medForm, drug_class: e.target.value })
                  }
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                />
                <input
                  type="text"
                  placeholder="Dose (e.g. 20 mg daily)"
                  value={medForm.dose}
                  onChange={(e) => setMedForm({ ...medForm, dose: e.target.value })}
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                />
                <input
                  type="date"
                  required
                  value={medForm.start_date}
                  onChange={(e) =>
                    setMedForm({ ...medForm, start_date: e.target.value })
                  }
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                />
              </div>
              {addMedicationMutation.isError && (
                <p className="text-xs text-sozo-danger">
                  Failed to add medication. Please try again.
                </p>
              )}
              {addMedicationMutation.isSuccess && (
                <p className="text-xs text-green-600">Medication added.</p>
              )}
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={addMedicationMutation.isPending}
                disabled={addMedicationMutation.isPending}
              >
                Add medication
              </Button>
            </form>
          </Card>

          {/* Treatment history */}
          <Card title="Treatment History">
            {treatmentsLoading ? (
              <LoadingSpinner size="sm" className="py-4" />
            ) : treatments.length === 0 ? (
              <p className="py-4 text-center text-sm text-gray-400">
                No treatment records yet.
              </p>
            ) : (
              <Table
                columns={treatmentCols}
                data={treatments as (TreatmentRecord & Record<string, unknown>)[]}
                keyExtractor={(row) => row.treatment_id as string}
                emptyMessage="No treatment records."
              />
            )}

            {/* Add treatment form */}
            <form
              onSubmit={submitTreatment}
              className="mt-4 space-y-3 border-t border-gray-100 pt-4"
            >
              <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Add treatment record
              </p>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Modality *</span>
                  <input
                    type="text"
                    required
                    placeholder="tms, tdcs, tfus..."
                    value={treatForm.modality}
                    onChange={(e) =>
                      setTreatForm({ ...treatForm, modality: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">
                    Condition slug *
                  </span>
                  <input
                    type="text"
                    required
                    placeholder="major_depressive_disorder"
                    value={treatForm.condition_slug}
                    onChange={(e) =>
                      setTreatForm({ ...treatForm, condition_slug: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Target *</span>
                  <input
                    type="text"
                    required
                    placeholder="L-DLPFC"
                    value={treatForm.target}
                    onChange={(e) =>
                      setTreatForm({ ...treatForm, target: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">
                    Sessions completed
                  </span>
                  <input
                    type="number"
                    min={0}
                    value={treatForm.sessions_completed}
                    onChange={(e) =>
                      setTreatForm({
                        ...treatForm,
                        sessions_completed: e.target.value,
                      })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm md:col-span-2">
                  <span className="mb-1 block text-xs text-gray-600">
                    Parameters summary
                  </span>
                  <input
                    type="text"
                    placeholder="10 Hz, 120% RMT, 3000 pulses/session"
                    value={treatForm.parameters_summary}
                    onChange={(e) =>
                      setTreatForm({
                        ...treatForm,
                        parameters_summary: e.target.value,
                      })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Outcome</span>
                  <select
                    value={treatForm.outcome}
                    onChange={(e) =>
                      setTreatForm({ ...treatForm, outcome: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  >
                    {TREATMENT_OUTCOMES.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">Start date *</span>
                  <input
                    type="date"
                    required
                    value={treatForm.start_date}
                    onChange={(e) =>
                      setTreatForm({ ...treatForm, start_date: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
                <label className="block text-sm">
                  <span className="mb-1 block text-xs text-gray-600">End date</span>
                  <input
                    type="date"
                    value={treatForm.end_date}
                    onChange={(e) =>
                      setTreatForm({ ...treatForm, end_date: e.target.value })
                    }
                    className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
                  />
                </label>
              </div>
              {addTreatmentMutation.isError && (
                <p className="text-xs text-sozo-danger">
                  Failed to add treatment record. Please verify the fields.
                </p>
              )}
              {addTreatmentMutation.isSuccess && (
                <p className="text-xs text-green-600">Treatment record added.</p>
              )}
              <Button
                type="submit"
                variant="primary"
                size="sm"
                isLoading={addTreatmentMutation.isPending}
                disabled={addTreatmentMutation.isPending}
              >
                Add treatment
              </Button>
            </form>
          </Card>
        </div>

        {/* ── Sidebar ──────────────────────────────────────────── */}
        <div className="space-y-6">
          {/* Summary */}
          <Card title="Summary">
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Patient ID</dt>
                <dd className="font-mono text-xs break-all">{patient.patient_id}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Enrolled</dt>
                <dd className="font-medium">
                  {format(new Date(patient.created_at), 'dd MMM yyyy')}
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Assessments</dt>
                <dd className="font-medium">{patient.assessments_count}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Active Protocols</dt>
                <dd className="flex items-center gap-1">
                  {patient.active_protocols > 0 ? (
                    <>
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span className="font-medium">{patient.active_protocols}</span>
                    </>
                  ) : (
                    <span className="text-gray-400">None assigned</span>
                  )}
                </dd>
              </div>
            </dl>
          </Card>

          {/* Actions */}
          <Card title="Actions">
            <div className="space-y-3">
              <Button
                variant="secondary"
                className="w-full"
                onClick={() => navigate(`/safety?patient_id=${id}`)}
              >
                <ShieldCheck className="mr-2 h-4 w-4" />
                Run Safety Check
              </Button>
              <Button
                variant="secondary"
                className="w-full"
                onClick={() =>
                  navigate(
                    `/personalization?patient_id=${id}${
                      patient.conditions[0]
                        ? `&condition=${patient.conditions[0]}`
                        : ''
                    }`,
                  )
                }
              >
                <Sliders className="mr-2 h-4 w-4" />
                Run Personalization
              </Button>
              <Button
                variant="ghost"
                className="w-full"
                onClick={() => navigate(`/patients/${id}/eeg`)}
              >
                <Activity className="mr-2 h-4 w-4" />
                View EEG Reports
              </Button>
            </div>
          </Card>

          {/* Conditions */}
          {patient.conditions.length > 0 && (
            <Card title="Active Conditions">
              <div className="flex flex-wrap gap-2">
                {patient.conditions.map((c) => (
                  <span
                    key={c}
                    className="rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700"
                  >
                    {c.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </Card>
          )}

          {/* Latest assessment highlight */}
          {assessments.length > 0 && (
            <Card title="Latest Assessment">
              {(() => {
                const latest = assessments[0];
                const isHigh =
                  latest.severity_band === 'severe' || latest.severity_band === 'moderate';
                return (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-sozo-text">
                        {latest.abbreviation}
                      </span>
                      <Badge status={severityStatus(latest.severity_band)} />
                    </div>
                    <div className="flex items-end gap-2">
                      <span className="text-3xl font-bold text-sozo-text">
                        {latest.score}
                      </span>
                      {isHigh && (
                        <AlertTriangle className="mb-1 h-5 w-5 text-yellow-500" />
                      )}
                    </div>
                    <p className="text-xs text-gray-400">
                      {format(new Date(latest.assessed_at), 'dd MMM yyyy')}
                    </p>
                  </div>
                );
              })()}
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Trajectory chart (raw SVG) ────────────────────────────────────────────────

interface TrajectoryChartProps {
  points: TrajectoryPoint[];
  scaleName: string;
}

function TrajectoryChart({ points, scaleName }: TrajectoryChartProps) {
  const width = 400;
  const height = 240;
  const padLeft = 40;
  const padRight = 12;
  const padTop = 24;
  const padBottom = 30;
  const innerW = width - padLeft - padRight;
  const innerH = height - padTop - padBottom;

  const scores = points.map((p) => p.score);
  const minScore = Math.min(...scores);
  const maxScore = Math.max(...scores);
  // Avoid zero-range: pad if all equal
  const yMin = minScore === maxScore ? minScore - 1 : minScore;
  const yMax = minScore === maxScore ? maxScore + 1 : maxScore;
  const yRange = yMax - yMin || 1;

  const n = points.length;
  const xFor = (i: number) =>
    padLeft + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW);
  const yFor = (score: number) =>
    padTop + innerH - ((score - yMin) / yRange) * innerH;

  // y-axis ticks (4)
  const yTicks = 4;
  const yTickValues = Array.from({ length: yTicks + 1 }, (_, i) => yMin + (yRange * i) / yTicks);

  // x-axis ticks: 4–6 evenly spaced indices
  const desiredTicks = Math.min(6, Math.max(2, n));
  const xTickIndices =
    n <= desiredTicks
      ? points.map((_, i) => i)
      : Array.from({ length: desiredTicks }, (_, i) =>
          Math.round((i / (desiredTicks - 1)) * (n - 1)),
        );

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xFor(i)} ${yFor(p.score)}`)
    .join(' ');

  return (
    <div className="w-full">
      <p className="mb-2 text-sm font-medium text-sozo-text">{scaleName} over time</p>
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full max-w-[400px]"
        role="img"
        aria-label={`${scaleName} score trajectory`}
      >
        {/* y-axis gridlines + labels */}
        {yTickValues.map((val, i) => {
          const y = yFor(val);
          return (
            <g key={`y-${i}`}>
              <line
                x1={padLeft}
                x2={width - padRight}
                y1={y}
                y2={y}
                className="stroke-gray-200"
                strokeWidth={1}
              />
              <text
                x={padLeft - 6}
                y={y + 3}
                textAnchor="end"
                className="fill-gray-500"
                fontSize={10}
              >
                {Number.isInteger(val) ? val : val.toFixed(1)}
              </text>
            </g>
          );
        })}

        {/* x-axis labels */}
        {xTickIndices.map((idx) => {
          const p = points[idx];
          const x = xFor(idx);
          return (
            <text
              key={`x-${idx}`}
              x={x}
              y={height - padBottom + 16}
              textAnchor="middle"
              className="fill-gray-500"
              fontSize={10}
            >
              {format(parseISO(p.date), 'MMM d')}
            </text>
          );
        })}

        {/* axes baseline */}
        <line
          x1={padLeft}
          x2={width - padRight}
          y1={height - padBottom}
          y2={height - padBottom}
          className="stroke-gray-300"
          strokeWidth={1}
        />
        <line
          x1={padLeft}
          x2={padLeft}
          y1={padTop}
          y2={height - padBottom}
          className="stroke-gray-300"
          strokeWidth={1}
        />

        {/* line */}
        <path
          d={pathD}
          fill="none"
          className="stroke-sozo-primary"
          strokeWidth={2}
          strokeLinejoin="round"
          strokeLinecap="round"
        />

        {/* points */}
        {points.map((p, i) => (
          <circle
            key={`pt-${i}`}
            cx={xFor(i)}
            cy={yFor(p.score)}
            r={3.5}
            className="fill-sozo-primary"
          />
        ))}
      </svg>
    </div>
  );
}
