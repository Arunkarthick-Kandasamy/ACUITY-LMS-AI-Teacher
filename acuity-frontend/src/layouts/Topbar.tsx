import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { authStore } from '@/store/authStore'

export function Topbar() {
  const navigate = useNavigate()
  const [user, setUser] = useState(authStore.user)

  useEffect(() => {
    const unsub = authStore.subscribe(() => setUser(authStore.user))
    return unsub
  }, [])

  const handleLogout = async () => {
    await authStore.logout()
    navigate('/')
  }

  return (
    <header className="h-14 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-slate-800">
          Welcome back, {user?.full_name?.split(' ')[0] || 'User'}
        </h2>
        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-[10px] font-medium text-slate-500 uppercase tracking-wider capitalize">
          {user?.role}
        </span>
      </div>

      <div className="flex items-center gap-2">
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
