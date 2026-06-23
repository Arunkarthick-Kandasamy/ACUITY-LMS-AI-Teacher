import { parentData, openScoreData } from '@/data/mockData'
import { getScoreColor, formatScore } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { Clock, TrendingUp, BookOpen, ArrowUpRight } from 'lucide-react'

export function ParentStudentDetail() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{parentData.studentName}'s Progress</h1>
          <p className="text-sm text-slate-500 mt-1">Grade {parentData.grade} · Detailed performance view</p>
        </div>
        <button className="btn-secondary text-sm">
          Download Report <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Open Score Parameters</h2>
          <div className="space-y-4">
            {[
              { label: 'Correctness', value: openScoreData.parameters.correctness, desc: 'Accuracy of answers' },
              { label: 'Response Time', value: openScoreData.parameters.responseTime, desc: 'Speed of answering' },
              { label: 'Retries', value: openScoreData.parameters.retries, desc: 'Attempts to reach correct answer' },
              { label: 'Skips', value: openScoreData.parameters.skips, desc: 'Questions avoided or abandoned' },
            ].map((param) => (
              <div key={param.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-700">{param.label}</span>
                  <span className={cn('font-medium', getScoreColor(param.value))}>{param.value}/100</span>
                </div>
                <div className="progress-bar">
                  <div className={cn(
                    'progress-bar-fill',
                    param.value >= 75 ? 'bg-emerald-500' : param.value >= 50 ? 'bg-amber-500' : 'bg-red-500'
                  )} style={{ width: `${param.value}%` }} />
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">{param.desc}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Learning Behavior</h2>
          <div className="space-y-4">
            {[
              { icon: Clock, label: 'Peak Learning Time', value: '10:00 AM - 12:00 PM', desc: 'Student performs best during this time' },
              { icon: BookOpen, label: 'Current Module', value: 'Simplified (Support Track)', desc: 'Open Score 72 — foundational reinforcement' },
              { icon: TrendingUp, label: 'Weekly Trend', value: '↑ Improving', desc: '+10% accuracy improvement this week' },
            ].map((item) => {
              const Icon = item.icon
              return (
                <div key={item.label} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
                  <div className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center mt-0.5">
                    <Icon className="w-4 h-4 text-slate-500" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400">{item.label}</div>
                    <div className="text-sm font-semibold text-slate-800">{item.value}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
