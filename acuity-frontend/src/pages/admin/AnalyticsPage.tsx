import { useAuthApi } from '@/hooks/useApi'
import { getAdminDashboard } from '@/services/admin'
import { BarChart3, TrendingUp, Users, BookOpen, Loader2 } from 'lucide-react'

export function AnalyticsPage() {
  const { data: stats, loading } = useAuthApi(() => getAdminDashboard(), [])

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
        <h1 className="text-xl font-semibold text-slate-900">Analytics</h1>
        <p className="text-sm text-slate-500 mt-1">System-wide performance metrics</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Platform Overview</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Total Users</span>
              <span className="font-bold text-slate-900">{stats?.total_users || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Students</span>
              <span className="font-bold text-slate-900">{stats?.total_students || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Parents</span>
              <span className="font-bold text-slate-900">{stats?.total_parents || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Admins</span>
              <span className="font-bold text-slate-900">{stats?.total_admins || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Performance Overview</h2>
          <div className="space-y-4">
            {[
              { icon: Users, label: 'Student-Teacher Ratio', value: stats?.total_students ? `${Math.round(stats.total_students / Math.max(stats.total_admins || 1, 1))}:1` : 'N/A', desc: 'AI-powered ratio' },
              { icon: BookOpen, label: 'Total Courses', value: String(stats?.total_courses || 0), desc: 'Available courses' },
              { icon: TrendingUp, label: 'Active Enrollments', value: String(stats?.active_enrollments || 0), desc: 'Current enrollments' },
              { icon: BarChart3, label: 'Completion Rate', value: stats?.completion_rate_avg ? `${Math.round(stats.completion_rate_avg * 100)}%` : 'N/A', desc: 'Average course completion' },
            ].map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                  <div className="w-9 h-9 rounded-lg bg-white border border-slate-200 flex items-center justify-center">
                    <Icon className="w-4.5 h-4.5 text-slate-500" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400">{stat.label}</div>
                    <div className="text-lg font-bold text-slate-900">{stat.value}</div>
                    <div className="text-[10px] text-slate-400">{stat.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
