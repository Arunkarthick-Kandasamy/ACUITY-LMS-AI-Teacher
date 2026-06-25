import { apiRequest } from './api'
import type {
  AssessmentAnalytics,
  CourseAnalytics,
  DashboardAnalyticsResponse,
  StudentProgressAnalytics,
} from './types'

export async function getAssessmentAnalytics(courseId: string) {
  return apiRequest<AssessmentAnalytics>(`/api/v1/analytics/assessments/${courseId}`)
}

export async function getStudentProgressAnalytics(studentId: string) {
  return apiRequest<StudentProgressAnalytics>(`/api/v1/analytics/students/${studentId}`)
}

export async function getCourseAnalytics(courseId: string) {
  return apiRequest<CourseAnalytics>(`/api/v1/analytics/courses/${courseId}`)
}

export async function getSystemOverview() {
  return apiRequest<DashboardAnalyticsResponse>('/api/v1/analytics/overview')
}
