import { apiRequest } from './api'
import type { PacingStatus } from './types'

export async function getPacingStatus() {
  return apiRequest<PacingStatus[]>('/api/v1/pacing')
}

export async function generateSchedule(enrollment_id: string) {
  return apiRequest<PacingStatus>('/api/v1/pacing/generate', {
    method: 'POST',
    body: JSON.stringify({ enrollment_id }),
  })
}

export async function updatePacing(enrollment_id: string, pace_status: string) {
  return apiRequest<PacingStatus>('/api/v1/pacing', {
    method: 'PATCH',
    body: JSON.stringify({ enrollment_id, pace_status }),
  })
}
