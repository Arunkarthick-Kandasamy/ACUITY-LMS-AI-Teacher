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

export async function createCourse(data: { code: string; title: string; description?: string; total_duration_hours: number; default_deadline_days: number }) {
  return apiRequest<Record<string, unknown>>('/api/v1/courses', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function publishCourse(courseId: string, is_published: boolean) {
  return apiRequest<Record<string, unknown>>(`/api/v1/courses/${courseId}/publish`, {
    method: 'PATCH',
    body: JSON.stringify({ is_published }),
  })
}

export async function deleteCourse(courseId: string) {
  return apiRequest<{ message: string }>(`/api/v1/courses/${courseId}`, {
    method: 'DELETE',
  })
}

export async function createModule(courseId: string, data: { title: string; description?: string; order_index: number; estimated_duration_hours?: number }) {
  return apiRequest<Record<string, unknown>>(`/api/v1/courses/${courseId}/modules`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteModule(courseId: string, moduleId: string) {
  return apiRequest<{ message: string }>(`/api/v1/courses/${courseId}/modules/${moduleId}`, {
    method: 'DELETE',
  })
}

export async function createLesson(courseId: string, moduleId: string, data: { title: string; description?: string; order_index: number; estimated_duration_minutes?: number }) {
  return apiRequest<Record<string, unknown>>(`/api/v1/courses/${courseId}/modules/${moduleId}/lessons`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteLesson(courseId: string, moduleId: string, lessonId: string) {
  return apiRequest<{ message: string }>(`/api/v1/courses/${courseId}/modules/${moduleId}/lessons/${lessonId}`, {
    method: 'DELETE',
  })
}

export async function getTeacherDashboard() {
  return apiRequest<TeacherDashboardData>('/api/v1/teacher/dashboard')
}
