import { useAuthApi } from '@/hooks/useApi'
import { getParentStudents } from '@/services/parent'
import { Clock, TrendingUp, BrainCircuit, BarChart3, Zap, Loader2 } from 'lucide-react'

export function InsightsPage() {
  const { data: students, loading } = useAuthApi(() => getParentStudents(), [])
  const student = students?.[0]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const masteryPct = student ? Math.round(student.overall_mastery_avg * 100) : 0
  const track = masteryPct >= 75 ? 'Good Learner' : 'Support Learner'

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Learning Insights</h1>
        <p className="text-sm text-slate-500 mt-1">AI-powered analysis of learning behavior</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {[
          { icon: Clock, title: 'Student Overview', desc: `${student?.full_name || 'N/A'} (${student?.grade_level || 'N/A'})`, detail: `${student?.active_courses || 0} active course(s) · ${masteryPct}% overall mastery`, color: 'bg-blue-50 border-blue-200' },
          { icon: TrendingUp, title: 'Performance Trend', desc: student ? `Mastery: ${masteryPct}% · ${track} Track` : 'N/A', detail: student ? `${student.current_streak_days || 0} day learning streak` : '', color: 'bg-emerald-50 border-emerald-200' },
          { icon: BrainCircuit, title: 'Learning Track', desc: `${track} — ${masteryPct >= 75 ? 'Advanced concept-based learning' : 'Simplified step-by-step approach'}`, detail: 'Personalized curriculum adapted to performance', color: 'bg-amber-50 border-amber-200' },
          { icon: BarChart3, title: 'Course Engagement', desc: `${student?.active_courses || 0} active course(s)`, detail: 'Track progress across all enrolled courses', color: 'bg-purple-50 border-purple-200' },
        ].map((item, i) => {
          const Icon = item.icon
          return (
            <div key={i} className={`rounded-xl border p-5 ${item.color}`}>
              <div className="flex items-center gap-2 mb-3">
                <Icon className="w-5 h-5 text-slate-700" />
                <h3 className="font-semibold text-slate-900">{item.title}</h3>
              </div>
              <p className="text-sm text-slate-700 mb-2">{item.desc}</p>
              <p className="text-xs text-slate-500">{item.detail}</p>
            </div>
          )
        })}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 mb-4">Recommendations</h2>
        <div className="space-y-3">
          {[
            { icon: Clock, text: masteryPct < 75 ? 'Focus on foundational concepts to build a stronger base.' : 'Continue challenging with advanced concepts and HOT questions.' },
            { icon: Zap, text: 'Regular practice of 15-20 minutes daily yields optimal results.' },
            { icon: TrendingUp, text: 'Review previous lesson concepts before starting new material for better retention.' },
          ].map((rec, i) => {
            const Icon = rec.icon
            return (
              <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
                <div className="w-7 h-7 rounded-full bg-navy-800 flex items-center justify-center mt-0.5">
                  <Icon className="w-3.5 h-3.5 text-white" />
                </div>
                <p className="text-sm text-slate-700">{rec.text}</p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
