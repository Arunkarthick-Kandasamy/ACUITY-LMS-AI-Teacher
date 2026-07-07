import { localDb } from './localDb'
import type { ApiResponse, Enrollment } from './types'

export async function enroll(course_id: string, _target_completion_date?: string) {
  return localDb.enroll(course_id) as unknown as ApiResponse<Enrollment>
}

export async function getEnrollments(status?: string) {
  return localDb.getEnrollments('u1', status) as unknown as ApiResponse<Enrollment[]>
}

export async function getEnrollment(enrollmentId: string) {
  const data = await localDb.getEnrollments('u1')
  const enrollment = data.data.find(e => e.enrollment_id === enrollmentId)
  return { status: 'success' as const, data: enrollment || data.data[0] }
}
