import { useAuthApi } from '@/hooks/useApi'
import { getTeacherStudents } from '@/services/teacher'
import { Loader2, Search, ArrowUpRight } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useState } from 'react'

export function TeacherStudentsPage() {
  const { data: students, loading } = useAuthApi(() => getTeacherStudents(), [])
  const [search, setSearch] = useState('')

  const filtered = students?.filter(s =>
    s.full_name.toLowerCase().includes(search.toLowerCase())
  ) || []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">My Students</h1>
        <p className="text-sm text-slate-500 mt-1">{students?.length || 0} assigned student(s)</p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search students..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-navy-500"
        />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Grade</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Courses</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Mastery</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Streak</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Last Active</th>
                <th className="text-right px-6 py-3 text-xs font-medium text-slate-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((s) => (
                <tr key={s.student_id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-3">
                    <div className="font-medium text-slate-800">{s.full_name}</div>
                    <div className="text-xs text-slate-400">{s.email}</div>
                  </td>
                  <td className="px-6 py-3 text-slate-600">{s.grade_level || 'N/A'}</td>
                  <td className="px-6 py-3 text-slate-600">{s.active_courses}</td>
                  <td className="px-6 py-3">
                    <span className={`font-semibold ${s.overall_mastery_avg >= 0.75 ? 'text-emerald-600' : s.overall_mastery_avg >= 0.5 ? 'text-amber-600' : 'text-red-600'}`}>
                      {Math.round(s.overall_mastery_avg * 100)}%
                    </span>
                  </td>
                  <td className="px-6 py-3 text-slate-600">{s.current_streak_days}d</td>
                  <td className="px-6 py-3 text-slate-400 text-xs">
                    {s.last_active ? new Date(s.last_active).toLocaleDateString() : 'Never'}
                  </td>
                  <td className="px-6 py-3 text-right">
                    <Link
                      to={`/teacher/students/${s.student_id}`}
                      className="inline-flex items-center gap-1 text-navy-600 hover:text-navy-800 text-sm font-medium"
                    >
                      View <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
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
