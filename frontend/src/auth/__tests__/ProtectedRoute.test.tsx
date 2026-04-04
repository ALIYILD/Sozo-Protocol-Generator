import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ROUTER_V7_FUTURE_FLAGS } from '../../routerFuture';
import type { AuthContextValue } from '../../hooks/useAuth';
import { AuthContext } from '../../hooks/useAuth';
import { ProtectedRoute } from '../ProtectedRoute';
import * as authBypass from '../authBypass';

vi.mock('../authBypass', async (importOriginal) => {
  const mod = await importOriginal<typeof import('../authBypass')>();
  return { ...mod, isAuthBypassEnabled: vi.fn() };
});

const authDefaults: AuthContextValue = {
  user: null,
  isLoading: false,
  isAuthenticated: false,
  login: vi.fn(),
  logout: vi.fn(),
};

function renderProtected(
  auth: Partial<AuthContextValue>,
  bypass: boolean,
) {
  vi.mocked(authBypass.isAuthBypassEnabled).mockReturnValue(bypass);
  return render(
    <MemoryRouter
      initialEntries={['/private']}
      future={ROUTER_V7_FUTURE_FLAGS}
    >
      <AuthContext.Provider value={{ ...authDefaults, ...auth }}>
        <Routes>
          <Route
            path="/private"
            element={
              <ProtectedRoute>
                <div data-testid="private">private</div>
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<div data-testid="login">login</div>} />
        </Routes>
      </AuthContext.Provider>
    </MemoryRouter>,
  );
}

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.mocked(authBypass.isAuthBypassEnabled).mockReset();
  });

  it('renders children when bypass is enabled', () => {
    renderProtected({}, true);
    expect(screen.getByTestId('private')).toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    renderProtected({ isAuthenticated: true, isLoading: false }, false);
    expect(screen.getByTestId('private')).toBeInTheDocument();
  });

  it('shows loading when auth is loading', () => {
    renderProtected({ isLoading: true, isAuthenticated: false }, false);
    expect(document.querySelector('svg.animate-spin')).toBeTruthy();
    expect(screen.queryByTestId('private')).not.toBeInTheDocument();
  });

  it('redirects to login when not authenticated', () => {
    renderProtected({ isLoading: false, isAuthenticated: false }, false);
    expect(screen.getByTestId('login')).toBeInTheDocument();
    expect(screen.queryByTestId('private')).not.toBeInTheDocument();
  });
});
