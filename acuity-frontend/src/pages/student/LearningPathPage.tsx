import { useState } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { getCurriculumTree } from '@/services/progress'
import { CheckCircle2, Lock, Play, Star, Loader2, Trophy, Sparkles, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { useGamification, xpForAction } from '@/hooks/useGamification'
import { Confetti } from '@/components/ui/Confetti'

const moduleColors = [
  { bg: 'from-blue-400 to-blue-600', light: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200', icon: '📐' },
  { bg: 'from-green-400 to-green-600', light: 'bg-green-50', text: 'text-green-600', border: 'border-green-200', icon: '🔬' },
  { bg: 'from-purple-400 to-purple-600', light: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-200', icon: '📖' },
  { bg: 'from-orange-400 to-orange-600', light: 'bg-orange-50', text: 'text-orange-600', border: 'border-orange-200', icon: '🌍' },
]

export function LearningPathPage() {
  const navigate = useNavigate()
  const { addXp, xp, level, xpProgress } = useGamification()
  const [confetti, setConfetti] = useState(false)

  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  const { data: curriculum, loading } = useAuthApi(
    () => courseId ? getCurriculumTree(courseId) : Promise.reject(),
    [courseId],
  )

  const modules = curriculum?.modules || []
  const allLessons = modules.flatMap((m, mi) =>
    (m.lessons || []).map(l => ({
      ...l,
      moduleTitle: m.title,
      moduleIndex: mi,
      moduleColor: moduleColors[mi % moduleColors.length],
    }))
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500 mx-auto mb-2" />
          <p className="text-sm text-slate-500">Loading your learning path...</p>
        </div>
      </div>
    )
  }

  if (allLessons.length === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-slate-900">My Learning Path 🗺️</h1>
          <p className="text-sm text-slate-500 mt-1">Your personalized adventure through knowledge!</p>
        </div>
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-12 text-center">
          <Trophy className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 font-medium">No lessons available yet. Enroll in a course to start your adventure!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <Confetti active={confetti} />

      {/* XP Bar */}
      <div className="flex items-center gap-3 mb-5 p-3 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shrink-0">
          <Zap className="w-4 h-4 text-white" />
        </div>
        <div className="flex-1">
          <div className="flex justify-between text-xs mb-0.5">
            <span className="font-semibold text-amber-800">Level {level}</span>
            <span className="text-amber-600">{xp % 200}/200 XP</span>
          </div>
          <div className="h-2 rounded-full bg-amber-200 overflow-hidden">
            <div className="h-full rounded-full bg-gradient-to-r from-amber-400 to-orange-500 transition-all duration-500" style={{ width: `${xpProgress}%` }} />
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          {curriculum?.course_title || 'Learning Path'} 🗺️
        </h1>
        <p className="text-sm text-slate-500 mt-1">Progress through your personalized curriculum adventure!</p>
      </div>

      {/* Module Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
        {modules.map((m, i) => {
          const c = moduleColors[i % moduleColors.length]
          const completed = m.lessons?.filter(l => l.status === 'completed').length || 0
          const total = m.lesson_count || m.lessons?.length || 0
          return (
            <div key={m.module_id} className={cn('rounded-xl border p-3 text-center transition-all hover:shadow-md', c.light, c.border)}>
              <div className="text-2xl mb-1">{c.icon}</div>
              <div className="text-xs font-bold text-slate-800 truncate">{m.title}</div>
              <div className="text-[10px] text-slate-500 mt-0.5">{completed}/{total} done</div>
              <div className="h-1.5 rounded-full bg-white/60 mt-1.5 overflow-hidden">
                <div className={cn('h-full rounded-full bg-gradient-to-r', c.bg)} style={{ width: `${total > 0 ? (completed / total) * 100 : 0}%` }} />
              </div>
            </div>
          )
        })}
      </div>

      <div className="space-y-3">
        {allLessons.map((lesson, i) => {
          const isFirstUnlocked = !allLessons.slice(0, i).some(l => l.status === 'locked') && (i === 0 || allLessons[i - 1].status === 'completed')
          const status = lesson.status || (isFirstUnlocked ? 'active' : 'locked')
          const c = lesson.moduleColor
          const isNewlyCompleted = status === 'completed'

          return (
            <div
              key={lesson.lesson_id}
              className={cn(
                'rounded-2xl border-2 p-5 transition-all',
                status === 'completed' && 'bg-white border-emerald-300 shadow-sm',
                status === 'active' && 'bg-white border-blue-300 shadow-md ring-2 ring-blue-500/10',
                status === 'locked' && 'bg-slate-50 border-slate-200 opacity-70',
              )}
            >
              <div className="flex items-center gap-4">
                <div className={cn(
                  'w-12 h-12 rounded-2xl flex items-center justify-center text-lg shadow-sm',
                  status === 'completed' && 'bg-gradient-to-br from-emerald-400 to-green-500',
                  status === 'active' && 'bg-gradient-to-br from-blue-400 to-blue-600',
                  status === 'locked' && 'bg-slate-200',
                )}>
                  {status === 'completed' && <CheckCircle2 className="w-6 h-6 text-white" />}
                  {status === 'active' && <Play className="w-6 h-6 text-white ml-0.5" />}
                  {status === 'locked' && <Lock className="w-5 h-5 text-slate-400" />}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className={cn('font-bold', status === 'locked' ? 'text-slate-400' : 'text-slate-900')}>
                      {lesson.title}
                    </h3>
                    {status === 'active' && (
                      <span className="px-2.5 py-0.5 rounded-full bg-blue-100 text-[10px] font-bold text-blue-700">
                        In Progress
                      </span>
                    )}
                    {status === 'completed' && (
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-100 text-[10px] font-bold text-emerald-700">
                        Done! ✓
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="text-xs text-slate-500">{lesson.moduleTitle}</span>
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <Star className="w-3 h-3" />
                      {lesson.estimated_duration_minutes || '?'} min
                    </span>
                  </div>
                </div>

                {status === 'active' && (
                  <button
                    onClick={() => navigate('/student/ai-tutor')}
                    className="px-5 py-2.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-bold rounded-xl hover:shadow-lg hover:-translate-y-0.5 transition-all active:scale-95"
                  >
                    Start Learning 🚀
                  </button>
                )}
                {status === 'completed' && (
                  <button className="px-4 py-2 text-sm font-semibold text-slate-600 rounded-xl bg-slate-100 hover:bg-slate-200 transition-all active:scale-95">
                    Review
                  </button>
                )}
                {status === 'locked' && (
                  <div className="flex items-center gap-1.5 text-xs text-slate-400">
                    <Lock className="w-3 h-3" /> Locked
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Progress Stats */}
      <div className="mt-8 p-5 rounded-2xl bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200">
        <h3 className="font-bold text-slate-800 mb-3 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-blue-500" /> Your Learning Stats
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-black text-blue-600">{allLessons.filter(l => l.status === 'completed').length}</div>
            <div className="text-xs text-slate-500 font-medium">Lessons Done</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-black text-green-600">{Math.round((allLessons.filter(l => l.status === 'completed').length / Math.max(1, allLessons.length)) * 100)}%</div>
            <div className="text-xs text-slate-500 font-medium">Progress</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-black text-purple-600">{level}</div>
            <div className="text-xs text-slate-500 font-medium">Your Level</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-black text-amber-600">{xp}</div>
            <div className="text-xs text-slate-500 font-medium">Total XP</div>
          </div>
        </div>
      </div>
    </div>
  )
}
