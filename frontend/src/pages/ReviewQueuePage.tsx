import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { format, parseISO } from 'date-fns';
import { ClipboardList } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import EmptyState from '../components/ui/EmptyState';
import {
  getReviewQueue,
  getReviewQueueCount,
  type ReviewQueueItem,
} from '../api/reviews';

const PAGE_SIZE = 20;

type PriorityFilter = '' | 'normal' | 'high';

function formatSubmitted(iso: string): string {
  try {
    return format(parseISO(iso), 'dd MMM yyyy HH:mm');
  } catch {
    return iso;
  }
}

export default function ReviewQueuePage() {
  const [page, setPage] = useState(1);
  const [priority, setPriority] = useState<PriorityFilter>('');

  const {
    data: queue,
    isLoading,
    error,
    isFetching,
  } = useQuery({
    queryKey: ['review-queue', page, PAGE_SIZE, priority],
    queryFn: () => getReviewQueue(page, PAGE_SIZE, undefined, priority || undefined),
  });

  const { data: countData } = useQuery({
    queryKey: ['review-queue-count'],
    queryFn: getReviewQueueCount,
  });

  const columns: Column<ReviewQueueItem & Record<string, unknown>>[] = [
    {
      key: 'condition_name',
      header: 'Condition',
      sortable: true,
      render: (row) => (
        <Link
          to={`/reviews/${row.protocol_id}`}
          className="font-medium text-sozo-primary hover:underline"
        >
          {row.condition_name}
        </Link>
      ),
    },
    {
      key: 'modality',
      header: 'Modality',
      render: (row) => (
        <span className="uppercase text-xs font-medium text-gray-600">
          {row.modality}
        </span>
      ),
    },
    { key: 'version', header: 'Version', sortable: true },
    {
      key: 'evidence_level',
      header: 'Evidence',
      render: (row) => (
        <span className="text-xs text-gray-700">{row.evidence_level}</span>
      ),
    },
    {
      key: 'qa_issues_count',
      header: 'QA issues',
      sortable: true,
      render: (row) => (
        <span
          className={
            row.qa_issues_count > 0
              ? 'font-semibold text-yellow-700'
              : 'text-gray-500'
          }
        >
          {row.qa_issues_count}
        </span>
      ),
    },
    {
      key: 'priority',
      header: 'Priority',
      render: (row) => <Badge status={row.priority} />,
    },
    {
      key: 'submitted_by',
      header: 'Submitted by',
      render: (row) => (
        <span className="text-xs text-gray-600">{row.submitted_by}</span>
      ),
    },
    {
      key: 'submitted_at',
      header: 'Submitted',
      sortable: true,
      render: (row) => (
        <span className="text-xs text-gray-600">
          {formatSubmitted(row.submitted_at)}
        </span>
      ),
    },
  ];

  const total = queue?.total ?? 0;
  const pageSize = queue?.page_size ?? PAGE_SIZE;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-sozo-text">Review queue</h1>
          <p className="text-sm text-gray-500 mt-1">
            Protocols awaiting clinician review. High-priority items carry
            safety or QA flags.
          </p>
        </div>
        {countData && (
          <div className="flex items-center gap-3">
            <div className="rounded-md border border-gray-200 bg-white px-3 py-2 text-sm">
              <span className="font-semibold text-sozo-text">
                {countData.pending}
              </span>
              <span className="text-gray-500"> pending</span>
            </div>
            <div className="rounded-md border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm">
              <span className="font-semibold text-yellow-800">
                {countData.high_priority}
              </span>
              <span className="text-yellow-700"> high priority</span>
            </div>
          </div>
        )}
      </div>

      <Card>
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <label className="text-xs font-medium text-gray-600">
            Priority
            <select
              value={priority}
              onChange={(e) => {
                setPriority(e.target.value as PriorityFilter);
                setPage(1);
              }}
              className="ml-2 rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm"
            >
              <option value="">All</option>
              <option value="high">High</option>
              <option value="normal">Normal</option>
            </select>
          </label>
          {isFetching && (
            <span className="text-xs text-gray-500" aria-live="polite">
              Updating…
            </span>
          )}
        </div>

        {isLoading && !queue && <LoadingSpinner size="md" />}

        {error && (
          <p className="text-sm text-red-600">
            Could not load the review queue. You may not have reviewer access
            or the service is unavailable.
          </p>
        )}

        {queue && queue.items.length === 0 && (
          <EmptyState
            icon={ClipboardList}
            title="No protocols pending review"
            description="The review queue is currently empty. New submissions will appear here."
          />
        )}

        {queue && queue.items.length > 0 && (
          <>
            <Table
              columns={columns}
              data={
                queue.items as (ReviewQueueItem & Record<string, unknown>)[]
              }
              keyExtractor={(row) => String(row.protocol_id)}
              emptyMessage="No protocols match the current filters."
            />
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-gray-100 pt-4 text-sm text-gray-600">
              <span>
                Page {page} of {totalPages}
                {total === 0
                  ? ' · No items'
                  : ` · ${(page - 1) * pageSize + 1}–${Math.min(
                      page * pageSize,
                      total,
                    )} of ${total}`}
              </span>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  disabled={page <= 1 || isFetching}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  disabled={page >= totalPages || isFetching}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        )}
      </Card>
    </div>
  );
}
