import Card from '../components/ui/Card';

export default function AuditLogPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-sozo-text">Audit Log</h1>
      <Card>
        <p className="text-sm text-gray-500">
          Audit logging will capture all protocol changes, review decisions, and user actions.
          This feature is under development.
        </p>
        <div className="mt-4 rounded-md bg-gray-50 p-4">
          <p className="text-xs font-medium text-gray-400">Planned columns:</p>
          <ul className="mt-2 list-inside list-disc text-sm text-gray-500">
            <li>Timestamp</li>
            <li>User</li>
            <li>Action</li>
            <li>Resource</li>
            <li>Details</li>
          </ul>
        </div>
      </Card>
    </div>
  );
}
