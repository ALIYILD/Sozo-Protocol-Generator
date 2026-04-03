import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { listConditions } from '../api/evidence';
import { createProtocol, getGenerationStatus } from '../api/protocols';
import type { ProtocolCreateResponse } from '../types';

export default function ProtocolBuilderPage() {
  const navigate = useNavigate();
  const [conditionSlug, setConditionSlug] = useState('');
  const [modality, setModality] = useState('');
  const [docType, setDocType] = useState('evidence_based_protocol');
  const [tier, setTier] = useState('fellow');
  const [prompt, setPrompt] = useState('');

  // Generation tracking
  const [taskId, setTaskId] = useState<string | null>(null);
  const [protocolId, setProtocolId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [genMessage, setGenMessage] = useState('');
  const [polling, setPolling] = useState(false);

  const { data: conditions, isLoading: conditionsLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createProtocol({
        condition_slug: conditionSlug,
        modality: modality || undefined,
        doc_type: docType,
        tier,
        prompt: prompt || undefined,
      }),
    onSuccess: (data: ProtocolCreateResponse) => {
      setProtocolId(data.protocol_id);
      setTaskId(data.task_id);
      setPolling(true);
      setProgress(0);
      setGenMessage('Generation queued...');
    },
  });

  // Poll generation status
  useEffect(() => {
    if (!polling || !taskId) return;

    const interval = setInterval(async () => {
      try {
        const status = await getGenerationStatus(taskId);
        setProgress(status.progress);
        setGenMessage(status.message);

        if (status.status === 'completed' || status.status === 'done') {
          setPolling(false);
          clearInterval(interval);
          // Navigate to the protocol detail
          if (protocolId) {
            navigate(`/protocols/${protocolId}`);
          }
        } else if (status.status === 'failed' || status.status === 'error') {
          setPolling(false);
          clearInterval(interval);
          setGenMessage(`Generation failed: ${status.message}`);
        }
      } catch {
        // If generation status endpoint not found, just navigate directly
        setPolling(false);
        clearInterval(interval);
        if (protocolId) {
          navigate(`/protocols/${protocolId}`);
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [polling, taskId, protocolId, navigate]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!conditionSlug) return;
    createMutation.mutate();
  }

  if (conditionsLoading) {
    return <LoadingSpinner size="lg" className="mt-20" />;
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-sozo-text">New Protocol</h1>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="condition" className="block text-sm font-medium text-gray-700">
              Condition
            </label>
            <select
              id="condition"
              required
              value={conditionSlug}
              onChange={(e) => setConditionSlug(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
            >
              <option value="">Select a condition...</option>
              {(conditions ?? []).map((c) => (
                <option key={c.slug} value={c.slug}>
                  {c.display_name} ({c.icd10})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="modality" className="block text-sm font-medium text-gray-700">
              Modality (optional)
            </label>
            <select
              id="modality"
              value={modality}
              onChange={(e) => setModality(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
            >
              <option value="">Auto-select (default: tdcs)</option>
              <option value="tdcs">tDCS</option>
              <option value="tps">TPS</option>
              <option value="tavns">tAVNS</option>
              <option value="ces">CES</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="docType" className="block text-sm font-medium text-gray-700">
                Document Type
              </label>
              <select
                id="docType"
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
              >
                <option value="evidence_based_protocol">Evidence-Based Protocol</option>
                <option value="clinical_guideline">Clinical Guideline</option>
                <option value="research_summary">Research Summary</option>
              </select>
            </div>
            <div>
              <label htmlFor="tier" className="block text-sm font-medium text-gray-700">
                Tier
              </label>
              <select
                id="tier"
                value={tier}
                onChange={(e) => setTier(e.target.value)}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
              >
                <option value="fellow">Fellow</option>
                <option value="partners">Partners</option>
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700">
              Custom Prompt (optional)
            </label>
            <textarea
              id="prompt"
              rows={3}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-sozo-secondary focus:outline-none focus:ring-1 focus:ring-sozo-secondary"
              placeholder="Optional: provide a natural-language prompt for LangGraph pipeline..."
            />
          </div>

          {createMutation.isError && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              Failed to create protocol. Please try again.
            </div>
          )}

          {/* Generation progress */}
          {(polling || protocolId) && (
            <div className="rounded-md bg-blue-50 p-4 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-blue-800">
                  {polling ? 'Generating...' : 'Protocol created'}
                </span>
                <span className="text-blue-600">{Math.round(progress * 100)}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-blue-200">
                <div
                  className="h-2 rounded-full bg-blue-600 transition-all duration-500"
                  style={{ width: `${Math.max(progress * 100, 5)}%` }}
                />
              </div>
              <p className="text-xs text-blue-600">{genMessage}</p>
              {protocolId && !polling && (
                <Button
                  type="button"
                  size="sm"
                  onClick={() => navigate(`/protocols/${protocolId}`)}
                >
                  View Protocol
                </Button>
              )}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              isLoading={createMutation.isPending || polling}
              disabled={!conditionSlug}
            >
              Generate Protocol
            </Button>
            <Button type="button" variant="ghost" onClick={() => navigate('/protocols')}>
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
