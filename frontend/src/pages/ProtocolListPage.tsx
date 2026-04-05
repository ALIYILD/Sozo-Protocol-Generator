import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, X, FilePlus, Search } from 'lucide-react';
import { listProtocols } from '../api/protocols';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import EmptyState from '../components/ui/EmptyState';
import type { ProtocolListItem } from '../types';
import { format } from 'date-fns';

export default function ProtocolListPage() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading, error } = useQuery({
    queryKey: ['protocols'],
    queryFn: () => listProtocols(),
  });

  const allProtocols = data?.items ?? [];
  const filtered = searchQuery
    ? allProtocols.filter(
        (p) =>
          p.condition_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          p.modality.toLowerCase().includes(searchQuery.toLowerCase()),
      )
    : allProtocols;
  const hasSearch = searchQuery.trim().length > 0;

  const columns: Column<ProtocolListItem & Record<string, unknown>>[] = [
    {
      key: 'condition_name',
      header: 'Condition',
      sortable: true,
    },
    {
      key: 'modality',
      header: 'Modality',
      render: (row) => (
        <span className="uppercase text-xs font-medium text-gray-600">
          {row.modality as string}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row) => <Badge status={row.status as string} />,
    },
    {
      key: 'evidence_level',
      header: 'Evidence',
      render: (row) => <Badge status={row.evidence_level as string} />,
    },
    { key: 'version', header: 'Version', sortable: true },
    {
      key: 'created_at',
      header: 'Created',
      sortable: true,
      render: (row) => {
        const d = row.created_at as string;
        return d ? format(new Date(d), 'dd MMM yyyy') : '-';
      },
    },
  ];

  if (isLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  if (error) {
    return (
      <div className="mt-20 text-center">
        <p className="text-red-600">Failed to load protocols.</p>
        <p className="text-sm text-gray-500 mt-1">Please check that the API is running.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-sozo-text">Protocol Library</h1>
        <Button onClick={() => navigate('/protocols/new')}>
          <Plus className="mr-2 h-4 w-4" />
          New Protocol
        </Button>
      </div>

      {/* Search bar (only shown when there are protocols to filter) */}
      {allProtocols.length > 0 && (
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search by condition or modality..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md border border-gray-300 py-2 pl-10 pr-4 text-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
          />
          {hasSearch && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}

      {/* Empty state: no protocols at all */}
      {allProtocols.length === 0 && (
        <EmptyState
          icon={FilePlus}
          title="No protocols yet"
          description="Your protocol library is empty. Create your first protocol to get started."
          action={{
            label: 'Create your first protocol',
            onClick: () => navigate('/protocols/new'),
          }}
        />
      )}

      {/* Empty state: search/filter active but no matches */}
      {allProtocols.length > 0 && filtered.length === 0 && hasSearch && (
        <EmptyState
          icon={X}
          title="No protocols match your filters"
          description={`No protocols found for "${searchQuery}". Try a different search term.`}
          action={{
            label: 'Clear Filters',
            onClick: () => setSearchQuery(''),
          }}
        />
      )}

      {/* Protocol table */}
      {filtered.length > 0 && (
        <Card>
          <Table
            columns={columns}
            data={filtered as (ProtocolListItem & Record<string, unknown>)[]}
            keyExtractor={(row) => row.protocol_id as string}
            onRowClick={(row) => navigate(`/protocols/${row.protocol_id}`)}
            emptyMessage="No protocols match your filters."
          />
        </Card>
      )}

      {data && data.pages > 1 && (
        <div className="flex justify-center">
          <p className="text-sm text-gray-500">
            Page {data.page} of {data.pages} ({data.total} total)
          </p>
        </div>
      )}
    </div>
  );
}
