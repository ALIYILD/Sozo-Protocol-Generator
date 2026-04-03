import api from './client';
import type { LoginRequest, RegisterRequest, TokenPair, User } from '../types';

export async function login(data: LoginRequest): Promise<TokenPair> {
  const res = await api.post<TokenPair>('/auth/login', data);
  return res.data;
}

export async function register(data: RegisterRequest): Promise<User> {
  const res = await api.post<User>('/auth/register', data);
  return res.data;
}

export async function refreshToken(refresh_token: string): Promise<TokenPair> {
  const res = await api.post<TokenPair>('/auth/refresh', { refresh_token });
  return res.data;
}

export async function getMe(): Promise<User> {
  const res = await api.get<User>('/auth/me');
  return res.data;
}
