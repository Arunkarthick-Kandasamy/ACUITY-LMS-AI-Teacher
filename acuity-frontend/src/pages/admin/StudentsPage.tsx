import { adminData, parentData } from '@/data/mockData'
import { cn } from '@/lib/utils'
import { Search, Filter } from 'lucide-react'

export function StudentsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Students</h1>
          <p className="text-sm text-slate-500 mt-1">Manage and monitor all students</p>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input type="text" placeholder="Search students..." className="input-field pl-10" />
        </div>
        <button className="btn-secondary">
          <Filter className="w-4 h-4 mr-1.5" /> Filters
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Grade</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Open Score</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Track</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Lessons Done</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {adminData.students.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-navy-100 flex items-center justify-center text-xs font-bold text-navy-700">
                        {s.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span className="font-medium text-slate-800">{s.name}</span>
                    </div>
                  </td>
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
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-1.5">
                      <div className={cn(
                        'w-1.5 h-1.5 rounded-full',
                        s.lastActive === 'Just now' ? 'bg-emerald-500' : 'bg-slate-300'
                      )} />
                      <span className="text-xs text-slate-400">{s.lastActive}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
