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

export interface SignupRequest {
  email: string;
  name: string;
  password: string;
}

/** Public self-service signup. Creates a clinician account and returns tokens. */
export async function signup(data: SignupRequest): Promise<TokenPair> {
  const res = await api.post<TokenPair>('/auth/signup', data);
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

export async function logout(): Promise<void> {
  await api.post('/auth/logout');
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

/** Change the current user's password. Returns 204 No Content on success. */
export async function changePassword(data: ChangePasswordRequest): Promise<void> {
  await api.put('/auth/password', data);
}
