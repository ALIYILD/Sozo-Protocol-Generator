import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { createElement } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import type { User, LoginRequest } from '../types';
import * as authApi from '../api/auth';

export interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  signup: (data: authApi.SignupRequest) => Promise<void>;
  logout: () => Promise<void>;
  changePassword: (data: authApi.ChangePasswordRequest) => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  useEffect(() => {
    const token = localStorage.getItem('sozo_token');
    if (token) {
      authApi
        .getMe()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('sozo_token');
          localStorage.removeItem('sozo_refresh_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (data: LoginRequest) => {
    const tokens = await authApi.login(data);
    localStorage.setItem('sozo_token', tokens.access_token);
    localStorage.setItem('sozo_refresh_token', tokens.refresh_token);
    const me = await authApi.getMe();
    setUser(me);
  }, []);

  const signup = useCallback(async (data: authApi.SignupRequest) => {
    const tokens = await authApi.signup(data);
    localStorage.setItem('sozo_token', tokens.access_token);
    localStorage.setItem('sozo_refresh_token', tokens.refresh_token);
    const me = await authApi.getMe();
    setUser(me);
  }, []);

  const changePassword = useCallback(async (data: authApi.ChangePasswordRequest) => {
    await authApi.changePassword(data);
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore server-side failure — we still clear local state so
      // the user isn't stuck on a broken session.
    }
    localStorage.removeItem('sozo_token');
    localStorage.removeItem('sozo_refresh_token');
    setUser(null);
    queryClient.clear();
    navigate('/login');
  }, [navigate, queryClient]);

  return createElement(
    AuthContext.Provider,
    {
      value: {
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
        changePassword,
      },
    },
    children,
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}
