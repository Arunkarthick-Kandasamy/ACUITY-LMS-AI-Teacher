import { localDb } from './localDb'
import type { ApiResponse, Attempt, TeachingSession } from './types'

export async function startSession(course_id: string, _resume_last = true) {
  return localDb.startSession(course_id) as unknown as ApiResponse<TeachingSession>
}

export async function getCurrentSession() {
  return localDb.getCurrentSession() as unknown as ApiResponse<TeachingSession | null>
}

export async function getSession(sessionId: string) {
  return localDb.getSession(sessionId) as unknown as ApiResponse<TeachingSession>
}

export async function pauseSession(sessionId: string) {
  return localDb.getSession(sessionId) as unknown as ApiResponse<TeachingSession>
}

export async function endSession(sessionId: string) {
  return localDb.endSession(sessionId) as unknown as ApiResponse<TeachingSession>
}

export async function getSessionHistory() {
  return localDb.getSessionHistory() as unknown as ApiResponse<TeachingSession[]>
}

export async function teach(course_id: string, student_input?: string) {
  return localDb.teach(course_id, student_input) as unknown as ApiResponse<{ action: string; content: unknown }>
}

export async function respondToExercise(data: { exercise_id: string; response: string }) {
  return localDb.recordAttempt(data.exercise_id, { response: data.response }) as unknown as ApiResponse<Attempt>
}
