import { useState, type FormEvent } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Shield, Plus, X, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { runSafetyCheck } from '../api/evidence';
import type { SafetyCheckResponse } from '../types';

const MODALITY_OPTIONS = [
  { value: 'tms', label: 'TMS' },
  { value: 'tdcs', label: 'tDCS' },
  { value: 'tps', label: 'TPS' },
  { value: 'tavns', label: 'tAVNS' },
  { value: 'ces', label: 'CES' },
];

export default function SafetyCheckPage() {
  const [age, setAge] = useState(30);
  const [sex, setSex] = useState('male');
  const [medications, setMedications] = useState<string[]>([]);
  const [medInput, setMedInput] = useState('');
  const [medicalHistory, setMedicalHistory] = useState<string[]>([]);
  const [historyInput, setHistoryInput] = useState('');
  const [modalities, setModalities] = useState<string[]>(['tms', 'tdcs']);

  const mutation = useMutation({
    mutationFn: () =>
      runSafetyCheck({
        demographics: { age, sex },
        medications,
        medical_history: medicalHistory,
        modalities: modalities.length > 0 ? modalities : undefined,
      }),
  });

  const result: SafetyCheckResponse | undefined = mutation.data;

  function addMedication() {
    const val = medInput.trim();
    if (val && !medications.includes(val)) {
      setMedications([...medications, val]);
      setMedInput('');
    }
  }

  function removeMedication(med: string) {
    setMedications(medications.filter((m) => m !== med));
  }

  function addHistory() {
    const val = historyInput.trim();
    if (val && !medicalHistory.includes(val)) {
      setMedicalHistory([...medicalHistory, val]);
      setHistoryInput('');
    }
  }

  function removeHistory(item: string) {
    setMedicalHistory(medicalHistory.filter((h) => h !== item));
  }

  function toggleModality(mod: string) {
    setModalities((prev) =>
      prev.includes(mod) ? prev.filter((m) => m !== mod) : [...prev, mod],
    );
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    mutation.mutate();
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <Shield className="h-7 w-7 text-red-600" />
        <h1 className="text-2xl font-bold text-sozo-text">Safety Check</h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Demographics */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-gray-700">
                Age
              </label>
              <input
                id="age"
                type="number"
                min={0}
                max={120}
                required
                value={age}
                onChange={(e) => setAge(Number(e.target.value))}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
              />
            </div>
            <div>
              <label htmlFor="sex" className="block text-sm font-medium text-gray-700">
                Sex
              </label>
              <select
                id="sex"
                value={sex}
                onChange={(e) => setSex(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>
          </div>

          {/* Medications */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medications
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={medInput}
                onChange={(e) => setMedInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addMedication();
                  }
                }}
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
                placeholder="e.g., sertraline, lithium..."
              />
              <Button type="button" size="sm" variant="secondary" onClick={addMedication}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {medications.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {medications.map((med) => (
                  <span
                    key={med}
                    className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700"
                  >
                    {med}
                    <button type="button" onClick={() => removeMedication(med)}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Medical History */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Medical History
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={historyInput}
                onChange={(e) => setHistoryInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addHistory();
                  }
                }}
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
                placeholder="e.g., epilepsy, metallic_implant_near_coil..."
              />
              <Button type="button" size="sm" variant="secondary" onClick={addHistory}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {medicalHistory.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {medicalHistory.map((item) => (
                  <span
                    key={item}
                    className="inline-flex items-center gap-1 rounded-full bg-purple-50 px-3 py-1 text-xs font-medium text-purple-700"
                  >
                    {item}
                    <button type="button" onClick={() => removeHistory(item)}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Target Modalities */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Modalities
            </label>
            <div className="flex flex-wrap gap-3">
              {MODALITY_OPTIONS.map((opt) => (
                <label
                  key={opt.value}
                  className={`inline-flex cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-sm transition-colors ${
                    modalities.includes(opt.value)
                      ? 'border-sozo-primary bg-sozo-primary/5 text-sozo-primary'
                      : 'border-gray-300 text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={modalities.includes(opt.value)}
                    onChange={() => toggleModality(opt.value)}
                    className="sr-only"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </div>

          {mutation.isError && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              Safety check failed. The API may not be available or the request was invalid.
            </div>
          )}

          <Button type="submit" isLoading={mutation.isPending}>
            <Shield className="mr-2 h-4 w-4" />
            Run Safety Check
          </Button>
        </form>
      </Card>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Clearance status */}
          <Card>
            <div className="flex items-center gap-4">
              {result.safety_cleared ? (
                <>
                  <div className="rounded-full bg-green-100 p-3">
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-green-700">Safety Cleared</p>
                    <p className="text-sm text-gray-500">No blocking contraindications found.</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="rounded-full bg-red-100 p-3">
                    <XCircle className="h-8 w-8 text-red-600" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-red-700">Safety Blocked</p>
                    <p className="text-sm text-gray-500">
                      Contraindications detected. Review findings below.
                    </p>
                  </div>
                </>
              )}
            </div>
          </Card>

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <Card title="Warnings">
              <div className="space-y-2">
                {result.warnings.map((w, i) => (
                  <div key={i} className="flex items-start gap-2 rounded-md bg-yellow-50 p-3">
                    <AlertTriangle className="mt-0.5 h-4 w-4 flex-shrink-0 text-yellow-600" />
                    <p className="text-sm text-yellow-800">{w}</p>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Contraindications */}
          {result.absolute_contraindications.length > 0 && (
            <Card title="Absolute Contraindications">
              <ul className="space-y-1">
                {result.absolute_contraindications.map((c, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span className="text-red-700">{c}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {result.relative_contraindications.length > 0 && (
            <Card title="Relative Contraindications">
              <ul className="space-y-1">
                {result.relative_contraindications.map((c, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <AlertTriangle className="h-4 w-4 text-yellow-500" />
                    <span className="text-yellow-700">{c}</span>
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Modality clearance grid */}
          {result.modality_clearance && Object.keys(result.modality_clearance).length > 0 && (
            <Card title="Modality Clearance">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
                {Object.entries(result.modality_clearance).map(([mod, status]) => {
                  const cleared = status === true || status === 'cleared';
                  return (
                    <div
                      key={mod}
                      className={`flex items-center justify-between rounded-lg border p-3 ${
                        cleared ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                      }`}
                    >
                      <span className="font-medium text-sm uppercase">{mod}</span>
                      {cleared ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                  );
                })}
              </div>
            </Card>
          )}

          {/* Medication summary */}
          {result.medication_summary && (
            <Card title="Medication Summary">
              <p className="text-sm text-gray-700">{result.medication_summary}</p>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
