import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import type { UserRole } from '../types';
import { isAuthBypassEnabled } from './authBypass';
import { getRequireRolesState } from './routeGuardState';

export function RequireRoles({
  roles,
  children,
}: {
  roles: UserRole[];
  children: React.ReactNode;
}) {
  const { user, isLoading } = useAuth();
  const state = getRequireRolesState(
    isAuthBypassEnabled(),
    isLoading,
    user,
    roles,
  );

  if (state === 'bypass' || state === 'allow') {
    return <>{children}</>;
  }
  if (state === 'loading') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-sozo-surface">
        <LoadingSpinner size="lg" />
      </div>
    );
  }
  return <Navigate to="/" replace />;
}
