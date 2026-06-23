import { useAuthApi } from '@/hooks/useApi'
import { getParentStudents, getParentStudentProgress } from '@/services/parent'
import { getScoreColor, cn } from '@/lib/utils'
import { Clock, TrendingUp, BookOpen, ArrowUpRight, Loader2 } from 'lucide-react'

export function ParentStudentDetail() {
  const { data: students, loading } = useAuthApi(() => getParentStudents(), [])
  const firstStudent = students?.[0]

  const { data: progress } = useAuthApi(
    () => firstStudent ? getParentStudentProgress(firstStudent.student_id) : Promise.reject(),
    [firstStudent?.student_id],
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const studentName = firstStudent?.full_name || 'Student'
  const overallMastery = firstStudent ? Math.round(firstStudent.overall_mastery_avg * 100) : 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{studentName}'s Progress</h1>
          <p className="text-sm text-slate-500 mt-1">Grade {firstStudent?.grade_level || 'N/A'} · Detailed performance view</p>
        </div>
        <button className="btn-secondary text-sm">
          Download Report <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
        </button>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Performance Overview</h2>
          <div className="space-y-4">
            {[
              { label: 'Overall Mastery', value: overallMastery, desc: 'Average across all concepts' },
              { label: 'Active Courses', value: firstStudent?.active_courses ? Math.min(firstStudent.active_courses * 25, 100) : 0, desc: 'Course engagement level' },
              { label: 'Streak', value: firstStudent?.current_streak_days ? Math.min(firstStudent.current_streak_days * 10, 100) : 0, desc: 'Learning consistency' },
            ].map((param) => (
              <div key={param.label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-700">{param.label}</span>
                  <span className={cn('font-medium', getScoreColor(param.value))}>{firstStudent?.current_streak_days || param.value}/100</span>
                </div>
                <div className="progress-bar">
                  <div className={cn(
                    'progress-bar-fill',
                    param.value >= 75 ? 'bg-emerald-500' : param.value >= 50 ? 'bg-amber-500' : 'bg-red-500'
                  )} style={{ width: `${param.value}%` }} />
                </div>
                <div className="text-[10px] text-slate-400 mt-0.5">{param.desc}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Learning Behavior</h2>
          <div className="space-y-4">
            {[
              { icon: Clock, label: 'Courses Active', value: String(firstStudent?.active_courses || 0), desc: 'Currently enrolled courses' },
              { icon: BookOpen, label: 'Mastery Level', value: `${overallMastery}%`, desc: 'Overall concept mastery' },
              { icon: TrendingUp, label: 'Streak', value: `${firstStudent?.current_streak_days || 0} days`, desc: 'Consecutive learning days' },
            ].map((item) => {
              const Icon = item.icon
              return (
                <div key={item.label} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50">
                  <div className="w-8 h-8 rounded-lg bg-white border border-slate-200 flex items-center justify-center mt-0.5">
                    <Icon className="w-4 h-4 text-slate-500" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400">{item.label}</div>
                    <div className="text-sm font-semibold text-slate-800">{item.value}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{item.desc}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
