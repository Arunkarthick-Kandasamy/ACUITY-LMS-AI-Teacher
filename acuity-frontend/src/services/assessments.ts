import { apiRequest } from './api'
import type {
  Assessment,
  AssessmentAttemptHistory,
  AssessmentAttemptStart,
  AssessmentResultResponse,
  AssessmentSubmitResponse,
} from './types'

export async function getAssessments(courseId?: string) {
  const qs = courseId ? `?course_id=${courseId}` : ''
  return apiRequest<Assessment[]>(`/api/v1/assessments${qs}`)
}

export async function getAvailableAssessments() {
  return apiRequest<Assessment[]>('/api/v1/assessments/available')
}

export async function getAssessmentDetail(id: string) {
  return apiRequest<Assessment>(`/api/v1/assessments/${id}`)
}

export async function startAssessment(id: string) {
  return apiRequest<AssessmentAttemptStart>(`/api/v1/assessments/${id}/start`, {
    method: 'POST',
  })
}

export async function submitAttempt(
  attemptId: string,
  responses: { question_id: string; response: string; time_taken_seconds?: number }[],
) {
  return apiRequest<AssessmentSubmitResponse>(`/api/v1/attempts/${attemptId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ responses }),
  })
}

export async function getAttemptResult(attemptId: string) {
  return apiRequest<AssessmentResultResponse>(`/api/v1/attempts/${attemptId}/result`)
}

export async function getAssessmentHistory(params?: { page?: number; per_page?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.per_page) searchParams.set('per_page', String(params.per_page))
  const qs = searchParams.toString()
  return apiRequest<AssessmentAttemptHistory[]>(`/api/v1/assessments/history${qs ? `?${qs}` : ''}`)
}

export async function createAssessment(data: {
  title: string
  description?: string
  course_id: string
  assessment_type: string
  passing_score?: number
  time_limit?: number
  max_attempts?: number
  is_published?: boolean
}) {
  return apiRequest<Assessment>('/api/v1/assessments', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function updateAssessment(id: string, data: Partial<Assessment>) {
  return apiRequest<Assessment>(`/api/v1/assessments/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

export async function deleteAssessment(id: string) {
  return apiRequest<void>(`/api/v1/assessments/${id}`, {
    method: 'DELETE',
  })
}

export async function createQuestion(data: {
  assessment_id: string
  question_type: string
  prompt: string
  options?: Record<string, string>
  correct_answer: string
  difficulty?: number
  marks?: number
  explanation?: string
  order_index?: number
}) {
  return apiRequest<Assessment>(`/api/v1/assessments/${data.assessment_id}/questions`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function deleteQuestion(questionId: string) {
  return apiRequest<void>(`/api/v1/questions/${questionId}`, {
    method: 'DELETE',
  })
}
