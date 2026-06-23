import { studentProfile, openScoreData, parentData } from '@/data/mockData'
import { getScoreColor, formatScore, getTrackLabel } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { TrendingUp, Clock, Target, Zap } from 'lucide-react'

export function ProgressPage() {
  const trackInfo = getTrackLabel(openScoreData.overall)
  const weakTopics = parentData.weakTopics
  const strongTopics = parentData.strongTopics

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">My Progress</h1>
        <p className="text-sm text-slate-500 mt-1">Track your learning journey and growth over time</p>
      </div>

      {/* Score History */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 mb-4">Open Score History</h2>
        <div className="flex items-end gap-2 h-32">
          {openScoreData.history.map((h, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <span className={cn('text-xs font-medium', getScoreColor(h.score))}>{h.score}</span>
              <div
                className={cn('w-full rounded-t-md transition-all hover:opacity-80',
                  h.score >= 75 ? 'bg-emerald-500' : h.score >= 50 ? 'bg-amber-500' : 'bg-red-500'
                )}
                style={{ height: `${h.score}%`, maxHeight: '100px', minHeight: '4px' }}
              />
              <span className="text-[10px] text-slate-400">{h.lesson}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Weak / Strong Topics */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Areas to Improve</h2>
          <div className="space-y-3">
            {weakTopics.map((topic) => (
              <div key={topic.topic}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-700">{topic.topic}</span>
                  <span className="text-red-500 font-medium">{topic.mastery}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-bar-fill bg-red-500" style={{ width: `${topic.mastery}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Strong Areas</h2>
          <div className="space-y-3">
            {strongTopics.map((topic) => (
              <div key={topic.topic} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <Zap className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="flex-1">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-700">{topic.topic}</span>
                    <span className="text-emerald-600 font-medium">{topic.mastery}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-bar-fill bg-emerald-500" style={{ width: `${topic.mastery}%` }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Learning Insights */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 mb-4">Learning Insights</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: TrendingUp, label: 'Track', value: trackInfo.label, color: 'text-navy-600 bg-navy-50' },
            { icon: Target, label: 'Current Score', value: `${openScoreData.overall}/100`, color: 'text-emerald-600 bg-emerald-50' },
            { icon: Clock, label: 'Peak Time', value: studentProfile.peakLearningTime, color: 'text-amber-600 bg-amber-50' },
            { icon: Zap, label: 'Pace', value: studentProfile.learningPace, color: 'text-blue-600 bg-blue-50' },
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
