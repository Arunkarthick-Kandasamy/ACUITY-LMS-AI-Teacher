import { apiRequest } from './api'
import type { AttemptItem, Misconception, SessionItem, TeacherCourse, TeacherDashboardData, TeacherStudent } from './types'

export async function getTeacherStudents() {
  return apiRequest<TeacherStudent[]>('/api/v1/teacher/students')
}

export async function getTeacherStudentProgress(studentId: string) {
  return apiRequest<Record<string, unknown>>(`/api/v1/teacher/students/${studentId}/progress`)
}

export async function getTeacherStudentMastery(studentId: string) {
  return apiRequest<Record<string, unknown>>(`/api/v1/teacher/students/${studentId}/mastery`)
}

export async function getTeacherStudentMisconceptions(studentId: string) {
  return apiRequest<Misconception[]>(`/api/v1/teacher/students/${studentId}/misconceptions`)
}

export async function getTeacherStudentSessions(studentId: string, page = 1, perPage = 20) {
  return apiRequest<SessionItem[]>(`/api/v1/teacher/students/${studentId}/sessions?page=${page}&per_page=${perPage}`)
}

export async function getTeacherStudentAttempts(studentId: string, page = 1, perPage = 20) {
  return apiRequest<AttemptItem[]>(`/api/v1/teacher/students/${studentId}/attempts?page=${page}&per_page=${perPage}`)
}

export async function getTeacherCourses() {
  return apiRequest<TeacherCourse[]>('/api/v1/teacher/courses')
}

export async function getTeacherDashboard() {
  return apiRequest<TeacherDashboardData>('/api/v1/teacher/dashboard')
}
