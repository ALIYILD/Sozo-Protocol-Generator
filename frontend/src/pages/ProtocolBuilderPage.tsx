import { useState, useEffect, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { listConditions } from '../api/evidence';
import {
  createProtocol,
  getGenerationStatus,
  listProtocolTemplates,
  cloneProtocol,
} from '../api/protocols';
import { generateProtocol, getGraphStatus } from '../api/graph';
import type { GraphGenerateResponse } from '../api/graph';
import type {
  ProtocolCreateResponse,
  ProtocolListItem,
  GraphStatusResponse,
} from '../types';

/** Terminal graph statuses — polling stops when we see one of these. */
const TERMINAL_STATUSES = new Set([
  'complete',
  'completed',
  'failed',
  'error',
  'cancelled',
  'canceled',
  'awaiting_review',
  'pending_review',
]);

function isTerminalStatus(status: string | undefined): boolean {
  return !!status && TERMINAL_STATUSES.has(status);
}

function progressLabel(status: string | undefined): string {
  switch (status) {
    case 'queued':
      return 'Waiting for a worker…';
    case 'running':
    case 'in_progress':
      return 'Generating protocol… (evidence pipeline + LLM synthesis can take 1–3 minutes)';
    case 'complete':
    case 'completed':
    case 'awaiting_review':
    case 'pending_review':
      return 'Complete — ready for review';
    case 'failed':
    case 'error':
      return 'Generation failed';
    case 'cancelled':
    case 'canceled':
      return 'Generation cancelled';
    default:
      return status ? `Status: ${status}` : 'Starting…';
  }
}

function formatElapsed(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

export default function ProtocolBuilderPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [cloningId, setCloningId] = useState<string | null>(null);
  const [conditionSlug, setConditionSlug] = useState('');
  const [modality, setModality] = useState('');
  const [docType, setDocType] = useState('evidence_based_protocol');
  const [tier, setTier] = useState('fellow');
  const [prompt, setPrompt] = useState('');
  const [useGraphPipeline, setUseGraphPipeline] = useState(true);

  // Patient context (for graph pipeline)
  const [patientAge, setPatientAge] = useState<number | undefined>();
  const [patientSex, setPatientSex] = useState('');
  const [medications, setMedications] = useState('');
  const [contraindications, setContraindications] = useState('');

  // Legacy generation tracking
  const [taskId, setTaskId] = useState<string | null>(null);
  const [protocolId, setProtocolId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [genMessage, setGenMessage] = useState('');
  const [polling, setPolling] = useState(false);

  // Graph pipeline state
  const [threadId, setThreadId] = useState<string | null>(null);
  const [graphResult, setGraphResult] = useState<GraphGenerateResponse | null>(null);
  const [graphStatus, setGraphStatus] = useState<string>('queued');
  const [graphStatusData, setGraphStatusData] = useState<GraphStatusResponse | null>(null);
  const [graphError, setGraphError] = useState<string | null>(null);
  const [graphStartedAt, setGraphStartedAt] = useState<number | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const { data: conditions, isLoading: conditionsLoading } = useQuery({
    queryKey: ['conditions'],
    queryFn: listConditions,
  });

  const {
    data: templates,
    isLoading: templatesLoading,
    isError: templatesError,
  } = useQuery({
    queryKey: ['protocols', 'templates'],
    queryFn: listProtocolTemplates,
  });

  const cloneMutation = useMutation({
    mutationFn: (templateId: string) => cloneProtocol(templateId),
    onMutate: (templateId: string) => {
      setCloningId(templateId);
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['protocols'] });
      const newId = (data as { protocol_id?: string }).protocol_id;
      setCloningId(null);
      if (newId) {
        navigate(`/protocols/${newId}`);
      }
    },
    onError: () => {
      setCloningId(null);
    },
  });

  // Legacy mutation
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

  // Graph pipeline mutation
  const graphMutation = useMutation({
    mutationFn: () => {
      const patientContext = (patientAge || patientSex || medications || contraindications) ? {
        age: patientAge,
        sex: patientSex || undefined,
        current_medications: medications ? medications.split(',').map(s => s.trim()).filter(Boolean) : undefined,
        contraindications: contraindications ? contraindications.split(',').map(s => s.trim()).filter(Boolean) : undefined,
      } : undefined;

      return generateProtocol({
        condition_slug: conditionSlug,
        modality: modality || undefined,
        tier,
        doc_type: docType,
        prompt: prompt || `Generate ${docType} for ${conditionSlug}`,
        patient_context: patientContext,
      });
    },
    onSuccess: (data: GraphGenerateResponse) => {
      setThreadId(data.thread_id);
      setGraphResult(data);
      setGraphStatus(data.status || 'queued');
      setGraphStatusData(null);
      setGraphError(null);
      setGraphStartedAt(Date.now());
      setElapsedSeconds(0);
    },
    onError: () => {
      setGraphStartedAt(null);
    },
  });

  // Poll legacy generation status
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
          if (protocolId) navigate(`/protocols/${protocolId}`);
        } else if (status.status === 'failed' || status.status === 'error') {
          setPolling(false);
          clearInterval(interval);
          setGenMessage(`Generation failed: ${status.message}`);
        }
      } catch {
        setPolling(false);
        clearInterval(interval);
        if (protocolId) navigate(`/protocols/${protocolId}`);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [polling, taskId, protocolId, navigate]);

  // Elapsed-time counter — runs while a thread is active and not terminal.
  useEffect(() => {
    if (!graphStartedAt) return;
    if (isTerminalStatus(graphStatus)) return;
    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - graphStartedAt) / 1000));
    }, 1000);
    return () => clearInterval(interval);
  }, [graphStartedAt, graphStatus]);

  // Poll graph status every 2s while queued/running. The first few polls may
  // race the Celery worker creating the checkpoint — getGraphStatus returns
  // null on 404 and we silently retry for up to ~10s before surfacing it.
  useEffect(() => {
    if (!threadId) return;
    if (isTerminalStatus(graphStatus)) return;

    let cancelled = false;
    let notFoundStreak = 0;
    const MAX_NOT_FOUND_STREAK = 5; // ~10s of grace

    const poll = async () => {
      try {
        const status = await getGraphStatus(threadId);
        if (cancelled) return;

        if (!status) {
          notFoundStreak += 1;
          if (notFoundStreak > MAX_NOT_FOUND_STREAK) {
            setGraphError('Thread not found after multiple retries.');
            setGraphStatus('failed');
          }
          return;
        }

        notFoundStreak = 0;
        setGraphStatusData(status);
        setGraphStatus(status.status);

        if (status.status === 'failed' || status.status === 'error') {
          const msg =
            (status.output && typeof status.output === 'object'
              ? (status.output as Record<string, unknown>).error
              : undefined) ??
            (status.output && typeof status.output === 'object'
              ? (status.output as Record<string, unknown>).message
              : undefined);
          setGraphError(typeof msg === 'string' ? msg : 'Generation failed.');
          return;
        }

        if (
          status.status === 'complete' ||
          status.status === 'completed' ||
          status.status === 'awaiting_review' ||
          status.status === 'pending_review'
        ) {
          // Preserve existing navigate-to-review behavior.
          navigate(`/review/${threadId}`);
        }
      } catch (err) {
        if (cancelled) return;
        setGraphError(err instanceof Error ? err.message : 'Status poll failed.');
        setGraphStatus('failed');
      }
    };

    // Kick off an immediate poll, then on an interval.
    void poll();
    const interval = setInterval(poll, 2000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [threadId, graphStatus, navigate]);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!conditionSlug) return;
    if (useGraphPipeline) {
      graphMutation.mutate();
    } else {
      createMutation.mutate();
    }
  }

  if (conditionsLoading) {
    return <LoadingSpinner size="lg" className="mt-20" />;
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-sozo-text">New Protocol</h1>

      <Card>
        <div className="space-y-4">
          <div>
            <h2 className="text-lg font-semibold text-sozo-text">Start from a template</h2>
            <p className="text-xs text-gray-500">
              Clone a curated template to bootstrap your protocol, or fill in the form below to start from scratch.
            </p>
          </div>

          {templatesLoading && (
            <div className="flex justify-center py-4">
              <LoadingSpinner size="md" />
            </div>
          )}

          {templatesError && !templatesLoading && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              Failed to load templates. You can still create a protocol manually below.
            </div>
          )}

          {!templatesLoading && !templatesError && (templates?.length ?? 0) === 0 && (
            <div className="rounded-md bg-gray-50 p-3 text-sm text-gray-600">
              No templates available yet. Use the form below to create a protocol from scratch.
            </div>
          )}

          {!templatesLoading && !templatesError && (templates?.length ?? 0) > 0 && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {(templates ?? []).map((t: ProtocolListItem) => {
                const isCloning = cloningId === t.protocol_id && cloneMutation.isPending;
                return (
                  <div
                    key={t.protocol_id}
                    className="flex flex-col justify-between rounded-lg border border-gray-200 p-3 hover:border-sozo-secondary"
                  >
                    <div className="space-y-1">
                      <div className="text-sm font-semibold text-sozo-text">
                        {t.condition_name}
                      </div>
                      <div className="flex flex-wrap gap-1 text-xs text-gray-500">
                        <span className="rounded bg-gray-100 px-1.5 py-0.5 uppercase">
                          {t.modality}
                        </span>
                        <span className="rounded bg-gray-100 px-1.5 py-0.5">
                          {t.evidence_level}
                        </span>
                        <span className="rounded bg-gray-100 px-1.5 py-0.5">
                          v{t.version}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600">
                        {t.condition_slug}
                      </div>
                    </div>
                    <div className="mt-3">
                      <Button
                        type="button"
                        size="sm"
                        isLoading={isCloning}
                        disabled={cloneMutation.isPending}
                        onClick={() => cloneMutation.mutate(t.protocol_id)}
                      >
                        Clone
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {cloneMutation.isError && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              Failed to clone template. Please try again.
            </div>
          )}
        </div>
      </Card>

      <Card>
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Pipeline toggle */}
          <div className="flex items-center gap-3 rounded-lg bg-blue-50 p-3">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={useGraphPipeline}
                onChange={(e) => setUseGraphPipeline(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-gray-300 rounded-full peer peer-checked:bg-blue-600 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-full" />
            </label>
            <span className="text-sm font-medium text-blue-800">
              {useGraphPipeline ? 'LangGraph Pipeline' : 'Legacy Generation'}
            </span>
            {useGraphPipeline && (
              <span className="text-xs text-blue-600">
                Evidence search + Safety gates + Clinician review
              </span>
            )}
          </div>

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
              <option value="">Auto-select</option>
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
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
              >
                <option value="evidence_based_protocol">Evidence-Based Protocol</option>
                <option value="all_in_one_protocol">All-in-One Protocol</option>
                <option value="clinical_exam">Clinical Exam</option>
                <option value="handbook">Handbook</option>
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
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
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
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm"
              placeholder="Optional: describe what you need in plain English..."
            />
          </div>

          {/* Patient context (graph pipeline only) */}
          {useGraphPipeline && (
            <div className="rounded-lg border border-gray-200 p-4 space-y-3">
              <h3 className="text-sm font-medium text-gray-700">Patient Context (optional)</h3>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500">Age</label>
                  <input
                    type="number"
                    value={patientAge ?? ''}
                    onChange={(e) => setPatientAge(e.target.value ? Number(e.target.value) : undefined)}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                    placeholder="e.g. 55"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500">Sex</label>
                  <select
                    value={patientSex}
                    onChange={(e) => setPatientSex(e.target.value)}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                  >
                    <option value="">Not specified</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-gray-500">Current Medications (comma-separated)</label>
                <input
                  type="text"
                  value={medications}
                  onChange={(e) => setMedications(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                  placeholder="e.g. sertraline, levodopa"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500">Known Contraindications (comma-separated)</label>
                <input
                  type="text"
                  value={contraindications}
                  onChange={(e) => setContraindications(e.target.value)}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
                  placeholder="e.g. metallic_cranial_implant"
                />
              </div>
            </div>
          )}

          {/* Error display */}
          {(createMutation.isError || graphMutation.isError) && (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              Failed to create protocol. Please try again.
            </div>
          )}

          {/* Legacy progress */}
          {!useGraphPipeline && (polling || protocolId) && (
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
            </div>
          )}

          {/* Graph pipeline progress panel */}
          {useGraphPipeline && graphResult && threadId && (
            <div
              className={`rounded-md p-4 space-y-3 ${
                graphStatus === 'failed' || graphStatus === 'error'
                  ? 'bg-red-50'
                  : isTerminalStatus(graphStatus)
                    ? 'bg-green-50'
                    : 'bg-blue-50'
              }`}
            >
              <div className="flex items-center gap-3">
                {!isTerminalStatus(graphStatus) && <LoadingSpinner size="sm" />}
                <div className="flex-1">
                  <div
                    className={`text-sm font-semibold ${
                      graphStatus === 'failed' || graphStatus === 'error'
                        ? 'text-red-800'
                        : isTerminalStatus(graphStatus)
                          ? 'text-green-800'
                          : 'text-blue-800'
                    }`}
                  >
                    {progressLabel(graphStatus)}
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-gray-600">
                    <span>
                      Elapsed: <span className="font-mono">{formatElapsed(elapsedSeconds)}</span>
                    </span>
                    <span className="text-gray-300">|</span>
                    <span>
                      Thread: <code className="font-mono text-[11px]">{threadId}</code>
                    </span>
                  </div>
                </div>
              </div>

              {graphError && (
                <div className="rounded bg-red-100 p-2 text-xs text-red-800">
                  {graphError}
                </div>
              )}

              {graphStatusData && isTerminalStatus(graphStatus) && graphStatus !== 'failed' && graphStatus !== 'error' && (
                <>
                  <div className="grid grid-cols-3 gap-3 text-center text-xs">
                    <div>
                      <div className="text-lg font-bold text-green-700">
                        {graphStatusData.evidence.article_count}
                      </div>
                      <div className="text-gray-500">Articles</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-green-700">
                        {graphStatusData.safety.cleared ? 'Cleared' : 'BLOCKED'}
                      </div>
                      <div className="text-gray-500">Safety</div>
                    </div>
                    <div>
                      <div className="text-lg font-bold text-green-700">
                        {graphStatusData.protocol.sections.length}
                      </div>
                      <div className="text-gray-500">Sections</div>
                    </div>
                  </div>
                  {graphStatusData.safety.off_label.length > 0 && (
                    <div className="text-xs text-amber-700 bg-amber-50 rounded p-2">
                      Off-label: {graphStatusData.safety.off_label.join('; ')}
                    </div>
                  )}
                  <Button
                    type="button"
                    size="sm"
                    onClick={() => navigate(`/review/${threadId}`)}
                  >
                    Review Protocol
                  </Button>
                </>
              )}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button
              type="submit"
              isLoading={
                createMutation.isPending ||
                graphMutation.isPending ||
                polling ||
                (useGraphPipeline && !!threadId && !isTerminalStatus(graphStatus))
              }
              disabled={!conditionSlug}
            >
              {useGraphPipeline ? 'Run Graph Pipeline' : 'Generate Protocol'}
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
