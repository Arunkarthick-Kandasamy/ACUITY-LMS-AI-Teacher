import { localDb } from './localDb'
import type { ApiResponse, AssessmentAnalytics, CourseAnalytics, DashboardAnalyticsResponse, StudentProgressAnalytics } from './types'

export async function getAssessmentAnalytics(courseId: string) {
  return localDb.getAssessmentAnalytics(courseId) as unknown as ApiResponse<AssessmentAnalytics>
}

export async function getStudentProgressAnalytics(studentId: string) {
  return localDb.getStudentProgressAnalytics(studentId) as unknown as ApiResponse<StudentProgressAnalytics>
}

export async function getCourseAnalytics(courseId: string) {
  return localDb.getCourseAnalytics(courseId) as unknown as ApiResponse<CourseAnalytics>
}

export async function getSystemOverview() {
  return localDb.getSystemOverview() as unknown as ApiResponse<DashboardAnalyticsResponse>
}
