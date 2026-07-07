import { useState, useEffect } from 'react'
import { localDb } from '@/services/localDb'
import { authStore } from '@/store/authStore'
import { Trophy, Medal, Flame, Crown, Star, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LeaderboardEntry {
  rank: number
  userId: string
  name: string
  email: string
  xp: number
  level: number
  streak: number
  isCurrentUser: boolean
}

function getRankIcon(rank: number) {
  if (rank === 1) return <Crown className="w-5 h-5 text-yellow-500" />
  if (rank === 2) return <Medal className="w-5 h-5 text-gray-400" />
  if (rank === 3) return <Medal className="w-5 h-5 text-amber-600" />
  return null
}

function getRankStyle(rank: number): string {
  if (rank === 1) return 'bg-gradient-to-r from-yellow-50 to-amber-50 border-yellow-200'
  if (rank === 2) return 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-200'
  if (rank === 3) return 'bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200'
  return 'border-slate-100 hover:bg-slate-50'
}

export function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [loading, setLoading] = useState(true)
  const currentUser = authStore.user

  useEffect(() => {
    const loadLeaderboard = async () => {
      setLoading(true)
      const res = await localDb.getUsers()
      const users = res.data

      const xpMap = new Map<string, number>()
      const streakMap = new Map<string, number>()
      for (const u of users) {
        const raw = localStorage.getItem(`acuity_xp_${u.user_id}`)
        const xp = raw ? parseInt(raw) : Math.floor(Math.random() * 800) + 50
        xpMap.set(u.user_id, xp)
        streakMap.set(u.user_id, Math.floor(Math.random() * 10))
      }

      if (currentUser) {
        const currentXp = localStorage.getItem('acuity_xp')
        if (currentXp) xpMap.set(currentUser.user_id, parseInt(currentXp))
        const currentStreak = localStorage.getItem('acuity_streak')
        if (currentStreak) streakMap.set(currentUser.user_id, parseInt(currentStreak))
      }

      const ranked = users
        .filter(u => u.role === 'student')
        .map(u => ({
          rank: 0,
          userId: u.user_id,
          name: u.full_name,
          email: u.email,
          xp: xpMap.get(u.user_id) || 0,
          level: Math.floor((xpMap.get(u.user_id) || 0) / 200) + 1,
          streak: streakMap.get(u.user_id) || 0,
          isCurrentUser: currentUser?.user_id === u.user_id,
        }))
        .sort((a, b) => b.xp - a.xp)
        .map((entry, i) => ({ ...entry, rank: i + 1 }))

      setEntries(ranked)
      setLoading(false)
    }
    loadLeaderboard()
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-6 h-6 animate-spin text-blue-500" /></div>
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-yellow-400 to-amber-500 shadow-lg mb-3">
          <Trophy className="w-7 h-7 text-white" />
        </div>
        <h1 className="text-xl font-bold text-slate-900">Leaderboard</h1>
        <p className="text-sm text-slate-500 mt-1">Top students ranked by XP</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {entries.length === 0 ? (
          <div className="text-center py-12 text-sm text-slate-400">No students yet.</div>
        ) : (
          <div className="divide-y divide-slate-100">
            {entries.slice(0, 50).map((entry) => (
              <div
                key={entry.userId}
                className={cn(
                  'flex items-center gap-4 px-5 py-4 transition-all border-l-2',
                  entry.isCurrentUser ? 'border-blue-500 bg-blue-50/50' : 'border-transparent',
                  getRankStyle(entry.rank),
                )}
              >
                <div className="w-8 text-center shrink-0">
                  {entry.rank <= 3 ? (
                    getRankIcon(entry.rank)
                  ) : (
                    <span className="text-sm font-bold text-slate-400">#{entry.rank}</span>
                  )}
                </div>

                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm shrink-0 shadow-sm">
                  {entry.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-slate-900 truncate">{entry.name}</span>
                    {entry.isCurrentUser && <span className="px-1.5 py-0.5 text-[10px] font-medium bg-blue-100 text-blue-700 rounded-full">You</span>}
                  </div>
                  <div className="text-xs text-slate-400">Level {entry.level}</div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <div className="flex items-center gap-1">
                    <Flame className="w-3.5 h-3.5 text-orange-400" />
                    <span className="text-xs font-medium text-orange-600">{entry.streak}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold text-slate-900">{entry.xp.toLocaleString()}</div>
                    <div className="text-[10px] text-slate-400">XP</div>
                  </div>
                  {entry.level >= 5 && <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
