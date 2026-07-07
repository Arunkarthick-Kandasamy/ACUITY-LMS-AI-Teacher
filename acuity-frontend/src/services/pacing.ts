import { localDb } from './localDb'
import type { ApiResponse, PacingStatus } from './types'

export async function getPacingStatus() {
  return localDb.getPacingStatus() as unknown as ApiResponse<PacingStatus[]>
}

export async function generateSchedule(_enrollment_id: string) {
  return localDb.generateSchedule() as unknown as ApiResponse<PacingStatus>
}

export async function updatePacing(enrollment_id: string, pace_status: string) {
  return localDb.updatePacing(enrollment_id, pace_status) as unknown as ApiResponse<PacingStatus>
}
