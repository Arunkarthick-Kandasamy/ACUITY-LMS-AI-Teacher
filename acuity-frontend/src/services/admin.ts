import { localDb } from './localDb'
import type { AdminDashboardStats, AdminUser, ApiResponse } from './types'

export async function getAdminDashboard() {
  return localDb.getAdminDashboard() as unknown as ApiResponse<AdminDashboardStats>
}

export async function getAdminUsers(_params?: { role?: string; is_active?: boolean; search?: string; page?: number; per_page?: number }) {
  return localDb.getAdminUsers()
}

export async function getAdminUser(userId: string) {
  return localDb.getAdminUser(userId)
}

export async function getAdminCourseAnalytics(courseId: string) {
  return localDb.getAdminCourseAnalytics(courseId)
}
