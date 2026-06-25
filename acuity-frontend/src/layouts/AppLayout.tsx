import { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'
import {
  LayoutDashboard, BookOpen, Bot, ClipboardCheck, BarChart3, User, GraduationCap,
} from 'lucide-react'

interface AppLayoutProps {
  children: ReactNode
  role: 'student' | 'parent' | 'admin' | 'teacher'
}

const sidebarConfig = {
  student: {
    title: 'Acuity',
    role: 'Student Portal',
    items: [
      { label: 'Dashboard', path: '/student/dashboard', icon: LayoutDashboard },
      { label: 'Learning Path', path: '/student/learning', icon: BookOpen },
      { label: 'AI Tutor', path: '/student/ai-tutor', icon: Bot },
      { label: 'Assessment', path: '/student/assessment', icon: ClipboardCheck },
      { label: 'My Progress', path: '/student/progress', icon: BarChart3 },
      { label: 'Profile', path: '/student/profile', icon: User },
    ],
  },
  parent: {
    title: 'Acuity',
    role: 'Parent Portal',
    items: [
      { label: 'Dashboard', path: '/parent/dashboard', icon: LayoutDashboard },
      { label: 'Progress', path: '/parent/student', icon: BarChart3 },
      { label: 'Reports', path: '/parent/reports', icon: ClipboardCheck },
      { label: 'Insights', path: '/parent/insights', icon: Bot },
    ],
  },
  admin: {
    title: 'Acuity',
    role: 'Admin Panel',
    items: [
      { label: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard },
      { label: 'Students', path: '/admin/students', icon: User },
      { label: 'Analytics', path: '/admin/analytics', icon: BarChart3 },
      { label: 'Assessments', path: '/admin/assessments', icon: ClipboardCheck },
    ],
  },
  teacher: {
    title: 'Acuity',
    role: 'Teacher Portal',
    items: [
      { label: 'Dashboard', path: '/teacher/dashboard', icon: LayoutDashboard },
      { label: 'Students', path: '/teacher/students', icon: User },
      { label: 'Courses', path: '/teacher/courses', icon: GraduationCap },
    ],
  },
}

export function AppLayout({ children, role }: AppLayoutProps) {
  const config = sidebarConfig[role]

  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar items={config.items} title={config.title} role={config.role} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
