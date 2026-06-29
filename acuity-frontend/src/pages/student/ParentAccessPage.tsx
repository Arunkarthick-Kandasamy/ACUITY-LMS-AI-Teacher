import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, RefreshCw, Copy, CheckCircle, Clock, Loader2, ArrowLeft, UserCheck, UserX, AlertCircle } from 'lucide-react'
import { apiRequest } from '@/services/api'
import { getPendingRequests, approveLink, rejectLink } from '@/services/parent'

interface PendingRequest {
  link_id: string
  parent_email: string | null
  parent_name: string
  parent_id: string
  requested_at: string
}

export function ParentAccessPage() {
  const navigate = useNavigate()
  const [linkingCode, setLinkingCode] = useState<{ code: string; expires_at: string } | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [pendingRequests, setPendingRequests] = useState<PendingRequest[]>([])
  const [pendingLoading, setPendingLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  const generateCode = useCallback(async () => {
    setLoading(true)
    try {
      const res = await apiRequest<{ code: string; expires_at: string }>('/api/v1/parents/link-codes/generate', {
        method: 'POST',
      })
      setLinkingCode(res.data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchPendingRequests = useCallback(async () => {
    try {
      const res = await getPendingRequests()
      setPendingRequests(res.data)
    } catch {
      // ignore
    } finally {
      setPendingLoading(false)
    }
  }, [])

  useEffect(() => {
    generateCode()
    fetchPendingRequests()
  }, [generateCode, fetchPendingRequests])

  const handleCopy = () => {
    if (linkingCode) {
      navigator.clipboard.writeText(linkingCode.code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleApprove = async (linkId: string) => {
    setActionLoading(linkId)
    try {
      await approveLink(linkId)
      setPendingRequests(prev => prev.filter(r => r.link_id !== linkId))
    } catch {
      // ignore
    } finally {
      setActionLoading(null)
    }
  }

  const handleReject = async (linkId: string) => {
    setActionLoading(linkId)
    try {
      await rejectLink(linkId)
      setPendingRequests(prev => prev.filter(r => r.link_id !== linkId))
    } catch {
      // ignore
    } finally {
      setActionLoading(null)
    }
  }

  const expiresIn = linkingCode ? Math.max(0, Math.floor((new Date(linkingCode.expires_at).getTime() - Date.now()) / 3600000)) : 0

  const formatTime = (iso: string) => {
    const d = new Date(iso)
    return d.toLocaleString()
  }

  return (
    <div className="max-w-lg mx-auto mt-8">
      <button onClick={() => navigate('/student/dashboard')} className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 mb-6">
        <ArrowLeft className="w-3 h-3" />
        Back to dashboard
      </button>

      <div className="mb-8">
        <h1 className="text-xl font-semibold text-slate-900">Parent Access</h1>
        <p className="text-sm text-slate-500 mt-1">
          Generate a code to share with your parent so they can request to view your progress.
        </p>
      </div>

      {/* Pending Requests Section */}
      {!pendingLoading && pendingRequests.length > 0 && (
        <div className="mb-6 bg-amber-50 rounded-xl border border-amber-200 p-4">
          <h3 className="text-sm font-semibold text-amber-800 mb-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4" />
            Pending Link Requests ({pendingRequests.length})
          </h3>
          <div className="space-y-3">
            {pendingRequests.map(req => (
              <div key={req.link_id} className="bg-white rounded-lg p-3 border border-amber-100">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{req.parent_name}</p>
                    {req.parent_email && (
                      <p className="text-xs text-slate-500">{req.parent_email}</p>
                    )}
                  </div>
                  <span className="text-[10px] text-slate-400">{formatTime(req.requested_at)}</span>
                </div>
                <p className="text-xs text-slate-500 mb-3">
                  This parent wants to link to your account to view your progress.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprove(req.link_id)}
                    disabled={actionLoading === req.link_id}
                    className="flex-1 py-1.5 bg-emerald-500 text-white rounded-lg text-xs font-medium hover:bg-emerald-600 transition-colors disabled:opacity-50 inline-flex items-center justify-center gap-1"
                  >
                    {actionLoading === req.link_id ? <Loader2 className="w-3 h-3 animate-spin" /> : <UserCheck className="w-3 h-3" />}
                    Approve
                  </button>
                  <button
                    onClick={() => handleReject(req.link_id)}
                    disabled={actionLoading === req.link_id}
                    className="flex-1 py-1.5 bg-red-500 text-white rounded-lg text-xs font-medium hover:bg-red-600 transition-colors disabled:opacity-50 inline-flex items-center justify-center gap-1"
                  >
                    <UserX className="w-3 h-3" />
                    Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 text-center">
        {loading && !linkingCode ? (
          <div className="py-8">
            <Loader2 className="w-6 h-6 animate-spin text-navy-600 mx-auto" />
          </div>
        ) : linkingCode ? (
          <>
            <div className="w-14 h-14 rounded-full bg-navy-50 flex items-center justify-center mx-auto mb-4">
              <Users className="w-7 h-7 text-navy-700" />
            </div>
            <h2 className="text-sm font-medium text-slate-700 mb-3">Share this code with your parent</h2>

            <div className="bg-slate-50 rounded-xl p-4 mb-4 border-2 border-dashed border-navy-200">
              <p className="text-3xl font-bold font-mono tracking-[0.3em] text-navy-900 select-all">
                {linkingCode.code}
              </p>
            </div>

            <div className="flex items-center justify-center gap-2 mb-4">
              <Clock className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-xs text-slate-500">
                Expires in {expiresIn} hour{expiresIn !== 1 ? 's' : ''}
              </span>
            </div>

            <div className="space-y-2">
              <button onClick={handleCopy} className="btn-primary w-full inline-flex items-center justify-center gap-2">
                {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Code'}
              </button>
              <button onClick={generateCode} disabled={loading} className="w-full py-2.5 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-all text-sm font-medium inline-flex items-center justify-center gap-2">
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Generate New Code
              </button>
            </div>
          </>
        ) : (
          <div className="py-8">
            <p className="text-sm text-red-600 mb-3">Failed to generate code.</p>
            <button onClick={generateCode} className="btn-primary">
              Try Again
            </button>
          </div>
        )}
      </div>

      <div className="mt-6 bg-slate-50 rounded-xl border border-slate-200 p-4">
        <h3 className="text-sm font-medium text-slate-700 mb-2">How it works</h3>
        <ul className="text-xs text-slate-500 space-y-1.5">
          <li>1. Share the code above with your parent</li>
          <li>2. They enter it in their account to request linking</li>
          <li>3. You approve or reject the request here</li>
          <li>4. Once approved, they can view your progress, reports, and insights</li>
          <li>5. Codes expire after 48 hours for security</li>
          <li>6. You can have up to 2 linked parents</li>
        </ul>
      </div>
    </div>
  )
}
