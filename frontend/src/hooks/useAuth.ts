import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react';
import { createElement } from 'react';
import type { User, LoginRequest } from '../types';
import * as authApi from '../api/auth';

export interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

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

  const logout = useCallback(() => {
    localStorage.removeItem('sozo_token');
    localStorage.removeItem('sozo_refresh_token');
    setUser(null);
    window.location.href = '/login';
  }, []);

  return createElement(
    AuthContext.Provider,
    {
      value: {
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        logout,
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
