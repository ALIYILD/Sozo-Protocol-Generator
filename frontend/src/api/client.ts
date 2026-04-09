import axios from 'axios';
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

let refreshInFlight: Promise<string | null> | null = null;

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sozo_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!axios.isAxiosError(error) || error.response?.status !== 401) {
      return Promise.reject(error);
    }
    const url = String(error.config?.url ?? '');
    if (
      url.includes('/auth/login')
      || url.includes('/auth/register')
      || url.includes('/auth/refresh')
    ) {
      return Promise.reject(error);
    }

    const originalRequest = error.config;
    if (!originalRequest) {
      return Promise.reject(error);
    }

    if ((originalRequest as any)._retry) {
      localStorage.removeItem('sozo_token');
      localStorage.removeItem('sozo_refresh_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
      return Promise.reject(error);
    }
    (originalRequest as any)._retry = true;

    const refreshToken = localStorage.getItem('sozo_refresh_token');
    if (!refreshToken) {
      localStorage.removeItem('sozo_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
      return Promise.reject(error);
    }

    if (!refreshInFlight) {
      refreshInFlight = refreshClient
        .post<TokenPair>('/auth/refresh', { refresh_token: refreshToken })
        .then((res) => {
          const next = res.data;
          if (!next?.access_token || !next?.refresh_token) {
            return null;
          }
          localStorage.setItem('sozo_token', next.access_token);
          localStorage.setItem('sozo_refresh_token', next.refresh_token);
          return next.access_token;
        })
        .catch(() => null)
        .finally(() => {
          refreshInFlight = null;
        });
    }

    const nextAccessToken = await refreshInFlight;
    if (!nextAccessToken) {
      localStorage.removeItem('sozo_token');
      localStorage.removeItem('sozo_refresh_token');
      if (!window.location.pathname.startsWith('/login')) {
        window.location.replace('/login');
      }
      return Promise.reject(error);
    }

    originalRequest.headers = originalRequest.headers ?? {};
    originalRequest.headers.Authorization = `Bearer ${nextAccessToken}`;
    return api.request(originalRequest);
  },
);

export default api;
