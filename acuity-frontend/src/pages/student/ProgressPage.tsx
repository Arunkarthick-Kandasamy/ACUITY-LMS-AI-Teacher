import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { getCourseMastery } from '@/services/mastery'
import { getTrackLabel } from '@/lib/utils'
import { TrendingUp, Clock, Target, Zap, Loader2 } from 'lucide-react'

export function ProgressPage() {
  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  const { data: masterySummary, loading } = useAuthApi(
    () => courseId ? getCourseMastery(courseId) : Promise.reject(),
    [courseId],
  )

  const trackInfo = getTrackLabel(masterySummary ? Math.round(masterySummary.average_mastery * 100) : 0)
  const overallScore = masterySummary ? Math.round(masterySummary.average_mastery * 100) : 0

  const weakConcepts = masterySummary?.concepts
    ?.filter(c => c.mastery_level < 0.5)
    ?.map(c => ({ topic: c.concept_title || c.concept_id, mastery: Math.round(c.mastery_level * 100) }))
    ?.sort((a, b) => a.mastery - b.mastery) || []

  const strongConcepts = masterySummary?.concepts
    ?.filter(c => c.mastery_level >= 0.5)
    ?.map(c => ({ topic: c.concept_title || c.concept_id, mastery: Math.round(c.mastery_level * 100) }))
    ?.sort((a, b) => b.mastery - a.mastery) || []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">My Progress</h1>
        <p className="text-sm text-slate-500 mt-1">Track your learning journey and growth over time</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Areas to Improve</h2>
          {weakConcepts.length === 0 ? (
            <p className="text-sm text-slate-400">No weak areas found. Great job!</p>
          ) : (
            <div className="space-y-3">
              {weakConcepts.map((topic) => (
                <div key={topic.topic} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center shrink-0">
                    <Zap className="w-4 h-4 text-red-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-700 truncate">{topic.topic}</span>
                      <span className="text-red-500 font-medium shrink-0 ml-2">{topic.mastery}%</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-bar-fill bg-red-500" style={{ width: `${topic.mastery}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Strong Areas</h2>
          {strongConcepts.length === 0 ? (
            <p className="text-sm text-slate-400">Keep practicing to build strong foundations!</p>
          ) : (
            <div className="space-y-3">
              {strongConcepts.map((topic) => (
                <div key={topic.topic} className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center shrink-0">
                    <Zap className="w-4 h-4 text-emerald-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-700 truncate">{topic.topic}</span>
                      <span className="text-emerald-600 font-medium shrink-0 ml-2">{topic.mastery}%</span>
                    </div>
                    <div className="progress-bar">
                      <div className="progress-bar-fill bg-emerald-500" style={{ width: `${topic.mastery}%` }} />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 mb-4">Learning Insights</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: TrendingUp, label: 'Track', value: trackInfo.label, color: 'text-navy-600 bg-navy-50' },
            { icon: Target, label: 'Overall Score', value: `${overallScore}/100`, color: 'text-emerald-600 bg-emerald-50' },
            { icon: Clock, label: 'Concepts', value: `${masterySummary?.total_concepts || 0} total`, color: 'text-amber-600 bg-amber-50' },
            { icon: Zap, label: 'Mastered', value: `${masterySummary?.mastered_concepts || 0} concepts`, color: 'text-blue-600 bg-blue-50' },
          ].map((item) => {
            const Icon = item.icon
            return (
              <div key={item.label} className="flex items-center gap-3 p-3 rounded-lg bg-slate-50">
                <div className={`w-9 h-9 rounded-lg ${item.color} flex items-center justify-center`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-400">{item.label}</div>
                  <div className="text-sm font-semibold text-slate-800">{item.value}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
