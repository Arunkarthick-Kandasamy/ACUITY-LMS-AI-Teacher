import { useState } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { getSystemOverview, getAssessmentAnalytics, getCourseAnalytics } from '@/services/analytics'
import { BarChart3, TrendingUp, Users, BookOpen, Loader2, Clock, CheckCircle2, XCircle } from 'lucide-react'

export function AnalyticsPage() {
  const [courseId, setCourseId] = useState('')
  const [showCourseAnalytics, setShowCourseAnalytics] = useState(false)

  const { data: overview, loading } = useAuthApi(() => getSystemOverview(), [])

  const { data: assessmentStats, loading: assessLoading, refetch: refetchAssess } =
    useAuthApi(() => getAssessmentAnalytics(courseId), [courseId, showCourseAnalytics])

  const { data: courseStats, refetch: refetchCourse } =
    useAuthApi(() => getCourseAnalytics(courseId), [courseId, showCourseAnalytics])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const handleAnalyze = () => {
    if (!courseId) return
    setShowCourseAnalytics(true)
    refetchAssess()
    refetchCourse()
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
              <span className="font-bold text-slate-900">{overview?.total_users || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Students</span>
              <span className="font-bold text-slate-900">{overview?.total_students || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Admins</span>
              <span className="font-bold text-slate-900">{overview?.total_admins || 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
              <span className="text-sm text-slate-600">Parents</span>
              <span className="font-bold text-slate-900">{overview?.total_parents || 0}</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Performance Overview</h2>
          <div className="space-y-4">
            {[
              { icon: Users, label: 'Active Enrollments', value: String(overview?.active_enrollments || 0), desc: 'Current enrollments' },
              { icon: BookOpen, label: 'Total Courses', value: String(overview?.total_courses || 0), desc: 'Available courses' },
              { icon: BarChart3, label: 'Completion Rate', value: overview?.overall_completion_rate != null ? `${Math.round(overview.overall_completion_rate)}%` : 'N/A', desc: 'Average lesson completion' },
              { icon: TrendingUp, label: 'Assessment Pass Rate', value: overview?.overall_pass_rate != null ? `${Math.round(overview.overall_pass_rate)}%` : 'N/A', desc: 'Overall pass rate' },
              { icon: Clock, label: 'Active Sessions Today', value: String(overview?.active_sessions_today || 0), desc: 'Sessions active in 24h' },
              { icon: BarChart3, label: 'Total Attempts', value: String(overview?.total_assessment_attempts || 0), desc: 'All assessment attempts' },
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

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 mb-4">Course & Assessment Analytics</h2>
        <div className="flex gap-3 mb-4">
          <input
            type="text"
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            placeholder="Enter Course ID"
            className="flex-1 px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-navy-500"
          />
          <button
            onClick={handleAnalyze}
            disabled={!courseId || assessLoading}
            className="px-4 py-2 bg-navy-600 text-white text-sm font-medium rounded-lg hover:bg-navy-700 disabled:opacity-50"
          >
            {assessLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Analyze'}
          </button>
        </div>

        {showCourseAnalytics && courseStats && (
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {[
              { label: 'Total Students', value: String(courseStats.total_students) },
              { label: 'Active Students', value: String(courseStats.active_students) },
              { label: 'Completion Rate', value: `${Math.round(courseStats.completion_rate)}%` },
              { label: 'Avg Mastery', value: `${(courseStats.avg_mastery * 100).toFixed(1)}%` },
              { label: 'Avg Assessment Score', value: `${Math.round(courseStats.avg_assessment_score)}%` },
              { label: 'Total Assessments', value: String(courseStats.total_assessments) },
            ].map((s) => (
              <div key={s.label} className="p-3 rounded-lg bg-slate-50 text-center">
                <div className="text-xs text-slate-400">{s.label}</div>
                <div className="text-xl font-bold text-slate-900">{s.value}</div>
              </div>
            ))}
          </div>
        )}

        {showCourseAnalytics && assessmentStats && (
          <div className="border-t border-slate-200 pt-4">
            <h3 className="text-sm font-medium text-slate-700 mb-3">Assessment Analytics</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-green-50">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <div>
                  <div className="text-xs text-slate-400">Passed</div>
                  <div className="text-lg font-bold text-green-700">{assessmentStats.pass_count}</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-red-50">
                <XCircle className="w-5 h-5 text-red-600" />
                <div>
                  <div className="text-xs text-slate-400">Failed</div>
                  <div className="text-lg font-bold text-red-700">{assessmentStats.fail_count}</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50">
                <TrendingUp className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="text-xs text-slate-400">Average Score</div>
                  <div className="text-lg font-bold text-blue-700">{assessmentStats.average_score.toFixed(1)}%</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                <BarChart3 className="w-5 h-5 text-slate-600" />
                <div>
                  <div className="text-xs text-slate-400">Pass Rate</div>
                  <div className="text-lg font-bold text-slate-900">{assessmentStats.pass_rate.toFixed(1)}%</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                <Clock className="w-5 h-5 text-slate-600" />
                <div>
                  <div className="text-xs text-slate-400">Avg Time</div>
                  <div className="text-lg font-bold text-slate-900">{Math.round(assessmentStats.avg_time_spent_seconds)}s</div>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                <BarChart3 className="w-5 h-5 text-slate-600" />
                <div>
                  <div className="text-xs text-slate-400">Total Attempts</div>
                  <div className="text-lg font-bold text-slate-900">{assessmentStats.total_attempts}</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
