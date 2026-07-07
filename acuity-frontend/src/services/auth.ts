import { setTokens, clearTokens } from './api'
import { localDb } from './localDb'
import type { AuthTokens, LoginResponse, User, UserRole } from './types'

export async function login(email: string, password: string, role: UserRole): Promise<LoginResponse> {
  const data = await localDb.login(email, password, role)
  setTokens(data.access_token, data.refresh_token)
  return data
}

export async function register(email: string, password: string, full_name: string, role: UserRole): Promise<User> {
  const user = await localDb.register(email, password, full_name, role)
  setTokens(`local_token_${user.user_id}`, `local_refresh_${user.user_id}`)
  return user
}

export async function logout(): Promise<void> {
  clearTokens()
}

export async function refreshToken(token: string): Promise<AuthTokens> {
  return { access_token: token, refresh_token: token, token_type: 'bearer', expires_in: 86400 }
}

export async function forgotPassword(_email: string): Promise<void> {}

export async function resetPassword(_token: string, _new_password: string): Promise<void> {}
