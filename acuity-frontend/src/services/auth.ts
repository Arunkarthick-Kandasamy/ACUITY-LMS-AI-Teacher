import { apiRequest, setTokens, clearTokens } from './api'
import type { ApiResponse, AuthTokens, LoginResponse, User, UserRole } from './types'

export async function login(email: string, password: string): Promise<LoginResponse> {
  const json = await apiRequest<LoginResponse>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  setTokens(json.data.access_token, json.data.refresh_token)
  return json.data
}

export async function register(
  email: string,
  password: string,
  full_name: string,
  role: UserRole,
): Promise<User> {
  const json = await apiRequest<User>('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, role }),
  })
  return json.data
}

export async function logout(): Promise<void> {
  try {
    await apiRequest<{ message: string }>('/api/v1/auth/logout', { method: 'POST' })
  } finally {
    clearTokens()
  }
}

export async function refreshToken(token: string): Promise<AuthTokens> {
  const json = await apiRequest<AuthTokens>('/api/v1/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: token }),
  })
  return json.data
}

export async function forgotPassword(email: string): Promise<void> {
  await apiRequest<{ message: string }>('/api/v1/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function resetPassword(token: string, new_password: string): Promise<void> {
  await apiRequest<{ message: string }>('/api/v1/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password }),
  })
}
