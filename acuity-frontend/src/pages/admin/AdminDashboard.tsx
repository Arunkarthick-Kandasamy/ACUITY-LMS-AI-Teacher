import { adminData } from '@/data/mockData'
import { Users, BookOpen, TrendingUp, BarChart3, Activity } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AdminDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Admin Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Platform overview and system analytics</p>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Users, label: 'Total Students', value: adminData.totalStudents.toLocaleString(), change: '+12 this week', color: 'text-blue-600 bg-blue-50' },
          { icon: Users, label: 'Total Parents', value: adminData.totalParents.toLocaleString(), change: '+8 this week', color: 'text-purple-600 bg-purple-50' },
          { icon: Activity, label: 'Active Today', value: adminData.activeToday.toLocaleString(), change: '42% of total', color: 'text-emerald-600 bg-emerald-50' },
          { icon: TrendingUp, label: 'Avg Open Score', value: `${adminData.avgOpenScore}`, change: '+2.5% this month', color: 'text-amber-600 bg-amber-50' },
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
              <div className="text-xs text-slate-500 mt-1">{stat.change}</div>
            </div>
          )
        })}
      </div>

      {/* Track Distribution */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Track Distribution</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">Good Learners (Score ≥ 75)</span>
                <span className="text-emerald-600 font-medium">{adminData.trackDistribution.good}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill bg-emerald-500" style={{ width: `${(adminData.trackDistribution.good / adminData.totalStudents) * 100}%` }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-700">Support Learners (Score &lt; 75)</span>
                <span className="text-amber-600 font-medium">{adminData.trackDistribution.support}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-bar-fill bg-amber-500" style={{ width: `${(adminData.trackDistribution.support / adminData.totalStudents) * 100}%` }} />
              </div>
            </div>
            <p className="text-xs text-slate-400 mt-2">
              {Math.round((adminData.trackDistribution.support / adminData.totalStudents) * 100)}% of students need additional support
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Weekly Enrollments</h2>
          <div className="flex items-end gap-2 h-32">
            {adminData.weeklyEnrollments.map((w, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-xs font-medium text-slate-500">{w.count}</span>
                <div className="w-full bg-navy-600 rounded-t-md" style={{ height: `${(w.count / 150) * 100}%` }} />
                <span className="text-[9px] text-slate-400">{w.week}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Students Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="font-semibold text-slate-900">Recent Students</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Grade</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Open Score</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Track</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Lessons</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Last Active</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {adminData.students.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-3 font-medium text-slate-800">{s.name}</td>
                  <td className="px-6 py-3 text-slate-500">{s.grade}</td>
                  <td className="px-6 py-3">
                    <span className={cn('font-medium', s.score >= 75 ? 'text-emerald-600' : s.score >= 50 ? 'text-amber-600' : 'text-red-600')}>
                      {s.score}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className={cn(
                      'badge',
                      s.track === 'Good' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                    )}>{s.track}</span>
                  </td>
                  <td className="px-6 py-3 text-slate-500">{s.lessons}</td>
                  <td className="px-6 py-3 text-slate-400 text-xs">{s.lastActive}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
