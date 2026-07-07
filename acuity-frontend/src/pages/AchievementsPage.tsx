import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trophy, Star, Zap, Flame, ArrowLeft, Sparkles, Medal, Target, CheckCircle2, Lock } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useGamification, xpForAction } from '@/hooks/useGamification'
import { Confetti } from '@/components/ui/Confetti'

interface Badge {
  id: string
  name: string
  icon: string
  description: string
  category: string
  earned: boolean
  earnedDate?: string
}

const defaultBadges: Badge[] = [
  { id: 'b1', name: 'First Steps', icon: '🌱', description: 'Complete your first lesson', category: 'Beginner', earned: true, earnedDate: new Date().toISOString() },
  { id: 'b2', name: 'Quick Learner', icon: '⚡', description: 'Complete 5 lessons', category: 'Progress', earned: true, earnedDate: new Date().toISOString() },
  { id: 'b3', name: 'Knowledge Seeker', icon: '📚', description: 'Complete 10 lessons', category: 'Progress', earned: false },
  { id: 'b4', name: 'Math Whiz', icon: '🧮', description: 'Master 5 Math concepts', category: 'Subject', earned: false },
  { id: 'b5', name: 'Science Star', icon: '🔬', description: 'Master 5 Science concepts', category: 'Subject', earned: false },
  { id: 'b6', name: 'Perfect Score', icon: '💯', description: 'Get 100% on any quiz', category: 'Achievement', earned: false },
  { id: 'b7', name: 'Streak Master', icon: '🔥', description: 'Maintain a 7-day streak', category: 'Streak', earned: true, earnedDate: new Date(Date.now() - 86400000 * 2).toISOString() },
  { id: 'b8', name: 'Quiz Champion', icon: '🏆', description: 'Pass 5 assessments', category: 'Achievement', earned: false },
  { id: 'b9', name: 'Super Student', icon: '⭐', description: 'Reach Level 5', category: 'Milestone', earned: false },
  { id: 'b10', name: 'Night Owl', icon: '🦉', description: 'Study for 7 days in a row', category: 'Streak', earned: true, earnedDate: new Date().toISOString() },
  { id: 'b11', name: 'Bookworm', icon: '🐛', description: 'Read 20 lessons', category: 'Progress', earned: false },
  { id: 'b12', name: 'Rising Star', icon: '🌟', description: 'Reach Level 3', category: 'Milestone', earned: true, earnedDate: new Date(Date.now() - 86400000 * 5).toISOString() },
]

const AchievementsPage = () => {
  const navigate = useNavigate()
  const { xp, level, streak, xpProgress } = useGamification()
  const [badges] = useState<Badge[]>(defaultBadges)
  const [confetti, setConfetti] = useState(false)
  const [activeTab, setActiveTab] = useState<'all' | 'earned' | 'locked'>('all')

  useEffect(() => {
    if (badges.some(b => b.earned)) setConfetti(true)
    setTimeout(() => setConfetti(false), 2500)
  }, [])

  const earned = badges.filter(b => b.earned).length
  const filtered = badges.filter(b => activeTab === 'all' ? true : activeTab === 'earned' ? b.earned : !b.earned)

  const categories = [...new Set(badges.map(b => b.category))]

  return (
    <div className="max-w-4xl mx-auto">
      <Confetti active={confetti} />

      {/* Header */}
      <div className="mb-6">
        <button onClick={() => navigate('/student/dashboard')} className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 mb-2 transition-colors">
          <ArrowLeft className="w-3 h-3" /> Back to Dashboard
        </button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <Trophy className="w-6 h-6 text-amber-500" /> Achievements
            </h1>
            <p className="text-sm text-slate-500 mt-0.5">Your badges and accomplishments</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div className="rounded-2xl bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 p-4 text-center">
          <div className="text-3xl font-black text-amber-600">{level}</div>
          <div className="text-xs text-amber-700 font-semibold mt-0.5">Level</div>
        </div>
        <div className="rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 p-4 text-center">
          <div className="text-3xl font-black text-blue-600">{xp}</div>
          <div className="text-xs text-blue-700 font-semibold mt-0.5">Total XP</div>
        </div>
        <div className="rounded-2xl bg-gradient-to-br from-red-50 to-pink-50 border border-red-200 p-4 text-center">
          <div className="text-3xl font-black text-red-500">{streak}</div>
          <div className="text-xs text-red-700 font-semibold mt-0.5">Day Streak</div>
        </div>
        <div className="rounded-2xl bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 p-4 text-center">
          <div className="text-3xl font-black text-green-600">{earned}/{badges.length}</div>
          <div className="text-xs text-green-700 font-semibold mt-0.5">Badges</div>
        </div>
      </div>

      {/* XP Progress */}
      <div className="mb-6 p-4 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            <span className="font-bold text-sm text-slate-800">Level {level} Progress</span>
          </div>
          <span className="text-xs text-slate-500 font-medium">{xp % 200}/200 XP to next level</span>
        </div>
        <div className="h-3 rounded-full bg-amber-100 overflow-hidden">
          <div className="h-full rounded-full bg-gradient-to-r from-amber-400 to-orange-500 transition-all duration-500" style={{ width: `${xpProgress}%` }} />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6">
        {(['all', 'earned', 'locked'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              'px-4 py-2 rounded-xl text-sm font-semibold transition-all',
              activeTab === tab
                ? 'bg-slate-900 text-white shadow-md'
                : 'bg-white text-slate-600 border border-slate-200 hover:border-slate-300'
            )}
          >
            {tab === 'all' ? 'All Badges' : tab === 'earned' ? `Earned (${earned})` : `Locked (${badges.length - earned})`}
          </button>
        ))}
      </div>

      {/* Category Sections */}
      {categories.map(cat => {
        const catBadges = filtered.filter(b => b.category === cat)
        if (catBadges.length === 0) return null
        return (
          <div key={cat} className="mb-6">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">{cat}</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {catBadges.map(badge => (
                <div
                  key={badge.id}
                  className={cn(
                    'rounded-2xl p-4 border-2 transition-all hover:shadow-md',
                    badge.earned
                      ? 'bg-white border-amber-300 shadow-sm'
                      : 'bg-slate-50 border-slate-200 opacity-60'
                  )}
                >
                  <div className={cn(
                    'text-4xl mb-2',
                    badge.earned ? '' : 'grayscale'
                  )}>
                    {badge.icon}
                  </div>
                  <div className={cn(
                    'font-bold text-sm',
                    badge.earned ? 'text-slate-900' : 'text-slate-400'
                  )}>
                    {badge.name}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">{badge.description}</div>
                  {badge.earned && badge.earnedDate && (
                    <div className="flex items-center gap-1 mt-2 text-[10px] text-emerald-600 font-medium">
                      <CheckCircle2 className="w-3 h-3" />
                      Earned
                    </div>
                  )}
                  {!badge.earned && (
                    <div className="flex items-center gap-1 mt-2 text-[10px] text-slate-400">
                      <Lock className="w-3 h-3" />
                      Keep learning to unlock!
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )
      })}

      {filtered.length === 0 && (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
          <Target className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500 font-medium">No badges found in this category</p>
        </div>
      )}
    </div>
  )
}

export default AchievementsPage
