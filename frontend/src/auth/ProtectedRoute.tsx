import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { isAuthBypassEnabled } from './authBypass';
import { getProtectedRouteState } from './routeGuardState';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isLoading, isAuthenticated } = useAuth();
  const state = getProtectedRouteState(
    isAuthBypassEnabled(),
    isLoading,
    isAuthenticated,
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
  return <Navigate to="/login" replace />;
}
