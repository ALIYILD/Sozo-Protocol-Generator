import { describe, expect, it } from 'vitest';
import {
  canAccessAdmin,
  canViewAudit,
  canViewStaleness,
} from '../permissions';
import type { User, UserRole } from '../../types';

function makeUser(role: UserRole): User {
  return {
    id: 'u1',
    email: 'u@test',
    name: 'U',
    role,
    active: true,
    created_at: '2020-01-01',
  };
}

describe('permission helpers', () => {
  it.each(['admin', 'operator'] as const)(
    'canViewAudit / canViewStaleness / canAccessAdmin are true for %s',
    (role) => {
      const u = makeUser(role);
      expect(canViewAudit(u)).toBe(true);
      expect(canViewStaleness(u)).toBe(true);
      expect(canAccessAdmin(u)).toBe(true);
    },
  );

  it.each(['clinician', 'reviewer', 'readonly', 'researcher', 'viewer'] as const)(
    'canViewAudit / canViewStaleness / canAccessAdmin are false for %s',
    (role) => {
      const u = makeUser(role);
      expect(canViewAudit(u)).toBe(false);
      expect(canViewStaleness(u)).toBe(false);
      expect(canAccessAdmin(u)).toBe(false);
    },
  );

  it('treats null / undefined user as no access', () => {
    expect(canViewAudit(null)).toBe(false);
    expect(canViewStaleness(undefined)).toBe(false);
    expect(canAccessAdmin(null)).toBe(false);
  });
});
