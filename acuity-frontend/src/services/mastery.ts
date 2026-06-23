import { apiRequest } from './api'
import type { MasteryRecord, MasterySummary } from './types'

export async function getMasteryOverview() {
  return apiRequest<MasteryRecord[]>('/api/v1/mastery')
}

export async function getMasteryByConcept(conceptId: string) {
  return apiRequest<MasteryRecord>(`/api/v1/mastery/concepts/${conceptId}`)
}

export async function getCourseMastery(courseId: string) {
  return apiRequest<MasterySummary>(`/api/v1/mastery/courses/${courseId}`)
}
