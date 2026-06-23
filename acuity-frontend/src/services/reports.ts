import { apiRequest } from './api'
import type { Report } from './types'

export async function generateReport(studentId: string, reportType = 'weekly') {
  return apiRequest<Report>(`/api/v1/reports/generate/${studentId}?report_type=${reportType}`, {
    method: 'POST',
  })
}

export async function getReport(reportId: string) {
  return apiRequest<Report>(`/api/v1/reports/${reportId}`)
}

export async function getStudentReports(studentId: string, page = 1, per_page = 20) {
  return apiRequest<Report[]>(`/api/v1/reports/student/${studentId}?page=${page}&per_page=${per_page}`)
}
