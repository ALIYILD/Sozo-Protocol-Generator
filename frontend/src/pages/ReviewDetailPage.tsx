import { useMemo, useState, type FormEvent } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { format, parseISO } from 'date-fns';
import { ArrowLeft, ChevronDown, ChevronRight, CheckCircle2 } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  getReviewView,
  getReviewDiff,
  getEvidenceCheck,
  listProtocolReviews,
  submitReviewDecision,
  signProtocol,
  overrideQaIssue,
  type ReviewDecision,
  type ReviewComment,
  type ReviewRecord,
  type QaIssue,
  type SignResult,
} from '../api/reviews';

type BannerState = {
  kind: 'success' | 'error';
  message: string;
} | null;

function formatTs(iso: string): string {
  try {
    return format(parseISO(iso), 'dd MMM yyyy HH:mm');
  } catch {
    return iso;
  }
}

function getErrorMessage(err: unknown): string {
  if (typeof err === 'object' && err !== null) {
    const maybe = err as {
      response?: { data?: { detail?: unknown } };
      message?: string;
    };
    const detail = maybe.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (maybe.message) return maybe.message;
  }
  return 'Something went wrong.';
}

export default function ReviewDetailPage() {
  const { protocolId } = useParams<{ protocolId: string }>();
  const queryClient = useQueryClient();

  const [decision, setDecision] = useState<ReviewDecision>('approve');
  const [overallNotes, setOverallNotes] = useState('');
  const [commentText, setCommentText] = useState('');
  const [commentSeverity, setCommentSeverity] =
    useState<ReviewComment['severity']>('comment');
  const [banner, setBanner] = useState<BannerState>(null);
  const [decisionSubmitted, setDecisionSubmitted] = useState<ReviewRecord | null>(
    null,
  );
  const [signResult, setSignResult] = useState<SignResult | null>(null);

  const [showDiff, setShowDiff] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);
  const [diffFrom, setDiffFrom] = useState(1);
  const [diffTo, setDiffTo] = useState(2);

  const [overrideOpenId, setOverrideOpenId] = useState<string | null>(null);
  const [overrideJustification, setOverrideJustification] = useState('');

  const enabled = Boolean(protocolId);

  const viewQuery = useQuery({
    queryKey: ['review-view', protocolId],
    queryFn: () => getReviewView(protocolId as string),
    enabled,
  });

  const reviewsQuery = useQuery({
    queryKey: ['review-history', protocolId],
    queryFn: () => listProtocolReviews(protocolId as string),
    enabled,
  });

  const diffQuery = useQuery({
    queryKey: ['review-diff', protocolId, diffFrom, diffTo],
    queryFn: () => getReviewDiff(protocolId as string, diffFrom, diffTo),
    enabled: enabled && showDiff && diffFrom < diffTo,
  });

  const evidenceQuery = useQuery({
    queryKey: ['review-evidence-check', protocolId],
    queryFn: () => getEvidenceCheck(protocolId as string),
    enabled: enabled && showEvidence,
  });

  const submitMutation = useMutation({
    mutationFn: (payload: {
      decision: ReviewDecision;
      comments: ReviewComment[];
      overall_notes: string | null;
    }) => submitReviewDecision(protocolId as string, payload),
    onSuccess: (record) => {
      setDecisionSubmitted(record);
      setBanner({
        kind: 'success',
        message: `Review submitted successfully (${record.status}).`,
      });
      queryClient.invalidateQueries({ queryKey: ['review-queue'] });
      queryClient.invalidateQueries({ queryKey: ['review-queue-count'] });
      queryClient.invalidateQueries({ queryKey: ['review-history', protocolId] });
    },
    onError: (err) => {
      setBanner({ kind: 'error', message: getErrorMessage(err) });
    },
  });

  const signMutation = useMutation({
    mutationFn: () => signProtocol(protocolId as string),
    onSuccess: (res) => {
      setSignResult(res);
      setBanner({
        kind: 'success',
        message: `Protocol signed. Hash: ${res.signature_hash.slice(0, 16)}…`,
      });
      queryClient.invalidateQueries({ queryKey: ['review-queue'] });
    },
    onError: (err) => {
      setBanner({ kind: 'error', message: getErrorMessage(err) });
    },
  });

  const overrideMutation = useMutation({
    mutationFn: (vars: { issueId: string; justification: string }) =>
      overrideQaIssue(protocolId as string, vars.issueId, vars.justification),
    onSuccess: () => {
      setOverrideOpenId(null);
      setOverrideJustification('');
      setBanner({ kind: 'success', message: 'QA issue overridden.' });
      queryClient.invalidateQueries({ queryKey: ['review-view', protocolId] });
    },
    onError: (err) => {
      setBanner({ kind: 'error', message: getErrorMessage(err) });
    },
  });

  const bundle = viewQuery.data;
  const qaIssues: QaIssue[] = useMemo(
    () => bundle?.qa_report?.issues ?? [],
    [bundle],
  );

  const handleSubmitDecision = (e: FormEvent) => {
    e.preventDefault();
    setBanner(null);
    const comments: ReviewComment[] = [];
    if (commentText.trim()) {
      comments.push({
        section_slug: null,
        text: commentText.trim(),
        severity: commentSeverity,
      });
    }
    submitMutation.mutate({
      decision,
      comments,
      overall_notes: overallNotes.trim() || null,
    });
  };

  if (!protocolId) {
    return (
      <div className="mt-20 text-center text-red-600">
        Missing protocol id in URL.
      </div>
    );
  }

  if (viewQuery.isLoading) return <LoadingSpinner size="lg" className="mt-20" />;

  if (viewQuery.error || !bundle) {
    return (
      <div className="mt-20 text-center">
        <p className="text-red-600">Failed to load review data.</p>
        <p className="text-sm text-gray-500 mt-1">
          {getErrorMessage(viewQuery.error)}
        </p>
        <Link
          to="/reviews"
          className="mt-4 inline-block text-sm text-sozo-primary hover:underline"
        >
          Back to queue
        </Link>
      </div>
    );
  }

  const approveDone = decisionSubmitted?.status === 'approve';
  const conditionName =
    (bundle.condition?.display_name as string | undefined) ?? 'Protocol';
  const modalityName =
    (bundle.modality?.display_name as string | undefined) ?? '';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Link
            to="/reviews"
            className="inline-flex items-center text-sm text-gray-500 hover:text-sozo-primary"
          >
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back to queue
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-sozo-text">
            {conditionName}
          </h1>
          <p className="text-sm text-gray-500">
            {modalityName} · version {bundle.version}
          </p>
        </div>
      </div>

      {banner && (
        <div
          className={
            banner.kind === 'success'
              ? 'rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800'
              : 'rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800'
          }
          role="status"
        >
          {banner.message}
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card title="Evidence summary">
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Total citations</dt>
              <dd className="font-medium">
                {bundle.evidence_summary?.total_citations ?? '—'}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Level I / II / III</dt>
              <dd className="font-medium">
                {bundle.evidence_summary?.level_I ?? 0} /{' '}
                {bundle.evidence_summary?.level_II ?? 0} /{' '}
                {bundle.evidence_summary?.level_III ?? 0}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Coverage</dt>
              <dd className="font-medium">
                {bundle.evidence_summary?.coverage_pct ?? 0}%
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Safety">
          <dl className="space-y-1 text-sm">
            <div>
              <dt className="text-gray-500">Contraindications</dt>
              <dd className="font-medium">
                {bundle.safety?.contraindications?.length ?? 0}
              </dd>
            </div>
            <div>
              <dt className="text-gray-500">Warnings</dt>
              <dd className="font-medium">
                {bundle.safety?.warnings?.length ?? 0}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="QA report">
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Total issues</dt>
              <dd className="font-medium">{bundle.qa_report?.total_issues ?? 0}</dd>
            </div>
            {bundle.qa_report?.by_severity &&
              Object.entries(bundle.qa_report.by_severity).map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <dt className="text-gray-500">{k}</dt>
                  <dd className="font-medium">{v}</dd>
                </div>
              ))}
          </dl>
        </Card>
      </div>

      {/* Sections */}
      <Card title="Protocol sections">
        <ul className="divide-y divide-gray-100">
          {bundle.sections.map((s) => (
            <li key={s.slug} className="py-3">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-semibold text-sozo-text">{s.title}</h4>
                {s.qa_status && (
                  <span
                    className={
                      s.qa_status === 'pass'
                        ? 'text-xs font-medium text-green-700'
                        : s.qa_status === 'warning'
                          ? 'text-xs font-medium text-yellow-700'
                          : 'text-xs font-medium text-red-700'
                    }
                  >
                    {s.qa_status}
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm text-gray-600">{s.content}</p>
              {s.evidence_citations.length > 0 && (
                <p className="mt-1 text-xs text-gray-500">
                  {s.evidence_citations.length} citation(s)
                </p>
              )}
            </li>
          ))}
        </ul>
      </Card>

      {/* QA issues with override */}
      {qaIssues.length > 0 && (
        <Card title="QA issues">
          <ul className="space-y-3">
            {qaIssues.map((issue) => (
              <li
                key={issue.id}
                className="rounded-md border border-gray-200 bg-gray-50 p-3"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-sozo-text">
                      <span className="mr-2 uppercase text-xs text-yellow-700">
                        {issue.severity}
                      </span>
                      {issue.message}
                    </p>
                    {issue.section && (
                      <p className="text-xs text-gray-500">
                        section: {issue.section}
                      </p>
                    )}
                    {issue.overridden && (
                      <p className="mt-1 text-xs text-green-700">Overridden</p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="secondary"
                    disabled={issue.overridden || overrideMutation.isPending}
                    onClick={() => {
                      setOverrideOpenId(
                        overrideOpenId === issue.id ? null : issue.id,
                      );
                      setOverrideJustification('');
                    }}
                  >
                    Override
                  </Button>
                </div>
                {overrideOpenId === issue.id && (
                  <form
                    className="mt-3 space-y-2"
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (overrideJustification.trim().length < 10) return;
                      overrideMutation.mutate({
                        issueId: issue.id,
                        justification: overrideJustification.trim(),
                      });
                    }}
                  >
                    <textarea
                      value={overrideJustification}
                      onChange={(e) => setOverrideJustification(e.target.value)}
                      className="w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
                      rows={2}
                      placeholder="Justification (min 10 chars)"
                    />
                    <div className="flex gap-2">
                      <Button
                        type="submit"
                        size="sm"
                        disabled={
                          overrideJustification.trim().length < 10 ||
                          overrideMutation.isPending
                        }
                        isLoading={overrideMutation.isPending}
                      >
                        Confirm override
                      </Button>
                      <Button
                        type="button"
                        size="sm"
                        variant="ghost"
                        onClick={() => {
                          setOverrideOpenId(null);
                          setOverrideJustification('');
                        }}
                        disabled={overrideMutation.isPending}
                      >
                        Cancel
                      </Button>
                    </div>
                  </form>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Diff section (collapsible) */}
      <Card>
        <button
          type="button"
          className="flex w-full items-center justify-between text-left"
          onClick={() => setShowDiff((v) => !v)}
        >
          <span className="text-lg font-semibold text-sozo-text">
            Version diff
          </span>
          {showDiff ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        {showDiff && (
          <div className="mt-4 space-y-3">
            <div className="flex flex-wrap items-center gap-3">
              <label className="text-xs text-gray-600">
                From version
                <input
                  type="number"
                  min={1}
                  value={diffFrom}
                  onChange={(e) => setDiffFrom(Number(e.target.value) || 1)}
                  className="ml-2 w-20 rounded-md border border-gray-300 px-2 py-1 text-sm"
                />
              </label>
              <label className="text-xs text-gray-600">
                To version
                <input
                  type="number"
                  min={1}
                  value={diffTo}
                  onChange={(e) => setDiffTo(Number(e.target.value) || 1)}
                  className="ml-2 w-20 rounded-md border border-gray-300 px-2 py-1 text-sm"
                />
              </label>
            </div>
            {diffFrom >= diffTo && (
              <p className="text-xs text-red-600">
                from_version must be less than to_version.
              </p>
            )}
            {diffQuery.isLoading && <LoadingSpinner size="sm" />}
            {diffQuery.error && (
              <p className="text-sm text-red-600">
                {getErrorMessage(diffQuery.error)}
              </p>
            )}
            {diffQuery.data && (
              <ul className="space-y-2">
                {diffQuery.data.changes.map((c, idx) => (
                  <li
                    key={`${c.section_slug}-${idx}`}
                    className="rounded-md border border-gray-200 p-3 text-sm"
                  >
                    <p className="font-medium text-sozo-text">
                      {c.section_slug}{' '}
                      <span className="ml-1 text-xs uppercase text-gray-500">
                        {c.change_type}
                      </span>
                    </p>
                    <p className="mt-1 text-gray-600">{c.summary}</p>
                    {c.old_snippet && (
                      <p className="mt-1 font-mono text-xs text-red-700">
                        - {c.old_snippet}
                      </p>
                    )}
                    {c.new_snippet && (
                      <p className="font-mono text-xs text-green-700">
                        + {c.new_snippet}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </Card>

      {/* Evidence check (collapsible) */}
      <Card>
        <button
          type="button"
          className="flex w-full items-center justify-between text-left"
          onClick={() => setShowEvidence((v) => !v)}
        >
          <span className="text-lg font-semibold text-sozo-text">
            Evidence check
          </span>
          {showEvidence ? (
            <ChevronDown className="h-5 w-5 text-gray-400" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-400" />
          )}
        </button>
        {showEvidence && (
          <div className="mt-4 space-y-3">
            {evidenceQuery.isLoading && <LoadingSpinner size="sm" />}
            {evidenceQuery.error && (
              <p className="text-sm text-red-600">
                {getErrorMessage(evidenceQuery.error)}
              </p>
            )}
            {evidenceQuery.data && (
              <>
                <ul className="space-y-2">
                  {evidenceQuery.data.sections.map((s) => (
                    <li
                      key={s.slug}
                      className="rounded-md border border-gray-200 p-3 text-sm"
                    >
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-sozo-text">{s.slug}</p>
                        <span className="text-xs text-gray-500">
                          {s.coverage_pct}% · {s.citations_count} citations
                        </span>
                      </div>
                      {s.low_evidence_claims.length > 0 && (
                        <ul className="mt-2 space-y-1 text-xs text-gray-600">
                          {s.low_evidence_claims.map((lc, i) => (
                            <li key={i}>
                              <span className="font-medium text-yellow-700">
                                [{lc.current_level}]
                              </span>{' '}
                              {lc.claim}
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
                {evidenceQuery.data.contradictions.length > 0 && (
                  <div>
                    <p className="text-sm font-medium text-sozo-text">
                      Contradictions
                    </p>
                    <ul className="mt-1 space-y-1 text-xs text-gray-600">
                      {evidenceQuery.data.contradictions.map((c, i) => (
                        <li key={i}>
                          <span className="text-red-700">A:</span> {c.claim_a}
                          <br />
                          <span className="text-red-700">B:</span> {c.claim_b}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </Card>

      {/* Past reviews */}
      <Card title="Past reviews">
        {reviewsQuery.isLoading && <LoadingSpinner size="sm" />}
        {reviewsQuery.error && (
          <p className="text-sm text-red-600">
            {getErrorMessage(reviewsQuery.error)}
          </p>
        )}
        {reviewsQuery.data && reviewsQuery.data.reviews.length === 0 && (
          <p className="text-sm text-gray-500">No previous reviews.</p>
        )}
        {reviewsQuery.data && reviewsQuery.data.reviews.length > 0 && (
          <ul className="space-y-3">
            {reviewsQuery.data.reviews.map((r) => (
              <li
                key={r.review_id}
                className="rounded-md border border-gray-200 p-3 text-sm"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sozo-text">{r.reviewer}</p>
                    <p className="text-xs text-gray-500">
                      v{r.protocol_version} · {formatTs(r.reviewed_at)}
                    </p>
                  </div>
                  <Badge status={r.status} />
                </div>
                {r.overall_notes && (
                  <p className="mt-2 text-sm text-gray-600">{r.overall_notes}</p>
                )}
                {r.comments.length > 0 && (
                  <ul className="mt-2 space-y-1 text-xs text-gray-600">
                    {r.comments.map((c, i) => (
                      <li key={i}>
                        <span className="font-medium">[{c.severity}]</span>{' '}
                        {c.section_slug ? `${c.section_slug}: ` : ''}
                        {c.text}
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>

      {/* Decision form */}
      <Card title="Submit decision">
        <form className="space-y-4" onSubmit={handleSubmitDecision}>
          <fieldset>
            <legend className="text-xs font-medium text-gray-600">
              Decision
            </legend>
            <div className="mt-2 flex flex-wrap gap-4">
              {(
                [
                  { value: 'approve', label: 'Approve' },
                  { value: 'request_revision', label: 'Request revision' },
                  { value: 'reject', label: 'Reject' },
                ] as const
              ).map((opt) => (
                <label
                  key={opt.value}
                  className="inline-flex items-center text-sm"
                >
                  <input
                    type="radio"
                    name="decision"
                    value={opt.value}
                    checked={decision === opt.value}
                    onChange={() => setDecision(opt.value)}
                    className="mr-2"
                  />
                  {opt.label}
                </label>
              ))}
            </div>
          </fieldset>

          <label className="block text-xs font-medium text-gray-600">
            Comment
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              rows={3}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
              placeholder={
                decision === 'reject'
                  ? 'Reason for rejection (required)'
                  : decision === 'request_revision'
                    ? 'Describe required changes'
                    : 'Optional comment'
              }
            />
          </label>

          <label className="block text-xs font-medium text-gray-600">
            Comment severity
            <select
              value={commentSeverity}
              onChange={(e) =>
                setCommentSeverity(
                  e.target.value as ReviewComment['severity'],
                )
              }
              className="mt-1 block w-full max-w-xs rounded-md border border-gray-300 bg-white px-2 py-2 text-sm"
            >
              <option value="comment">comment</option>
              <option value="suggestion">suggestion</option>
              <option value="required_change">required_change</option>
              <option value="blocking">blocking</option>
            </select>
          </label>

          <label className="block text-xs font-medium text-gray-600">
            Overall notes
            <textarea
              value={overallNotes}
              onChange={(e) => setOverallNotes(e.target.value)}
              rows={2}
              className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-2 text-sm"
              placeholder="Optional summary"
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              type="submit"
              disabled={submitMutation.isPending}
              isLoading={submitMutation.isPending}
            >
              Submit review
            </Button>
            <Button
              type="button"
              variant="secondary"
              disabled={!approveDone || signMutation.isPending || Boolean(signResult)}
              isLoading={signMutation.isPending}
              onClick={() => signMutation.mutate()}
            >
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Sign off
            </Button>
            {!approveDone && (
              <span className="text-xs text-gray-500">
                Sign-off enabled after an approve decision is submitted.
              </span>
            )}
            {signResult && (
              <span className="text-xs text-green-700">
                Signed {formatTs(signResult.signed_at)}
              </span>
            )}
          </div>
        </form>
      </Card>
    </div>
  );
}
