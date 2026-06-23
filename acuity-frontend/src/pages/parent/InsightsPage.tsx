import { parentData, openScoreData } from '@/data/mockData'
import { Clock, TrendingUp, BrainCircuit, BarChart3, Zap } from 'lucide-react'

export function InsightsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Learning Insights</h1>
        <p className="text-sm text-slate-500 mt-1">AI-powered analysis of learning behavior</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {[
          { icon: Clock, title: 'Peak Learning Time', desc: 'Your child performs best between 10:00 AM - 12:00 PM.', detail: 'Accuracy during this period is 15% higher than other times. Consider scheduling study sessions accordingly.', color: 'bg-blue-50 border-blue-200' },
          { icon: TrendingUp, title: 'Performance Trend', desc: 'Open Score has improved 8% over the last 4 lessons.', detail: 'Consistent improvement in Correctness (+12%) and Response Time (+5%). Retries decreased by 20%.', color: 'bg-emerald-50 border-emerald-200' },
          { icon: BrainCircuit, title: 'Learning Pattern', desc: 'Support Learner Track — Simplified module approach.', detail: 'Step-by-step explanations with examples yield 25% better retention. HOT questions will be introduced gradually.', color: 'bg-amber-50 border-amber-200' },
          { icon: BarChart3, title: 'Subject Breakdown', desc: 'Algebra: Strong (92%). Trigonometry: Needs improvement (25%).', detail: 'Recommended focus: Trigonometric identities and chain rule applications.', color: 'bg-purple-50 border-purple-200' },
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
            { icon: Clock, text: 'Schedule study sessions during peak hours (10 AM - 12 PM) for optimal performance.' },
            { icon: Zap, text: 'Focus on Trigonometry fundamentals — 15 minutes of daily practice recommended.' },
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
