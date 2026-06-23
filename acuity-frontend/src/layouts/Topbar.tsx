import { useNavigate } from 'react-router-dom'
import { Bell, LogOut, User, Settings } from 'lucide-react'
import { authStore } from '@/store/authStore'

export function Topbar() {
  const navigate = useNavigate()
  const user = authStore.user

  const handleLogout = () => {
    authStore.logout()
    navigate('/')
  }

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-slate-800">
          Welcome back, {user?.name?.split(' ')[0]}
        </h2>
        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-[10px] font-medium text-slate-500 uppercase tracking-wider">
          {user?.role}
        </span>
      </div>

      <div className="flex items-center gap-2">
        <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all">
          <Bell className="w-4.5 h-4.5" />
        </button>
        <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all">
          <Settings className="w-4.5 h-4.5" />
        </button>
        <div className="w-px h-5 bg-slate-200 mx-1" />
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm text-slate-500 hover:text-red-600 hover:bg-red-50 transition-all"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>
    </header>
  )
}
