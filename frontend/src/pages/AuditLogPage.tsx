import { useEffect, useState, type ChangeEvent } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format, parseISO } from 'date-fns';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import {
  listAuditEvents,
  getAuditActions,
  getAuditEntityTypes,
  type AuditEventFilters,
} from '../api/audit';
import type { AuditEvent } from '../types';

const PAGE_SIZE = 25;

type AuditFilterForm = {
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  thread_id: string;
  build_id: string;
  date_from: string;
  date_to: string;
  node_name: string;
};

const INITIAL_FORM: AuditFilterForm = {
  entity_type: '',
  entity_id: '',
  action: '',
  actor: '',
  thread_id: '',
  build_id: '',
  date_from: '',
  date_to: '',
  node_name: '',
};

function formToFilters(f: AuditFilterForm): AuditEventFilters {
  const out: AuditEventFilters = {};
  (Object.entries(f) as [keyof AuditEventFilters, string][]).forEach(([k, v]) => {
    if (v.trim()) out[k] = v.trim();
  });
  return out;
}

function formatAuditTime(iso: string): string {
  try {
    return format(parseISO(iso), 'yyyy-MM-dd HH:mm:ss');
  } catch {
    return iso;
  }
}

function detailsPreview(details: Record<string, unknown>): string {
  if (!details || Object.keys(details).length === 0) return '—';
  const s = JSON.stringify(details);
  return s.length > 96 ? `${s.slice(0, 96)}…` : s;
}

export default function AuditLogPage() {
  const [page, setPage] = useState(1);
  const [draft, setDraft] = useState<AuditFilterForm>({ ...INITIAL_FORM });
  const [applied, setApplied] = useState<AuditEventFilters>({});

  const { data: entityTypes = [] } = useQuery({
    queryKey: ['audit-entity-types'],
    queryFn: getAuditEntityTypes,
  });

  const { data: actionOptions = [] } = useQuery({
    queryKey: ['audit-actions'],
    queryFn: getAuditActions,
  });

  const { data, isLoading, error, isFetching } = useQuery({
    queryKey: ['audit-events', page, PAGE_SIZE, applied],
    queryFn: () => listAuditEvents(page, PAGE_SIZE, applied),
  });

  useEffect(() => {
    if (!data) return;
    const ps = data.page_size || PAGE_SIZE;
    const totalPages = Math.max(1, Math.ceil(data.total / ps));
    if (page > totalPages) setPage(totalPages);
  }, [data, page]);

  const applyFilters = () => {
    setApplied(formToFilters(draft));
    setPage(1);
  };

  const clearFilters = () => {
    setDraft({ ...INITIAL_FORM });
    setApplied({});
    setPage(1);
  };

  const setField =
    (key: keyof AuditFilterForm) =>
    (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const v = e.target.value;
      setDraft((d) => ({ ...d, [key]: v }));
    };

  const columns: Column<AuditEvent & Record<string, unknown>>[] = [
    {
      key: 'timestamp',
      header: 'Time',
      sortable: true,
      render: (row) => formatAuditTime(row.timestamp),
    },
    { key: 'actor', header: 'Actor', render: (row) => row.actor ?? '—' },
    { key: 'action', header: 'Action', sortable: true },
    { key: 'entity_type', header: 'Entity', sortable: true },
    {
      key: 'entity_id',
      header: 'Entity ID',
      render: (row) => (
        <span className="font-mono text-xs break-all" title={row.entity_id}>
          {row.entity_id.length > 24 ? `${row.entity_id.slice(0, 24)}…` : row.entity_id}
        </span>
      ),
    },
    {
      key: 'node_name',
      header: 'Node',
      render: (row) => row.node_name ?? '—',
    },
    {
      key: 'details',
      header: 'Details',
      render: (row) => (
        <span className="text-xs text-gray-600" title={JSON.stringify(row.details)}>
          {detailsPreview(row.details)}
        </span>
      ),
    },
  ];

  const total = data?.total ?? 0;
  const pageSize = data?.page_size ?? PAGE_SIZE;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-sozo-text">Audit log</h1>

      <Card>
        <p className="text-sm text-gray-500 mb-4">
          Append-only governance trail from <span className="font-mono">audit_log</span>
          (newest first). Filters map to <span className="font-mono">GET /api/audit/events</span>
          query parameters.
        </p>

        <form
          className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 border border-gray-100 rounded-lg p-4 bg-gray-50/50"
          onSubmit={(e) => {
            e.preventDefault();
            applyFilters();
          }}
        >
          <label className="block text-xs font-medium text-gray-600">
            Entity type
            <select
              value={draft.entity_type}
              onChange={setField('entity_type')}
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-2 py-2 text-sm"
            >
              <option value="">Any</option>
              {entityTypes.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Action
            <select
              value={draft.action}
              onChange={setField('action')}
              className="mt-1 block w-full rounded-md border border-gray-300 bg-white px-2 py-2 text-sm"
            >
              <option value="">Any</option>
              {actionOptions.map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Entity ID
            <input
              type="text"
              value={draft.entity_id}
              onChange={setField('entity_id')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
              placeholder="UUID or id"
            />
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Actor
            <input
              type="text"
              value={draft.actor}
              onChange={setField('actor')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
              placeholder="Email or system"
            />
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Thread ID
            <input
              type="text"
              value={draft.thread_id}
              onChange={setField('thread_id')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm font-mono text-xs"
              placeholder="Graph run / details.thread_id"
            />
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Build ID
            <input
              type="text"
              value={draft.build_id}
              onChange={setField('build_id')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm font-mono text-xs"
              placeholder="details.build_id"
            />
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Date from
            <input
              type="date"
              value={draft.date_from}
              onChange={setField('date_from')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
            />
          </label>
          <label className="block text-xs font-medium text-gray-600">
            Date to
            <input
              type="date"
              value={draft.date_to}
              onChange={setField('date_to')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
            />
          </label>
          <label className="block text-xs font-medium text-gray-600 lg:col-span-2">
            LangGraph node
            <input
              type="text"
              value={draft.node_name}
              onChange={setField('node_name')}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
              placeholder="Node id filter"
            />
          </label>
          <div className="flex flex-wrap items-end gap-2 lg:col-span-3">
            <Button type="submit" disabled={isFetching}>
              Apply filters
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={clearFilters}
              disabled={isFetching}
            >
              Clear
            </Button>
          </div>
        </form>

        {isLoading && !data && <LoadingSpinner size="md" />}
        {error && (
          <p className="text-sm text-red-600">
            Could not load audit events. You may not have access or the service is unavailable.
          </p>
        )}
        {data && (
          <>
            {isFetching && (
              <p className="text-xs text-gray-500 mb-2" aria-live="polite">
                Updating results…
              </p>
            )}
            <Table
              columns={columns}
              data={data.items as (AuditEvent & Record<string, unknown>)[]}
              keyExtractor={(row) => String(row.id)}
              emptyMessage="No audit events match the current filters."
            />
            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-gray-100 pt-4 text-sm text-gray-600">
              <span>
                Page {page} of {totalPages}
                {total === 0
                  ? ' · No events'
                  : ` · ${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, total)} of ${total}`}
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
