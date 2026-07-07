import { useState } from 'react'
import { useAuthApi, useAuthMutation } from '@/hooks/useApi'
import { getTeacherCourses, createCourse, publishCourse, deleteCourse } from '@/services/teacher'
import { localDb } from '@/services/localDb'
import { BookOpen, Loader2, Plus, CheckCircle, XCircle, Trash2, ChevronDown, ChevronRight } from 'lucide-react'

export function TeacherCoursesPage() {
  const { data: assignments, loading, refetch } = useAuthApi(() => getTeacherCourses(), [])
  const [courses, setCourses] = useState<Record<string, any>>({})
  const [showCreate, setShowCreate] = useState(false)
  const [expanded, setExpanded] = useState<string | null>(null)
  const [courseModules, setCourseModules] = useState<Record<string, any[]>>({})
  const [loadingModules, setLoadingModules] = useState<Record<string, boolean>>({})

  const [form, setForm] = useState({ code: '', title: '', description: '', total_duration_hours: 40, default_deadline_days: 90 })

  const createMut = useAuthMutation(createCourse)

  const loadCourseDetail = async (courseId: string) => {
    if (courses[courseId]) return
    try {
      const res = await localDb.getCourse(courseId)
      setCourses(prev => ({ ...prev, [courseId]: res.data }))
    } catch { }
  }

  const loadModules = async (courseId: string) => {
    if (courseModules[courseId]) return
    setLoadingModules(prev => ({ ...prev, [courseId]: true }))
    try {
      const res = await localDb.getCourseModules(courseId)
      setCourseModules(prev => ({ ...prev, [courseId]: res.data }))
    } catch { }
    setLoadingModules(prev => ({ ...prev, [courseId]: false }))
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createMut.mutateAsync(form)
      setShowCreate(false)
      setForm({ code: '', title: '', description: '', total_duration_hours: 40, default_deadline_days: 90 })
      refetch()
    } catch { }
  }

  const handlePublish = async (courseId: string, isPublished: boolean) => {
    try {
      await publishCourse(courseId, !isPublished)
      setCourses(prev => prev[courseId] ? { ...prev, [courseId]: { ...prev[courseId], is_published: !isPublished } } : prev)
    } catch { }
  }

  const handleDelete = async (courseId: string) => {
    if (!confirm('Delete this course? This action cannot be undone.')) return
    try {
      await deleteCourse(courseId)
      refetch()
      setCourses(prev => { const { [courseId]: _, ...rest } = prev; return rest })
    } catch { }
  }

  const toggleExpand = async (courseId: string) => {
    if (expanded === courseId) { setExpanded(null); return }
    setExpanded(courseId)
    await Promise.all([loadCourseDetail(courseId), loadModules(courseId)])
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-6 h-6 animate-spin text-navy-600" /></div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">My Courses</h1>
          <p className="text-sm text-slate-500 mt-1">{assignments?.length || 0} assigned course(s)</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="inline-flex items-center gap-2 px-4 py-2 bg-navy-800 text-white rounded-lg hover:bg-navy-700 transition-all text-sm font-medium shadow-sm"><Plus className="w-4 h-4" /> Create Course</button>
      </div>

      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-lg w-full p-6">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">Create New Course</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Course Code</label>
                <input type="text" value={form.code} onChange={e => setForm(p => ({ ...p, code: e.target.value }))} className="input-field" placeholder="e.g. MATH-101" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Title</label>
                <input type="text" value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))} className="input-field" placeholder="e.g. Algebra I" required />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} className="input-field" rows={3} placeholder="Course description..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Duration (hours)</label>
                  <input type="number" value={form.total_duration_hours} onChange={e => setForm(p => ({ ...p, total_duration_hours: +e.target.value }))} className="input-field" min={1} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Deadline (days)</label>
                  <input type="number" value={form.default_deadline_days} onChange={e => setForm(p => ({ ...p, default_deadline_days: +e.target.value }))} className="input-field" min={1} required />
                </div>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" disabled={createMut.isPending} className="btn-primary flex-1 disabled:opacity-50">{createMut.isPending ? 'Creating...' : 'Create Course'}</button>
                <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary flex-1">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {assignments && assignments.length > 0 ? assignments.map((c) => (
          <div key={c.course_id} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <button onClick={() => toggleExpand(c.course_id)} className="w-full flex items-center gap-4 p-5 hover:bg-slate-50 transition-all text-left">
              <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center flex-shrink-0"><BookOpen className="w-5 h-5 text-navy-600" /></div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="font-semibold text-slate-900 truncate">{c.title}</h3>
                  {courses[c.course_id]?.is_published && <span className="px-2 py-0.5 text-[10px] font-medium bg-emerald-50 text-emerald-700 rounded-full">Published</span>}
                  {courses[c.course_id] && !courses[c.course_id].is_published && <span className="px-2 py-0.5 text-[10px] font-medium bg-slate-100 text-slate-500 rounded-full">Draft</span>}
                </div>
                <p className="text-xs text-slate-400">{c.code}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                {courses[c.course_id] && (
                  <button onClick={e => { e.stopPropagation(); handlePublish(c.course_id, courses[c.course_id].is_published) }} className={`p-2 rounded-lg text-xs font-medium transition-all ${courses[c.course_id].is_published ? 'text-amber-600 hover:bg-amber-50' : 'text-emerald-600 hover:bg-emerald-50'}`}>
                    {courses[c.course_id].is_published ? <XCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
                  </button>
                )}
                {expanded === c.course_id ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
              </div>
            </button>

            {expanded === c.course_id && (
              <div className="border-t border-slate-100 p-5 bg-slate-50/50">
                {courses[c.course_id] && (
                  <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                    <div><span className="text-slate-400">Duration:</span> <span className="font-medium">{courses[c.course_id].total_duration_hours}h</span></div>
                    <div><span className="text-slate-400">Deadline:</span> <span className="font-medium">{courses[c.course_id].default_deadline_days} days</span></div>
                    <div><span className="text-slate-400">Status:</span> <span className={`font-medium ${courses[c.course_id].is_published ? 'text-emerald-600' : 'text-amber-600'}`}>{courses[c.course_id].is_published ? 'Published' : 'Draft'}</span></div>
                  </div>
                )}
                <h4 className="text-sm font-medium text-slate-700 mb-3">Modules & Lessons</h4>
                {loadingModules[c.course_id] ? (
                  <Loader2 className="w-4 h-4 animate-spin text-navy-600" />
                ) : courseModules[c.course_id] ? (
                  <div className="space-y-2">
                    {courseModules[c.course_id].length === 0 ? (
                      <p className="text-xs text-slate-400">No modules yet.</p>
                    ) : (
                      courseModules[c.course_id].map((mod: any) => (
                        <div key={mod.module_id} className="bg-white rounded-lg border border-slate-200 p-3">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-slate-800">{mod.order_index}. {mod.title}</span>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                ) : null}
                <div className="mt-4 flex gap-2">
                  <button className="px-3 py-1.5 text-xs font-medium text-navy-700 bg-navy-50 border border-navy-200 rounded-lg hover:bg-navy-100 transition-all">+ Add Module</button>
                  {courses[c.course_id] && !courses[c.course_id].is_published && (
                    <button onClick={() => handlePublish(c.course_id, false)} className="px-3 py-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-all">Publish Course</button>
                  )}
                  <button onClick={() => handleDelete(c.course_id)} className="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-all ml-auto"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </div>
            )}
          </div>
        )) : (
          <div className="text-center py-16">
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-400 mb-4">No courses yet.</p>
            <button onClick={() => setShowCreate(true)} className="btn-primary inline-flex items-center gap-2"><Plus className="w-4 h-4" /> Create Your First Course</button>
          </div>
        )}
      </div>
    </div>
  )
}
