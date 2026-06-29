import { useState, useEffect } from 'react'
import { getAdminUsers } from '@/services/admin'
import { mockUsers } from './admin-mock-data'
import { cn } from '@/lib/utils'
import { Search, Filter, Loader2, CheckCircle2, XCircle } from 'lucide-react'

interface Student {
  user_id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
  profile?: {
    grade_level: string
    avg_session_duration_minutes: number
    current_streak_days: number
  }
}

export function StudentsPage() {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')

  useEffect(() => {
    getAdminUsers({ per_page: 50 })
      .then(res => setStudents(res.data.filter(u => u.role === 'student')))
      .catch(() => setStudents(mockUsers.filter(u => u.role === 'student') as Student[]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = students.filter(s =>
    s.full_name.toLowerCase().includes(search.toLowerCase()) ||
    s.email.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Students</h1>
          <p className="text-sm text-gray-500 mt-1">Manage and monitor all students ({students.length})</p>
        </div>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search students..."
            className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
          />
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-all">
          <Filter className="w-4 h-4" /> Filters
        </button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Email</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Grade</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-400">No students found</td>
                </tr>
              ) : (
                filtered.map((s) => (
                  <tr key={s.user_id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-xs font-bold text-blue-700">
                          {s.full_name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <span className="font-medium text-gray-800">{s.full_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-gray-500">{s.email}</td>
                    <td className="px-6 py-3">
                      <span className="text-gray-600">{s.profile?.grade_level || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-3">
                      <span className={cn('inline-flex items-center gap-1 text-xs font-medium', s.is_active ? 'text-emerald-600' : 'text-red-500')}>
                        {s.is_active ? <CheckCircle2 className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
                        {s.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-gray-400 text-xs">
                      {s.created_at ? new Date(s.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
