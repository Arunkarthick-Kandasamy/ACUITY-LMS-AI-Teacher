import { useState, useEffect } from 'react'
import {
  getAssessments, createAssessment, deleteAssessment,
} from '@/services/assessments'
import { getCourses } from '@/services/curriculum'
import { mockAssessments, mockCourses } from './admin-mock-data'
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

interface Assessment {
  id: string
  title: string
  description?: string
  course_id: string
  assessment_type: string
  passing_score: number
  time_limit?: number
  max_attempts: number
  is_published: boolean
  question_count: number
  created_at?: string
}

interface Course {
  course_id: string
  title: string
}

export function AssessmentManagementPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [creating, setCreating] = useState(false)

  const [form, setForm] = useState({
    title: '',
    description: '',
    course_id: '',
    assessment_type: 'quiz',
    passing_score: 70,
    time_limit: 30,
    max_attempts: 1,
    is_published: false,
  })

  const loadData = () => {
    Promise.all([
      getAssessments().catch(() => ({ data: mockAssessments })),
      getCourses({}).catch(() => ({ data: mockCourses })),
    ]).then(([aRes, cRes]) => {
      setAssessments(aRes.data)
      setCourses(cRes.data)
    }).catch(() => {
      setAssessments(mockAssessments as unknown as Assessment[])
      setCourses(mockCourses as unknown as Course[])
    }).finally(() => setLoading(false))
  }

  useEffect(() => { loadData() }, [])

  const handleCreate = async () => {
    setCreating(true)
    try {
      await createAssessment({
        title: form.title,
        description: form.description,
        course_id: form.course_id,
        assessment_type: form.assessment_type,
        passing_score: form.passing_score / 100,
        time_limit: form.time_limit || undefined,
        max_attempts: form.max_attempts,
        is_published: form.is_published,
      })
      setShowCreate(false)
      setForm({ title: '', description: '', course_id: '', assessment_type: 'quiz', passing_score: 70, time_limit: 30, max_attempts: 1, is_published: false })
      loadData()
    } catch {}
    setCreating(false)
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this assessment?')) return
    try {
      await deleteAssessment(id)
      loadData()
    } catch {}
  }

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
          <h1 className="text-xl font-semibold text-gray-900">Assessment Management</h1>
          <p className="text-sm text-gray-500 mt-1">Create and manage assessments</p>
        </div>
        <button onClick={() => setShowCreate(!showCreate)} className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all text-sm font-medium shadow-sm">
          <Plus className="w-4 h-4" /> New Assessment
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Create Assessment</h2>
          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Title</label>
              <input value={form.title} onChange={e => setForm({ ...form, title: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="Assessment title" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Course</label>
              <select value={form.course_id} onChange={e => setForm({ ...form, course_id: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all bg-white">
                <option value="">Select course</option>
                {(courses || []).map((c: Course) => (
                  <option key={c.course_id} value={c.course_id}>{c.title}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Description</label>
              <input value={form.description} onChange={e => setForm({ ...form, description: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="Brief description" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Type</label>
              <select value={form.assessment_type} onChange={e => setForm({ ...form, assessment_type: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all bg-white">
                {assessmentTypes.map(t => (
                  <option key={t.value} value={t.value}>{t.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Passing Score (%)</label>
              <input type="number" min={0} max={100} value={form.passing_score}
                onChange={e => setForm({ ...form, passing_score: Math.max(0, Math.min(100, Number(e.target.value))) })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Time Limit (minutes)</label>
              <input type="number" min={0} value={form.time_limit}
                onChange={e => setForm({ ...form, time_limit: e.target.value ? Number(e.target.value) : 0 })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Max Attempts</label>
              <input type="number" min={1} value={form.max_attempts}
                onChange={e => setForm({ ...form, max_attempts: Number(e.target.value) })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all" />
            </div>
          </div>
          <div className="flex items-center gap-2 mb-4">
            <input type="checkbox" id="is_published" checked={form.is_published}
              onChange={e => setForm({ ...form, is_published: e.target.checked })}
              className="rounded border-gray-300 text-blue-500 focus:ring-blue-500" />
            <label htmlFor="is_published" className="text-sm text-gray-600">Published</label>
          </div>
          <div className="flex items-center gap-2">
            <button onClick={handleCreate} disabled={creating || !form.title || !form.course_id}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-all text-sm font-medium">
              {creating ? 'Creating...' : 'Create'}
            </button>
            <button onClick={() => setShowCreate(false)}
              className="inline-flex items-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 transition-all">
              Cancel
            </button>
          </div>
        </div>
      )}

      {assessments.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-8 text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No assessments created yet.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Title</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Questions</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Pass</th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {assessments.map((a) => (
                  <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-3">
                      <div className="font-medium text-gray-800">{a.title}</div>
                      {a.description && <div className="text-xs text-gray-400 truncate max-w-[200px]">{a.description}</div>}
                    </td>
                    <td className="px-6 py-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-700 capitalize">
                        {a.assessment_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-gray-500">{a.question_count}</td>
                    <td className="px-6 py-3 text-gray-500">{Math.round(a.passing_score * 100)}%</td>
                    <td className="px-6 py-3">
                      {a.is_published
                        ? <span className="flex items-center gap-1 text-emerald-600 text-xs font-medium"><CheckCircle2 className="w-3.5 h-3.5" /> Published</span>
                        : <span className="flex items-center gap-1 text-gray-400 text-xs"><XCircle className="w-3.5 h-3.5" /> Draft</span>
                      }
                    </td>
                    <td className="px-6 py-3 text-right">
                      <button onClick={() => handleDelete(a.id)}
                        className="p-1.5 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all">
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
