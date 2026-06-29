import { useState, useEffect } from 'react'
import { apiRequest } from '@/services/api'
import { mockModerationItems } from './admin-mock-data'
import { Loader2, CheckCircle2, XCircle, Clock, AlertTriangle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ModerationItem {
  id: string
  content_id: string
  content_type: string
  uploader_name: string
  status: string
  flag_reason: string | null
  created_at: string
  review_notes: string | null
}

export default function ModerationPage() {
  const [items, setItems] = useState<ModerationItem[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<string>('pending')
  const [notes, setNotes] = useState<Record<string, string>>({})

  useEffect(() => {
    const url = filter ? `/moderation/queue?status=${filter}` : '/moderation/queue'
    apiRequest(url)
      .then((res: any) => setItems(res?.data || []))
      .catch(() => setItems(mockModerationItems.filter(i => filter === 'all' || i.status === filter)))
      .finally(() => setLoading(false))
  }, [filter])

  const review = async (itemId: string, status: string) => {
    try {
      await apiRequest(`/moderation/queue/${itemId}/review`, {
        method: 'POST',
        body: JSON.stringify({ status, review_notes: notes[itemId] || '' }),
      })
      setItems((prev) => prev.filter((i) => i.id !== itemId))
    } catch {
      setItems((prev) => prev.filter((i) => i.id !== itemId))
    }
  }

  const statusStyles: Record<string, string> = {
    pending: 'bg-amber-50 text-amber-700',
    approved: 'bg-emerald-50 text-emerald-700',
    rejected: 'bg-red-50 text-red-700',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900">Content Moderation</h1>
        <p className="text-sm text-gray-500 mt-1">Review and manage flagged content across the platform.</p>
      </div>

      <div className="flex gap-2">
        {[
          { key: 'pending', label: 'Pending', count: items.filter(i => i.status === 'pending').length },
          { key: 'approved', label: 'Approved', count: items.filter(i => i.status === 'approved').length },
          { key: 'rejected', label: 'Rejected', count: items.filter(i => i.status === 'rejected').length },
        ].map((s) => (
          <button key={s.key} onClick={() => setFilter(s.key)}
            className={cn('inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all', filter === s.key ? 'bg-gray-900 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100')}>
            {s.key === 'pending' && <Clock className="w-4 h-4" />}
            {s.key === 'approved' && <CheckCircle2 className="w-4 h-4" />}
            {s.key === 'rejected' && <XCircle className="w-4 h-4" />}
            {s.label}
            <span className={cn('text-xs px-1.5 py-0.5 rounded-full', filter === s.key ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-600')}>{s.count}</span>
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <CheckCircle2 className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-400">No {filter} items found</p>
          </div>
        ) : (
          items.map((item) => (
            <div key={item.id} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-all">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={cn('flex h-9 w-9 items-center justify-center rounded-lg', statusStyles[item.status] || 'bg-gray-100')}>
                    {item.status === 'pending' && <Clock className="w-4 h-4" />}
                    {item.status === 'approved' && <CheckCircle2 className="w-4 h-4" />}
                    {item.status === 'rejected' && <XCircle className="w-4 h-4" />}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.content_type}</p>
                    <p className="text-xs text-gray-400">by {item.uploader_name}</p>
                  </div>
                </div>
                <span className={cn('inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', statusStyles[item.status])}>
                  {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                </span>
              </div>
              {item.flag_reason && (
                <div className="flex items-center gap-1.5 text-xs text-red-600 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  {item.flag_reason}
                </div>
              )}
              <p className="text-xs text-gray-400">ID: {item.content_id} &middot; {new Date(item.created_at).toLocaleDateString()}</p>
              {item.status === 'pending' && (
                <div className="mt-4 flex gap-3 items-start">
                  <textarea
                    placeholder="Add review notes..."
                    value={notes[item.id] || ''}
                    onChange={(e) => setNotes((prev) => ({ ...prev, [item.id]: e.target.value }))}
                    className="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all resize-none"
                    rows={2}
                  />
                  <div className="flex gap-2 shrink-0">
                    <button onClick={() => review(item.id, 'approved')}
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-all text-sm font-medium">
                      <CheckCircle2 className="w-4 h-4" /> Approve
                    </button>
                    <button onClick={() => review(item.id, 'rejected')}
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all text-sm font-medium">
                      <XCircle className="w-4 h-4" /> Reject
                    </button>
                  </div>
                </div>
              )}
              {item.status === 'rejected' && item.review_notes && (
                <div className="mt-2 p-2.5 rounded-lg bg-gray-50 text-xs text-gray-600">
                  <span className="font-medium text-gray-700">Review notes:</span> {item.review_notes}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
