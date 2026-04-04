import { useQuery } from '@tanstack/react-query';
import { getProtocolAudit } from '../../api/protocols';
import { canViewAudit } from '../../auth/permissions';
import { useAuth } from '../../hooks/useAuth';
import Card from '../ui/Card';
import LoadingSpinner from '../ui/LoadingSpinner';

/** Fetches `GET /protocols/:id/audit` only when `canViewAudit(user)`. */
export function ProtocolAuditSection({ protocolId }: { protocolId: string }) {
  const { user } = useAuth();
  const showAuditTrail = canViewAudit(user);

  const { data: auditPayload, isLoading: auditLoading, error: auditError } = useQuery({
    queryKey: ['protocol-audit', protocolId],
    queryFn: () => getProtocolAudit(protocolId),
    enabled: !!protocolId && showAuditTrail,
  });

  if (!showAuditTrail) return null;

  return (
    <Card title="Protocol audit trail">
      {auditLoading && <LoadingSpinner size="md" />}
      {auditError && (
        <p className="text-sm text-red-600">Could not load protocol audit data.</p>
      )}
      {auditPayload != null && !auditLoading && (
        <pre className="max-h-[320px] overflow-auto rounded-md bg-gray-50 p-4 text-xs text-gray-700">
          {JSON.stringify(auditPayload, null, 2)}
        </pre>
      )}
    </Card>
  );
}
