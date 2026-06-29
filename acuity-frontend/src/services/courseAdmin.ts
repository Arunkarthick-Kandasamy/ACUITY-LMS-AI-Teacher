import { apiRequest } from './api'
import type { CourseBrief, CourseDetail, DashboardStats, KnowledgeSourceInfo, PipelineStageInfo } from './types'

export async function getDashboard() {
  return apiRequest<DashboardStats>('/api/v1/course-admin/dashboard')
}

export async function listCourses() {
  return apiRequest<CourseBrief[]>('/api/v1/course-admin/courses')
}

export async function getCourse(courseId: string) {
  return apiRequest<CourseDetail>(`/api/v1/course-admin/courses/${courseId}`)
}

export async function getStageDetail(courseId: string, stageName: string) {
  return apiRequest<PipelineStageInfo>(`/api/v1/course-admin/courses/${courseId}/stages/${stageName}`)
}

export async function createCourse(name: string, description?: string) {
  return apiRequest<CourseDetail>('/api/v1/course-admin/courses', {
    method: 'POST',
    body: JSON.stringify({ name, description }),
  })
}

export async function deleteCourse(courseId: string) {
  return apiRequest<{ message: string }>(`/api/v1/course-admin/courses/${courseId}`, {
    method: 'DELETE',
  })
}

export async function uploadKnowledgeSource(courseId: string, file: File) {
  const token = localStorage.getItem('access_token')
  const res = await fetch(`http://localhost:8000/api/v1/course-admin/courses/${courseId}/sources`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: (() => { const fd = new FormData(); fd.append('file', file); return fd })(),
  })
  const json = await res.json()
  if (!res.ok) throw new Error(json.error?.message || 'Upload failed')
  return json as { status: string; data: KnowledgeSourceInfo }
}

export async function runStage(courseId: string, stageName: string) {
  return apiRequest<CourseDetail>(
    `/api/v1/course-admin/courses/${courseId}/run/${stageName}`,
    { method: 'POST' }
  )
}

export async function updateKnowledgeGraph(courseId: string, data: Record<string, unknown>) {
  return apiRequest<CourseDetail>(
    `/api/v1/course-admin/courses/${courseId}/knowledge-graph`,
    { method: 'PUT', body: JSON.stringify({ knowledge_graph_data: data }) }
  )
}

export async function updateProfile(courseId: string, data: Record<string, unknown>) {
  return apiRequest<CourseDetail>(
    `/api/v1/course-admin/courses/${courseId}/profile`,
    { method: 'PUT', body: JSON.stringify({ teaching_profile: data }) }
  )
}

export async function updateCourseStructure(courseId: string, data: Record<string, unknown>) {
  return apiRequest<CourseDetail>(
    `/api/v1/course-admin/courses/${courseId}/structure`,
    { method: 'PUT', body: JSON.stringify({ course_structure: data }) }
  )
}

export async function retryStage(courseId: string, stageName: string) {
  return apiRequest<CourseDetail>(
    `/api/v1/course-admin/courses/${courseId}/retry/${stageName}`,
    { method: 'POST' }
  )
}
