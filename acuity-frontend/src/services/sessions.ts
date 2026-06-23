import { apiRequest } from './api'
import type { Attempt, TeachingSession } from './types'

export async function startSession(course_id: string, resume_last = true) {
  return apiRequest<TeachingSession>('/api/v1/sessions', {
    method: 'POST',
    body: JSON.stringify({ course_id, resume_last }),
  })
}

export async function getCurrentSession() {
  return apiRequest<TeachingSession | null>('/api/v1/sessions/current')
}

export async function getSession(sessionId: string) {
  return apiRequest<TeachingSession>(`/api/v1/sessions/${sessionId}`)
}

export async function pauseSession(sessionId: string) {
  return apiRequest<TeachingSession>(`/api/v1/sessions/${sessionId}/pause`, {
    method: 'PATCH',
  })
}

export async function endSession(sessionId: string) {
  return apiRequest<TeachingSession>(`/api/v1/sessions/${sessionId}/end`, {
    method: 'PATCH',
  })
}

export async function getSessionHistory() {
  return apiRequest<TeachingSession[]>('/api/v1/sessions/history')
}

export async function teach(course_id: string, student_input?: string) {
  return apiRequest<{ action: string; content: unknown }>('/api/v1/teacher/teach', {
    method: 'POST',
    body: JSON.stringify({ course_id, student_input }),
  })
}

export async function respondToExercise(data: { exercise_id: string; response: string }) {
  return apiRequest<Attempt>(`/api/v1/sessions/${data.exercise_id}/respond`, {
    method: 'POST',
    body: JSON.stringify(data),
  })
}
