import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Download, ImageOff } from 'lucide-react';
import { listVisualsLibrary } from '../api/visuals';
import type { VisualItem } from '../api/visuals';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const ALL_CONDITIONS = [
  { slug: '', label: 'All Conditions' },
  { slug: 'adhd', label: 'ADHD' },
  { slug: 'alzheimers', label: "Alzheimer's" },
  { slug: 'anxiety', label: 'Anxiety' },
  { slug: 'asd', label: 'ASD' },
  { slug: 'ces_alphastem', label: 'CES / AlphaStem' },
  { slug: 'chronic_pain', label: 'Chronic Pain' },
  { slug: 'depression', label: 'Depression' },
  { slug: 'dystonia', label: 'Dystonia' },
  { slug: 'epilepsy', label: 'Epilepsy' },
  { slug: 'essential_tremor', label: 'Essential Tremor' },
  { slug: 'fibromyalgia', label: 'Fibromyalgia' },
  { slug: 'home_tdcs_mdd_anxiety', label: 'Home tDCS (MDD/Anxiety)' },
  { slug: 'insomnia', label: 'Insomnia' },
  { slug: 'long_covid', label: 'Long COVID' },
  { slug: 'mild_cognitive_impairment', label: 'Mild Cognitive Impairment' },
  { slug: 'ms', label: 'Multiple Sclerosis' },
  { slug: 'neuroonica_combo', label: 'Neuroonica Combo' },
  { slug: 'ocd', label: 'OCD' },
  { slug: 'parkinsons', label: "Parkinson's" },
  { slug: 'ptsd', label: 'PTSD' },
  { slug: 'schizophrenia', label: 'Schizophrenia' },
  { slug: 'shared', label: 'Shared / Legend' },
  { slug: 'stroke_rehab', label: 'Stroke Rehab' },
  { slug: 'tbi', label: 'TBI' },
  { slug: 'tinnitus', label: 'Tinnitus' },
  { slug: 'trd_vns', label: 'TRD / VNS' },
  { slug: 'tvns', label: 'tVNS' },
];

const VISUAL_TYPES = [
  { value: '', label: 'All Types' },
  { value: 'brain_map', label: 'Brain Map' },
  { value: 'network_diagram', label: 'Network Diagram' },
  { value: 'symptom_flow', label: 'Symptom Flow' },
  { value: 'patient_journey', label: 'Patient Journey' },
];

const TYPE_BADGE_COLORS: Record<string, string> = {
  brain_map: 'bg-purple-100 text-purple-700',
  network_diagram: 'bg-blue-100 text-blue-700',
  symptom_flow: 'bg-orange-100 text-orange-700',
  patient_journey: 'bg-green-100 text-green-700',
};

function VisualCard({ item }: { item: VisualItem }) {
  const [imgError, setImgError] = useState(false);
  const badgeClass = TYPE_BADGE_COLORS[item.visual_type] ?? 'bg-gray-100 text-gray-600';

  const handleDownload = () => {
    const anchor = document.createElement('a');
    anchor.href = item.url;
    anchor.download = item.filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
  };

  return (
    <div className="flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm transition-shadow hover:shadow-md">
      {/* Image area */}
      <div className="flex h-44 items-center justify-center overflow-hidden bg-gray-50">
        {imgError ? (
          <div className="flex flex-col items-center gap-2 text-gray-400">
            <ImageOff className="h-8 w-8" />
            <span className="text-xs">Image unavailable</span>
          </div>
        ) : (
          <img
            src={item.url}
            alt={item.filename}
            className="h-full w-full object-contain p-2"
            onError={() => setImgError(true)}
            loading="lazy"
          />
        )}
      </div>

      {/* Info + action */}
      <div className="flex flex-1 flex-col gap-2 p-3">
        <p className="text-sm font-medium text-sozo-text leading-tight">{item.condition_name}</p>
        <div className="flex items-center justify-between">
          <span className={`rounded px-2 py-0.5 text-xs font-medium ${badgeClass}`}>
            {item.visual_type_label}
          </span>
          <button
            onClick={handleDownload}
            title="Download PNG"
            className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-sozo-primary transition-colors"
          >
            <Download className="h-4 w-4" />
          </button>
        </div>
        <p className="truncate text-xs text-gray-400" title={item.filename}>
          {item.filename}
        </p>
      </div>
    </div>
  );
}

export default function VisualsPage() {
  const [conditionFilter, setConditionFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['visuals-library', conditionFilter, typeFilter],
    queryFn: () => listVisualsLibrary(conditionFilter || undefined, typeFilter || undefined),
  });

  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-sozo-text">Clinical Visuals Library</h1>
        <p className="mt-1 text-sm text-gray-500">
          Pre-rendered brain maps, network diagrams, symptom flows, and patient journeys
          across all neuromodulation conditions.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={conditionFilter}
          onChange={(e) => setConditionFilter(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sozo-primary"
        >
          {ALL_CONDITIONS.map((c) => (
            <option key={c.slug} value={c.slug}>
              {c.label}
            </option>
          ))}
        </select>

        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sozo-primary"
        >
          {VISUAL_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>

        {(conditionFilter || typeFilter) && (
          <button
            onClick={() => { setConditionFilter(''); setTypeFilter(''); }}
            className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 focus:outline-none"
          >
            Clear filters
          </button>
        )}

        {data && (
          <span className="flex items-center text-sm text-gray-500">
            {data.total} visual{data.total !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Content */}
      {isLoading && <LoadingSpinner size="lg" className="mt-16" />}

      {error && (
        <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-600">
          Failed to load visuals. The server may be unavailable.
        </div>
      )}

      {!isLoading && !error && items.length === 0 && (
        <div className="flex flex-col items-center justify-center py-24 text-gray-400">
          <ImageOff className="mb-3 h-12 w-12" />
          <p className="text-base font-medium">No visuals found</p>
          <p className="mt-1 text-sm">Try changing the condition or type filter.</p>
        </div>
      )}

      {!isLoading && !error && items.length > 0 && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
          {items.map((item) => (
            <VisualCard key={`${item.condition}-${item.filename}`} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
