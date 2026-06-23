import { apiRequest } from './api'
import type { Misconception, ParentDashboardData, ParentStudent } from './types'

export async function getParentStudents() {
  return apiRequest<ParentStudent[]>('/api/v1/parents/students')
}

export async function getParentStudent(studentId: string) {
  return apiRequest<ParentStudent>(`/api/v1/parents/students/${studentId}`)
}

export async function getParentStudentProgress(studentId: string) {
  return apiRequest<Record<string, unknown>>(`/api/v1/parents/students/${studentId}/progress`)
}

export async function getParentStudentCurriculum(studentId: string, courseId: string) {
  return apiRequest<Record<string, unknown>>(`/api/v1/parents/students/${studentId}/curriculum?course_id=${courseId}`)
}

export async function getParentDashboard() {
  return apiRequest<ParentDashboardData>('/api/v1/parents/dashboard')
}

export async function getParentStudentMisconceptions(studentId: string) {
  return apiRequest<Misconception[]>(`/api/v1/parents/students/${studentId}/misconceptions`)
}

export async function getParentStudentSessions(studentId: string, limit = 10) {
  return apiRequest<Record<string, unknown>[]>(`/api/v1/parents/students/${studentId}/sessions?limit=${limit}`)
}

export async function getParentStudentRecentActivity(studentId: string, days = 7) {
  return apiRequest<Record<string, unknown>[]>(`/api/v1/parents/students/${studentId}/recent-activity?days=${days}`)
}
