import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Send, CheckCircle, Copy } from 'lucide-react';
import { getProtocol, submitForReview, cloneProtocol } from '../api/protocols';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { format } from 'date-fns';

export default function ProtocolDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: protocol, isLoading, error } = useQuery({
    queryKey: ['protocol', id],
    queryFn: () => getProtocol(id!),
    enabled: !!id,
  });

  const submitMutation = useMutation({
    mutationFn: () => submitForReview(id!),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['protocol', id] }),
  });

  const cloneMutation = useMutation({
    mutationFn: () => cloneProtocol(id!),
    onSuccess: (data) => {
      const newId = (data as Record<string, string>).protocol_id;
      if (newId) navigate(`/protocols/${newId}`);
    },
  });

  if (isLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  if (error || !protocol) {
    return (
      <div className="mt-20 text-center">
        <p className="text-gray-500">Protocol not found.</p>
        <Button variant="ghost" className="mt-4" onClick={() => navigate('/protocols')}>
          Back to Library
        </Button>
      </div>
    );
  }

  const data = protocol.data as Record<string, unknown>;
  const sections = (data?.sections ?? {}) as Record<string, unknown>;
  const evidence = protocol.evidence;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/protocols')}
          className="rounded-md p-2 hover:bg-gray-100"
        >
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-sozo-text">{protocol.condition_name}</h1>
          <p className="text-sm text-gray-500">
            Version {protocol.version} &middot; {protocol.modality.toUpperCase()} &middot;
            Created {format(new Date(protocol.created_at), 'dd MMM yyyy')}
          </p>
        </div>
        <Badge status={protocol.status} />
        <Badge status={protocol.evidence_level} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main content */}
        <div className="space-y-6 lg:col-span-2">
          <Card title="Protocol Details">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Condition</p>
                <p className="font-medium">{protocol.condition_name}</p>
              </div>
              <div>
                <p className="text-gray-500">Condition Slug</p>
                <p className="font-mono text-xs">{protocol.condition_slug}</p>
              </div>
              <div>
                <p className="text-gray-500">Modality</p>
                <p className="font-medium uppercase">{protocol.modality}</p>
              </div>
              <div>
                <p className="text-gray-500">Generation Method</p>
                <p className="font-medium">{protocol.generation_method}</p>
              </div>
              <div>
                <p className="text-gray-500">Template</p>
                <p className="font-medium">{protocol.is_template ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <p className="text-gray-500">Created By</p>
                <p className="font-medium">{protocol.created_by}</p>
              </div>
            </div>
          </Card>

          {/* Stimulation parameters if available */}
          {!!sections.stimulation_parameters && (
            <Card title="Stimulation Parameters">
              <div className="grid grid-cols-2 gap-4 text-sm">
                {Object.entries(sections.stimulation_parameters as Record<string, unknown>).map(
                  ([key, value]) => (
                    <div key={key}>
                      <p className="text-gray-500">{key.replace(/_/g, ' ')}</p>
                      <p className="font-medium">{String(value as string)}</p>
                    </div>
                  ),
                )}
              </div>
            </Card>
          )}

          {/* Target regions */}
          {!!sections.target_regions && (
            <Card title="Target Regions">
              <div className="flex flex-wrap gap-2">
                {(sections.target_regions as string[]).map((region) => (
                  <span
                    key={region}
                    className="rounded bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700"
                  >
                    {region.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </Card>
          )}

          {/* Safety info */}
          {!!sections.safety && (
            <Card title="Safety">
              <div className="space-y-3 text-sm">
                {!!(sections.safety as Record<string, unknown>).contraindications && (
                  <div>
                    <p className="text-gray-500 font-medium">Contraindications</p>
                    <ul className="mt-1 list-inside list-disc text-gray-600">
                      {(
                        (sections.safety as Record<string, unknown>).contraindications as string[]
                      ).map((c) => (
                        <li key={c}>{c.replace(/_/g, ' ')}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {!!(sections.safety as Record<string, unknown>).monitoring && (
                  <div>
                    <p className="text-gray-500 font-medium">Monitoring</p>
                    <p className="text-gray-600">
                      {String((sections.safety as Record<string, unknown>).monitoring)}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Evidence summary */}
          {evidence && evidence.articles_count > 0 && (
            <Card title="Evidence Summary">
              <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                <div>
                  <p className="text-gray-500">Articles Included</p>
                  <p className="text-xl font-bold">{evidence.articles_count}</p>
                </div>
                <div>
                  <p className="text-gray-500">PRISMA Screened</p>
                  <p className="text-xl font-bold">{evidence.prisma_screened}</p>
                </div>
              </div>
              {!!sections.evidence_summary && (
                <p className="text-sm text-gray-600">
                  {String(sections.evidence_summary)}
                </p>
              )}
              {evidence.top_articles && evidence.top_articles.length > 0 && (
                <div className="mt-4 space-y-2">
                  <p className="text-xs font-medium text-gray-500 uppercase">Key Articles</p>
                  {evidence.top_articles.map((a, i) => (
                    <div key={i} className="rounded border border-gray-100 bg-gray-50 px-3 py-2 text-sm">
                      <p className="font-medium">{a.title}</p>
                      <p className="text-xs text-gray-500">
                        PMID: {a.pmid} | {a.year} | {a.evidence_type} | {a.relation}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          )}

          {/* Raw data fallback */}
          {Object.keys(data).length > 0 && !sections.stimulation_parameters && (
            <Card title="Protocol Data">
              <pre className="max-h-[400px] overflow-auto rounded-md bg-gray-50 p-4 text-xs text-gray-700">
                {JSON.stringify(data, null, 2)}
              </pre>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <Card title="Actions">
            <div className="space-y-3">
              {protocol.status === 'draft' && (
                <Button
                  className="w-full"
                  onClick={() => submitMutation.mutate()}
                  isLoading={submitMutation.isPending}
                >
                  <Send className="mr-2 h-4 w-4" />
                  Submit for Review
                </Button>
              )}
              {protocol.status === 'pending_review' && (
                <Button
                  className="w-full"
                  variant="secondary"
                  onClick={() => navigate(`/protocols/${id}/review`)}
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Review Protocol
                </Button>
              )}
              <Button
                variant="secondary"
                className="w-full"
                onClick={() => cloneMutation.mutate()}
                isLoading={cloneMutation.isPending}
              >
                <Copy className="mr-2 h-4 w-4" />
                Clone Protocol
              </Button>
              <Button
                variant="ghost"
                className="w-full"
                onClick={() => navigate(`/protocols/${id}/review`)}
              >
                View Review Details
              </Button>
            </div>
          </Card>

          <Card title="Metadata">
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-gray-500">Protocol ID</dt>
                <dd className="font-mono text-xs break-all">{protocol.protocol_id}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Version ID</dt>
                <dd className="font-mono text-xs break-all">{protocol.version_id}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Created by</dt>
                <dd className="font-medium">{protocol.created_by}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Updated</dt>
                <dd className="font-medium">
                  {format(new Date(protocol.updated_at), 'dd MMM yyyy HH:mm')}
                </dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </div>
  );
}
