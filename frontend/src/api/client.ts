import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sozo_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!axios.isAxiosError(error) || error.response?.status !== 401) {
      return Promise.reject(error);
    }
    const url = String(error.config?.url ?? '');
    if (url.includes('/auth/login') || url.includes('/auth/register')) {
      return Promise.reject(error);
    }
    localStorage.removeItem('sozo_token');
    localStorage.removeItem('sozo_refresh_token');
    if (!window.location.pathname.startsWith('/login')) {
      window.location.replace('/login');
    }
    return Promise.reject(error);
  },
);

export default api;
