import { useState, type ReactNode } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard, BookOpen, Bot, ClipboardCheck, BarChart3, User,
  GraduationCap, Users, Link2, GitBranch, Upload, MessageSquare,
  Shield, School, Trophy, CreditCard, Menu, X, Search,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { UserMenu } from '@/components/UserMenu'
import { authStore } from '@/store/authStore'

const sidebarConfig = {
  student: {
    title: 'Acuity',
    items: [
      { label: 'Dashboard', path: '/student/dashboard', icon: LayoutDashboard },
      { label: 'Learning Path', path: '/student/learning', icon: BookOpen },
      { label: 'AI Tutor', path: '/student/ai-tutor', icon: Bot },
      { label: 'Assessments', path: '/student/assessments', icon: ClipboardCheck },
      { label: 'My Progress', path: '/student/progress', icon: BarChart3 },
      { label: 'Messages', path: '/student/messages', icon: MessageSquare },
      { label: 'Achievements', path: '/student/achievements', icon: Trophy },
      { label: 'Profile', path: '/student/profile', icon: User },
    ],
  },
  parent: {
    title: 'Acuity',
    items: [
      { label: 'Dashboard', path: '/parent/dashboard', icon: LayoutDashboard },
      { label: 'Progress', path: '/parent/student', icon: BarChart3 },
      { label: 'Link Student', path: '/parent/link', icon: Link2 },
      { label: 'Reports', path: '/parent/reports', icon: ClipboardCheck },
      { label: 'Insights', path: '/parent/insights', icon: Bot },
    ],
  },
  admin: {
    title: 'Acuity',
    items: [
      { label: 'Dashboard', path: '/admin/dashboard', icon: LayoutDashboard },
      { label: 'Students', path: '/admin/students', icon: User },
      { label: 'Analytics', path: '/admin/analytics', icon: BarChart3 },
      { label: 'Assessments', path: '/admin/assessments', icon: ClipboardCheck },
      { label: 'Knowledge Graph', path: '/admin/knowledge-graph', icon: GitBranch },
      { label: 'Moderation', path: '/admin/moderation', icon: Shield },
      { label: 'Schools', path: '/admin/schools', icon: School },
    ],
  },
  teacher: {
    title: 'Acuity',
    items: [
      { label: 'Dashboard', path: '/teacher/dashboard', icon: LayoutDashboard },
      { label: 'Students', path: '/teacher/students', icon: User },
      { label: 'Courses', path: '/teacher/courses', icon: GraduationCap },
      { label: 'Upload Content', path: '/teacher/upload', icon: Upload },
      { label: 'Messages', path: '/teacher/messages', icon: MessageSquare },
      { label: 'Subscription', path: '/teacher/subscription', icon: CreditCard },
    ],
  },
}

function SidebarNav({
  items,
  onNav,
}: {
  items: { label: string; path: string; icon: React.ComponentType<{ className?: string }> }[]
  onNav?: () => void
}) {
  return (
    <nav className="flex-1 px-3 py-5 space-y-0.5">
      {items.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          onClick={onNav}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
              isActive
                ? 'text-blue-600 bg-blue-50'
                : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
            )
          }
        >
          <item.icon className="h-4.5 w-4.5 shrink-0" />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  )
}

function getPageTitle(pathname: string, items: { label: string; path: string }[]): string {
  const match = items.find(i => pathname.startsWith(i.path))
  return match?.label || 'Dashboard'
}

export function AppLayout({ children, role }: { children: ReactNode; role: string }) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()
  const config = sidebarConfig[role as keyof typeof sidebarConfig]
  const user = authStore.user

  const handleLogout = () => {
    authStore.logout()
    navigate('/login')
  }

  const pageTitle = getPageTitle(window.location.pathname, config.items)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Desktop Sidebar — CK12 clean style */}
      <aside className="hidden lg:flex lg:flex-col lg:w-56 lg:border-r lg:border-gray-200 bg-white">
        <div className="flex items-center gap-2.5 px-4 h-14 border-b border-gray-100">
          <div className="h-7 w-7 rounded-md bg-blue-500 flex items-center justify-center text-white text-xs font-bold">
            A
          </div>
          <span className="text-sm font-semibold text-gray-900">Acuity</span>
        </div>
        <SidebarNav items={config.items} />
        <div className="p-4 border-t border-gray-100">
          <p className="text-[10px] text-gray-400 text-center">&copy; 2026 Acuity</p>
        </div>
      </aside>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm lg:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.aside
            initial={{ x: -240 }}
            animate={{ x: 0 }}
            exit={{ x: -240 }}
            transition={{ type: 'spring', damping: 25, stiffness: 250 }}
            className="fixed inset-y-0 left-0 z-50 w-56 bg-white border-r border-gray-200 lg:hidden"
          >
            <div className="flex items-center justify-between px-4 h-14 border-b border-gray-100">
              <div className="flex items-center gap-2.5">
                <div className="h-7 w-7 rounded-md bg-blue-500 flex items-center justify-center text-white text-xs font-bold">A</div>
                <span className="text-sm font-semibold text-gray-900">Acuity</span>
              </div>
              <button onClick={() => setMobileOpen(false)} className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors">
                <X className="h-4 w-4 text-gray-500" />
              </button>
            </div>
            <SidebarNav items={config.items} onNav={() => setMobileOpen(false)} />
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header — CK12 minimal style */}
        <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-4 lg:px-6 shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileOpen(true)}
              className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <Menu className="h-4.5 w-4.5 text-gray-500" />
            </button>
            <h1 className="text-[15px] font-semibold text-gray-900">{pageTitle}</h1>
          </div>
          <UserMenu user={user} onLogout={handleLogout} />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 lg:p-8 max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.25 }}
            >
              {children}
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  )
}
