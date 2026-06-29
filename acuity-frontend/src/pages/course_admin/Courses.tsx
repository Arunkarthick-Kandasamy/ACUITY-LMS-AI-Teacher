import { useState, useMemo } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { listCourses, deleteCourse } from '@/services/courseAdmin'
import { Link, useNavigate } from 'react-router-dom'
import {
  Plus, Search, Bot, Loader2, CheckCircle2, XCircle, AlertCircle, Clock,
  Brain, Trash2, ExternalLink, BookOpen, Users, BarChart3, FileText,
  Upload, Sparkles, ShieldCheck, Play, Filter, ArrowUpDown,
} from 'lucide-react'
import type { CourseBrief } from '@/services/types'
import { STAGE_ORDER } from '@/services/types'

const statusCfg: Record<string, { label: string; color: string; bg: string; icon: typeof Bot }> = {
  draft: { label: 'Draft', color: 'text-slate-600', bg: 'bg-slate-50', icon: Clock },
  training: { label: 'Training', color: 'text-blue-600', bg: 'bg-blue-50', icon: Brain },
  review: { label: 'Review', color: 'text-amber-600', bg: 'bg-amber-50', icon: AlertCircle },
  ready: { label: 'Ready', color: 'text-emerald-600', bg: 'bg-emerald-50', icon: CheckCircle2 },
  deployed: { label: 'Published', color: 'text-purple-600', bg: 'bg-purple-50', icon: Bot },
  archived: { label: 'Archived', color: 'text-slate-400', bg: 'bg-slate-50', icon: Clock },
}

const FILTERS = ['all', 'draft', 'training', 'review', 'ready', 'deployed', 'archived'] as const

