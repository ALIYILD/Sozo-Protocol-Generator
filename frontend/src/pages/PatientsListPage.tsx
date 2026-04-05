import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, Search, X } from 'lucide-react';
import { listPatients, createPatient, type PatientListItem } from '../api/patients';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import { format } from 'date-fns';

// ── New Patient Modal ─────────────────────────────────────────────────────────

interface NewPatientModalProps {
  onClose: () => void;
  onCreated: (id: string) => void;
}

function NewPatientModal({ onClose, onCreated }: NewPatientModalProps) {
  const queryClient = useQueryClient();
  const [externalId, setExternalId] = useState('');
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('male');
  const [conditionInput, setConditionInput] = useState('');
  const [notes, setNotes] = useState('');
  const [validationError, setValidationError] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: createPatient,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      onCreated(data.patient_id as string);
    },
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const ageNum = parseInt(age, 10);
    if (!age || isNaN(ageNum) || ageNum < 0 || ageNum > 120) {
      setValidationError('Age must be a number between 0 and 120.');
      return;
    }
    setValidationError(null);
    mutation.mutate({
      external_id: externalId || undefined,
      demographics: { age: ageNum, sex, handedness: 'right' },
      conditions: conditionInput
        ? conditionInput.split(',').map((s) => s.trim()).filter(Boolean)
        : [],
      notes: notes || undefined,
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-lg border border-gray-200 bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-sozo-text">New Patient</h2>
          <button onClick={onClose} className="rounded p-1 hover:bg-gray-100">
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4 px-6 py-5">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              External / Chart ID <span className="text-gray-400">(optional)</span>
            </label>
            <input
              type="text"
              value={externalId}
              onChange={(e) => setExternalId(e.target.value)}
              placeholder="e.g. PT-0042"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Age</label>
              <input
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                min={0}
                max={120}
                required
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Sex</label>
              <select
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Conditions <span className="text-gray-400">(comma-separated slugs)</span>
            </label>
            <input
              type="text"
              value={conditionInput}
              onChange={(e) => setConditionInput(e.target.value)}
              placeholder="e.g. mdd, ptsd"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Notes <span className="text-gray-400">(optional)</span>
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={2}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
            />
          </div>

          {(validationError || mutation.error) && (
            <p className="text-sm text-red-600">
              {validationError ?? 'Failed to create patient. Please try again.'}
            </p>
          )}

          <div className="flex justify-end gap-3 pt-1">
            <Button variant="ghost" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" isLoading={mutation.isPending}>
              Create Patient
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function PatientsListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [conditionFilter, setConditionFilter] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['patients', search, conditionFilter],
    queryFn: () =>
      listPatients({
        search: search || undefined,
        condition: conditionFilter || undefined,
      }),
  });

  const columns: Column<PatientListItem & Record<string, unknown>>[] = [
    {
      key: 'external_id',
      header: 'Patient ID',
      render: (row) => (
        <span className="font-mono text-xs text-sozo-text">
          {(row.external_id as string) ?? (row.patient_id as string).slice(0, 8)}
        </span>
      ),
    },
    {
      key: 'conditions',
      header: 'Conditions',
      render: (row) => {
        const conds = row.conditions as string[];
        if (!conds || conds.length === 0)
          return <span className="text-gray-400 text-xs">—</span>;
        return (
          <div className="flex flex-wrap gap-1">
            {conds.map((c) => (
              <span
                key={c}
                className="rounded bg-sozo-surface px-1.5 py-0.5 text-xs font-medium text-sozo-text"
              >
                {c.toUpperCase()}
              </span>
            ))}
          </div>
        );
      },
    },
    {
      key: 'demographics',
      header: 'Demographics',
      render: (row) => {
        const demo = row.demographics as { age: number; sex: string };
        return (
          <span className="text-sm text-gray-600">
            {demo?.age}y &middot; {demo?.sex}
          </span>
        );
      },
    },
    {
      key: 'assessments_count',
      header: 'Assessments',
      render: (row) => (
        <span className="text-sm text-gray-700">{row.assessments_count as number}</span>
      ),
    },
    {
      key: 'active_protocols',
      header: 'Status',
      render: (row) => (
        <Badge
          status={(row.active_protocols as number) > 0 ? 'approved' : 'draft'}
        />
      ),
    },
    {
      key: 'created_at',
      header: 'Enrolled',
      sortable: true,
      render: (row) => {
        const d = row.created_at as string;
        return d ? format(new Date(d), 'dd MMM yyyy') : '—';
      },
    },
  ];

  if (isLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  if (error) {
    return (
      <div className="mt-20 text-center">
        <p className="text-red-600">Failed to load patients.</p>
        <p className="text-sm text-gray-500 mt-1">Please check that the API is running.</p>
      </div>
    );
  }

  const patients = (data?.patients ?? []) as (PatientListItem & Record<string, unknown>)[];

  return (
    <>
      {showNewModal && (
        <NewPatientModal
          onClose={() => setShowNewModal(false)}
          onCreated={(id) => {
            setShowNewModal(false);
            navigate(`/patients/${id}`);
          }}
        />
      )}

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-sozo-text">Patients</h1>
          <Button onClick={() => setShowNewModal(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Patient
          </Button>
        </div>

        {/* Filters */}
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by ID or notes…"
              className="w-full rounded-md border border-gray-300 py-2 pl-9 pr-3 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
            />
          </div>
          <input
            type="text"
            value={conditionFilter}
            onChange={(e) => setConditionFilter(e.target.value)}
            placeholder="Filter by condition slug…"
            className="w-56 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-sozo-primary focus:outline-none focus:ring-1 focus:ring-sozo-primary"
          />
        </div>

        <Card>
          <Table
            columns={columns}
            data={patients}
            keyExtractor={(row) => row.patient_id as string}
            onRowClick={(row) => navigate(`/patients/${row.patient_id}`)}
            emptyMessage="No patients found. Add your first patient to get started."
          />
        </Card>

        {data && data.pages > 1 && (
          <div className="flex justify-center">
            <p className="text-sm text-gray-500">
              Page {data.page} of {data.pages} ({data.total} total)
            </p>
          </div>
        )}
      </div>
    </>
  );
}
