import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ROUTER_V7_FUTURE_FLAGS } from '../../routerFuture';
import type { AuthContextValue } from '../../hooks/useAuth';
import { AuthContext } from '../../hooks/useAuth';
import type { User } from '../../types';
import { RequireRoles } from '../RequireRoles';
import * as authBypass from '../authBypass';

vi.mock('../authBypass', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../authBypass')>();
  return { ...mod, isAuthBypassEnabled: vi.fn() };
});

const adminUser: User = {
  id: '1',
  email: 'a@b',
  name: 'A',
  role: 'admin',
  active: true,
  created_at: '',
};

const authDefaults: AuthContextValue = {
  user: null,
  isLoading: false,
  isAuthenticated: false,
  login: vi.fn(),
  logout: vi.fn(),
};

function renderRoles(
  auth: Partial<AuthContextValue>,
  bypass: boolean,
  allowedRoles: Array<'admin' | 'operator'> = ['admin'],
) {
  vi.mocked(authBypass.isAuthBypassEnabled).mockReturnValue(bypass);
  return render(
    <MemoryRouter
      initialEntries={['/secret']}
      future={ROUTER_V7_FUTURE_FLAGS}
    >
      <AuthContext.Provider value={{ ...authDefaults, ...auth }}>
        <Routes>
          <Route
            path="/secret"
            element={
              <RequireRoles roles={allowedRoles}>
                <div data-testid="secret">secret</div>
              </RequireRoles>
            }
          />
          <Route path="/" element={<div data-testid="home">home</div>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>,
  );
}

describe('RequireRoles', () => {
  beforeEach(() => {
    vi.mocked(authBypass.isAuthBypassEnabled).mockReset();
  });

  it('renders children when bypass is enabled', () => {
    renderRoles({ user: null, isLoading: false }, true);
    expect(screen.getByTestId('secret')).toBeInTheDocument();
  });

  it('renders children when user has an allowed role', () => {
    renderRoles(
      { user: adminUser, isLoading: false, isAuthenticated: true },
      false,
    );
    expect(screen.getByTestId('secret')).toBeInTheDocument();
  });

  it('shows loading while auth is resolving', () => {
    renderRoles({ isLoading: true, user: null }, false);
    expect(document.querySelector('svg.animate-spin')).toBeTruthy();
    expect(screen.queryByTestId('secret')).not.toBeInTheDocument();
  });

  it('redirects home when role is not allowed', () => {
    const clinician: User = { ...adminUser, role: 'clinician' };
    renderRoles(
      { user: clinician, isLoading: false, isAuthenticated: true },
      false,
      ['admin'],
    );
    expect(screen.getByTestId('home')).toBeInTheDocument();
    expect(screen.queryByTestId('secret')).not.toBeInTheDocument();
  });
});
