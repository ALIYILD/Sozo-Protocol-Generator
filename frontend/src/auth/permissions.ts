/**
 * Centralized role checks aligned with sozo_api RBAC (JWT claims).
 */
import type { User, UserRole } from '../types';

/** Roles that may call audit APIs and operator dashboards (VIEW_AUDIT). */
export const ROLES_AUDIT_AND_OPS: UserRole[] = ['admin', 'operator'];

function hasRole(user: User | null | undefined, roles: readonly UserRole[]): boolean {
  return !!user && roles.includes(user.role);
}

/** GET /api/audit/* */
export function canViewAudit(user: User | null | undefined): boolean {
  return hasRole(user, ROLES_AUDIT_AND_OPS);
}

/** GET /api/evidence/staleness and /api/cockpit/* (ops metrics). */
export function canViewStaleness(user: User | null | undefined): boolean {
  return hasRole(user, ROLES_AUDIT_AND_OPS);
}

/** SPA routes under /admin/* (navigation + RequireRoles). */
export function canAccessAdmin(user: User | null | undefined): boolean {
  return hasRole(user, ROLES_AUDIT_AND_OPS);
}
