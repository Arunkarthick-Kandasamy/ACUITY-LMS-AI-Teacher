import { apiRequest } from './api'
import type { Attempt, CurriculumTree, LessonProgress } from './types'

export async function getCurriculumTree(courseId: string) {
  return apiRequest<CurriculumTree>(`/api/v1/courses/${courseId}/curriculum`)
}

export async function getLessonProgress(lessonId: string) {
  return apiRequest<LessonProgress | null>(`/api/v1/lessons/${lessonId}/progress`)
}

export async function updateLessonProgress(lessonId: string, data: { status?: string; completion_percentage?: number }) {
  return apiRequest<LessonProgress>(`/api/v1/lessons/${lessonId}/progress`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  })
}

export async function recordAttempt(exerciseId: string, data: { response: string }) {
  return apiRequest<Attempt>(`/api/v1/exercises/${exerciseId}/attempts`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getAttempts(params?: { page?: number; per_page?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.per_page) searchParams.set('per_page', String(params.per_page))
  const qs = searchParams.toString()
  return apiRequest<Attempt[]>(`/api/v1/attempts${qs ? `?${qs}` : ''}`)
}
