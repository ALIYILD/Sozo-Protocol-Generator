import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import type { TokenPair } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

const refreshClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let refreshInFlight: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = localStorage.getItem('sozo_refresh_token');
  if (!refreshToken) return null;
  try {
    const res = await refreshClient.post<TokenPair>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    const next = res.data;
    if (!next?.access_token || !next?.refresh_token) return null;
    localStorage.setItem('sozo_token', next.access_token);
    localStorage.setItem('sozo_refresh_token', next.refresh_token);
    return next.access_token;
  } catch {
    return null;
  }
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sozo_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (!axios.isAxiosError(error) || error.response?.status !== 401) {
      return Promise.reject(error);
    }

    const url = String(error.config?.url ?? '');
    if (
      url.includes('/auth/login')
      || url.includes('/auth/signup')
      || url.includes('/auth/register')
    ) {
      return Promise.reject(error);
    }

    if (url.includes('/auth/refresh')) {
      localStorage.removeItem('sozo_token');
      localStorage.removeItem('sozo_refresh_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
      return Promise.reject(error);
    }

    const originalRequest = error.config as RetryConfig | undefined;
    if (!originalRequest || originalRequest._retry) {
      localStorage.removeItem('sozo_token');
      localStorage.removeItem('sozo_refresh_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;
    if (!refreshInFlight) {
      refreshInFlight = refreshAccessToken().finally(() => {
        refreshInFlight = null;
      });
    }
    const newToken = await refreshInFlight;
    if (!newToken) {
      localStorage.removeItem('sozo_token');
      localStorage.removeItem('sozo_refresh_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
      return Promise.reject(error);
    }

    originalRequest.headers = originalRequest.headers ?? {};
    originalRequest.headers.Authorization = `Bearer ${newToken}`;
    return api.request(originalRequest);
  },
);

export default api;
