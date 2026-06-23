import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useLocation } from 'react-router-dom'
import {
  LayoutDashboard, BookOpen, Bot, ClipboardCheck, BarChart3, User, GraduationCap,
} from 'lucide-react'

interface SidebarItem {
  label: string
  path: string
  icon: React.ElementType
}

interface SidebarProps {
  items: SidebarItem[]
  title: string
  role: string
}

export function Sidebar({ items, title, role }: SidebarProps) {
  const location = useLocation()

  return (
    <aside className="w-60 min-h-screen bg-white border-r border-slate-200 flex flex-col">
      <div className="p-5 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <GraduationCap className="w-7 h-7 text-navy-800" />
          <div>
            <h1 className="text-base font-bold text-navy-800">{title}</h1>
            <span className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">{role}</span>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {items.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/')
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-navy-800 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              )}
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0" />
              {item.label}
            </NavLink>
          )
        })}
      </nav>

      <div className="p-3 border-t border-slate-100">
        <NavLink
          to="/"
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 transition-all"
        >
          <BarChart3 className="w-4.5 h-4.5" />
          Back to Home
        </NavLink>
      </div>
    </aside>
  )
}
