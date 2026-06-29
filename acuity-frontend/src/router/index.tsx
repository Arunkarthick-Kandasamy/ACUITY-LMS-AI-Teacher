import { createBrowserRouter, Outlet } from 'react-router-dom'
import { LandingPage } from '@/pages/landing/LandingPage'
import { ProtectedRoute } from '@/router/ProtectedRoute'
import { LoginPage } from '@/pages/auth/LoginPage'
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage'
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage'
import { StudentOnboarding } from '@/pages/auth/StudentOnboarding'
import { CourseCatalogPage } from '@/pages/catalog/CourseCatalogPage'
import { ParentAccessPage } from '@/pages/student/ParentAccessPage'
import { LinkStudentPage } from '@/pages/parent/LinkStudentPage'
import { KnowledgeGraphPage } from '@/pages/admin/KnowledgeGraphPage'
import { ContentUploadPage } from '@/pages/teacher/ContentUploadPage'
import { AppLayout } from '@/layouts/AppLayout'
import { StudentDashboard } from '@/pages/student/StudentDashboard'
import { LearningPathPage } from '@/pages/student/LearningPathPage'
import { AITutorPage } from '@/pages/student/AITutorPage'
import { AssessmentPage } from '@/pages/student/AssessmentPage'
import { AssessmentListPage } from '@/pages/student/AssessmentListPage'
import { AssessmentDetailPage } from '@/pages/student/AssessmentDetailPage'
import { AssessmentAttemptPage } from '@/pages/student/AssessmentAttemptPage'
import { AssessmentResultPage } from '@/pages/student/AssessmentResultPage'
import { AssessmentManagementPage } from '@/pages/admin/AssessmentManagementPage'
import { ProgressPage } from '@/pages/student/ProgressPage'
import { ProfilePage } from '@/pages/student/ProfilePage'
import { ParentDashboard } from '@/pages/parent/ParentDashboard'
import { ParentStudentDetail } from '@/pages/parent/ParentStudentDetail'
import { ReportsPage } from '@/pages/parent/ReportsPage'
import { InsightsPage } from '@/pages/parent/InsightsPage'
import { AdminDashboard } from '@/pages/admin/AdminDashboard'
import { StudentsPage } from '@/pages/admin/StudentsPage'
import { AnalyticsPage } from '@/pages/admin/AnalyticsPage'
import { TeacherDashboard } from '@/pages/teacher/TeacherDashboard'
import { TeacherStudentsPage } from '@/pages/teacher/TeacherStudentsPage'
import { TeacherStudentDetail } from '@/pages/teacher/TeacherStudentDetail'
import { TeacherCoursesPage } from '@/pages/teacher/TeacherCoursesPage'
import MessagesPage from '@/pages/messages/MessagesPage'
import ModerationPage from '@/pages/admin/ModerationPage'
import SchoolsPage from '@/pages/admin/SchoolsPage'
import AchievementsPage from '@/pages/AchievementsPage'
import SubscriptionPage from '@/pages/SubscriptionPage'
import OfflinePage from '@/pages/OfflinePage'

function StudentLayout() {
  return <AppLayout role="student"><Outlet /></AppLayout>
}

function ParentLayout() {
  return <AppLayout role="parent"><Outlet /></AppLayout>
}

function AdminLayout() {
  return <AppLayout role="admin"><Outlet /></AppLayout>
}

function TeacherLayout() {
  return <AppLayout role="teacher"><Outlet /></AppLayout>
}

export const router = createBrowserRouter([
  { path: '/', element: <LandingPage /> },
  { path: '/courses', element: <CourseCatalogPage /> },
  { path: '/forgot-password', element: <ForgotPasswordPage /> },
  { path: '/reset-password', element: <ResetPasswordPage /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/onboarding', element: <StudentOnboarding /> },
  {
    element: <ProtectedRoute allowedRoles={['student']} />,
    children: [{
      element: <StudentLayout />,
      children: [
        { path: '/student/dashboard', element: <StudentDashboard /> },
        { path: '/student/learning', element: <LearningPathPage /> },
        { path: '/student/ai-tutor', element: <AITutorPage /> },
        { path: '/student/assessment', element: <AssessmentPage /> },
        { path: '/student/assessments', element: <AssessmentListPage /> },
        { path: '/student/assessments/:id', element: <AssessmentDetailPage /> },
        { path: '/student/assessments/:id/attempt', element: <AssessmentAttemptPage /> },
        { path: '/student/assessments/:id/result', element: <AssessmentResultPage /> },
        { path: '/student/progress', element: <ProgressPage /> },
        { path: '/student/profile', element: <ProfilePage /> },
        { path: '/student/parent-access', element: <ParentAccessPage /> },
        { path: '/student/messages', element: <MessagesPage /> },
        { path: '/student/achievements', element: <AchievementsPage /> },
      ],
    }],
  },
  {
    element: <ProtectedRoute allowedRoles={['parent']} />,
    children: [{
      element: <ParentLayout />,
      children: [
        { path: '/parent/dashboard', element: <ParentDashboard /> },
        { path: '/parent/student', element: <ParentStudentDetail /> },
        { path: '/parent/link', element: <LinkStudentPage /> },
        { path: '/parent/reports', element: <ReportsPage /> },
        { path: '/parent/insights', element: <InsightsPage /> },
      ],
    }],
  },
  {
    element: <ProtectedRoute allowedRoles={['admin']} />,
    children: [{
      element: <AdminLayout />,
      children: [
        { path: '/admin/dashboard', element: <AdminDashboard /> },
        { path: '/admin/students', element: <StudentsPage /> },
        { path: '/admin/analytics', element: <AnalyticsPage /> },
        { path: '/admin/assessments', element: <AssessmentManagementPage /> },
        { path: '/admin/knowledge-graph', element: <KnowledgeGraphPage /> },
        { path: '/admin/moderation', element: <ModerationPage /> },
        { path: '/admin/schools', element: <SchoolsPage /> },
      ],
    }],
  },
  {
    element: <ProtectedRoute allowedRoles={['teacher', 'admin']} />,
    children: [{
      element: <TeacherLayout />,
      children: [
        { path: '/teacher/dashboard', element: <TeacherDashboard /> },
        { path: '/teacher/students', element: <TeacherStudentsPage /> },
        { path: '/teacher/students/:id', element: <TeacherStudentDetail /> },
        { path: '/teacher/courses', element: <TeacherCoursesPage /> },
        { path: '/teacher/upload', element: <ContentUploadPage /> },
        { path: '/teacher/messages', element: <MessagesPage /> },
        { path: '/teacher/subscription', element: <SubscriptionPage /> },
      ],
    }],
  },
])
