import { useState } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { getCurriculumTree } from '@/services/progress'
import { CheckCircle2, Lock, Play, Star, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'

export function LearningPathPage() {
  const navigate = useNavigate()

  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  const { data: curriculum, loading } = useAuthApi(
    () => courseId ? getCurriculumTree(courseId) : Promise.reject(),
    [courseId],
  )

  const lessons = curriculum?.modules?.flatMap(m =>
    m.lessons?.map(l => ({
      id: l.lesson_id,
      title: l.title,
      status: l.status || 'locked',
      order: l.order_index,
      duration: l.estimated_duration_minutes,
    })) || []
  )?.sort((a, b) => a.order - b.order) || []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  if (lessons.length === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-slate-900">Learning Path</h1>
          <p className="text-sm text-slate-500 mt-1">Progress through your personalized curriculum</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <p className="text-slate-500">No lessons available yet. Enroll in a course to get started.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">{curriculum?.course_title || 'Learning Path'}</h1>
        <p className="text-sm text-slate-500 mt-1">Progress through your personalized curriculum</p>
      </div>

      <div className="space-y-3">
        {lessons.map((lesson) => (
          <div
            key={lesson.id}
            className={cn(
              'rounded-xl border p-5 transition-all',
              lesson.status === 'completed' && 'bg-white border-emerald-200 shadow-sm',
              lesson.status === 'active' && 'bg-white border-navy-300 shadow-md ring-1 ring-navy-800/10',
              lesson.status === 'locked' && 'bg-slate-50 border-slate-200',
            )}
          >
            <div className="flex items-center gap-4">
              <div className={cn(
                'w-10 h-10 rounded-lg flex items-center justify-center',
                lesson.status === 'completed' && 'bg-emerald-100',
                lesson.status === 'active' && 'bg-navy-100',
                lesson.status === 'locked' && 'bg-slate-100',
              )}>
                {lesson.status === 'completed' && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
                {lesson.status === 'active' && <Play className="w-5 h-5 text-navy-700 ml-0.5" />}
                {lesson.status === 'locked' && <Lock className="w-4 h-4 text-slate-400" />}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className={cn(
                    'font-medium',
                    lesson.status === 'locked' ? 'text-slate-400' : 'text-slate-900'
                  )}>
                    {lesson.title}
                  </h3>
                  {lesson.status === 'active' && (
                    <span className="px-2 py-0.5 rounded-full bg-navy-100 text-[10px] font-medium text-navy-700">
                      In Progress
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3 mt-1">
                  <span className="flex items-center gap-1 text-xs text-slate-400">
                    <Star className="w-3 h-3" />
                    {lesson.duration || 0} min
                  </span>
                </div>
              </div>

              {lesson.status === 'active' && (
                <button
                  onClick={() => navigate('/student/ai-tutor')}
                  className="px-4 py-2 bg-navy-800 text-white text-sm rounded-lg hover:bg-navy-700 transition-all shadow-sm"
                >
                  Continue
                </button>
              )}
              {lesson.status === 'completed' && (
                <button className="px-4 py-2 text-sm text-slate-500 rounded-lg hover:bg-slate-100 transition-all">
                  Review
                </button>
              )}
              {lesson.status === 'locked' && (
                <span className="text-xs text-slate-400">
                  Complete previous to unlock
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
