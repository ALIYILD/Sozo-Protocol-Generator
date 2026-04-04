/**
 * Pure routing guard state — easy to unit test without React.
 */
import type { User, UserRole } from '../types';

export type ProtectedRouteState = 'bypass' | 'loading' | 'redirect' | 'allow';

export function getProtectedRouteState(
  bypassEnabled: boolean,
  isLoading: boolean,
  isAuthenticated: boolean,
): ProtectedRouteState {
  if (bypassEnabled) {
    return 'bypass';
  }
  if (isLoading) {
    return 'loading';
  }
  if (!isAuthenticated) {
    return 'redirect';
  }
  return 'allow';
}

export type RequireRolesState = 'bypass' | 'loading' | 'forbidden' | 'allow';

export function getRequireRolesState(
  bypassEnabled: boolean,
  isLoading: boolean,
  user: User | null,
  roles: UserRole[],
): RequireRolesState {
  if (bypassEnabled) {
    return 'bypass';
  }
  if (isLoading) {
    return 'loading';
  }
  if (!user || !roles.includes(user.role)) {
    return 'forbidden';
  }
  return 'allow';
}
