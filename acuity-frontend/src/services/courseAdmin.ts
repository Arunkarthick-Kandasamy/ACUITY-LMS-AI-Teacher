import { localDb } from './localDb'
import type { ApiResponse, CourseBrief, CourseDetail, DashboardStats, KnowledgeSourceInfo } from './types'

export async function getDashboard() {
  return localDb.getCourseAdminDashboard() as unknown as ApiResponse<DashboardStats>
}

export async function listCourses() {
  return localDb.listCourseAdminCourses() as unknown as ApiResponse<CourseBrief[]>
}

export async function getCourse(courseId: string) {
  return localDb.getCourseAdminCourse(courseId) as unknown as ApiResponse<CourseDetail>
}

export async function getStageDetail(_courseId: string, _stageName: string) {
  return { status: 'success' as const, data: null }
}

export async function createCourse(name: string, description?: string) {
  return localDb.createCourseAdminCourse(name, description) as unknown as ApiResponse<CourseDetail>
}

export async function deleteCourse(courseId: string) {
  return localDb.deleteCourse(courseId) as unknown as ApiResponse<{ message: string }>
}

export async function uploadKnowledgeSource(_courseId: string, file: File) {
  return {
    status: 'success' as const,
    data: {
      id: 'ks_1',
      filename: file.name,
      file_type: file.type,
      file_size: file.size,
      status: 'processed',
      created_at: new Date().toISOString(),
    } as KnowledgeSourceInfo,
  }
}

export async function runStage(_courseId: string, _stageName: string) {
  return { status: 'success' as const, data: null }
}

export async function updateKnowledgeGraph(_courseId: string, _data: Record<string, unknown>) {
  return { status: 'success' as const, data: null }
}

export async function updateProfile(_courseId: string, _data: Record<string, unknown>) {
  return { status: 'success' as const, data: null }
}

export async function updateCourseStructure(_courseId: string, _data: Record<string, unknown>) {
  return { status: 'success' as const, data: null }
}

export async function retryStage(_courseId: string, _stageName: string) {
  return { status: 'success' as const, data: null }
}
