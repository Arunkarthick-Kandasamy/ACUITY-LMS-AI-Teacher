import { apiRequest } from './api'
import type { AdminDashboardStats, AdminUser, Course } from './types'

export async function getAdminDashboard() {
  return apiRequest<AdminDashboardStats>('/api/v1/admin/dashboard')
}

export async function getAdminUsers(params?: { role?: string; is_active?: boolean; search?: string; page?: number; per_page?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.role) searchParams.set('role', params.role)
  if (params?.is_active !== undefined) searchParams.set('is_active', String(params.is_active))
  if (params?.search) searchParams.set('search', params.search)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.per_page) searchParams.set('per_page', String(params.per_page))
  const qs = searchParams.toString()
  return apiRequest<AdminUser[]>(`/api/v1/admin/users${qs ? `?${qs}` : ''}`)
}

export async function getAdminUser(userId: string) {
  return apiRequest<AdminUser>(`/api/v1/admin/users/${userId}`)
}

export async function getAdminCourseAnalytics(courseId: string) {
  return apiRequest<Record<string, unknown>>(`/api/v1/admin/courses/${courseId}/analytics`)
}
