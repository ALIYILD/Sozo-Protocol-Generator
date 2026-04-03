import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { listProtocols } from '../api/protocols';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import type { ProtocolListItem } from '../types';
import { format } from 'date-fns';

export default function ProtocolListPage() {
  const navigate = useNavigate();

  const { data, isLoading, error } = useQuery({
    queryKey: ['protocols'],
    queryFn: () => listProtocols(),
  });

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

      <Card>
        <Table
          columns={columns}
          data={(data?.items ?? []) as (ProtocolListItem & Record<string, unknown>)[]}
          keyExtractor={(row) => row.protocol_id as string}
          onRowClick={(row) => navigate(`/protocols/${row.protocol_id}`)}
          emptyMessage="No protocols yet. Create your first one!"
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
  );
}
