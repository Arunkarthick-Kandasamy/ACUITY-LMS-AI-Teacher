import { adminData } from '@/data/mockData'
import { BarChart3, TrendingUp, Users, BookOpen } from 'lucide-react'

export function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Analytics</h1>
        <p className="text-sm text-slate-500 mt-1">System-wide performance metrics</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Enrollment Growth</h2>
          <div className="flex items-end gap-2 h-40">
            {adminData.weeklyEnrollments.map((w, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-xs font-medium text-slate-500">{w.count}</span>
                <div className="w-full bg-gradient-to-t from-navy-700 to-navy-500 rounded-t-md" style={{ height: `${(w.count / 150) * 100}%` }} />
                <span className="text-[9px] text-slate-400">{w.week}</span>
              </div>
            ))}
          </div>
          <p className="text-xs text-slate-400 mt-3">Total growth: {((adminData.weeklyEnrollments[adminData.weeklyEnrollments.length - 1].count - adminData.weeklyEnrollments[0].count) / adminData.weeklyEnrollments[0].count * 100).toFixed(0)}% over 8 weeks</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Performance Overview</h2>
          <div className="space-y-4">
            {[
              { icon: Users, label: 'Student-Teacher Ratio', value: '48:1', desc: 'AI-powered ratio' },
              { icon: TrendingUp, label: 'Avg Improvement Rate', value: '+12%', desc: 'Per student per month' },
              { icon: BookOpen, label: 'Lessons Completed', value: '12,847', desc: 'Total platform-wide' },
              { icon: BarChart3, label: 'Avg Open Score', value: '68.5', desc: 'Across all students' },
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
    </div>
  )
}
