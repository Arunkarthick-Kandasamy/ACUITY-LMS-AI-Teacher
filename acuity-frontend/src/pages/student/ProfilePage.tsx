import { authStore } from '@/store/authStore'
import { User, Mail, BookOpen, Calendar } from 'lucide-react'

export function ProfilePage() {
  const user = authStore.user

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">My Profile</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your learning preferences</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-slate-100">
          <div className="w-16 h-16 rounded-full bg-navy-800 flex items-center justify-center text-xl font-bold text-white">
            {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{user?.full_name || 'Student'}</h2>
            <p className="text-sm text-slate-500 capitalize">{user?.role || 'Student'}</p>
          </div>
        </div>

        <div className="space-y-4">
          {[
            { icon: User, label: 'Name', value: user?.full_name || 'N/A' },
            { icon: Mail, label: 'Email', value: user?.email || 'N/A' },
            { icon: BookOpen, label: 'Role', value: user?.role || 'N/A' },
            { icon: Calendar, label: 'Member Since', value: user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A' },
          ].map((item) => {
            const Icon = item.icon
            return (
              <div key={item.label} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-slate-500" />
                </div>
                <div className="flex-1">
                  <div className="text-xs text-slate-400">{item.label}</div>
                  <div className="text-sm font-medium text-slate-800 capitalize">{item.value}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
