import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen, AlertCircle, CheckCircle, Clock, Shield, Sliders } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import { listConditions, getStalenessReport } from '../api/evidence';
import { listProtocols } from '../api/protocols';
import type { ProtocolListItem, StalenessCondition } from '../types';

export default function DashboardPage() {
  const navigate = useNavigate();

  const { data: conditions, isLoading: conditionsLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  });

  const { data: staleness, isLoading: stalenessLoading } = useQuery({
    queryKey: ['staleness'],
    queryFn: getStalenessReport,
  });

  const { data: protocolsData, isLoading: protocolsLoading } = useQuery({
    queryKey: ['protocols-recent'],
    queryFn: () => listProtocols(1, 5),
  });

  const isLoading = conditionsLoading || stalenessLoading || protocolsLoading;

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-20" />;
  }

  const recentProtocols = protocolsData?.items ?? [];

  const protocolColumns: Column<ProtocolListItem & Record<string, unknown>>[] = [
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
  ];

  const freshnessColor = (f: string) => {
    switch (f) {
      case 'fresh': return 'text-green-600';
      case 'aging': return 'text-yellow-600';
      case 'stale': return 'text-orange-600';
      case 'expired': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-sozo-text">Dashboard</h1>
        <div className="flex gap-3">
          <Button onClick={() => navigate('/protocols/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Protocol
          </Button>
          <Button variant="secondary" onClick={() => navigate('/protocols')}>
            <BookOpen className="mr-2 h-4 w-4" />
            Browse Library
          </Button>
        </div>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-green-50 p-3">
              <CheckCircle className="h-6 w-6 text-sozo-accent" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Conditions</p>
              <p className="text-2xl font-bold text-sozo-text">
                {conditions?.length ?? 0}
              </p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-3">
              <BookOpen className="h-6 w-6 text-sozo-secondary" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Protocols</p>
              <p className="text-2xl font-bold text-sozo-text">
                {protocolsData?.total ?? 0}
              </p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-purple-50 p-3">
              <AlertCircle className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Evidence Health</p>
              <p className="text-lg font-semibold text-sozo-text capitalize">
                {staleness?.overall_health ?? 'Unknown'}
              </p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-yellow-50 p-3">
              <Clock className="h-6 w-6 text-sozo-warning" />
            </div>
            <div>
              <p className="text-sm text-gray-500">Needs Refresh</p>
              <p className="text-2xl font-bold text-sozo-text">
                {staleness?.high_priority_refreshes?.length ?? 0}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card>
          <button
            onClick={() => navigate('/safety')}
            className="flex w-full items-center gap-4 text-left hover:bg-gray-50 rounded-md p-2 -m-2 transition-colors"
          >
            <div className="rounded-lg bg-red-50 p-3">
              <Shield className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <p className="font-medium text-sozo-text">Safety Check</p>
              <p className="text-sm text-gray-500">Screen patient contraindications and medication interactions</p>
            </div>
          </button>
        </Card>
        <Card>
          <button
            onClick={() => navigate('/personalization')}
            className="flex w-full items-center gap-4 text-left hover:bg-gray-50 rounded-md p-2 -m-2 transition-colors"
          >
            <div className="rounded-lg bg-indigo-50 p-3">
              <Sliders className="h-6 w-6 text-indigo-600" />
            </div>
            <div>
              <p className="font-medium text-sozo-text">Personalization</p>
              <p className="text-sm text-gray-500">Generate personalized protocol recommendations</p>
            </div>
          </button>
        </Card>
      </div>

      {/* Evidence freshness by condition */}
      {staleness && staleness.conditions.length > 0 && (
        <Card title="Evidence Freshness by Condition">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
            {staleness.conditions.map((c: StalenessCondition) => (
              <div
                key={c.slug}
                className="flex items-center justify-between rounded-md border border-gray-100 px-3 py-2"
              >
                <span className="text-sm text-gray-700 truncate mr-2">{c.name}</span>
                <span className={`text-xs font-medium capitalize ${freshnessColor(c.freshness)}`}>
                  {c.freshness}
                </span>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Recent protocols */}
      <Card title="Recent Protocols">
        <Table
          columns={protocolColumns}
          data={recentProtocols as (ProtocolListItem & Record<string, unknown>)[]}
          keyExtractor={(row) => row.protocol_id as string}
          onRowClick={(row) => navigate(`/protocols/${row.protocol_id}`)}
          emptyMessage="No protocols yet. Create your first one!"
        />
      </Card>
    </div>
  );
}
