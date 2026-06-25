import { useAuthApi } from '@/hooks/useApi'
import { getTeacherDashboard } from '@/services/teacher'
import { Users, BookOpen, TrendingUp, Clock, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'

export function TeacherDashboard() {
  const { data: dashboard, loading } = useAuthApi(() => getTeacherDashboard(), [])

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
        <h1 className="text-xl font-semibold text-slate-900">Teacher Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Monitor your students and courses</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Users, label: 'Total Students', value: String(dashboard?.total_students || 0), color: 'text-blue-600 bg-blue-50' },
          { icon: BookOpen, label: 'Total Courses', value: String(dashboard?.total_courses || 0), color: 'text-purple-600 bg-purple-50' },
          { icon: TrendingUp, label: 'Avg Mastery', value: dashboard?.students?.length
              ? `${Math.round(dashboard.students.reduce((a, s) => a + s.overall_mastery_avg, 0) / dashboard.students.length * 100)}%`
              : 'N/A', color: 'text-emerald-600 bg-emerald-50' },
          { icon: Clock, label: 'Active Students', value: String(dashboard?.students?.filter(s => s.last_active).length || 0), color: 'text-amber-600 bg-amber-50' },
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
            </div>
          )
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Your Students</h2>
            <Link to="/teacher/students" className="text-sm text-navy-600 hover:underline">View all</Link>
          </div>
          {dashboard?.students && dashboard.students.length > 0 ? (
            <div className="space-y-3">
              {dashboard.students.slice(0, 5).map((s) => (
                <Link key={s.student_id} to={`/teacher/students/${s.student_id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 transition-colors">
                  <div>
                    <div className="text-sm font-medium text-slate-800">{s.full_name}</div>
                    <div className="text-xs text-slate-400">{s.active_courses} active courses</div>
                  </div>
                  <div className="text-sm font-semibold text-emerald-600">{Math.round(s.overall_mastery_avg * 100)}%</div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No students assigned yet.</p>
          )}
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Sessions</h2>
          {dashboard?.recent_sessions && dashboard.recent_sessions.length > 0 ? (
            <div className="space-y-3">
              {dashboard.recent_sessions.slice(0, 5).map((s) => (
                <div key={s.session_id} className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
                  <div>
                    <div className="text-sm font-medium text-slate-700">{s.course_title || 'Unknown Course'}</div>
                    <div className="text-xs text-slate-400">{s.state}</div>
                  </div>
                  <div className="text-xs text-slate-400">{s.last_activity_at ? new Date(s.last_activity_at).toLocaleDateString() : ''}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-400">No recent sessions.</p>
          )}
        </div>
      </div>
    </div>
  )
}
