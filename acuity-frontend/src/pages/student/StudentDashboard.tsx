import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { getMasteryOverview } from '@/services/mastery'
import { getCurriculumTree } from '@/services/progress'
import { getAccessToken } from '@/services/api'
import { authStore } from '@/store/authStore'
import { getTrackLabel, getScoreColor, formatScore, cn } from '@/lib/utils'
import { BookOpen, TrendingUp, Clock, Target, ArrowRight, CheckCircle2, Lock, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export function StudentDashboard() {
  const navigate = useNavigate()
  const user = authStore.user

  const { data: enrollments, loading: loadingEnrollments } = useAuthApi(
    () => getEnrollments('active'),
    [],
  )
  const { data: masteryRecords, loading: loadingMastery } = useAuthApi(
    () => getMasteryOverview(),
    [],
  )

  const enrollment = enrollments?.[0]
  const courseId = enrollment?.course_id

  const { data: curriculum, loading: loadingCurriculum } = useAuthApi(
    () => courseId ? getCurriculumTree(courseId) : Promise.reject(),
    [courseId],
  )

  const loading = loadingEnrollments || loadingMastery || loadingCurriculum

  const overallMastery = masteryRecords && masteryRecords.length > 0
    ? Math.round(masteryRecords.reduce((s, r) => s + r.mastery_level, 0) / masteryRecords.length * 100)
    : 0

  const trackInfo = getTrackLabel(overallMastery)

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

  return (
    <div className="space-y-6">
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">
                Hi, {user?.full_name?.split(' ')[0] || 'Student'}!
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                {enrollment?.course_title || 'No active course'}
              </p>
            </div>
            <span className={cn('badge', trackInfo.color)}>
              {trackInfo.label}
            </span>
          </div>

          <p className="text-xs text-slate-400 mt-3">
            Overall Mastery: {overallMastery}/100 · {trackInfo.desc}
          </p>
        </div>

        <div className="space-y-3">
          {[
            { icon: BookOpen, label: 'Current Lesson', value: lessons.find(l => l.status === 'active')?.title || 'No active lesson', color: 'text-blue-600 bg-blue-50' },
            { icon: TrendingUp, label: 'Overall Mastery', value: `${overallMastery}/100`, color: 'text-emerald-600 bg-emerald-50' },
            { icon: Clock, label: 'Course', value: enrollment?.course_title || 'N/A', color: 'text-amber-600 bg-amber-50' },
          ].map((stat) => {
            const Icon = stat.icon
            return (
              <div key={stat.label} className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm flex items-center gap-3">
                <div className={`w-9 h-9 rounded-lg ${stat.color} flex items-center justify-center`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">{stat.label}</div>
                  <div className="text-sm font-semibold text-slate-800">{stat.value}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {lessons.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-slate-900">Learning Path</h2>
            <button onClick={() => navigate('/student/learning')} className="text-sm text-navy-700 hover:text-navy-900 font-medium flex items-center gap-1">
              View All <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
            {lessons.slice(0, 6).map((lesson) => (
              <div
                key={lesson.id}
                className={cn(
                  'rounded-xl p-4 border text-center transition-all',
                  lesson.status === 'completed' && 'bg-emerald-50 border-emerald-200',
                  lesson.status === 'active' && 'bg-navy-50 border-navy-300 ring-2 ring-navy-800/10',
                  lesson.status === 'locked' && 'bg-slate-50 border-slate-200 opacity-60',
                )}
              >
                <div className="flex justify-center mb-2">
                  {lesson.status === 'completed' && <CheckCircle2 className="w-6 h-6 text-emerald-500" />}
                  {lesson.status === 'active' && <Target className="w-6 h-6 text-navy-700" />}
                  {lesson.status === 'locked' && <Lock className="w-6 h-6 text-slate-300" />}
                </div>
                <div className={cn(
                  'text-xs font-medium',
                  lesson.status === 'locked' ? 'text-slate-400' : 'text-slate-700'
                )}>
                  {lesson.title}
                </div>
                {lesson.status === 'active' && (
                  <button
                    onClick={() => navigate('/student/ai-tutor')}
                    className="mt-2 text-[10px] bg-navy-800 text-white px-2 py-1 rounded-md hover:bg-navy-700"
                  >
                    Continue
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { title: 'AI Tutor', desc: 'Chat with your AI tutor', path: '/student/ai-tutor', color: 'bg-navy-50 border-navy-200 hover:bg-navy-100' },
          { title: 'Assessment', desc: 'Take a quiz', path: '/student/assessment', color: 'bg-emerald-50 border-emerald-200 hover:bg-emerald-100' },
          { title: 'My Progress', desc: 'View detailed analytics', path: '/student/progress', color: 'bg-amber-50 border-amber-200 hover:bg-amber-100' },
        ].map((action) => (
          <button
            key={action.title}
            onClick={() => navigate(action.path)}
            className={`rounded-xl border p-4 text-left transition-all ${action.color}`}
          >
            <div className="text-sm font-semibold text-slate-900">{action.title}</div>
            <div className="text-xs text-slate-500 mt-0.5">{action.desc}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
