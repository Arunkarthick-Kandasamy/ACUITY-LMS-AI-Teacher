import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { startSession, teach, endSession } from '@/services/sessions'
import { Send, Sparkles, Loader2, X, Clock, MessageSquare, BookOpen, Brain, Zap, Star } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useGamification, xpForAction } from '@/hooks/useGamification'
import { Confetti } from '@/components/ui/Confetti'
import { LevelUpModal } from '@/components/ui/LevelUpModal'

interface Message {
  id: number
  role: 'user' | 'ai'
  content: string
  time: string
}

const aiAvatars = ['🤖', '🧠', '🌟', '🎓', '🦉', '🌈']

const funFacts = [
  "Did you know? Your brain can process images in just 13 milliseconds!",
  "Fun fact: The word 'math' comes from the Greek word 'mathema' meaning 'knowledge'!",
  "Learning new things actually makes your brain grow stronger! 🧠💪",
]

export function AITutorPage() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, role: 'ai', content: "Hey there! I'm your AI learning buddy! 🚀 Ready to discover something amazing today?", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [sessionStartedAt] = useState(new Date())
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [confetti, setConfetti] = useState(false)
  const [showFunFact, setShowFunFact] = useState(true)
  const scrollRef = useRef<HTMLDivElement>(null)
  const { addXp, level, showLevelUp, xp, xpProgress } = useGamification()
  const [aiAvatar] = useState(() => aiAvatars[Math.floor(Math.random() * aiAvatars.length)])

  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  interface SessionSummary {
    sessionId: string
    startedAt: Date
    duration: string
    exchanges: number
  }

  const doEndSession = useCallback(async (sid: string) => {
    try {
      const now = new Date()
      const diffMs = now.getTime() - sessionStartedAt.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const hours = Math.floor(diffMins / 60)
      const mins = diffMins % 60
      const duration = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
      setSummary({ sessionId: sid, startedAt: sessionStartedAt, duration, exchanges: Math.max(0, Math.floor((messages.length - 1) / 2)) })
      await endSession(sid)
      addXp(xpForAction('complete_lesson') + Math.floor(diffMins * 2))
      setConfetti(true)
      setTimeout(() => setConfetti(false), 3000)
    } catch {}
  }, [sessionStartedAt, messages.length, addXp])

  useEffect(() => {
    if (courseId && !sessionId) {
      startSession(courseId).then(res => setSessionId(res.data.session_id)).catch(() => {})
    }
    return () => { if (sessionId && !summary) { endSession(sessionId).catch(() => {}) } }
  }, [courseId, sessionId, summary])

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || sending || !courseId) return

    const userMsg: Message = {
      id: messages.length + 1, role: 'user', content: input,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setSending(true)

    try {
      const res = await teach(courseId, input)
      const aiContent = typeof res.data.content === 'string' ? res.data.content : JSON.stringify(res.data.content)
      setMessages(prev => [...prev, {
        id: prev.length + 1, role: 'ai', content: aiContent || 'Great question! Let me explain that step by step.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }])
      addXp(xpForAction('correct_answer'))
    } catch {
      setMessages(prev => [...prev, {
        id: prev.length + 1, role: 'ai',
        content: "I'm here to help! Could you try asking in a different way? 😊",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }])
    } finally {
      setSending(false)
    }
  }

  const handleEndSession = async () => { if (sessionId) await doEndSession(sessionId) }

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <Confetti active={confetti} />
      <LevelUpModal level={level} show={showLevelUp} onClose={() => {}} />

      {/* XP Bar */}
      <div className="flex items-center gap-3 mb-3 p-3 rounded-xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
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

      <div className="mb-3 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            AI Learning Buddy {aiAvatar}
          </h1>
          <p className="text-xs text-slate-500">Your personal AI tutor • Ask me anything!</p>
        </div>
        {sessionId && !summary && (
          <button onClick={handleEndSession} className="px-4 py-2 text-xs font-semibold text-red-600 border border-red-200 rounded-xl hover:bg-red-50 transition-all active:scale-95">
            End Session
          </button>
        )}
      </div>

      {/* Fun Fact Banner */}
      {showFunFact && (
        <div className="mb-3 p-3 rounded-xl bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 flex items-center gap-2 text-xs text-purple-700">
          <Brain className="w-4 h-4 text-purple-500 shrink-0" />
          <span className="flex-1">{funFacts[Math.floor(Math.random() * funFacts.length)]}</span>
          <button onClick={() => setShowFunFact(false)} className="text-purple-400 hover:text-purple-600"><X className="w-3 h-3" /></button>
        </div>
      )}

      <div className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={cn('flex items-end gap-2', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
              {msg.role === 'ai' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-sm shrink-0 shadow-sm">
                  {aiAvatar}
                </div>
              )}
              <div className={cn(
                'max-w-[80%] rounded-2xl px-4 py-3',
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-md shadow-md'
                  : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-bl-md'
              )}>
                <p className="text-sm leading-relaxed whitespace-pre-line">{msg.content}</p>
                <p className={cn('text-[10px] mt-1.5', msg.role === 'user' ? 'text-white/60' : 'text-slate-400')}>{msg.time}</p>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center text-sm shrink-0 shadow-sm">
                  😊
                </div>
              )}
            </div>
          ))}
          {sending && (
            <div className="flex justify-start items-end gap-2">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-sm shrink-0">🤖</div>
              <div className="bg-slate-50 border border-slate-200 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-slate-200 p-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Ask your AI buddy anything... 💭"
                className="w-full h-11 rounded-xl border border-gray-200 bg-white px-4 pr-10 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                disabled={sending || !!summary}
              />
              <Sparkles className="absolute right-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            </div>
            <button onClick={handleSend} disabled={sending || !!summary} className="h-11 w-11 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white flex items-center justify-center hover:shadow-md hover:-translate-y-0.5 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Session Summary Modal */}
      {summary && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-6 relative overflow-hidden">
            <div className="absolute -top-10 -right-10 w-32 h-32 bg-gradient-to-br from-amber-200 to-orange-200 rounded-full blur-2xl" />
            <button onClick={() => navigate('/student/dashboard')} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600 z-10"><X className="w-5 h-5" /></button>
            <div className="text-center mb-6 relative">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center mx-auto mb-3 shadow-lg">
                <Star className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-bold text-slate-900">Amazing Work! 🌟</h2>
              <p className="text-sm text-slate-500 mt-1">You're doing great! Here's your session summary.</p>
            </div>
            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-4 text-center border border-blue-100">
                <Clock className="w-5 h-5 text-blue-600 mx-auto mb-1" />
                <p className="text-xl font-bold text-slate-900">{summary.duration}</p>
                <p className="text-xs text-slate-500 font-medium">Duration</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-4 text-center border border-green-100">
                <MessageSquare className="w-5 h-5 text-green-600 mx-auto mb-1" />
                <p className="text-xl font-bold text-slate-900">{summary.exchanges}</p>
                <p className="text-xs text-slate-500 font-medium">Exchanges</p>
              </div>
            </div>
            <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 mb-6 flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-600 shrink-0" />
              <span className="text-sm font-semibold text-amber-800">+{xpForAction('complete_lesson') + Math.floor((Date.now() - sessionStartedAt.getTime()) / 60000) * 2} XP earned!</span>
            </div>
            <div className="space-y-2.5">
              <button
                onClick={() => {
                  setSummary(null)
                  setSessionId(null)
                  setMessages([{ id: 1, role: 'ai', content: "Hey there! I'm your AI learning buddy! 🚀 Ready to discover something amazing today?", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }])
                }}
                className="w-full py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl hover:shadow-lg hover:-translate-y-0.5 transition-all text-sm font-bold shadow-md active:scale-[0.98]"
              >
                Start New Session 🚀
              </button>
              <button onClick={() => navigate('/student/dashboard')} className="w-full py-3 border border-slate-300 text-slate-700 rounded-2xl hover:bg-slate-50 transition-all text-sm font-semibold active:scale-[0.98]">
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
