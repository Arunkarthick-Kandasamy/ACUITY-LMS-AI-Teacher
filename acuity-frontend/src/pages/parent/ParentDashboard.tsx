import { parentData, openScoreData } from '@/data/mockData'
import { TrendingUp, Clock, AlertTriangle, BookOpen, ArrowUpRight, Award } from 'lucide-react'
import { cn } from '@/lib/utils'

export function ParentDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Parent Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Track {parentData.studentName}'s learning journey</p>
      </div>

      {/* Overview Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { icon: Award, label: 'Overall Mastery', value: `${parentData.overallMastery}%`, change: '+5% this week', color: 'text-emerald-600 bg-emerald-50' },
          { icon: BookOpen, label: 'Current Track', value: 'Support Learner', desc: parentData.trackReason, color: 'text-amber-600 bg-amber-50' },
          { icon: Clock, label: 'Time This Week', value: `${parentData.timeSpentThisWeek}h`, change: `↑ ${Math.round((parentData.timeSpentThisWeek - parentData.previousWeekTime) / parentData.previousWeekTime * 100)}% vs last week`, color: 'text-blue-600 bg-blue-50' },
          { icon: TrendingUp, label: 'Module Type', value: 'Simplified', desc: 'Step-by-step with examples', color: 'text-purple-600 bg-purple-50' },
        ].map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
              <div className="flex items-center gap-3 mb-3">
                <div className={`w-9 h-9 rounded-lg ${stat.color} flex items-center justify-center`}>
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div className="text-xs text-slate-400 font-medium">{stat.label}</div>
              </div>
              <div className="text-2xl font-bold text-slate-900">{stat.value}</div>
              {'change' in stat && stat.change && <div className="text-xs text-emerald-600 mt-1">{stat.change}</div>}
              {'desc' in stat && stat.desc && <div className="text-xs text-slate-400 mt-1">{stat.desc}</div>}
            </div>
          )
        })}
      </div>

      {/* Weekly Scores */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900 mb-4">Weekly Performance</h2>
        <div className="flex items-end gap-2 h-32">
          {parentData.weeklyScores.map((day, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-1">
              <span className={cn('text-xs font-medium', day.score >= 75 ? 'text-emerald-600' : 'text-amber-600')}>{day.score}</span>
              <div
                className={cn('w-full rounded-t-md transition-all', day.score >= 75 ? 'bg-emerald-500' : 'bg-amber-500')}
                style={{ height: `${day.score}%`, maxHeight: '100px', minHeight: '4px' }}
              />
              <span className="text-[10px] text-slate-400">{day.day}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Weak Topics & Alerts */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Areas Needing Support</h2>
          <div className="space-y-3">
            {parentData.weakTopics.map((topic) => (
              <div key={topic.topic}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-700">{topic.topic}</span>
                  <span className="text-red-500 font-medium">{topic.mastery}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-bar-fill bg-red-500" style={{ width: `${topic.mastery}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 p-3 rounded-lg bg-amber-50 border border-amber-200">
            <div className="flex items-center gap-2 text-sm text-amber-800">
              <AlertTriangle className="w-4 h-4" />
              <span>Simplified module recommended based on current scores</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="font-semibold text-slate-900 mb-4">Recent Updates</h2>
          <div className="space-y-3">
            {parentData.alerts.map((alert) => (
              <div key={alert.id} className={cn(
                'flex items-start gap-3 p-3 rounded-lg border',
                alert.type === 'success' && 'bg-emerald-50 border-emerald-200',
                alert.type === 'warning' && 'bg-amber-50 border-amber-200',
                alert.type === 'info' && 'bg-blue-50 border-blue-200',
              )}>
                {alert.type === 'success' && <TrendingUp className="w-4 h-4 text-emerald-600 mt-0.5" />}
                {alert.type === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-600 mt-0.5" />}
                {alert.type === 'info' && <Clock className="w-4 h-4 text-blue-600 mt-0.5" />}
                <div>
                  <p className={cn(
                    'text-sm font-medium',
                    alert.type === 'success' && 'text-emerald-800',
                    alert.type === 'warning' && 'text-amber-800',
                    alert.type === 'info' && 'text-blue-800',
                  )}>{alert.message}</p>
                  <p className="text-xs text-slate-400 mt-0.5">{alert.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
