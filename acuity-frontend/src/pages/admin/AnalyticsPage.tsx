import { useState, useEffect } from 'react'
import { getSystemOverview, getAssessmentAnalytics, getCourseAnalytics } from '@/services/analytics'
import { mockSystemOverview, mockAssessmentAnalytics, mockCourseAnalytics } from './admin-mock-data'
import { BarChart3, TrendingUp, Users, BookOpen, Loader2, Clock, CheckCircle2, XCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AnalyticsPage() {
  const [courseId, setCourseId] = useState('')
  const [overview, setOverview] = useState<typeof mockSystemOverview | null>(null)
  const [courseStats, setCourseStats] = useState<typeof mockCourseAnalytics | null>(null)
  const [assessmentStats, setAssessmentStats] = useState<typeof mockAssessmentAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [showCourseAnalytics, setShowCourseAnalytics] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)

  useEffect(() => {
    getSystemOverview()
      .then(res => setOverview(res.data ?? mockSystemOverview))
      .catch(() => setOverview(mockSystemOverview))
      .finally(() => setLoading(false))
  }, [])

  const handleAnalyze = async () => {
    if (!courseId) return
    setAnalyzing(true)
    setShowCourseAnalytics(true)
    const [cRes, aRes] = await Promise.all([
      getCourseAnalytics(courseId).catch(() => ({ data: mockCourseAnalytics })),
      getAssessmentAnalytics(courseId).catch(() => ({ data: mockAssessmentAnalytics })),
    ])
    setCourseStats(cRes.data ?? mockCourseAnalytics)
    setAssessmentStats(aRes.data ?? mockAssessmentAnalytics)
    setAnalyzing(false)
  }

  const displayOverview = overview ?? mockSystemOverview
  const displayCourse = courseStats ?? mockCourseAnalytics
  const displayAssess = assessmentStats ?? mockAssessmentAnalytics

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
        <h1 className="text-xl font-semibold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">System-wide performance metrics</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Platform Overview</h2>
          <div className="space-y-3">
            {[
              { label: 'Total Users', value: displayOverview.total_users },
              { label: 'Students', value: displayOverview.total_students },
              { label: 'Admins', value: displayOverview.total_admins },
              { label: 'Parents', value: displayOverview.total_parents },
            ].map(s => (
              <div key={s.label} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                <span className="text-sm text-gray-600">{s.label}</span>
                <span className="font-bold text-gray-900">{s.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Performance Overview</h2>
          <div className="space-y-3">
            {[
              { icon: Users, label: 'Active Enrollments', value: displayOverview.active_enrollments.toLocaleString(), desc: 'Current enrollments' },
              { icon: BookOpen, label: 'Total Courses', value: String(displayOverview.total_courses), desc: 'Available courses' },
              { icon: BarChart3, label: 'Completion Rate', value: `${Math.round(displayOverview.overall_completion_rate)}%`, desc: 'Average lesson completion' },
              { icon: TrendingUp, label: 'Assessment Pass Rate', value: `${Math.round(displayOverview.overall_pass_rate)}%`, desc: 'Overall pass rate' },
              { icon: Clock, label: 'Active Sessions Today', value: String(displayOverview.active_sessions_today), desc: 'Sessions active in 24h' },
              { icon: BarChart3, label: 'Total Attempts', value: displayOverview.total_assessment_attempts.toLocaleString(), desc: 'All assessment attempts' },
            ].map((stat) => {
              const Icon = stat.icon
              return (
                <div key={stat.label} className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <div className="w-9 h-9 rounded-lg bg-white border border-gray-200 flex items-center justify-center">
                    <Icon className="w-4.5 h-4.5 text-gray-500" />
                  </div>
                  <div>
                    <div className="text-xs text-gray-400">{stat.label}</div>
                    <div className="text-lg font-bold text-gray-900">{stat.value}</div>
                    <div className="text-[10px] text-gray-400">{stat.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h2 className="font-semibold text-gray-900 mb-4">Course & Assessment Analytics</h2>
        <div className="flex gap-3 mb-4">
          <input
            type="text"
            value={courseId}
            onChange={(e) => setCourseId(e.target.value)}
            placeholder="Enter Course ID (e.g. course_001)"
            className="flex-1 px-3.5 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
          />
          <button
            onClick={handleAnalyze}
            disabled={!courseId || analyzing}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-all"
          >
            {analyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
            Analyze
          </button>
        </div>

        {showCourseAnalytics && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-3 gap-4">
              {[
                { label: 'Total Students', value: displayCourse.total_students.toLocaleString() },
                { label: 'Active Students', value: displayCourse.active_students.toLocaleString() },
                { label: 'Completion Rate', value: `${Math.round(displayCourse.completion_rate)}%` },
                { label: 'Avg Mastery', value: `${(displayCourse.avg_mastery * 100).toFixed(1)}%` },
                { label: 'Avg Assessment Score', value: `${Math.round(displayCourse.avg_assessment_score)}%` },
                { label: 'Total Assessments', value: String(displayCourse.total_assessments) },
              ].map((s) => (
                <div key={s.label} className="p-3 rounded-lg bg-gray-50 text-center">
                  <div className="text-xs text-gray-400">{s.label}</div>
                  <div className="text-xl font-bold text-gray-900">{s.value}</div>
                </div>
              ))}
            </div>

            <div className="border-t border-gray-100 pt-4">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Assessment Analytics</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-3 rounded-lg bg-green-50">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <div>
                    <div className="text-xs text-gray-400">Passed</div>
                    <div className="text-lg font-bold text-green-700">{displayAssess.pass_count.toLocaleString()}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-red-50">
                  <XCircle className="w-5 h-5 text-red-600" />
                  <div>
                    <div className="text-xs text-gray-400">Failed</div>
                    <div className="text-lg font-bold text-red-700">{displayAssess.fail_count.toLocaleString()}</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-blue-50">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="text-xs text-gray-400">Average Score</div>
                    <div className="text-lg font-bold text-blue-700">{displayAssess.average_score.toFixed(1)}%</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <BarChart3 className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-xs text-gray-400">Pass Rate</div>
                    <div className="text-lg font-bold text-gray-900">{displayAssess.pass_rate.toFixed(1)}%</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <Clock className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-xs text-gray-400">Avg Time</div>
                    <div className="text-lg font-bold text-gray-900">{Math.round(displayAssess.avg_time_spent_seconds / 60)} min</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
                  <BarChart3 className="w-5 h-5 text-gray-600" />
                  <div>
                    <div className="text-xs text-gray-400">Total Attempts</div>
                    <div className="text-lg font-bold text-gray-900">{displayAssess.total_attempts.toLocaleString()}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
