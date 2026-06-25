import { useState } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import {
  getAssessments, createAssessment, deleteAssessment,
  createQuestion, deleteQuestion,
} from '@/services/assessments'
import { getCourses } from '@/services/curriculum'
import {
  Plus, Trash2, Loader2, FileText, CheckCircle2, XCircle,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const assessmentTypes = [
  { value: 'quiz', label: 'Quiz' },
  { value: 'practice_test', label: 'Practice Test' },
  { value: 'chapter_test', label: 'Chapter Test' },
  { value: 'diagnostic', label: 'Diagnostic' },
  { value: 'final', label: 'Final Assessment' },
]

const questionTypes = [
  { value: 'mcq', label: 'Multiple Choice' },
  { value: 'multi_select', label: 'Multiple Select' },
  { value: 'true_false', label: 'True/False' },
  { value: 'short_answer', label: 'Short Answer' },
  { value: 'numeric', label: 'Numeric' },
  { value: 'fill_blank', label: 'Fill in Blank' },
]

export function AssessmentManagementPage() {
  const { data: assessments, loading, refetch } = useAuthApi(() => getAssessments(), [])
  const { data: courses } = useAuthApi(() => getCourses({}), [])

  const [showCreate, setShowCreate] = useState(false)
  const [selectedAssessment, setSelectedAssessment] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  const [form, setForm] = useState({
    title: '',
    description: '',
    course_id: '',
    assessment_type: 'quiz',
    passing_score: 0.7,
    time_limit: 30,
    max_attempts: 1,
    is_published: false,
  })

  const handleCreate = async () => {
    setCreating(true)
    try {
      await createAssessment(form)
      setShowCreate(false)
      setForm({ title: '', description: '', course_id: '', assessment_type: 'quiz', passing_score: 0.7, time_limit: 30, max_attempts: 1, is_published: false })
      refetch()
    } catch {}
    setCreating(false)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this assessment?')) return
    try {
      await deleteAssessment(id)
      refetch()
    } catch {}
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Assessment Management</h1>
          <p className="text-sm text-slate-500 mt-1">Create and manage assessments</p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> New Assessment
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="font-semibold text-slate-900 mb-4">Create Assessment</h2>
          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Title</label>
              <input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} className="input-field" placeholder="Assessment title" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Course</label>
              <select value={form.course_id} onChange={e => setForm({ ...form, course_id: e.target.value })} className="input-field">
                <option value="">Select course</option>
                {(courses || []).map((c: any) => (
                  <option key={c.course_id} value={c.course_id}>{c.title}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Type</label>
              <select value={form.assessment_type} onChange={e => setForm({ ...form, assessment_type: e.target.value })} className="input-field">
                {assessmentTypes.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Passing Score (%)</label>
              <input type="number" min={0} max={100} value={Math.round(form.passing_score * 100)} onChange={e => setForm({ ...form, passing_score: Math.max(0, Math.min(100, Number(e.target.value))) / 100 })} className="input-field" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Time Limit (minutes)</label>
              <input type="number" min={0} value={form.time_limit || ''} onChange={e => setForm({ ...form, time_limit: e.target.value ? Number(e.target.value) : undefined })} className="input-field" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Max Attempts</label>
              <input type="number" min={1} value={form.max_attempts} onChange={e => setForm({ ...form, max_attempts: Number(e.target.value) })} className="input-field" />
            </div>
          </div>
          <div className="flex items-center gap-2 mb-4">
            <input type="checkbox" id="is_published" checked={form.is_published} onChange={e => setForm({ ...form, is_published: e.target.checked })} className="rounded" />
            <label htmlFor="is_published" className="text-sm text-slate-600">Published</label>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleCreate} disabled={creating || !form.title || !form.course_id} className="btn-primary">
              {creating ? 'Creating...' : 'Create'}
            </button>
            <button onClick={() => setShowCreate(false)} className="btn-secondary">Cancel</button>
          </div>
        </div>
      )}

      {(!assessments || assessments.length === 0) ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No assessments created yet.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Title</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Type</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Questions</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Pass</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-slate-500 uppercase">Status</th>
                  <th className="text-right px-6 py-3 text-xs font-medium text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {assessments.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3">
                      <div className="font-medium text-slate-800">{a.title}</div>
                      {a.description && <div className="text-xs text-slate-400 truncate max-w-[200px]">{a.description}</div>}
                    </td>
                    <td className="px-6 py-3">
                      <span className="badge bg-slate-100 text-slate-700 capitalize">{a.assessment_type.replace('_', ' ')}</span>
                    </td>
                    <td className="px-6 py-3 text-slate-500">{a.question_count}</td>
                    <td className="px-6 py-3 text-slate-500">{Math.round(a.passing_score * 100)}%</td>
                    <td className="px-6 py-3">
                      {a.is_published
                        ? <span className="flex items-center gap-1 text-emerald-600 text-xs"><CheckCircle2 className="w-3.5 h-3.5" /> Published</span>
                        : <span className="flex items-center gap-1 text-slate-400 text-xs"><XCircle className="w-3.5 h-3.5" /> Draft</span>
                      }
                    </td>
                    <td className="px-6 py-3 text-right">
                      <button
                        onClick={() => handleDelete(a.id)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-all"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
