import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Activity, Brain } from 'lucide-react';
import { getPatient, getPatientEEG } from '../api/patients';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';

// ── EEG report shape (future backend) ────────────────────────────────────────
// When the backend implements GET /api/patients/:id/eeg, records will look
// like this. For now the endpoint stub returns [] so we always show the
// empty state.
interface EEGReport {
  report_id: string;
  date: string;
  type: string;       // e.g. "resting_state", "task_evoked", "sleep"
  findings: string;
  image_url?: string; // optional topomap / spectrogram URL
}

// ── Page ─────────────────────────────────────────────────────────────────────

export default function PatientEEGPage() {
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

  const {
    data: eegReports = [],
    isLoading: eegLoading,
  } = useQuery({
    queryKey: ['patient-eeg', id],
    queryFn: () => getPatientEEG(id!),
    enabled: !!id,
  });

  const reports = eegReports as EEGReport[];

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

  const label =
    patient.external_id ?? (patient.patient_id as string).slice(0, 8).toUpperCase();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate(`/patients/${id}`)}
          className="rounded-md p-2 hover:bg-gray-100"
        >
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-sozo-text">
            EEG Reports — Patient {label}
          </h1>
          <p className="text-sm text-gray-500">
            {patient.demographics.age}y &middot; {patient.demographics.sex}
            {patient.conditions.length > 0 && (
              <> &middot; {patient.conditions.join(', ')}</>
            )}
          </p>
        </div>
        <Button variant="ghost" onClick={() => navigate(`/patients/${id}`)}>
          Back to Patient
        </Button>
      </div>

      {/* EEG content */}
      {eegLoading ? (
        <LoadingSpinner size="lg" className="mt-16" />
      ) : reports.length === 0 ? (
        /* ── Empty state ── */
        <Card>
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 rounded-full bg-gray-100 p-4">
              <Brain className="h-10 w-10 text-gray-400" />
            </div>
            <h3 className="mb-2 text-lg font-semibold text-sozo-text">
              No EEG Data Yet
            </h3>
            <p className="max-w-sm text-sm text-gray-500">
              EEG reports and topomaps will appear here once recordings have been
              uploaded and processed. Contact your system administrator to enable
              EEG data ingestion.
            </p>
            <div className="mt-6 flex gap-3">
              <Button variant="secondary" onClick={() => navigate(`/patients/${id}`)}>
                Back to Patient
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        /* ── Report list ── */
        <div className="space-y-4">
          {reports.map((report) => (
            <Card key={report.report_id}>
              <div className="flex items-start gap-4">
                <div className="rounded-lg bg-sozo-surface p-3">
                  <Activity className="h-6 w-6 text-sozo-primary" />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-sozo-text capitalize">
                      {report.type.replace(/_/g, ' ')}
                    </span>
                    <span className="text-xs text-gray-400">{report.date}</span>
                  </div>
                  <p className="text-sm text-gray-600">{report.findings}</p>
                </div>
              </div>

              {/* Topomap / spectrogram image */}
              {report.image_url && (
                <div className="mt-4 overflow-hidden rounded-md border border-gray-200 bg-gray-50">
                  <img
                    src={report.image_url}
                    alt={`EEG topomap — ${report.type}`}
                    className="max-h-64 w-full object-contain"
                  />
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
