import type { ApiResponse } from './types'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

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

async function refreshAccessToken(): Promise<boolean> {
  if (!refreshToken) return false
  try {
    const res = await fetch(`${BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!res.ok) {
      clearTokens()
      return false
    }
    const json: ApiResponse<{ access_token: string; refresh_token: string }> = await res.json()
    setTokens(json.data.access_token, json.data.refresh_token)
    return true
  } catch {
    clearTokens()
    return false
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<ApiResponse<T>> {
  const url = `${BASE_URL}${path}`
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`
  }

  let res = await fetch(url, { ...options, headers })

  if (res.status === 401 && refreshToken) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      headers['Authorization'] = `Bearer ${accessToken}`
      res = await fetch(url, { ...options, headers })
    }
  }

  const json = await res.json()

  if (!res.ok) {
    throw new ApiError(
      json.error?.message || 'An unexpected error occurred',
      json.error?.code || 'UNKNOWN_ERROR',
      res.status,
      json.error?.details || [],
    )
  }

  return json
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
