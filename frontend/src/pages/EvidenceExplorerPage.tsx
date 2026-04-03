import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, RefreshCw } from 'lucide-react';
import Card from '../components/ui/Card';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { getStalenessReport, getCondition } from '../api/evidence';
import type { StalenessCondition } from '../types';

export default function EvidenceExplorerPage() {
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const { data: staleness, isLoading, error } = useQuery({
    queryKey: ['staleness'],
    queryFn: getStalenessReport,
  });

  const { data: conditionDetail, isLoading: detailLoading } = useQuery({
    queryKey: ['condition', selectedSlug],
    queryFn: () => getCondition(selectedSlug!),
    enabled: !!selectedSlug,
  });

  const freshnessStyles = (freshness: string) => {
    switch (freshness) {
      case 'fresh':
        return {
          bg: 'bg-green-50 border-green-200',
          text: 'text-green-700',
          dot: 'bg-green-500',
        };
      case 'aging':
        return {
          bg: 'bg-yellow-50 border-yellow-200',
          text: 'text-yellow-700',
          dot: 'bg-yellow-500',
        };
      case 'stale':
        return {
          bg: 'bg-orange-50 border-orange-200',
          text: 'text-orange-700',
          dot: 'bg-orange-500',
        };
      case 'expired':
        return {
          bg: 'bg-red-50 border-red-200',
          text: 'text-red-700',
          dot: 'bg-red-500',
        };
      default:
        return {
          bg: 'bg-gray-50 border-gray-200',
          text: 'text-gray-700',
          dot: 'bg-gray-500',
        };
    }
  };

  if (isLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  if (error) {
    return (
      <div className="mt-20 text-center">
        <p className="text-red-600">Failed to load evidence data.</p>
        <p className="text-sm text-gray-500 mt-1">The staleness endpoint may not be available.</p>
      </div>
    );
  }

  const conditions = staleness?.conditions ?? [];
  const filtered = searchQuery
    ? conditions.filter(
        (c) =>
          c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.slug.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : conditions;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-sozo-text">Evidence Explorer</h1>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search conditions..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="rounded-md border border-gray-300 py-2 pl-10 pr-4 text-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
          />
        </div>
      </div>

      {/* Overall health summary */}
      {staleness && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-500">Overall</p>
              <p className="text-lg font-bold capitalize text-sozo-text">
                {staleness.overall_health}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-500">Fresh</p>
              <p className="text-2xl font-bold text-green-600">{staleness.fresh}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-500">Aging</p>
              <p className="text-2xl font-bold text-yellow-600">{staleness.aging}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-500">Stale</p>
              <p className="text-2xl font-bold text-orange-600">{staleness.stale}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-500">Expired</p>
              <p className="text-2xl font-bold text-red-600">{staleness.expired}</p>
            </div>
          </Card>
        </div>
      )}

      {/* High priority refreshes */}
      {staleness && staleness.high_priority_refreshes.length > 0 && (
        <Card title="High Priority Refreshes">
          <div className="flex flex-wrap gap-2">
            {staleness.high_priority_refreshes.map((slug) => (
              <span
                key={slug}
                className="inline-flex items-center gap-1 rounded-full bg-red-50 px-3 py-1 text-xs font-medium text-red-700"
              >
                <RefreshCw className="h-3 w-3" />
                {slug.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Condition list */}
        <div className="lg:col-span-1 space-y-2">
          <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wider px-1">
            Conditions ({filtered.length})
          </h2>
          <div className="space-y-2 max-h-[600px] overflow-y-auto">
            {filtered.length === 0 && (
              <p className="text-sm text-gray-500 px-1">No conditions found.</p>
            )}
            {filtered.map((c: StalenessCondition) => {
              const styles = freshnessStyles(c.freshness);
              const isSelected = selectedSlug === c.slug;
              return (
                <button
                  key={c.slug}
                  onClick={() => setSelectedSlug(c.slug)}
                  className={`w-full text-left rounded-lg border p-3 transition-all ${
                    isSelected
                      ? 'border-sozo-primary bg-sozo-primary/5 ring-1 ring-sozo-primary'
                      : `${styles.bg} hover:shadow-sm`
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm text-sozo-text">{c.name}</span>
                    <div className="flex items-center gap-1.5">
                      <span className={`h-2 w-2 rounded-full ${styles.dot}`} />
                      <span className={`text-xs font-medium capitalize ${styles.text}`}>
                        {c.freshness}
                      </span>
                    </div>
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-gray-500">
                    <span>{c.days_since_search}d since search</span>
                    <span>Evidence: {c.evidence_level}</span>
                    {c.needs_refresh && (
                      <span className="text-orange-600 font-medium">Needs refresh</span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Detail panel */}
        <div className="lg:col-span-2">
          {selectedSlug ? (
            detailLoading ? (
              <LoadingSpinner size="lg" className="mt-10" />
            ) : conditionDetail ? (
              <Card title={String((conditionDetail as Record<string, unknown>).display_name ?? selectedSlug)}>
                <div className="space-y-4">
                  {/* Summary fields */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {(conditionDetail as Record<string, unknown>).icd10 != null && (
                      <div>
                        <p className="text-gray-500">ICD-10</p>
                        <p className="font-medium">
                          {String((conditionDetail as Record<string, unknown>).icd10)}
                        </p>
                      </div>
                    )}
                    {(conditionDetail as Record<string, unknown>).category != null && (
                      <div>
                        <p className="text-gray-500">Category</p>
                        <p className="font-medium">
                          {String((conditionDetail as Record<string, unknown>).category)}
                        </p>
                      </div>
                    )}
                  </div>
                  {/* Full JSON */}
                  <details className="mt-4">
                    <summary className="cursor-pointer text-sm font-medium text-gray-500 hover:text-gray-700">
                      View full knowledge data
                    </summary>
                    <pre className="mt-2 max-h-[500px] overflow-auto rounded-md bg-gray-50 p-4 text-xs text-gray-700">
                      {JSON.stringify(conditionDetail, null, 2)}
                    </pre>
                  </details>
                </div>
              </Card>
            ) : (
              <Card>
                <p className="text-sm text-gray-500">Could not load condition details.</p>
              </Card>
            )
          ) : (
            <Card>
              <div className="text-center py-12">
                <Search className="mx-auto h-12 w-12 text-gray-300" />
                <p className="mt-4 text-sm text-gray-500">
                  Select a condition from the list to view its knowledge detail and evidence freshness.
                </p>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
