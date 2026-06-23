import { useAuthApi } from '@/hooks/useApi'
import { getAdminDashboard, getAdminUsers } from '@/services/admin'
import { getEnrollments } from '@/services/enrollment'
import { Users, BookOpen, TrendingUp, BarChart3, Activity, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AdminDashboard() {
  const { data: stats, loading } = useAuthApi(() => getAdminDashboard(), [])
  const { data: users } = useAuthApi(() => getAdminUsers({ per_page: 10 }), [])
  const { data: enrollments } = useAuthApi(() => getEnrollments(), [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Admin Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Platform overview and system analytics</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Users, label: 'Total Students', value: stats?.total_students?.toLocaleString() || 'N/A', change: `${stats?.active_sessions_today || 0} active today`, color: 'text-blue-600 bg-blue-50' },
          { icon: Users, label: 'Total Parents', value: stats?.total_parents?.toLocaleString() || 'N/A', color: 'text-purple-600 bg-purple-50' },
          { icon: Activity, label: 'Active Today', value: stats?.active_sessions_today?.toLocaleString() || 'N/A', change: 'sessions today', color: 'text-emerald-600 bg-emerald-50' },
          { icon: TrendingUp, label: 'Avg Completion', value: stats?.completion_rate_avg ? `${Math.round(stats.completion_rate_avg * 100)}%` : 'N/A', color: 'text-amber-600 bg-amber-50' },
        ].map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-9 h-9 rounded-lg ${stat.color} flex items-center justify-center`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div className="text-xs text-slate-400 font-medium">{stat.label}</div>
              </div>
              <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
              {stat.change && <div className="text-xs text-slate-500 mt-1">{stat.change}</div>}
            </div>
          )
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Platform Stats</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">Total Courses</span>
                <span className="text-emerald-600 font-medium">{stats?.total_courses || 0}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill bg-emerald-500" style={{ width: `${Math.min((stats?.total_courses || 0) * 5, 100)}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">Active Enrollments</span>
                <span className="text-amber-600 font-medium">{stats?.active_enrollments || 0}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill bg-amber-500" style={{ width: `${Math.min((stats?.active_enrollments || 0) / 5, 100)}%` }} />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Activity</h2>
          <div className="space-y-3">
            <p className="text-sm text-slate-500">{users?.length || 0} users registered</p>
            <p className="text-sm text-slate-500">{enrollments?.length || 0} active enrollments</p>
          </div>
        </div>
      </div>

      {users && users.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h2 className="font-semibold text-slate-900">Recent Users</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Name</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Role</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Email</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3 font-medium text-slate-800">{u.full_name}</td>
                    <td className="px-6 py-3">
                      <span className={cn(
                        'badge',
                        u.role === 'admin' ? 'bg-purple-50 text-purple-700' :
                        u.role === 'student' ? 'bg-blue-50 text-blue-700' :
                        'bg-emerald-50 text-emerald-700'
                      )}>{u.role}</span>
                    </td>
                    <td className="px-6 py-3 text-slate-500">{u.email}</td>
                    <td className="px-6 py-3">
                      <span className={u.is_active ? 'text-emerald-600' : 'text-red-500'}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
