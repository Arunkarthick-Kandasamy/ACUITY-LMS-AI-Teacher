import { useAuthApi } from '@/hooks/useApi'
import { getTeacherCourses } from '@/services/teacher'
import { BookOpen, Loader2 } from 'lucide-react'

export function TeacherCoursesPage() {
  const { data: courses, loading } = useAuthApi(() => getTeacherCourses(), [])

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
        <h1 className="text-xl font-semibold text-slate-900">My Courses</h1>
        <p className="text-sm text-slate-500 mt-1">{courses?.length || 0} assigned course(s)</p>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {courses && courses.length > 0 ? courses.map((c) => (
          <div key={c.course_id} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-navy-600" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900">{c.title}</h3>
                <p className="text-xs text-slate-400">{c.code}</p>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>Role: {c.role}</span>
              {c.assigned_at && (
                <span>Since {new Date(c.assigned_at).toLocaleDateString()}</span>
              )}
            </div>
          </div>
        )) : (
          <div className="col-span-full text-center py-12">
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-400">No courses assigned yet.</p>
          </div>
        )}
      </div>
    </div>
  )
}
