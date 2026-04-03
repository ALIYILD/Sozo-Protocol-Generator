import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, CheckCircle, XCircle } from 'lucide-react';
import { getProtocol, transitionStatus } from '../api/protocols';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';

export default function ProtocolReviewPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [notes, setNotes] = useState('');

  const { data: protocol, isLoading } = useQuery({
    queryKey: ['protocol', id],
    queryFn: () => getProtocol(id!),
    enabled: !!id,
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
        <button
          onClick={() => navigate(`/protocols/${id}`)}
          className="rounded-md p-2 hover:bg-gray-100"
        >
          <ArrowLeft className="h-5 w-5 text-gray-500" />
        </button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-sozo-text">
            Review: {protocol.condition_name}
          </h1>
          <p className="text-sm text-gray-500">
            {protocol.modality.toUpperCase()} | v{protocol.version}
          </p>
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

      {canReview ? (
        <Card title="Submit Review">
          <div className="space-y-4">
            <div>
              <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                Review Notes
              </label>
              <textarea
                id="notes"
                rows={5}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
                placeholder="Add review comments..."
              />
            </div>

            {approveMutation.isError && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
                Failed to approve. Check that the status transition is valid.
              </div>
            )}

            {rejectMutation.isError && (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
                Failed to reject. Check that the status transition is valid.
              </div>
            )}

            <div className="flex gap-3">
              <Button
                onClick={() => approveMutation.mutate()}
                isLoading={approveMutation.isPending}
              >
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
            This protocol is not currently pending review. Current status:{' '}
            <Badge status={protocol.status} />
          </p>
        </Card>
      )}
    </div>
  );
}
