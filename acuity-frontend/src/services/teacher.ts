import { localDb } from './localDb'
import type { ApiResponse, AttemptItem, Misconception, SessionItem, TeacherCourse, TeacherDashboardData, TeacherStudent } from './types'

export async function getTeacherStudents() {
  return localDb.getTeacherStudents() as unknown as ApiResponse<TeacherStudent[]>
}

export async function getTeacherStudentProgress(studentId: string) {
  return localDb.getTeacherStudentProgress(studentId)
}

export async function getTeacherStudentMastery(studentId: string) {
  return localDb.getTeacherStudentMastery(studentId)
}

export async function getTeacherStudentMisconceptions(studentId: string) {
  return localDb.getMisconceptions(studentId) as unknown as ApiResponse<Misconception[]>
}

export async function getTeacherStudentSessions(studentId: string, _page = 1, _perPage = 20) {
  return localDb.getTeacherStudentSessions(studentId) as unknown as ApiResponse<SessionItem[]>
}

export async function getTeacherStudentAttempts(studentId: string, _page = 1, _perPage = 20) {
  return localDb.getTeacherStudentAttempts(studentId) as unknown as ApiResponse<AttemptItem[]>
}

export async function getTeacherCourses() {
  return localDb.getTeacherCourses() as unknown as ApiResponse<TeacherCourse[]>
}

export async function createCourse(data: { code: string; title: string; description?: string; total_duration_hours: number; default_deadline_days: number }) {
  return localDb.createCourse(data)
}

export async function publishCourse(courseId: string, _is_published: boolean) {
  const data = await localDb.getCourse(courseId)
  return { status: 'success' as const, data: { published: true } }
}

export async function deleteCourse(courseId: string) {
  return localDb.deleteCourse(courseId)
}

export async function createModule(_courseId: string, data: { title: string; description?: string; order_index: number }) {
  return { status: 'success' as const, data: { module_id: 'new_mod', ...data } }
}

export async function deleteModule(_courseId: string, _moduleId: string) {
  return { status: 'success' as const, data: { message: 'Module deleted' } }
}

export async function createLesson(_courseId: string, _moduleId: string, data: { title: string; order_index: number }) {
  return { status: 'success' as const, data: { lesson_id: 'new_lesson', ...data } }
}

export async function deleteLesson(_courseId: string, _moduleId: string, _lessonId: string) {
  return { status: 'success' as const, data: { message: 'Lesson deleted' } }
}

export async function getTeacherDashboard() {
  return localDb.getTeacherDashboard() as unknown as ApiResponse<TeacherDashboardData>
}
