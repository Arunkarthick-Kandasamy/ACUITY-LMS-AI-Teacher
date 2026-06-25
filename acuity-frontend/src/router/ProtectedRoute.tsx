import { Navigate, Outlet } from 'react-router-dom'
import { authStore } from '@/store/authStore'
import type { UserRole } from '@/store/authStore'

interface ProtectedRouteProps {
  allowedRoles: UserRole[]
}

const roleToDashboard: Record<string, string> = {
  student: '/student/dashboard',
  parent: '/parent/dashboard',
  admin: '/admin/dashboard',
  teacher: '/teacher/dashboard',
}

export function ProtectedRoute({ allowedRoles }: ProtectedRouteProps) {
  const user = authStore.user

  if (!authStore.isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (user && !allowedRoles.includes(user.role)) {
    const redirect = roleToDashboard[user.role] || '/'
    return <Navigate to={redirect} replace />
  }

  return <Outlet />
}
