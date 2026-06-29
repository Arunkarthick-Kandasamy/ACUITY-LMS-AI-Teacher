import { useAuthApi } from '@/hooks/useApi'
import { getDashboard } from '@/services/courseAdmin'
import { Link } from 'react-router-dom'
import {
  Bot, Users, BookOpen, Loader2, Plus, CheckCircle2,
  Clock, AlertCircle, Brain, BarChart3, FileText,
  AlertTriangle, GraduationCap,
} from 'lucide-react'

const statusColors: Record<string, string> = {
  draft: 'bg-slate-100 text-slate-600',
  training: 'bg-blue-100 text-blue-700',
  review: 'bg-amber-100 text-amber-700',
  ready: 'bg-emerald-100 text-emerald-700',
  deployed: 'bg-purple-100 text-purple-700',
  archived: 'bg-slate-100 text-slate-400',
}

export function CourseAdminDashboard() {
  const { data: stats, loading } = useAuthApi(() => getDashboard(), [])

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-5 h-5 animate-spin text-blue-600" /></div>
  }

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-sm font-semibold text-slate-900">Dashboard</h1>
          <p className="text-[10px] text-slate-400 mt-0.5">{stats?.total_courses || 0} courses · {stats?.total_published || 0} published</p>
        </div>
        <Link to="/course-admin/create" className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700">
          <Plus className="w-3.5 h-3.5" />
          Create Course
        </Link>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-7 gap-3">
        {[
          { icon: GraduationCap, label: 'Total', value: stats?.total_courses ?? 0, color: 'text-indigo-600 bg-indigo-50' },
          { icon: CheckCircle2, label: 'Published', value: stats?.deployed_count ?? 0, color: 'text-purple-600 bg-purple-50' },
          { icon: Brain, label: 'Training', value: stats?.training_count ?? 0, color: 'text-blue-600 bg-blue-50' },
          { icon: AlertCircle, label: 'Review', value: stats?.review_count ?? 0, color: 'text-amber-600 bg-amber-50' },
          { icon: Clock, label: 'Draft', value: stats?.draft_count ?? 0, color: 'text-slate-600 bg-slate-50' },
          { icon: BookOpen, label: 'Published', value: stats?.total_published ?? 0, color: 'text-emerald-600 bg-emerald-50' },
          { icon: AlertTriangle, label: 'Failed', value: stats?.failed_stages_count ?? 0, color: 'text-red-600 bg-red-50' },
        ].map(stat => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white rounded-lg border border-slate-200 p-3 shadow-sm">
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`w-6 h-6 rounded ${stat.color} flex items-center justify-center`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="text-[10px] text-slate-400 font-medium uppercase tracking-wide">{stat.label}</span>
              </div>
              <div className="text-lg font-bold text-slate-900">{stat.value}</div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Recent Courses */}
        <div className="col-span-2 bg-white rounded-lg border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100">
            <h2 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">Recent Courses</h2>
            <Link to="/course-admin/courses" className="text-[10px] text-blue-600 hover:underline">View all</Link>
          </div>
          {stats?.recent_courses?.length ? (
            <div className="divide-y divide-slate-50">
              {stats.recent_courses.map(c => {
                const sp = c.stage_progress
                return (
                  <Link key={c.id} to={`/course-admin/courses/${c.id}`}
                    className="flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50 transition-colors group">
                    <div className="w-7 h-7 rounded bg-indigo-50 flex items-center justify-center shrink-0">
                      <GraduationCap className="w-3.5 h-3.5 text-indigo-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-medium text-slate-800 truncate">{c.name}</div>
                      <div className="text-[10px] text-slate-400">{c.description || '—'}</div>
                    </div>
                    <div className="flex items-center gap-3">
                      {sp && (
                        <div className="flex items-center gap-1.5">
                          <div className="w-16 bg-slate-100 rounded-full h-1.5">
                            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${sp.pct}%` }} />
                          </div>
                          <span className="text-[10px] text-slate-400 font-medium">{sp.completed}/{sp.total}</span>
                        </div>
                      )}
                      <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${statusColors[c.status] || ''}`}>
                        {c.status}
                      </span>
                    </div>
                  </Link>
                )
              })}
            </div>
          ) : (
            <div className="p-8 text-center">
              <GraduationCap className="w-8 h-8 text-slate-200 mx-auto mb-2" />
              <p className="text-xs text-slate-400">No courses yet</p>
              <Link to="/course-admin/create" className="text-xs text-blue-600 hover:underline mt-1 inline-block">Create your first</Link>
            </div>
          )}
        </div>

        {/* Side panel */}
        <div className="space-y-3">
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
            <h2 className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-3">Content Generated</h2>
            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">Concepts</span>
                  <span className="font-semibold text-slate-800">{stats?.total_concepts_generated ?? 0}</span>
                </div>
                <div className="mt-1 w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${Math.min(100, (stats?.total_concepts_generated ?? 0) * 5)}%` }} />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">Exercises</span>
                  <span className="font-semibold text-slate-800">{stats?.total_exercises_generated ?? 0}</span>
                </div>
                <div className="mt-1 w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${Math.min(100, (stats?.total_exercises_generated ?? 0) * 2)}%` }} />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-500">Coverage</span>
                  <span className="font-semibold text-slate-800">{stats?.avg_coverage_pct ?? 0}%</span>
                </div>
                <div className="mt-1 w-full bg-slate-100 rounded-full h-1.5">
                  <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${stats?.avg_coverage_pct ?? 0}%` }} />
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
            <h2 className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Quick Actions</h2>
            <div className="space-y-1">
              <Link to="/course-admin/create" className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-slate-600 hover:bg-slate-50">
                <Plus className="w-3 h-3 text-blue-500" />
                Create Course
              </Link>
              {stats?.pending_review_count ? (
                <Link to="/course-admin/courses" className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-amber-600 hover:bg-amber-50">
                  <AlertCircle className="w-3 h-3" />
                  {stats.pending_review_count} pending review
                </Link>
              ) : null}
              {stats?.failed_stages_count ? (
                <Link to="/course-admin/courses" className="flex items-center gap-2 px-2 py-1.5 rounded text-xs text-red-600 hover:bg-red-50">
                  <AlertTriangle className="w-3 h-3" />
                  {stats.failed_stages_count} failed stages
                </Link>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
