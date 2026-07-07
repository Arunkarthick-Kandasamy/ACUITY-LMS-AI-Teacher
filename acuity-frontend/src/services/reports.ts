import { localDb } from './localDb'
import type { ApiResponse, Report } from './types'

export async function generateReport(studentId: string, _reportType = 'weekly') {
  return localDb.generateReport(studentId) as unknown as ApiResponse<Report>
}

export async function getReport(reportId: string) {
  return localDb.getReport(reportId) as unknown as ApiResponse<Report>
}

export async function getStudentReports(studentId: string, _page = 1, _per_page = 20) {
  return localDb.getStudentReports(studentId) as unknown as ApiResponse<Report[]>
}
