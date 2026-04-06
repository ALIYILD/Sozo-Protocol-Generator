import { useState, type FormEvent } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileUp, Download } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { listConditions } from '../api/evidence';

const DOC_TYPE_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'Infer from template filename (default)' },
  { value: 'evidence_based_protocol', label: 'Evidence-based protocol' },
  { value: 'clinical_exam', label: 'Clinical exam' },
  { value: 'network_assessment', label: 'Network assessment' },
  { value: 'handbook', label: 'Handbook' },
  { value: 'all_in_one_protocol', label: 'All-in-one protocol' },
  { value: 'phenotype_classification', label: 'Phenotype classification' },
  { value: 'responder_tracking', label: 'Responder tracking' },
  { value: 'psych_intake', label: 'Psych intake' },
];

const TIER_OPTIONS = [
  { value: 'fellow', label: 'Fellow' },
  { value: 'partners', label: 'Partners' },
  { value: 'both', label: 'Both (Fellow + Partners)' },
];

export default function TemplateBatchPage() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedSlugs, setSelectedSlugs] = useState<string[]>([]);
  const [tier, setTier] = useState('fellow');
  const [docType, setDocType] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const { data: conditions, isLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  });

  const toggleSlug = (slug: string) => {
    setSelectedSlugs((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug],
    );
  };

  const selectAll = () => {
    if (!conditions?.length) return;
    setSelectedSlugs(conditions.map((c) => c.slug));
  };

  const clearSlugs = () => setSelectedSlugs([]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setStatus(null);
    if (!file) {
      setError('Choose a .docx template.');
      return;
    }
    if (!file.name.toLowerCase().endsWith('.docx')) {
      setError('File must be a .docx document.');
      return;
    }
    if (selectedSlugs.length === 0) {
      setError('Select at least one condition.');
      return;
    }

    const token = localStorage.getItem('sozo_token');
    if (!token) {
      setError('Not signed in.');
      return;
    }

    const form = new FormData();
    form.append('template', file);
    form.append('condition_slugs', selectedSlugs.join(','));
    form.append('tier', tier);
    if (docType) form.append('document_type', docType);

    setBusy(true);
    try {
      const res = await fetch('/api/generate/template-batch', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: form,
      });
      if (!res.ok) {
        let detail = `Request failed (${res.status})`;
        try {
          const j = await res.json();
          if (typeof j?.detail === 'string') detail = j.detail;
        } catch {
          /* use generic */
        }
        setError(detail);
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'sozo_template_batch.zip';
      a.click();
      URL.revokeObjectURL(url);
      setStatus(`Downloaded ZIP with ${selectedSlugs.length} condition(s).`);
    } catch {
      setError('Network error — could not reach the API.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-4 md:p-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Generate from template
        </h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Upload a gold-standard DOCX (Heading styles), select conditions and tier, then download a
          ZIP of rendered documents. Page size and margins match your template; content comes from
          the condition registry (same pipeline as the ops Streamlit tool).
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
            <FileUp className="h-5 w-5" />
            Template (.docx)
          </h2>
          <input
            type="file"
            accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            className="mt-4 block w-full text-sm text-gray-600 dark:text-gray-400 file:mr-4 file:rounded-md file:border-0 file:bg-sozo-primary file:px-4 file:py-2 file:text-sm file:font-medium file:text-white"
            onChange={(ev) => setFile(ev.target.files?.[0] ?? null)}
          />
        </Card>

        <Card className="p-6">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Conditions</h2>
            <div className="flex gap-2">
              <Button type="button" variant="secondary" onClick={selectAll} disabled={isLoading}>
                Select all
              </Button>
              <Button type="button" variant="secondary" onClick={clearSlugs}>
                Clear
              </Button>
            </div>
          </div>
          {isLoading ? (
            <div className="mt-4 flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : (
            <div className="mt-4 grid max-h-64 grid-cols-1 gap-2 overflow-y-auto sm:grid-cols-2">
              {conditions?.map((c) => (
                <label
                  key={c.slug}
                  className="flex cursor-pointer items-center gap-2 rounded-md border border-gray-200 px-3 py-2 text-sm dark:border-gray-700"
                >
                  <input
                    type="checkbox"
                    checked={selectedSlugs.includes(c.slug)}
                    onChange={() => toggleSlug(c.slug)}
                  />
                  <span className="text-gray-800 dark:text-gray-200">{c.display_name}</span>
                </label>
              ))}
            </div>
          )}
        </Card>

        <Card className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Tier
            </label>
            <select
              value={tier}
              onChange={(e) => setTier(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900"
            >
              {TIER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Document type
            </label>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-900"
            >
              {DOC_TYPE_OPTIONS.map((o) => (
                <option key={o.value || 'infer'} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </Card>

        {error && (
          <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-800 dark:bg-red-950 dark:text-red-200">
            {error}
          </div>
        )}
        {status && (
          <div className="rounded-md bg-green-50 px-4 py-3 text-sm text-green-800 dark:bg-green-950 dark:text-green-200 flex items-center gap-2">
            <Download className="h-4 w-4 shrink-0" />
            {status}
          </div>
        )}

        <Button type="submit" isLoading={busy} className="w-full sm:w-auto">
          Generate & download ZIP
        </Button>
      </form>
    </div>
  );
}
