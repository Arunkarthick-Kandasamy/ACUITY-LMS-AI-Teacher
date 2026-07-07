import { localDb } from './localDb'
import type { ApiResponse } from './types'

let accessToken: string | null = localStorage.getItem('access_token')
let refreshToken: string | null = localStorage.getItem('refresh_token')

export function setTokens(access: string, refresh: string) {
  accessToken = access
  refreshToken = refresh
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

export function clearTokens() {
  accessToken = null
  refreshToken = null
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export function getAccessToken() {
  return accessToken
}

export function getRefreshToken() {
  return refreshToken
}

export async function refreshAccessToken(): Promise<boolean> {
  return true
}

export async function apiRequest<T>(
  _path: string,
  _options: RequestInit = {},
): Promise<ApiResponse<T>> {
  return { status: 'success', data: {} as T }
}

export class ApiError extends Error {
  code: string
  status: number
  details: string[]
  constructor(message: string, code: string, status: number, details: string[] = []) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
    this.details = details
  }
}
