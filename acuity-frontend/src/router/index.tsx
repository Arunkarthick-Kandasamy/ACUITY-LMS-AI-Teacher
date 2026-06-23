import { createBrowserRouter, Navigate, Outlet } from 'react-router-dom'
import { LandingPage } from '@/pages/landing/LandingPage'
import { LoginPage } from '@/pages/auth/LoginPage'
import { StudentOnboarding } from '@/pages/auth/StudentOnboarding'
import { AppLayout } from '@/layouts/AppLayout'
import { StudentDashboard } from '@/pages/student/StudentDashboard'
import { LearningPathPage } from '@/pages/student/LearningPathPage'
import { AITutorPage } from '@/pages/student/AITutorPage'
import { AssessmentPage } from '@/pages/student/AssessmentPage'
import { ProgressPage } from '@/pages/student/ProgressPage'
import { ProfilePage } from '@/pages/student/ProfilePage'
import { ParentDashboard } from '@/pages/parent/ParentDashboard'
import { ParentStudentDetail } from '@/pages/parent/ParentStudentDetail'
import { ReportsPage } from '@/pages/parent/ReportsPage'
import { InsightsPage } from '@/pages/parent/InsightsPage'
import { AdminDashboard } from '@/pages/admin/AdminDashboard'
import { StudentsPage } from '@/pages/admin/StudentsPage'
import { AnalyticsPage } from '@/pages/admin/AnalyticsPage'

function StudentLayout() {
  return <AppLayout role="student"><Outlet /></AppLayout>
}

function ParentLayout() {
  return <AppLayout role="parent"><Outlet /></AppLayout>
}

function AdminLayout() {
  return <AppLayout role="admin"><Outlet /></AppLayout>
}

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/onboarding', element: <StudentOnboarding /> },
  {
    element: <StudentLayout />,
    children: [
      { index: true, path: '/student/dashboard', element: <StudentDashboard /> },
      { path: '/student/learning', element: <LearningPathPage /> },
      { path: '/student/ai-tutor', element: <AITutorPage /> },
      { path: '/student/assessment', element: <AssessmentPage /> },
      { path: '/student/progress', element: <ProgressPage /> },
      { path: '/student/profile', element: <ProfilePage /> },
    ],
  },
  {
    element: <ParentLayout />,
    children: [
      { index: true, path: '/parent/dashboard', element: <ParentDashboard /> },
      { path: '/parent/student', element: <ParentStudentDetail /> },
      { path: '/parent/reports', element: <ReportsPage /> },
      { path: '/parent/insights', element: <InsightsPage /> },
    ],
  },
  {
    element: <AdminLayout />,
    children: [
      { index: true, path: '/admin/dashboard', element: <AdminDashboard /> },
      { path: '/admin/students', element: <StudentsPage /> },
      { path: '/admin/analytics', element: <AnalyticsPage /> },
    ],
  },
])
