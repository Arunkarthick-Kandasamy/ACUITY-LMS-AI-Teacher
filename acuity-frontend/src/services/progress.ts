import { localDb } from './localDb'
import type { ApiResponse, Attempt, CurriculumTree, LessonProgress } from './types'

export async function getCurriculumTree(courseId: string) {
  return localDb.getCurriculumTree(courseId) as unknown as ApiResponse<CurriculumTree>
}

export async function getLessonProgress(lessonId: string) {
  return localDb.getLessonProgress(lessonId) as unknown as ApiResponse<LessonProgress | null>
}

export async function updateLessonProgress(lessonId: string, data: { status?: string; completion_percentage?: number }) {
  return localDb.updateLessonProgress(lessonId, data) as unknown as ApiResponse<LessonProgress>
}

export async function recordAttempt(exerciseId: string, data: { response: string }) {
  return localDb.recordAttempt(exerciseId, data) as unknown as ApiResponse<Attempt>
}

export async function getAttempts(_params?: { page?: number; per_page?: number }) {
  return localDb.getAttempts() as unknown as ApiResponse<Attempt[]>
}
