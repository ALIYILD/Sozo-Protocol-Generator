import { useState, type FormEvent } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Sliders, Plus, X } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { listConditions, runPersonalization } from '../api/evidence';
import type { PersonalizationResponse } from '../types';

export default function PersonalizationPage() {
  const [conditionSlug, setConditionSlug] = useState('');
  const [age, setAge] = useState(35);
  const [sex, setSex] = useState('male');

  // Symptoms as name+score pairs
  const [symptoms, setSymptoms] = useState<Array<{ name: string; score: number }>>([]);
  const [symptomName, setSymptomName] = useState('');
  const [symptomScore, setSymptomScore] = useState(5);

  // Medications
  const [medications, setMedications] = useState<string[]>([]);
  const [medInput, setMedInput] = useState('');

  // Medical history
  const [medicalHistory, setMedicalHistory] = useState<string[]>([]);
  const [historyInput, setHistoryInput] = useState('');

  const { data: conditions, isLoading: conditionsLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  });

  const mutation = useMutation({
    mutationFn: () =>
      runPersonalization({
        condition_slug: conditionSlug,
        demographics: { age, sex },
        symptoms,
        medications,
        treatment_history: [],
        medical_history: medicalHistory,
      }),
  });

  const result: PersonalizationResponse | undefined = mutation.data;

  function addSymptom() {
    const name = symptomName.trim();
    if (name && !symptoms.some((s) => s.name === name)) {
      setSymptoms([...symptoms, { name, score: symptomScore }]);
      setSymptomName('');
      setSymptomScore(5);
    }
  }

  function removeSymptom(name: string) {
    setSymptoms(symptoms.filter((s) => s.name !== name));
  }

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

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!conditionSlug) return;
    mutation.mutate();
  }

  if (conditionsLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <Sliders className="h-7 w-7 text-indigo-600" />
        <h1 className="text-2xl font-bold text-sozo-text">Personalization</h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Condition */}
          <div>
            <label htmlFor="condition" className="block text-sm font-medium text-gray-700">
              Condition
            </label>
            <select
              id="condition"
              required
              value={conditionSlug}
              onChange={(e) => setConditionSlug(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
            >
              <option value="">Select a condition...</option>
              {(conditions ?? []).map((c) => (
                <option key={c.slug} value={c.slug}>
                  {c.display_name} ({c.icd10})
                </option>
              ))}
            </select>
          </div>

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

          {/* Symptom Scores */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Symptom Scores
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={symptomName}
                onChange={(e) => setSymptomName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addSymptom();
                  }
                }}
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
                placeholder="Symptom name (e.g., depression)"
              />
              <input
                type="number"
                min={0}
                max={100}
                value={symptomScore}
                onChange={(e) => setSymptomScore(Number(e.target.value))}
                className="w-20 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
                placeholder="Score"
              />
              <Button type="button" size="sm" variant="secondary" onClick={addSymptom}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {symptoms.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {symptoms.map((s) => (
                  <span
                    key={s.name}
                    className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700"
                  >
                    {s.name}: {s.score}
                    <button type="button" onClick={() => removeSymptom(s.name)}>
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
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
                placeholder="e.g., sertraline"
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
                placeholder="e.g., epilepsy, hypertension"
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

          {mutation.isError && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              Personalization failed. The engine may not be available or the request was invalid.
            </div>
          )}

          <Button type="submit" isLoading={mutation.isPending} disabled={!conditionSlug}>
            <Sliders className="mr-2 h-4 w-4" />
            Run Personalization
          </Button>
        </form>
      </Card>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Safety status */}
          <Card>
            <div className="flex items-center gap-3">
              <Badge status={result.safety_cleared ? 'approved' : 'rejected'} />
              <span className="text-sm text-gray-600">
                {result.safety_cleared
                  ? 'Safety cleared for personalization'
                  : 'Safety concerns detected'}
              </span>
            </div>
          </Card>

          {/* Confidence score */}
          <Card title="Confidence">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">
                  Confidence Score
                </span>
                <span className="text-lg font-bold text-sozo-text">
                  {Math.round(result.confidence_score * 100)}%
                </span>
              </div>
              <div className="h-3 w-full rounded-full bg-gray-200">
                <div
                  className={`h-3 rounded-full transition-all duration-700 ${
                    result.confidence_score >= 0.7
                      ? 'bg-green-500'
                      : result.confidence_score >= 0.4
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.round(result.confidence_score * 100)}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 capitalize">
                Band: {result.confidence_band}
              </p>
              {result.matched_phenotype && (
                <p className="text-sm text-gray-600">
                  Matched phenotype: <span className="font-medium">{result.matched_phenotype}</span>
                </p>
              )}
            </div>
          </Card>

          {/* Recommended protocol */}
          {result.recommended_protocol && (
            <Card title="Recommended Protocol">
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Modality</p>
                    <p className="font-medium uppercase">{result.recommended_protocol.modality}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Target</p>
                    <p className="font-medium">{result.recommended_protocol.target}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Evidence Level</p>
                    <Badge status={result.recommended_protocol.evidence_level} />
                  </div>
                  <div>
                    <p className="text-gray-500">Score</p>
                    <p className="font-medium">{result.recommended_protocol.score.toFixed(2)}</p>
                  </div>
                </div>

                {result.recommended_protocol.rationale && (
                  <div>
                    <p className="text-sm font-medium text-gray-500">Rationale</p>
                    <p className="mt-1 text-sm text-gray-700">
                      {result.recommended_protocol.rationale}
                    </p>
                  </div>
                )}

                {Object.keys(result.recommended_protocol.parameters).length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-gray-500 mb-2">Parameters</p>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries(result.recommended_protocol.parameters).map(([key, val]) => (
                        <div key={key} className="rounded bg-gray-50 px-3 py-2">
                          <p className="text-gray-500 text-xs">{key.replace(/_/g, ' ')}</p>
                          <p className="font-medium">{String(val)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Explanation */}
          {result.explanation && (
            <Card title="Explanation">
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{result.explanation}</p>
            </Card>
          )}

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <Card title="Warnings">
              <ul className="space-y-2">
                {result.warnings.map((w, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-yellow-800 bg-yellow-50 rounded-md p-2">
                    <span className="text-yellow-600 mt-0.5">!</span>
                    {w}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Blocked modalities */}
          {result.blocked_modalities.length > 0 && (
            <Card title="Blocked Modalities">
              <div className="flex flex-wrap gap-2">
                {result.blocked_modalities.map((mod) => (
                  <span
                    key={mod}
                    className="rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-700 uppercase"
                  >
                    {mod}
                  </span>
                ))}
              </div>
            </Card>
          )}

          {/* Stats */}
          <Card>
            <p className="text-xs text-gray-500">
              {result.ranked_protocols_count} protocol(s) evaluated
            </p>
          </Card>
        </div>
      )}
    </div>
  );
}
