import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Flame, Clock, Play, CheckCircle2, BookOpen, Sparkles,
  ChevronRight, Search, ArrowRight, Star, Zap, Trophy,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge, Avatar, AvatarFallback } from '@/components/ui'
import {
  student, subjects, recentActivity, recommendedLessons,
  type Subject,
} from './dashboard/dashboard-data'
import { useGamification } from '@/hooks/useGamification'

const subjectStyles: Record<string, { bg: string; text: string; bar: string; light: string }> = {
  blue:    { bg: 'bg-blue-500', text: 'text-blue-600', bar: 'bg-gradient-to-r from-blue-400 to-blue-600', light: 'bg-blue-50' },
  green:   { bg: 'bg-green-500', text: 'text-green-600', bar: 'bg-gradient-to-r from-green-400 to-green-600', light: 'bg-green-50' },
  purple:  { bg: 'bg-purple-500', text: 'text-purple-600', bar: 'bg-gradient-to-r from-purple-400 to-purple-600', light: 'bg-purple-50' },
  orange:  { bg: 'bg-orange-500', text: 'text-orange-600', bar: 'bg-gradient-to-r from-orange-400 to-orange-600', light: 'bg-orange-50' },
}

const activityIcons: Record<string, typeof Play> = {
  quiz: CheckCircle2, lesson: Play, badge: Sparkles, practice: BookOpen,
}

const activityColors: Record<string, string> = {
  quiz: 'text-emerald-600 bg-emerald-100',
  lesson: 'text-blue-600 bg-blue-100',
  badge: 'text-amber-600 bg-amber-100',
  practice: 'text-purple-600 bg-purple-100',
}

function ProgressRing({ progress, color }: { progress: number; color: string }) {
  const size = 52
  const stroke = 4
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const offset = c - (progress / 100) * c
  const ref = useRef<SVGCircleElement>(null)

  useEffect(() => {
    if (ref.current) {
      const el = ref.current
      el.style.strokeDasharray = `${c}`
      el.style.strokeDashoffset = `${c}`
      requestAnimationFrame(() => { el.style.strokeDashoffset = `${offset}` })
    }
  }, [offset, c])

  return (
    <svg width={size} height={size} className="-rotate-90 shrink-0">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#f1f5f9" strokeWidth={stroke} />
      <circle
        ref={ref}
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke={color} strokeWidth={stroke} strokeLinecap="round"
        style={{ transition: 'stroke-dashoffset 0.9s cubic-bezier(0.4, 0, 0.2, 1)' }}
      />
    </svg>
  )
}

function SubjectCard({ subject }: { subject: Subject }) {
  const s = subjectStyles[subject.color]
  return (
    <div className="group relative rounded-2xl border border-gray-100 bg-white p-5 transition-all duration-200 hover:border-gray-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer active:scale-[0.98]">
      <div className="flex items-start justify-between mb-3">
        <div className={cn('flex h-12 w-12 items-center justify-center rounded-xl text-xl shadow-sm', s.light)}>
          {subject.icon}
        </div>
        <ProgressRing progress={subject.progress} color={subject.colorHex} />
      </div>
      <h3 className="text-sm font-bold text-gray-900">{subject.name}</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-3">{subject.lessonsCompleted}/{subject.totalLessons} lessons done</p>
      <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-700 ease-out', s.bar)}
          style={{ width: `${subject.progress}%` }}
        />
      </div>
    </div>
  )
}

