import { localDb } from './localDb'
import type { ApiResponse, MasteryRecord, MasterySummary } from './types'

export async function getMasteryOverview() {
  return localDb.getMasteryOverview() as unknown as ApiResponse<MasteryRecord[]>
}

export async function getMasteryByConcept(conceptId: string) {
  const data = await localDb.getConcept(conceptId)
  const record = data.data.mastery
  return {
    status: 'success' as const,
    data: {
      record_id: conceptId,
      student_id: 'u1',
      concept_id: conceptId,
      concept_title: data.data.title,
      mastery_level: record?.mastery_level || 0,
      total_attempts: record?.total_attempts || 0,
      consecutive_correct: record?.consecutive_correct || 0,
      status: (record?.mastery_level || 0) >= 0.7 ? 'mastered' as const : (record?.mastery_level || 0) >= 0.3 ? 'in_progress' as const : 'not_started' as const,
    },
  }
}

export async function getCourseMastery(courseId: string) {
  return localDb.getCourseMastery(courseId) as unknown as ApiResponse<MasterySummary>
}
