import { studentProfile, openScoreData, lessons } from '@/data/mockData'
import { getTrackLabel, getScoreColor, formatScore } from '@/lib/utils'
import { BookOpen, TrendingUp, Clock, Target, ArrowRight, CheckCircle2, Lock } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'

export function StudentDashboard() {
  const navigate = useNavigate()
  const trackInfo = getTrackLabel(openScoreData.overall)

  return (
    <div className="space-y-6">
      {/* Welcome + Open Score */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-xl font-semibold text-slate-900">
                Hi, {studentProfile.name}! 👋
              </h1>
              <p className="text-sm text-slate-500 mt-1">
                Grade {studentProfile.grade} · {studentProfile.subject}
              </p>
            </div>
            <span className={cn('badge', trackInfo.color)}>
              {trackInfo.label}
            </span>
          </div>

          {/* Open Score */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
            {[
              { label: 'Correctness', value: openScoreData.parameters.correctness, icon: '✓' },
              { label: 'Response Time', value: openScoreData.parameters.responseTime, icon: '⏱' },
              { label: 'Retries', value: openScoreData.parameters.retries, icon: '↻' },
              { label: 'Skips', value: openScoreData.parameters.skips, icon: '→' },
            ].map((param) => (
              <div key={param.label} className="bg-slate-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-slate-500">{param.label}</span>
                  <span className="text-xs">{param.icon}</span>
                </div>
                <div className={cn('text-lg font-bold', getScoreColor(param.value))}>
                  {formatScore(param.value)}
                </div>
                <div className="progress-bar mt-1">
                  <div
                    className={cn('progress-bar-fill', param.value >= 75 ? 'bg-emerald-500' : param.value >= 50 ? 'bg-amber-500' : 'bg-red-500')}
                    style={{ width: `${param.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <p className="text-xs text-slate-400 mt-3">
            Open Score: {openScoreData.overall}/100 · {trackInfo.desc}
          </p>
        </div>

        {/* Quick Stats */}
        <div className="space-y-3">
          {[
            { icon: BookOpen, label: 'Current Lesson', value: studentProfile.currentLesson, color: 'text-blue-600 bg-blue-50' },
            { icon: TrendingUp, label: 'Open Score', value: `${openScoreData.overall}/100`, color: 'text-emerald-600 bg-emerald-50' },
            { icon: Clock, label: 'Peak Time', value: studentProfile.peakLearningTime, color: 'text-amber-600 bg-amber-50' },
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

      {/* Learning Path Progress */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-slate-900">Learning Path</h2>
          <button onClick={() => navigate('/student/learning')} className="text-sm text-navy-700 hover:text-navy-900 font-medium flex items-center gap-1">
            View All <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {lessons.map((lesson, i) => (
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
              {lesson.score && (
                <div className="text-[10px] text-emerald-600 font-medium mt-1">Score: {lesson.score}</div>
              )}
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

      {/* Quick Actions */}
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
