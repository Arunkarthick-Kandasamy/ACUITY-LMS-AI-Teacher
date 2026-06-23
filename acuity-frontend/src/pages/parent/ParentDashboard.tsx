import { useAuthApi } from '@/hooks/useApi'
import { getParentStudents, getParentStudentProgress } from '@/services/parent'
import { TrendingUp, Clock, AlertTriangle, BookOpen, Award, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ParentDashboard() {
  const { data: students, loading } = useAuthApi(() => getParentStudents(), [])
  const firstStudent = students?.[0]

  const { data: progress } = useAuthApi(
    () => firstStudent ? getParentStudentProgress(firstStudent.student_id) : Promise.reject(),
    [firstStudent?.student_id],
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const studentName = firstStudent?.full_name || 'Student'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Parent Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Track {studentName}'s learning journey</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Award, label: 'Overall Mastery', value: firstStudent ? `${Math.round(firstStudent.overall_mastery_avg * 100)}%` : 'N/A', change: `${firstStudent?.active_courses || 0} active courses`, color: 'text-emerald-600 bg-emerald-50' },
          { icon: BookOpen, label: 'Status', value: firstStudent?.overall_mastery_avg && firstStudent.overall_mastery_avg >= 0.75 ? 'Good Learner' : 'Support Learner', desc: 'Personalized learning track', color: 'text-amber-600 bg-amber-50' },
          { icon: Clock, label: 'Active Courses', value: String(firstStudent?.active_courses || 0), change: `${firstStudent?.current_streak_days || 0} day streak`, color: 'text-blue-600 bg-blue-50' },
          { icon: TrendingUp, label: 'Last Active', value: firstStudent?.last_active ? new Date(firstStudent.last_active).toLocaleDateString() : 'N/A', color: 'text-purple-600 bg-purple-50' },
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
              {stat.change && <div className="text-xs text-emerald-600 mt-1">{stat.change}</div>}
              {'desc' in stat && stat.desc && <div className="text-xs text-slate-400 mt-1">{stat.desc}</div>}
            </div>
          )
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Activity</h2>
          {progress ? (
            <div className="space-y-3">
              <div className="flex justify-between text-sm p-3 rounded-lg bg-slate-50">
                <span className="text-slate-600">Courses</span>
                <span className="font-medium">{(progress as Record<string, unknown>)?.courses ? ((progress as Record<string, unknown>).courses as unknown[]).length : 0}</span>
              </div>
              <div className="flex justify-between text-sm p-3 rounded-lg bg-slate-50">
                <span className="text-slate-600">Mastery Avg</span>
                <span className="font-medium">{firstStudent ? `${Math.round(firstStudent.overall_mastery_avg * 100)}%` : 'N/A'}</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-slate-400">No recent activity data available.</p>
          )}
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Quick Actions</h2>
          <div className="space-y-2">
            <button className="w-full text-left p-3 rounded-lg bg-navy-50 border border-navy-200 hover:bg-navy-100 transition-all">
              <span className="text-sm font-medium text-navy-800">View Full Progress</span>
            </button>
            <button className="w-full text-left p-3 rounded-lg bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 transition-all">
              <span className="text-sm font-medium text-emerald-800">Generate Report</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
