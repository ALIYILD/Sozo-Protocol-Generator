import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  ArrowLeft,
  ShieldCheck,
  Sliders,
  Activity,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';
import {
  getPatient,
  getPatientAssessments,
  getPatientTreatments,
  getPatientMedications,
} from '../api/patients';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import type { TreatmentRecord, AssessmentRecord, MedicationRecord } from '../api/patients';
import { format } from 'date-fns';

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

export default function PatientDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const {
    data: patient,
    isLoading: patientLoading,
    error: patientError,
  } = useQuery({
    queryKey: ['patient', id],
    queryFn: () => getPatient(id!),
    enabled: !!id,
  });

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
      </div>

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
                    className="flex items-start justify-between py-3"
                  >
                    <div>
                      <p className="text-sm font-medium text-sozo-text">{med.name}</p>
                      <p className="text-xs text-gray-500">
                        {med.drug_class}{med.dose ? ` · ${med.dose}` : ''}
                      </p>
                    </div>
                    <span className="text-xs text-gray-400">
                      since {format(new Date(med.start_date), 'dd MMM yyyy')}
                    </span>
                  </div>
                ))}
              </div>
            )}
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
