import { useState, useCallback, useEffect } from 'react'
import { useSound } from './useSound'

const XP_KEY = 'acuity_xp'
const LEVEL_KEY = 'acuity_level'
const STREAK_KEY = 'acuity_streak'
const LAST_ACTIVE_KEY = 'acuity_last_active'

const XP_PER_LEVEL = 200

export function useGamification() {
  const [xp, setXp] = useState(() => {
    try { return parseInt(localStorage.getItem(XP_KEY) || '0') } catch { return 0 }
  })
  const [level, setLevel] = useState(() => {
    try { return parseInt(localStorage.getItem(LEVEL_KEY) || '1') } catch { return 1 }
  })
  const [streak, setStreak] = useState(() => {
    try { return parseInt(localStorage.getItem(STREAK_KEY) || '0') } catch { return 0 }
  })
  const [showLevelUp, setShowLevelUp] = useState(false)
  const { playCorrect, playLevelUp } = useSound()

  useEffect(() => {
    const lastActive = localStorage.getItem(LAST_ACTIVE_KEY)
    if (lastActive) {
      const diff = Date.now() - new Date(lastActive).getTime()
      const daysSince = Math.floor(diff / 86400000)
      if (daysSince > 1) {
        setStreak(0)
        localStorage.setItem(STREAK_KEY, '0')
      } else if (daysSince === 1) {
        const newStreak = streak + 1
        setStreak(newStreak)
        localStorage.setItem(STREAK_KEY, String(newStreak))
      }
    }
    localStorage.setItem(LAST_ACTIVE_KEY, new Date().toISOString())
  }, [])

  const addXp = useCallback((amount: number) => {
    playCorrect()
    setXp(prev => {
      const newTotal = prev + amount
      localStorage.setItem(XP_KEY, String(newTotal))
      const newLevel = Math.floor(newTotal / XP_PER_LEVEL) + 1
      const prevLevel = Math.floor(prev / XP_PER_LEVEL) + 1
      if (newLevel > prevLevel) {
        setLevel(newLevel)
        localStorage.setItem(LEVEL_KEY, String(newLevel))
        setShowLevelUp(true)
        playLevelUp()
        setTimeout(() => setShowLevelUp(false), 3000)
      }
      return newTotal
    })
  }, [playCorrect, playLevelUp])

  const xpInLevel = xp % XP_PER_LEVEL
  const xpProgress = (xpInLevel / XP_PER_LEVEL) * 100
  const xpToNextLevel = XP_PER_LEVEL - xpInLevel

  return { xp, level, streak, showLevelUp, addXp, xpProgress, xpInLevel, xpToNextLevel }
}

export function xpForAction(action: string): number {
  const rewards: Record<string, number> = {
    complete_lesson: 50,
    perfect_score: 100,
    correct_answer: 10,
    streak_bonus: 25,
    login_bonus: 5,
    assessment_pass: 75,
    assessment_perfect: 150,
  }
  return rewards[action] || 5
}