export function StudentDashboard() {
  const navigate = useNavigate()
  const { xp, level, streak, xpProgress } = useGamification()

  return (
    <div>
      {/* XP & Level Bar */}
      <div className="flex items-center gap-4 mb-6 p-4 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center shadow-sm">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-xs text-amber-700 font-medium">Level {level}</div>
            <div className="text-lg font-bold text-amber-900">{xp} XP</div>
          </div>
        </div>
        <div className="flex-1">
          <div className="h-2.5 rounded-full bg-amber-200 overflow-hidden">
            <div className="h-full rounded-full bg-gradient-to-r from-amber-400 to-orange-500 transition-all duration-500" style={{ width: `${xpProgress}%` }} />
          </div>
          <div className="text-[10px] text-amber-600 mt-0.5 font-medium">
            {xp % 200}/200 XP to next level
          </div>
        </div>
        <div className="flex items-center gap-1.5 bg-white/60 rounded-xl px-3 py-2">
          <Flame className="w-4 h-4 text-orange-500" />
          <span className="font-bold text-orange-600">{streak}</span>
          <span className="text-xs text-orange-500">day streak</span>
        </div>
      </div>

      {/* Top bar: Greeting + Search + Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Hey, {student.name.split(' ')[0]}! <span className="inline-block animate-bounce">👋</span>
          </h1>
          <p className="text-sm text-gray-400 mt-0.5">Ready for an awesome learning adventure today?</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input type="text" placeholder="Search subjects..." className="w-48 h-9 rounded-xl border border-gray-200 bg-white pl-9 pr-3 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all" />
          </div>
          <div className="flex items-center gap-3 text-sm">
            <div className="flex items-center gap-1.5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl px-3 py-1.5 border border-blue-100">
              <Clock className="h-4 w-4 text-blue-500" />
              <span className="font-bold text-blue-700">{student.weeklyHours}h</span>
              <span className="text-blue-500 text-xs hidden sm:inline">this week</span>
            </div>
          </div>
        </div>
      </div>

      {/* Subjects Grid — 4 cols (4 modules) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {subjects.map((subject) => (
          <SubjectCard key={subject.id} subject={subject} />
        ))}
      </div>

      {/* Quick Action Buttons */}
      <div className="flex gap-3 mb-8 flex-wrap">
        <button onClick={() => navigate('/student/ai-tutor')} className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all active:scale-95">
          <Sparkles className="w-4 h-4" /> Learn with AI Tutor
        </button>
        <button onClick={() => navigate('/student/assessments')} className="flex items-center gap-2 px-5 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 text-sm font-semibold hover:border-gray-300 hover:shadow-sm transition-all active:scale-95">
          <Trophy className="w-4 h-4 text-amber-500" /> Take a Quiz
        </button>
        <button onClick={() => navigate('/student/achievements')} className="flex items-center gap-2 px-5 py-3 rounded-xl bg-white border border-gray-200 text-gray-700 text-sm font-semibold hover:border-gray-300 hover:shadow-sm transition-all active:scale-95">
          <Star className="w-4 h-4 text-purple-500" /> Achievements
        </button>
      </div>

      {/* Bottom: Recent Activity (3/5) + Recommended (2/5) */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Recent Activity</h2>
            <button onClick={() => navigate('/student/progress')} className="text-xs text-blue-600 font-semibold hover:text-blue-700 transition-colors flex items-center gap-0.5">
              View all <ChevronRight className="h-3 w-3" />
            </button>
          </div>
          <div className="space-y-1.5">
            {recentActivity.map((activity) => {
              const Icon = activityIcons[activity.type]
              const color = activityColors[activity.type]
              return (
                <div key={activity.id} className="flex items-center gap-3.5 rounded-xl px-4 py-3 transition-colors hover:bg-white cursor-default border border-transparent hover:border-gray-100">
                  <div className={cn('flex h-9 w-9 items-center justify-center rounded-xl shrink-0', color)}>
                    <Icon className="h-4.5 w-4.5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800">{activity.description}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{activity.subject} &middot; {activity.timestamp}</p>
                  </div>
                  {activity.score !== undefined && (
                    <Badge variant={activity.score >= 90 ? 'success' : 'warning'} className="text-[10px] px-2.5 py-0.5 rounded-full shrink-0 font-semibold">
                      {activity.score}%
                    </Badge>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Recommended */}
        <div className="lg:col-span-2">
          <h2 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-4">Continue Learning</h2>
          <div className="space-y-2.5">
            {recommendedLessons.map((lesson) => (
              <button
                key={lesson.id}
                onClick={() => navigate('/student/learning')}
                className="flex items-center gap-3.5 w-full rounded-xl border border-gray-100 bg-white px-4 py-4 transition-all duration-150 hover:border-gray-200 hover:shadow-md text-left active:scale-[0.99] group"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl shrink-0 text-white shadow-sm" style={{ backgroundColor: lesson.subjectColor }}>
                  <Play className="h-4 w-4 fill-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-bold text-gray-800 truncate">{lesson.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{lesson.subject} &middot; {lesson.duration}</p>
                </div>
                <ArrowRight className="h-4 w-4 text-gray-300 group-hover:text-gray-500 transition-colors shrink-0" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
