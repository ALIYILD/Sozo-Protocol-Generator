import { describe, expect, it } from 'vitest';
import {
  getProtectedRouteState,
  getRequireRolesState,
} from '../routeGuardState';
import type { User } from '../../types';

const adminUser: User = {
  id: '1',
  email: 'a@b',
  name: 'A',
  role: 'admin',
  active: true,
  created_at: '',
};

describe('getProtectedRouteState', () => {
  it('returns bypass when auth bypass flag is enabled', () => {
    expect(getProtectedRouteState(true, false, false)).toBe('bypass');
  });

  it('returns loading while auth is resolving', () => {
    expect(getProtectedRouteState(false, true, false)).toBe('loading');
  });

  it('returns redirect when not authenticated', () => {
    expect(getProtectedRouteState(false, false, false)).toBe('redirect');
  });

  it('returns allow when authenticated', () => {
    expect(getProtectedRouteState(false, false, true)).toBe('allow');
  });
});

describe('getRequireRolesState', () => {
  it('returns bypass when auth bypass flag is enabled', () => {
    expect(getRequireRolesState(true, true, null, ['admin'])).toBe('bypass');
  });

  it('returns loading while auth is resolving', () => {
    expect(getRequireRolesState(false, true, adminUser, ['admin'])).toBe(
      'loading',
    );
  });

  it('returns forbidden when user is missing', () => {
    expect(getRequireRolesState(false, false, null, ['admin'])).toBe(
      'forbidden',
    );
  });

  it('returns forbidden when role is not allowed', () => {
    const clinician: User = { ...adminUser, role: 'clinician' };
    expect(getRequireRolesState(false, false, clinician, ['admin'])).toBe(
      'forbidden',
    );
  });

  it('returns allow when role matches', () => {
    expect(getRequireRolesState(false, false, adminUser, ['admin'])).toBe(
      'allow',
    );
  });
});
