import { apiRequest } from './api'
import type { Enrollment } from './types'

export async function enroll(course_id: string, target_completion_date?: string) {
  return apiRequest<Enrollment>('/api/v1/enrollments', {
    method: 'POST',
    body: JSON.stringify({ course_id, target_completion_date }),
  })
}

export async function getEnrollments(status?: string) {
  const qs = status ? `?status=${status}` : ''
  return apiRequest<Enrollment[]>(`/api/v1/enrollments${qs}`)
}

export async function getEnrollment(enrollmentId: string) {
  return apiRequest<Enrollment>(`/api/v1/enrollments/${enrollmentId}`)
}
