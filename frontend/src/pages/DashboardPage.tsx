import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Plus, BookOpen, AlertCircle, CheckCircle, Clock, Shield, Sliders } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import Table, { type Column } from '../components/ui/Table';
import {
  listConditions,
  getStalenessReport,
  getCockpitOverview,
  getCockpitConditions,
} from '../api/evidence';
import { listProtocols } from '../api/protocols';
import type {
  ProtocolListItem,
  StalenessCondition,
  CockpitConditionSummary,
  CockpitOverview,
} from '../types';
import { canViewStaleness } from '../auth/permissions';
import { useAuth } from '../hooks/useAuth';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const showStaleness = canViewStaleness(user);

  const { data: conditions, isLoading: conditionsLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  });

  const { data: staleness, isLoading: stalenessLoading } = useQuery({
    queryKey: ['staleness'],
    queryFn: getStalenessReport,
    enabled: showStaleness,
  });

  const { data: cockpit, isLoading: cockpitLoading } = useQuery({
    queryKey: ['cockpit-overview'],
    queryFn: getCockpitOverview,
    enabled: showStaleness,
  });

  const { data: cockpitConditions, isLoading: cockpitConditionsLoading } = useQuery({
    queryKey: ['cockpit-conditions'],
    queryFn: getCockpitConditions,
    enabled: showStaleness,
  });

  const { data: protocolsData, isLoading: protocolsLoading } = useQuery({
    queryKey: ['protocols-recent'],
    queryFn: () => listProtocols(1, 5),
  });

  const isLoading =
    conditionsLoading ||
    protocolsLoading ||
    (showStaleness && stalenessLoading) ||
    (showStaleness && cockpitLoading) ||
    (showStaleness && cockpitConditionsLoading);

  if (isLoading) {
    return <LoadingSpinner size="lg" className="mt-20" />;
  }

  const recentProtocols = protocolsData?.items ?? [];

  const conditionsCount =
    showStaleness && cockpit != null
      ? cockpit.conditions_count
      : conditions?.length ?? 0;

  const cockpitDocTotal = (c: CockpitOverview) =>
    c.documents_ready + c.documents_review_required + c.documents_incomplete;

  const protocolsTotal =
    showStaleness && cockpit != null
      ? cockpitDocTotal(cockpit)
      : protocolsData?.total ?? 0;

  const cockpitConditionColumns: Column<
    CockpitConditionSummary & Record<string, unknown>
  >[] = [
    {
      key: 'condition',
      header: 'Condition',
      sortable: true,
      render: (row) =>
        String(row.condition).replace(/_/g, ' ').replace(/\b\w/g, (x) => x.toUpperCase()),
    },
    { key: 'total_docs', header: 'Paths' },
    { key: 'ready', header: 'Ready' },
    { key: 'review_required', header: 'Review' },
    { key: 'incomplete', header: 'Incomplete' },
    { key: 'total_pmids', header: 'PMIDs' },
  ];

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
              <p className="text-2xl font-bold text-sozo-text">{conditionsCount}</p>
            </div>
          </div>
        </Card>
        <Card>
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-50 p-3">
              <BookOpen className="h-6 w-6 text-sozo-secondary" />
            </div>
            <div>
              <p className="text-sm text-gray-500">
                {showStaleness && cockpit != null ? 'Knowledge docs' : 'Protocols'}
              </p>
              <p className="text-2xl font-bold text-sozo-text">{protocolsTotal}</p>
              {showStaleness && cockpit != null && cockpit.documents_review_required > 0 && (
                <p className="text-xs text-amber-700 mt-1">
                  {cockpit.documents_review_required} in review
                </p>
              )}
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
                {showStaleness ? staleness?.overall_health ?? 'Unknown' : '—'}
              </p>
              {!showStaleness && (
                <p className="text-xs text-gray-400">Operators / admins only</p>
              )}
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
                {showStaleness ? staleness?.high_priority_refreshes?.length ?? 0 : '—'}
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

      {showStaleness && cockpitConditions && cockpitConditions.length > 0 && (
        <Card title="Knowledge cockpit by condition">
          <Table
            columns={cockpitConditionColumns}
            data={
              cockpitConditions as (CockpitConditionSummary & Record<string, unknown>)[]
            }
            keyExtractor={(row) => row.condition}
            emptyMessage="No cockpit rows yet."
          />
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
