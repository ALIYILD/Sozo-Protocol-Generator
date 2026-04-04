import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, CheckCircle, XCircle } from 'lucide-react';
import { getProtocol, transitionStatus } from '../api/protocols';
import { getGraphStatus, submitReview } from '../api/graph';
import { ProtocolAuditSection } from '../components/protocol/ProtocolAuditSection';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { protocolIdFromGraphOutput } from '../utils/protocolIdFromGraphOutput';

export default function ProtocolReviewPage() {
  const { id, threadId } = useParams<{ id?: string; threadId?: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState('');
  const [reviewerId, setReviewerId] = useState('');

  // If threadId is present, use graph review mode
  const isGraphReview = !!threadId;

  // ═══ GRAPH REVIEW MODE ═══════════════════════════════════════════
  const { data: graphState, isLoading: graphLoading } = useQuery({
    queryKey: ['graph-status', threadId],
    queryFn: () => getGraphStatus(threadId!),
    enabled: isGraphReview,
    refetchInterval: false,
  });

  const graphApproveMutation = useMutation({
    mutationFn: () =>
      submitReview({
        thread_id: threadId!,
        decision: 'approve',
        reviewer_id: reviewerId,
        review_notes: notes,
      }),
    onSuccess: () => {
      navigate('/protocols');
    },
  });

  const graphRejectMutation = useMutation({
    mutationFn: () =>
      submitReview({
        thread_id: threadId!,
        decision: 'reject',
        reviewer_id: reviewerId,
        review_notes: notes,
      }),
    onSuccess: () => {
      navigate('/protocols');
    },
  });

  if (isGraphReview) {
    if (graphLoading) return <LoadingSpinner size="lg" className="mt-20" />;
    if (!graphState) return <p className="mt-20 text-center text-gray-500">Thread not found.</p>;

    const graphLinkedProtocolId = protocolIdFromGraphOutput(graphState.output);

    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="rounded-md p-2 hover:bg-gray-100">
            <ArrowLeft className="h-5 w-5 text-gray-500" />
          </button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-sozo-text">
              Review: {graphState.condition.display_name}
            </h1>
            <p className="text-sm text-gray-500">
              Thread: {threadId?.slice(0, 8)}... | Revision {graphState.revision_number}
            </p>
          </div>
          <Badge status={graphState.safety.cleared ? 'approved' : 'rejected'} />
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-4 gap-4">
          <Card>
            <div className="text-center">
              <div className="text-2xl font-bold">{graphState.evidence.article_count}</div>
              <div className="text-xs text-gray-500">Articles</div>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {graphState.evidence.grade_distribution.A || 0}
              </div>
              <div className="text-xs text-gray-500">Grade A</div>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {graphState.protocol.grounding_score != null
                  ? `${Math.round(graphState.protocol.grounding_score * 100)}%`
                  : 'N/A'}
              </div>
              <div className="text-xs text-gray-500">Grounding</div>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {graphState.safety.cleared ? 'Clear' : 'BLOCKED'}
              </div>
              <div className="text-xs text-gray-500">Safety</div>
            </div>
          </Card>
        </div>

        {/* Safety warnings */}
        {graphState.safety.off_label.length > 0 && (
          <div className="rounded-lg bg-amber-50 border border-amber-200 p-4">
            <h3 className="text-sm font-semibold text-amber-800">Off-Label Use</h3>
            {graphState.safety.off_label.map((flag, i) => (
              <p key={i} className="text-sm text-amber-700 mt-1">{flag}</p>
            ))}
          </div>
        )}

        {/* Protocol sections */}
        <Card title="Protocol Sections">
          {graphState.protocol.sections.map((section) => (
            <div key={section.section_id} className="border-b border-gray-100 pb-4 mb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-sozo-text">{section.title}</h4>
                <Badge status={section.confidence === 'high' ? 'approved' : section.confidence === 'medium' ? 'pending_review' : 'draft'} />
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{section.content}</p>
              {section.cited_evidence_ids.length > 0 && (
                <p className="text-xs text-gray-400 mt-2">
                  Citations: {section.cited_evidence_ids.join(', ')}
                </p>
              )}
            </div>
          ))}
        </Card>

        {/* Evidence */}
        <Card title={`Evidence (${graphState.evidence_articles.length} articles)`}>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {graphState.evidence_articles.map((a, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className={`inline-flex items-center justify-center w-6 h-6 rounded text-xs font-bold ${
                  a.grade === 'A' ? 'bg-green-100 text-green-800' :
                  a.grade === 'B' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {a.grade}
                </span>
                <div>
                  <span className="text-gray-800">{a.title?.slice(0, 80)}</span>
                  <span className="text-gray-400 ml-1">
                    ({a.authors?.slice(0, 2).join(', ')}, {a.year})
                  </span>
                  {a.pmid && <span className="text-blue-500 ml-1">PMID: {a.pmid}</span>}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Node execution log">
          <div className="space-y-1">
            {graphState.node_history.map((n, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span>{n.status === 'success' ? '\u2705' : '\u274c'}</span>
                <span className="font-mono text-gray-600">{n.node_id}</span>
                <span className="text-gray-400">{n.duration_ms?.toFixed(0)}ms</span>
              </div>
            ))}
          </div>
        </Card>

        {graphLinkedProtocolId && (
          <ProtocolAuditSection protocolId={graphLinkedProtocolId} />
        )}

        {/* Review form */}
        <Card title="Your Decision">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Reviewer ID</label>
              <input
                type="text"
                value={reviewerId}
                onChange={(e) => setReviewerId(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                placeholder="e.g. dr_smith"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Review Notes</label>
              <textarea
                rows={4}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
                placeholder="Your review comments..."
              />
            </div>

            {(graphApproveMutation.isError || graphRejectMutation.isError) && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
                Review submission failed. Please try again.
              </div>
            )}

            <div className="flex gap-3">
              <Button
                onClick={() => graphApproveMutation.mutate()}
                isLoading={graphApproveMutation.isPending}
                disabled={!reviewerId}
              >
                <CheckCircle className="mr-2 h-4 w-4" />
                Approve Protocol
              </Button>
              <Button
                variant="danger"
                onClick={() => graphRejectMutation.mutate()}
                isLoading={graphRejectMutation.isPending}
                disabled={!reviewerId || !notes.trim()}
              >
                <XCircle className="mr-2 h-4 w-4" />
                Reject
              </Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  // ═══ LEGACY REVIEW MODE ══════════════════════════════════════════
  const { data: protocol, isLoading } = useQuery({
    queryKey: ['protocol', id],
    queryFn: () => getProtocol(id!),
    enabled: !!id && !isGraphReview,
  });

  const approveMutation = useMutation({
    mutationFn: () => transitionStatus(id!, 'approved', notes || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['protocol', id] });
      navigate(`/protocols/${id}`);
    },
  });

  const rejectMutation = useMutation({
    mutationFn: () => transitionStatus(id!, 'rejected', notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['protocol', id] });
      navigate(`/protocols/${id}`);
    },
  });

  if (isLoading) return <LoadingSpinner size="lg" className="mt-20" />;
  if (!protocol) return <p className="mt-20 text-center text-gray-500">Protocol not found.</p>;

  const canReview = protocol.status === 'pending_review';

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(`/protocols/${id}`)} className="rounded-md p-2 hover:bg-gray-100">
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-sozo-text">Review: {protocol.condition_name}</h1>
          <p className="text-sm text-gray-500">{protocol.modality.toUpperCase()} | v{protocol.version}</p>
        </div>
        <Badge status={protocol.status} />
      </div>

      <Card title="Protocol Summary">
        <dl className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">Condition</dt>
            <dd className="font-medium">{protocol.condition_name}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Modality</dt>
            <dd className="font-medium uppercase">{protocol.modality}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Evidence Level</dt>
            <dd><Badge status={protocol.evidence_level} /></dd>
          </div>
          <div>
            <dt className="text-gray-500">Generation Method</dt>
            <dd className="font-medium">{protocol.generation_method}</dd>
          </div>
        </dl>
      </Card>

      {id && <ProtocolAuditSection protocolId={id} />}

      {canReview ? (
        <Card title="Submit Review">
          <div className="space-y-4">
            <textarea
              rows={5}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="block w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
              placeholder="Add review comments..."
            />
            <div className="flex gap-3">
              <Button onClick={() => approveMutation.mutate()} isLoading={approveMutation.isPending}>
                <CheckCircle className="mr-2 h-4 w-4" />
                Approve
              </Button>
              <Button
                variant="danger"
                onClick={() => rejectMutation.mutate()}
                isLoading={rejectMutation.isPending}
                disabled={!notes.trim()}
              >
                <XCircle className="mr-2 h-4 w-4" />
                Reject
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        <Card>
          <p className="text-sm text-gray-500">
            Not pending review. Status: <Badge status={protocol.status} />
          </p>
        </Card>
      )}
    </div>
  );
}
