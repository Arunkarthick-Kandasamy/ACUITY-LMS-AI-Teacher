import { localDb } from './localDb'
import type { ApiResponse, Concept, ConceptDetail, ConceptContent, Course, CourseDetail, Example, Exercise, Lesson, Module } from './types'

export async function getCourses(_params?: { is_published?: boolean; search?: string; page?: number; per_page?: number }) {
  return localDb.getCourses() as unknown as ApiResponse<Course[]>
}

export async function getCourse(courseId: string) {
  return localDb.getCourse(courseId) as unknown as ApiResponse<CourseDetail>
}

export async function getCourseModules(courseId: string) {
  return localDb.getCourseModules(courseId)
}

export async function getModuleLessons(moduleId: string) {
  return localDb.getModuleLessons(moduleId)
}

export async function getLesson(lessonId: string) {
  return localDb.getLesson(lessonId)
}

export async function getLessonConcepts(lessonId: string) {
  return localDb.getLessonConcepts(lessonId)
}

export async function getConcept(conceptId: string) {
  return localDb.getConcept(conceptId)
}

export async function getConceptContents(_conceptId: string) {
  return { status: 'success' as const, data: [] as ConceptContent[] }
}

export async function getConceptExercises(conceptId: string) {
  return localDb.getConceptExercises(conceptId)
}

export async function getConceptExamples(_conceptId: string) {
  return { status: 'success' as const, data: [] as Example[] }
}
