import { useState, useRef, useEffect } from 'react'
import { chatHistory } from '@/data/mockData'
import { Send, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AITutorPage() {
  const [messages, setMessages] = useState(chatHistory)
  const [input, setInput] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    const newMsg = { id: messages.length + 1, role: 'user' as const, content: input, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
    setMessages(prev => [...prev, newMsg])
    setInput('')

    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'ai' as const,
        content: `Great question! Let me explain "${input.slice(0, 30)}..." in a way that's easy to understand. First, think of it like building blocks — each concept builds on the previous one. Here's a step-by-step breakdown...`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }])
    }, 1000)
  }

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-xl font-semibold text-slate-900">AI Tutor</h1>
        <p className="text-sm text-slate-500 mt-1">Your personal adaptive learning assistant</p>
      </div>

      {/* Chat area */}
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
              />
              <Sparkles className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-300" />
            </div>
            <button onClick={handleSend} className="btn-primary px-4">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
