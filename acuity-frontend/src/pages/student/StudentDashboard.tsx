import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Flame, Clock, Play, CheckCircle2, BookOpen, Sparkles,
  ChevronRight, Search, ArrowRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { Badge, Avatar, AvatarFallback } from '@/components/ui'
import {
  student, subjects, recentActivity, recommendedLessons,
  type Subject,
} from './dashboard/dashboard-data'

const subjectStyles: Record<string, { bg: string; text: string; bar: string; light: string }> = {
  blue:    { bg: 'bg-blue-500', text: 'text-blue-600', bar: 'bg-blue-500', light: 'bg-blue-50' },
  green:   { bg: 'bg-green-500', text: 'text-green-600', bar: 'bg-green-500', light: 'bg-green-50' },
  purple:  { bg: 'bg-purple-500', text: 'text-purple-600', bar: 'bg-purple-500', light: 'bg-purple-50' },
  orange:  { bg: 'bg-orange-500', text: 'text-orange-600', bar: 'bg-orange-500', light: 'bg-orange-50' },
}

const activityIcons: Record<string, typeof Play> = {
  quiz: CheckCircle2, lesson: Play, badge: Sparkles, practice: BookOpen,
}

const activityColors: Record<string, string> = {
  quiz: 'text-emerald-600 bg-emerald-50',
  lesson: 'text-blue-600 bg-blue-50',
  badge: 'text-amber-600 bg-amber-50',
  practice: 'text-purple-600 bg-purple-50',
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
    <div className="group relative rounded-xl border border-gray-200 bg-white p-5 transition-all duration-150 hover:border-gray-300 hover:shadow-sm cursor-pointer active:scale-[0.99]">
      <div className="flex items-start justify-between mb-3">
        <div className={cn('flex h-11 w-11 items-center justify-center rounded-lg text-lg', s.light)}>
          {subject.icon}
        </div>
        <ProgressRing progress={subject.progress} color={subject.color} />
      </div>
      <h3 className="text-sm font-semibold text-gray-900">{subject.name}</h3>
      <p className="text-xs text-gray-400 mt-0.5 mb-3">{subject.lessonsCompleted}/{subject.totalLessons} lessons</p>
      <div className="h-1.5 rounded-full bg-gray-100 overflow-hidden">
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

  return (
    <div>
      {/* Top bar: Greeting + Search + Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">
            Hi, {student.name.split(' ')[0]}!
          </h1>
          <p className="text-sm text-gray-400 mt-0.5">Ready for today's lessons?</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search subjects..."
              className="w-48 h-9 rounded-lg border border-gray-200 bg-white pl-9 pr-3 text-sm text-gray-700 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
            />
          </div>
          <div className="flex items-center gap-3 text-sm">
            <div className="flex items-center gap-1">
              <Flame className="h-4 w-4 text-orange-500" />
              <span className="font-semibold text-gray-900">{student.streak}</span>
              <span className="text-gray-400 hidden sm:inline">day streak</span>
            </div>
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4 text-gray-400" />
              <span className="font-semibold text-gray-900">{student.weeklyHours}h</span>
              <span className="text-gray-400 hidden sm:inline">this week</span>
            </div>
          </div>
        </div>
      </div>

      {/* Subjects Grid — 4 cols */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {subjects.map((subject) => (
          <SubjectCard key={subject.id} subject={subject} />
        ))}
      </div>

      {/* Bottom: Recent Activity (3/5) + Recommended (2/5) */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Recent Activity */}
        <div className="lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recent Activity</h2>
            <button
              onClick={() => navigate('/student/progress')}
              className="text-xs text-blue-500 font-medium hover:text-blue-600 transition-colors flex items-center gap-0.5"
            >
              View all <ChevronRight className="h-3 w-3" />
            </button>
          </div>
          <div className="space-y-1">
            {recentActivity.map((activity) => {
              const Icon = activityIcons[activity.type]
              const color = activityColors[activity.type]
              return (
                <div
                  key={activity.id}
                  className="flex items-center gap-3.5 rounded-lg px-3.5 py-3 transition-colors hover:bg-white cursor-default"
                >
                  <div className={cn('flex h-8 w-8 items-center justify-center rounded-lg shrink-0', color)}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800">{activity.description}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{activity.subject} &middot; {activity.timestamp}</p>
                  </div>
                  {activity.score !== undefined && (
                    <Badge variant={activity.score >= 90 ? 'success' : 'warning'} className="text-[10px] px-2 py-0.5 rounded-full shrink-0">
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
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">Continue Learning</h2>
          <div className="space-y-2">
            {recommendedLessons.map((lesson) => (
              <button
                key={lesson.id}
                onClick={() => navigate('/student/learning')}
                className="flex items-center gap-3.5 w-full rounded-lg border border-gray-200 bg-white px-3.5 py-3.5 transition-all duration-150 hover:border-gray-300 hover:shadow-sm text-left active:scale-[0.99] group"
              >
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-lg shrink-0 text-white"
                  style={{ backgroundColor: lesson.subjectColor }}
                >
                  <Play className="h-3.5 w-3.5 fill-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{lesson.title}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{lesson.subject} &middot; {lesson.duration}</p>
                </div>
                <ArrowRight className="h-3.5 w-3.5 text-gray-300 group-hover:text-gray-500 transition-colors shrink-0" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
