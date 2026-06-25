import { useAuthApi } from '@/hooks/useApi'
import { getTeacherStudentMastery, getTeacherStudentProgress, getTeacherStudentSessions, getTeacherStudentAttempts, getTeacherStudentMisconceptions } from '@/services/teacher'
import { Loader2, ArrowLeft, BookOpen, BarChart3, AlertTriangle } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'
import { getScoreColor, cn } from '@/lib/utils'

export function TeacherStudentDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: progress, loading: progressLoading } = useAuthApi(
    () => id ? getTeacherStudentProgress(id) : Promise.reject(), [id]
  )
  const { data: mastery, loading: masteryLoading } = useAuthApi(
    () => id ? getTeacherStudentMastery(id) : Promise.reject(), [id]
  )
  const { data: misconceptions } = useAuthApi(
    () => id ? getTeacherStudentMisconceptions(id) : Promise.reject(), [id]
  )
  const { data: sessions } = useAuthApi(
    () => id ? getTeacherStudentSessions(id, 1, 5) : Promise.reject(), [id]
  )
  const { data: attempts } = useAuthApi(
    () => id ? getTeacherStudentAttempts(id, 1, 10) : Promise.reject(), [id]
  )

  if (progressLoading || masteryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const masterySum = mastery as { total_concepts?: number; mastered_concepts?: number; average_mastery?: number; concepts?: { concept_title?: string; mastery_level: number }[] } | null
  const avgScore = masterySum ? Math.round((masterySum.average_mastery || 0) * 100) : 0

  return (
    <div className="space-y-6">
      <Link to="/teacher/students" className="inline-flex items-center gap-1 text-sm text-navy-600 hover:underline">
        <ArrowLeft className="w-4 h-4" /> Back to Students
      </Link>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: BookOpen, label: 'Completion', value: progress ? `${(progress as Record<string, unknown>).completion_percentage || 0}%` : 'N/A', color: 'text-blue-600 bg-blue-50' },
          { icon: BarChart3, label: 'Avg Mastery', value: `${avgScore}%`, color: 'text-emerald-600 bg-emerald-50' },
          { icon: AlertTriangle, label: 'Misconceptions', value: String(misconceptions?.length || 0), color: 'text-amber-600 bg-amber-50' },
          { icon: BookOpen, label: 'Sessions', value: String(sessions?.length || 0), color: 'text-purple-600 bg-purple-50' },
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
          <h2 className="font-semibold text-slate-900 mb-4">Progress Overview</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">Completed Lessons</span>
                <span className="text-emerald-600 font-medium">{progress ? (progress as Record<string, unknown>).completed_lessons || 0 : 0}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill bg-emerald-500" style={{ width: `${progress ? (progress as Record<string, unknown>).completion_percentage || 0 : 0}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">In Progress Lessons</span>
                <span className="text-amber-600 font-medium">{progress ? (progress as Record<string, unknown>).in_progress_lessons || 0 : 0}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill bg-amber-500" style={{ width: `${progress ? ((progress as Record<string, unknown>).in_progress_lessons as number || 0) * 10 : 0}%` }} />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Mastery Details</h2>
          <div className="space-y-3">
            {masterySum?.concepts?.slice(0, 10).map((c) => (
              <div key={c.concept_title || ''} className="flex items-center justify-between p-2 rounded-lg bg-slate-50">
                <span className="text-sm text-slate-700 truncate mr-2">{c.concept_title || 'Unknown Concept'}</span>
                <span className={cn('text-sm font-semibold', getScoreColor(Math.round(c.mastery_level * 100)))}>
                  {Math.round(c.mastery_level * 100)}%
                </span>
              </div>
            ))}
            {(!masterySum?.concepts || masterySum.concepts.length === 0) && (
              <p className="text-sm text-slate-400">No mastery data available.</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Sessions</h2>
          <div className="space-y-2">
            {sessions && sessions.length > 0 ? sessions.map((s) => (
              <div key={s.session_id} className="flex justify-between items-center p-3 rounded-lg bg-slate-50">
                <div>
                  <div className="text-sm font-medium text-slate-700">{s.course_title || 'Unknown'}</div>
                  <div className="text-xs text-slate-400">{s.state}</div>
                </div>
                <div className="text-xs text-slate-400">{s.last_activity_at ? new Date(s.last_activity_at).toLocaleDateString() : ''}</div>
              </div>
            )) : <p className="text-sm text-slate-400">No sessions found.</p>}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Attempts</h2>
          <div className="space-y-2">
            {attempts && attempts.length > 0 ? attempts.map((a) => (
              <div key={a.attempt_id} className="flex justify-between items-center p-3 rounded-lg bg-slate-50">
                <div>
                  <div className="text-sm font-medium text-slate-700">{a.concept_title || 'Exercise'}</div>
                  <div className={`text-xs ${a.is_correct ? 'text-emerald-600' : 'text-red-500'}`}>
                    {a.is_correct ? 'Correct' : 'Incorrect'} · Score: {a.score}
                  </div>
                </div>
                <div className="text-xs text-slate-400">{a.attempted_at ? new Date(a.attempted_at).toLocaleDateString() : ''}</div>
              </div>
            )) : <p className="text-sm text-slate-400">No attempts found.</p>}
          </div>
        </div>
      </div>

      {misconceptions && misconceptions.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Active Misconceptions</h2>
          <div className="space-y-3">
            {misconceptions.map((m) => (
              <div key={m.misconception_id} className="flex items-start gap-3 p-3 rounded-lg bg-red-50 border border-red-100">
                <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="text-sm font-medium text-slate-800">{m.concept_title || 'Unknown Concept'}</div>
                  <div className="text-xs text-slate-600">{m.description}</div>
                  <div className="text-xs text-slate-400 mt-1">Category: {m.category} · Frequency: {m.frequency}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
