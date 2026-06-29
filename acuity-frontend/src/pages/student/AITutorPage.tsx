import { useState, useRef, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { startSession, teach, endSession } from '@/services/sessions'
import { Send, Sparkles, Loader2, X, Clock, MessageSquare, BookOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Message {
  id: number
  role: 'user' | 'ai'
  content: string
  time: string
}

interface SessionSummary {
  sessionId: string
  startedAt: Date
  duration: string
  exchanges: number
}

export function AITutorPage() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, role: 'ai', content: "Hi! I'm your AI tutor. Let me know if you're ready to start learning.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [sessionStartedAt] = useState(new Date())
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  const doEndSession = useCallback(async (sid: string) => {
    try {
      const now = new Date()
      const diffMs = now.getTime() - sessionStartedAt.getTime()
      const diffMins = Math.floor(diffMs / 60000)
      const hours = Math.floor(diffMins / 60)
      const mins = diffMins % 60
      const duration = hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
      setSummary({
        sessionId: sid,
        startedAt: sessionStartedAt,
        duration,
        exchanges: Math.max(0, Math.floor((messages.length - 1) / 2)),
      })
      await endSession(sid)
    } catch {
      // ignore
    }
  }, [sessionStartedAt, messages.length])

  useEffect(() => {
    if (courseId && !sessionId) {
      startSession(courseId).then(res => {
        setSessionId(res.data.session_id)
      }).catch(() => {})
    }
    return () => {
      if (sessionId && !summary) {
        endSession(sessionId).catch(() => {})
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId, sessionId])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || sending || !courseId) return

    const userMsg: Message = {
      id: messages.length + 1,
      role: 'user',
      content: input,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setSending(true)

    try {
      const res = await teach(courseId, input)
      const aiContent = typeof res.data.content === 'string'
        ? res.data.content
        : JSON.stringify(res.data.content)

      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'ai',
        content: aiContent || 'I understood your question. Let me explain that in detail.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }])
    } catch {
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'ai',
        content: "I'm here to help! Could you please rephrase your question?",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }])
    } finally {
      setSending(false)
    }
  }

  const handleEndSession = async () => {
    if (sessionId) await doEndSession(sessionId)
  }

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">AI Tutor</h1>
          <p className="text-sm text-slate-500 mt-1">Your personal adaptive learning assistant</p>
        </div>
        {sessionId && !summary && (
          <button
            onClick={handleEndSession}
            className="px-3 py-1.5 text-xs font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50 transition-all"
          >
            End Session
          </button>
        )}
      </div>

      <div className="flex-1 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
              <div className={cn(
                'max-w-[75%] rounded-xl px-4 py-3',
                msg.role === 'user'
                  ? 'bg-navy-800 text-white'
                  : 'bg-slate-50 border border-slate-200 text-slate-800'
              )}>
                <p className="text-sm leading-relaxed">{msg.content}</p>
                <p className={cn(
                  'text-[10px] mt-1',
                  msg.role === 'user' ? 'text-white/50' : 'text-slate-400'
                )}>{msg.time}</p>
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-slate-50 border border-slate-200 rounded-xl px-4 py-3">
                <Loader2 className="w-4 h-4 animate-spin text-navy-600" />
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
                placeholder="Ask your AI tutor anything..."
                className="input-field pr-10"
                disabled={sending || !!summary}
              />
              <Sparkles className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            </div>
            <button onClick={handleSend} disabled={sending || !!summary} className="btn-primary px-4 disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Session Summary Modal */}
      {summary && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 relative">
            <button
              onClick={() => navigate('/student/dashboard')}
              className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="text-center mb-6">
              <div className="w-14 h-14 rounded-full bg-navy-50 flex items-center justify-center mx-auto mb-3">
                <BookOpen className="w-7 h-7 text-navy-700" />
              </div>
              <h2 className="text-lg font-semibold text-slate-900">Session Complete</h2>
              <p className="text-sm text-slate-500 mt-1">Great work! Here's your session summary.</p>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-slate-50 rounded-xl p-4 text-center">
                <Clock className="w-5 h-5 text-navy-600 mx-auto mb-1" />
                <p className="text-lg font-semibold text-slate-900">{summary.duration}</p>
                <p className="text-xs text-slate-500">Duration</p>
              </div>
              <div className="bg-slate-50 rounded-xl p-4 text-center">
                <MessageSquare className="w-5 h-5 text-navy-600 mx-auto mb-1" />
                <p className="text-lg font-semibold text-slate-900">{summary.exchanges}</p>
                <p className="text-xs text-slate-500">Exchanges</p>
              </div>
            </div>
            <div className="space-y-2">
              <button
                onClick={() => {
                  setSummary(null)
                  setSessionId(null)
                  setMessages([{ id: 1, role: 'ai', content: "Hi! I'm your AI tutor. Let me know if you're ready to start learning.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }])
                }}
                className="w-full py-2.5 bg-navy-800 text-white rounded-xl hover:bg-navy-700 transition-all text-sm font-medium shadow-sm"
              >
                Start New Session
              </button>
              <button
                onClick={() => navigate('/student/dashboard')}
                className="w-full py-2.5 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-all text-sm font-medium"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
