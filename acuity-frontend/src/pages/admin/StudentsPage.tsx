import { useAuthApi } from '@/hooks/useApi'
import { getAdminUsers } from '@/services/admin'
import { cn } from '@/lib/utils'
import { Search, Filter, Loader2 } from 'lucide-react'

export function StudentsPage() {
  const { data: users, loading } = useAuthApi(() => getAdminUsers({ per_page: 50 }), [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const students = users?.filter(u => u.role === 'student') || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Students</h1>
          <p className="text-sm text-slate-500 mt-1">Manage and monitor all students ({students.length})</p>
        </div>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input type="text" placeholder="Search students..." className="input-field pl-10" />
        </div>
        <button className="btn-secondary">
          <Filter className="w-4 h-4 mr-1.5" /> Filters
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Name</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Email</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Status</th>
                <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {students.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-slate-400">No students found</td>
                </tr>
              ) : (
                students.map((s) => (
                  <tr key={s.user_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-navy-100 flex items-center justify-center text-xs font-bold text-navy-700">
                          {s.full_name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <span className="font-medium text-slate-800">{s.full_name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-3 text-slate-500">{s.email}</td>
                    <td className="px-6 py-3">
                      <span className={s.is_active ? 'text-emerald-600 font-medium' : 'text-red-500 font-medium'}>
                        {s.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-slate-400 text-xs">
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
