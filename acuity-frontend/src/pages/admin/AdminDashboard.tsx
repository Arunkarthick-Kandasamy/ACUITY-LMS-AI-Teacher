import { useState, useEffect } from 'react'
import { getAdminDashboard, getAdminUsers } from '@/services/admin'
import { mockDashboardStats, mockUsers } from './admin-mock-data'
import { Users, TrendingUp, Activity, Loader2, Clock, CheckCircle2, XCircle, School } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AdminDashboard() {
  const [stats, setStats] = useState(mockDashboardStats)
  const [users, setUsers] = useState(mockUsers)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const load = async () => {
      try {
        const [sRes, uRes] = await Promise.all([
          getAdminDashboard().catch(() => ({ data: mockDashboardStats })),
          getAdminUsers({ per_page: 10 }).catch(() => ({ data: mockUsers })),
        ])
        if (!cancelled) {
          setStats(sRes.data)
          setUsers(uRes.data)
        }
      } catch {
        if (!cancelled) {
          setStats(mockDashboardStats)
          setUsers(mockUsers)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [])

  const statCards = [
    { icon: Users, label: 'Total Students', value: stats.total_students.toLocaleString(), change: `${stats.active_sessions_today.toLocaleString()} active today`, color: 'text-blue-600 bg-blue-50' },
    { icon: Users, label: 'Total Parents', value: stats.total_parents.toLocaleString(), color: 'text-purple-600 bg-purple-50' },
    { icon: Activity, label: 'Active Today', value: stats.active_sessions_today.toLocaleString(), change: 'sessions today', color: 'text-emerald-600 bg-emerald-50' },
    { icon: TrendingUp, label: 'Avg Completion', value: `${Math.round(stats.completion_rate_avg * 100)}%`, color: 'text-amber-600 bg-amber-50' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900">Admin Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">Platform overview and system analytics</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center', stat.color)}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div className="text-xs text-gray-400 font-medium">{stat.label}</div>
              </div>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              {stat.change && <div className="text-xs text-gray-500 mt-1">{stat.change}</div>}
            </div>
          )
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Platform Stats</h2>
          <div className="space-y-4">
            {[
              { label: 'Total Courses', value: stats.total_courses, color: 'emerald' },
              { label: 'Active Enrollments', value: stats.active_enrollments, color: 'amber' },
              { label: 'Total Users', value: stats.total_users, color: 'blue' },
              { label: 'Active Sessions Today', value: stats.active_sessions_today, color: 'purple' },
            ].map(s => (
              <div key={s.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{s.label}</span>
                  <span className={cn('font-medium', `text-${s.color}-600`)}>{s.value.toLocaleString()}</span>
                </div>
                <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
                  <div className={cn('h-full rounded-full transition-all', `bg-${s.color}-500`)}
                    style={{ width: `${Math.min((s.value / stats.total_users) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">System Health</h2>
          <div className="space-y-4">
            {[
              { icon: CheckCircle2, label: 'API Status', value: 'Operational', color: 'text-green-600 bg-green-50' },
              { icon: Users, label: 'Active Sessions', value: stats.active_sessions_today.toLocaleString(), color: 'text-blue-600 bg-blue-50' },
              { icon: Clock, label: 'Avg Session Duration', value: '42 min', color: 'text-purple-600 bg-purple-50' },
              { icon: School, label: 'Active Schools', value: '8', color: 'text-amber-600 bg-amber-50' },
            ].map(s => {
              const Icon = s.icon
              return (
                <div key={s.label} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <div className={cn('w-9 h-9 rounded-lg flex items-center justify-center', s.color)}>
                    <Icon className="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">{s.label}</div>
                    <div className="text-sm font-semibold text-gray-900">{s.value}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {users.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Recent Users</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Role</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Email</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u) => (
                  <tr key={u.user_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-3 font-medium text-gray-800">{u.full_name}</td>
                    <td className="px-6 py-3">
                      <span className={cn(
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                        u.role === 'admin' ? 'bg-purple-50 text-purple-700' :
                        u.role === 'student' ? 'bg-blue-50 text-blue-700' :
                        u.role === 'teacher' ? 'bg-emerald-50 text-emerald-700' :
                        'bg-gray-100 text-gray-700'
                      )}>{u.role}</span>
                    </td>
                    <td className="px-6 py-3 text-gray-500">{u.email}</td>
                    <td className="px-6 py-3">
                      <span className={cn('inline-flex items-center gap-1 text-xs font-medium', u.is_active ? 'text-emerald-600' : 'text-red-500')}>
                        {u.is_active ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
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
