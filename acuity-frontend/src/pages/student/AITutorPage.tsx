import { useState, useRef, useEffect } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { startSession, teach, endSession } from '@/services/sessions'
import { Send, Sparkles, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Message {
  id: number
  role: 'user' | 'ai'
  content: string
  time: string
}

export function AITutorPage() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, role: 'ai', content: "Hi! I'm your AI tutor. Let me know if you're ready to start learning.", time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  useEffect(() => {
    if (courseId && !sessionId) {
      startSession(courseId).then(res => {
        setSessionId(res.data.session_id)
      }).catch(() => {})
    }
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

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-xl font-semibold text-slate-900">AI Tutor</h1>
        <p className="text-sm text-slate-500 mt-1">Your personal adaptive learning assistant</p>
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
                disabled={sending}
              />
              <Sparkles className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            </div>
            <button onClick={handleSend} disabled={sending} className="btn-primary px-4 disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
