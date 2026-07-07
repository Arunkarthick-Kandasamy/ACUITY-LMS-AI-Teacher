import { localDb } from './localDb'
import type { ApiResponse, Misconception, ParentDashboardData, ParentStudent } from './types'

export async function generateLinkingCode() {
  return localDb.generateLinkingCode()
}

export async function linkStudent(code: string, _parentEmail?: string) {
  return localDb.linkStudent(code)
}

export async function unlinkStudent(_studentId: string) {
  return { status: 'success' as const, data: { message: 'Student unlinked' } }
}

export async function getPendingRequests() {
  return { status: 'success' as const, data: [] }
}

export async function approveLink(_linkId: string) {
  return { status: 'success' as const, data: { link_id: '', status: 'approved', message: 'Approved' } }
}

export async function rejectLink(_linkId: string) {
  return { status: 'success' as const, data: { link_id: '', status: 'rejected', message: 'Rejected' } }
}

export async function getParentStudents() {
  const data = await localDb.getParentDashboard()
  return { status: 'success' as const, data: data.data.students }
}

export async function getParentStudent(studentId: string) {
  return localDb.getParentStudent(studentId) as unknown as ApiResponse<ParentStudent>
}

export async function getParentStudentProgress(studentId: string) {
  return localDb.getParentStudentProgress(studentId)
}

export async function getParentStudentCurriculum(studentId: string, courseId: string) {
  return localDb.getParentStudentCurriculum(studentId, courseId)
}

export async function getParentDashboard() {
  return localDb.getParentDashboard() as unknown as ApiResponse<ParentDashboardData>
}

export async function getParentStudentMisconceptions(studentId: string) {
  return localDb.getMisconceptions(studentId) as unknown as ApiResponse<Misconception[]>
}

export async function getParentStudentSessions(studentId: string, _limit = 10) {
  return localDb.getParentStudentSessions(studentId)
}

export async function getParentStudentRecentActivity(studentId: string, _days = 7) {
  return localDb.getParentStudentRecentActivity(studentId)
}

export async function getAuditLog(_studentId: string) {
  return { status: 'success' as const, data: [] }
}