export function Courses() {
  const navigate = useNavigate()
  const { data: courses, loading, refetch } = useAuthApi(() => listCourses(), [])
  const [deleting, setDeleting] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<string>('all')

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this course? This action cannot be undone.')) return
    setDeleting(id)
    try { await deleteCourse(id); refetch() }
    catch { alert('Failed to delete') }
    finally { setDeleting(null) }
  }

  const filtered = useMemo(() => {
    if (!courses) return []
    return courses.filter(c => {
      if (filter !== 'all' && c.status !== filter) return false
      if (search && !c.name.toLowerCase().includes(search.toLowerCase()) && !c.description?.toLowerCase().includes(search.toLowerCase())) return false
      return true
    })
  }, [courses, filter, search])

  const stats = useMemo(() => {
    if (!courses) return { total: 0, draft: 0, training: 0, review: 0, ready: 0, deployed: 0, archived: 0, failed: 0 }
    return {
      total: courses.length,
      draft: courses.filter(c => c.status === 'draft').length,
      training: courses.filter(c => c.status === 'training').length,
      review: courses.filter(c => c.status === 'review').length,
      ready: courses.filter(c => c.status === 'ready').length,
      deployed: courses.filter(c => c.status === 'deployed').length,
      archived: courses.filter(c => c.status === 'archived').length,
      failed: courses.filter(c => c.stages?.some(s => s.status === 'failed')).length,
    }
  }, [courses])

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-5 h-5 animate-spin text-blue-600" /></div>
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-sm font-semibold text-slate-900">Courses</h1>
          <p className="text-[10px] text-slate-400">{stats.total} total</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3 h-3 absolute left-2 top-1/2 -translate-y-1/2 text-slate-400" />
            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search courses..."
              className="w-44 pl-6 pr-2 py-1 border border-slate-200 rounded text-[10px] focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500" />
          </div>
          <Link to="/course-admin/create" className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700">
            <Plus className="w-3.5 h-3.5" />Create Course
          </Link>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-8 gap-2">
        {[
          { label: 'Total', value: stats.total, color: 'text-slate-600 bg-slate-50', filter: 'all' },
          { label: 'Published', value: stats.deployed, color: 'text-purple-600 bg-purple-50', filter: 'deployed' },
          { label: 'Training', value: stats.training, color: 'text-blue-600 bg-blue-50', filter: 'training' },
          { label: 'Draft', value: stats.draft, color: 'text-slate-600 bg-slate-50', filter: 'draft' },
          { label: 'Review', value: stats.review, color: 'text-amber-600 bg-amber-50', filter: 'review' },
          { label: 'Ready', value: stats.ready, color: 'text-emerald-600 bg-emerald-50', filter: 'ready' },
          { label: 'Archived', value: stats.archived, color: 'text-slate-400 bg-slate-50', filter: 'archived' },
          { label: 'Failed', value: stats.failed, color: 'text-red-600 bg-red-50', filter: 'all' },
        ].map(s => (
          <button key={s.label} onClick={() => setFilter(s.filter)}
            className={`p-2 rounded-lg border ${filter === s.filter ? 'border-blue-300 ring-1 ring-blue-200' : 'border-slate-200'} bg-white shadow-sm text-left hover:border-slate-300`}>
            <div className={`text-[9px] font-medium uppercase tracking-wide ${s.color.split(' ')[0]}`}>{s.label}</div>
            <div className="text-base font-bold text-slate-900 mt-0.5">{s.value}</div>
          </button>
        ))}
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-1 border-b border-slate-200">
        {FILTERS.map(f => (
          <button key={f} onClick={() => setFilter(f)}
            className={`px-3 py-1.5 text-[10px] font-medium border-b-2 transition-colors ${filter === f ? 'border-blue-500 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>
            {f === 'all' ? 'All Courses' : f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Course table */}
      {filtered.length > 0 ? (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="text-left px-3 py-2 font-medium text-slate-500 text-[10px] uppercase tracking-wide">Course</th>
                <th className="text-left px-3 py-2 font-medium text-slate-500 text-[10px] uppercase tracking-wide">Status</th>
                <th className="text-left px-3 py-2 font-medium text-slate-500 text-[10px] uppercase tracking-wide">Progress</th>
                <th className="text-left px-3 py-2 font-medium text-slate-500 text-[10px] uppercase tracking-wide">Pipeline</th>
                <th className="text-left px-3 py-2 font-medium text-slate-500 text-[10px] uppercase tracking-wide">Created</th>
                <th className="text-right px-3 py-2 font-medium text-slate-500 text-[10px] uppercase tracking-wide">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map(c => {
                const cfg = statusCfg[c.status] || statusCfg.draft
                const Icon = cfg.icon
                const sp = c.stage_progress
                const pct = sp ? sp.pct : 0
                return (
                  <tr key={c.id} className="hover:bg-slate-50/50 cursor-pointer" onClick={() => navigate(`/course-admin/courses/${c.id}`)}>
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-md bg-indigo-50 flex items-center justify-center shrink-0">
                          <Bot className="w-3.5 h-3.5 text-indigo-600" />
                        </div>
                        <div className="min-w-0">
                          <div className="text-xs font-medium text-slate-800 truncate max-w-[200px]">{c.name}</div>
                          {c.description && <div className="text-[10px] text-slate-400 truncate max-w-[200px]">{c.description}</div>}
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-2.5">
                      <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${cfg.bg} ${cfg.color}`}>
                        <Icon className="w-3 h-3" />{cfg.label}
                      </span>
                    </td>
                    <td className="px-3 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-100 rounded-full h-1.5">
                          <div className={`h-1.5 rounded-full ${pct === 100 ? 'bg-emerald-400' : 'bg-blue-400'}`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-[10px] text-slate-400 w-8 text-right">{sp?.completed || 0}/{sp?.total || 10}</span>
                      </div>
                    </td>
                    <td className="px-3 py-2.5">
                      {c.stage_progress && (
                        <div className="flex items-center gap-0.5">
                          {STAGE_ORDER.map(key => {
                            const map: Record<string, string> = {
                              completed: 'bg-emerald-400', in_progress: 'bg-blue-400 animate-pulse',
                              failed: 'bg-red-400', pending: 'bg-slate-200',
                            }
                            return <div key={key} className={`w-1.5 h-3 rounded-sm ${map.pending}`} />
                          })}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-2.5 text-[10px] text-slate-400">{new Date(c.created_at).toLocaleDateString()}</td>
                    <td className="px-3 py-2.5 text-right">
                      <div className="flex items-center justify-end gap-1" onClick={e => e.stopPropagation()}>
                        <Link to={`/course-admin/courses/${c.id}`} className="p-1 hover:bg-slate-100 rounded" title="View">
                          <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
                        </Link>
                        {c.status !== 'deployed' && (
                          <button onClick={() => handleDelete(c.id)} disabled={deleting === c.id}
                            className="p-1 hover:bg-red-50 rounded" title="Delete">
                            {deleting === c.id ? <Loader2 className="w-3.5 h-3.5 animate-spin text-red-400" /> : <Trash2 className="w-3.5 h-3.5 text-red-400" />}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-10 text-center">
          <Bot className="w-10 h-10 text-slate-200 mx-auto mb-3" />
          <p className="text-xs font-medium text-slate-700 mb-1">No courses found</p>
          <p className="text-[10px] text-slate-400 mb-4">
            {search || filter !== 'all' ? 'Try adjusting your search or filters.' : 'Create your first course to get started.'}
          </p>
          {!search && filter === 'all' && (
            <Link to="/course-admin/create" className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700">
              <Plus className="w-3.5 h-3.5" />Create Course
            </Link>
          )}
        </div>
      )}
    </div>
  )
}
