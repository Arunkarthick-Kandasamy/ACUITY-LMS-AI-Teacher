import { apiRequest } from './api'
import type { ApiResponse, Concept, ConceptDetail, ConceptContent, Course, CourseDetail, Example, Exercise, Lesson, Module } from './types'

export async function getCourses(params?: { is_published?: boolean; search?: string; page?: number; per_page?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.is_published !== undefined) searchParams.set('is_published', String(params.is_published))
  if (params?.search) searchParams.set('search', params.search)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.per_page) searchParams.set('per_page', String(params.per_page))
  const qs = searchParams.toString()
  return apiRequest<Course[]>(`/api/v1/courses${qs ? `?${qs}` : ''}`)
}

export async function getCourse(courseId: string) {
  return apiRequest<CourseDetail>(`/api/v1/courses/${courseId}`)
}

export async function createCourse(data: { code: string; title: string; description?: string; total_duration_hours: number; default_deadline_days: number }) {
  return apiRequest<Course>('/api/v1/courses', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getCourseModules(courseId: string) {
  return apiRequest<Module[]>(`/api/v1/courses/${courseId}/modules`)
}

export async function getModuleLessons(moduleId: string) {
  return apiRequest<Lesson[]>(`/api/v1/modules/${moduleId}/lessons`)
}

export async function getLesson(lessonId: string) {
  return apiRequest<Lesson>(`/api/v1/lessons/${lessonId}`)
}

export async function getLessonConcepts(lessonId: string) {
  return apiRequest<Concept[]>(`/api/v1/lessons/${lessonId}/concepts`)
}

export async function getConcept(conceptId: string) {
  return apiRequest<ConceptDetail>(`/api/v1/concepts/${conceptId}`)
}

export async function getConceptContents(conceptId: string) {
  return apiRequest<ConceptContent[]>(`/api/v1/concepts/${conceptId}/contents`)
}

export async function getConceptExercises(conceptId: string) {
  return apiRequest<Exercise[]>(`/api/v1/concepts/${conceptId}/exercises`)
}

export async function getConceptExamples(conceptId: string) {
  return apiRequest<Example[]>(`/api/v1/concepts/${conceptId}/examples`)
}
