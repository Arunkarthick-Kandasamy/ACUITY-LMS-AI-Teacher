import { apiRequest } from './api'
import type { Misconception, ParentDashboardData, ParentStudent } from './types'

export async function generateLinkingCode() {
  return apiRequest<{ code: string; expires_at: string }>('/api/v1/parents/link-codes/generate', {
    method: 'POST',
  })
}

export async function linkStudent(code: string, parentEmail?: string) {
  return apiRequest<{ link_id: string; student_id: string; full_name: string; status: string; message: string }>('/api/v1/parents/link', {
    method: 'POST',
    body: JSON.stringify({ code, parent_email: parentEmail }),
  })
}

export async function unlinkStudent(studentId: string) {
  return apiRequest<{ message: string }>(`/api/v1/parents/students/${studentId}`, {
    method: 'DELETE',
  })
}

export async function getPendingRequests() {
  return apiRequest<Array<{ link_id: string; parent_email: string | null; parent_name: string; parent_id: string; requested_at: string }>>('/api/v1/parents/pending-requests')
}

export async function approveLink(linkId: string) {
  return apiRequest<{ link_id: string; status: string; message: string }>(`/api/v1/parents/approve/${linkId}`, {
    method: 'POST',
  })
}

export async function rejectLink(linkId: string) {
  return apiRequest<{ link_id: string; status: string; message: string }>(`/api/v1/parents/reject/${linkId}`, {
    method: 'POST',
  })
}

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

export async function getAuditLog(studentId: string) {
  return apiRequest<Array<{ id: string; action: string; actor_id: string | null; parent_email: string | null; details: string | null; created_at: string }>>(`/api/v1/parents/students/${studentId}/audit-log`)
}
