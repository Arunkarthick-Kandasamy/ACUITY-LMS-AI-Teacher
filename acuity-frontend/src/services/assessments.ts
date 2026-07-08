import { localDb } from './localDb'
import type {
  ApiResponse, Assessment, AssessmentAttemptHistory, AssessmentAttemptStart,
  AssessmentResultResponse, AssessmentSubmitResponse,
} from './types'

export async function getAssessments(courseId?: string) {
  return localDb.getAssessments(courseId) as unknown as ApiResponse<Assessment[]>
}

export async function getAvailableAssessments() {
  return localDb.getAssessments() as unknown as ApiResponse<Assessment[]>
}

export async function getAssessmentDetail(id: string) {
  const data = await localDb.getAssessments()
  const assessment = data.data.find(a => a.id === id)
  return { status: 'success' as const, data: assessment || data.data[0] }
}

export async function startAssessment(id: string) {
  return localDb.startAssessment(id) as unknown as ApiResponse<AssessmentAttemptStart>
}

export async function submitAttempt(attemptId: string, responses: { question_id: string; response: string; time_taken_seconds?: number }[]) {
  return localDb.submitAttempt(attemptId, responses) as unknown as ApiResponse<AssessmentSubmitResponse>
}

export async function getAttemptResult(attemptId: string) {
  return localDb.getAttemptResult(attemptId) as unknown as ApiResponse<AssessmentResultResponse>
}

export async function getAssessmentHistory() {
  return localDb.getAssessmentHistory() as unknown as ApiResponse<AssessmentAttemptHistory[]>
}

export async function createAssessment(data: {
  title: string; description?: string; course_id: string; assessment_type: string
  passing_score?: number; time_limit?: number; max_attempts?: number; is_published?: boolean
}) {
  const assessment: Assessment = {
    id: `a_${Date.now()}`,
    title: data.title,
    course_id: data.course_id,
    assessment_type: data.assessment_type,
    passing_score: data.passing_score || 60,
    max_attempts: data.max_attempts || 3,
    is_published: data.is_published !== false,
    question_count: 0,
    created_at: new Date().toISOString(),
  }
  return { status: 'success' as const, data: assessment }
}

export async function updateAssessment(id: string, data: Partial<Assessment>) {
  return { status: 'success' as const, data: { id, ...data } as Assessment }
}

export async function deleteAssessment(id: string) {
  return { status: 'success' as const, data: undefined }
}

export async function createQuestion(data: {
  assessment_id: string; question_type: string; prompt: string
  options?: Record<string, string>; correct_answer: string; difficulty?: number; marks?: number
}) {
  return { status: 'success' as const, data: { id: `q_${Date.now()}`, ...data } }
}

export async function deleteQuestion(_questionId: string) {
  return { status: 'success' as const, data: undefined }
}
