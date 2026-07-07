import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Link2, ArrowRight, CheckCircle, Loader2, Clock, Mail } from 'lucide-react'
import { linkStudent } from '@/services/parent'

export function LinkStudentPage() {
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [parentEmail, setParentEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState<{ link_id: string; student_id: string; full_name: string; status: string; message: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await linkStudent(code.toUpperCase(), parentEmail || undefined)
      setSuccess(res.data)
    } catch (err: any) {
      setError(err.message || 'Invalid or expired linking code.')
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="max-w-lg mx-auto mt-12 text-center">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
          {success.status === 'pending' ? (
            <>
              <Clock className="w-12 h-12 text-amber-500 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-slate-900 mb-2">Request Sent!</h2>
              <p className="text-sm text-slate-600 mb-6">Your link request has been sent to <strong>{success.full_name}</strong>. They need to <strong>approve</strong> the request from their Parent Access settings before you can view their progress.</p>
            </>
          ) : (
            <>
              <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-slate-900 mb-2">Student Linked!</h2>
              <p className="text-sm text-slate-600 mb-6">You are now linked to <strong>{success.full_name}</strong>. You can view their progress and reports.</p>
            </>
          )}
          <div className="space-y-2">
            <button onClick={() => navigate('/parent/dashboard')} className="btn-primary w-full">Go to Dashboard</button>
            <button onClick={() => { setSuccess(null); setCode(''); setParentEmail('') }} className="w-full py-2.5 border border-slate-300 text-slate-700 rounded-xl hover:bg-slate-50 transition-all text-sm font-medium">Link Another Student</button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-lg mx-auto mt-8">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-slate-900">Link a Student</h1>
        <p className="text-sm text-slate-500 mt-1">Enter the 8-character code from your student's Parent Access settings to request linking.</p>
      </div>
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        {error && <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Linking Code</label>
            <input type="text" value={code} onChange={(e) => setCode(e.target.value.toUpperCase().slice(0, 8))} className="w-full px-4 py-3 text-lg font-mono text-center tracking-widest rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-navy-800/20 focus:border-navy-800" placeholder="XXXXXXXX" maxLength={8} required autoComplete="off" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Your Email (optional)</label>
            <input type="email" value={parentEmail} onChange={(e) => setParentEmail(e.target.value)} className="w-full px-4 py-3 rounded-xl border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-navy-800/20 focus:border-navy-800" placeholder="parent@example.com" autoComplete="email" />
            <p className="text-[10px] text-slate-400 mt-1">Your email helps the student identify who is requesting access.</p>
          </div>
          <button type="submit" disabled={loading || code.length < 8} className="btn-primary w-full disabled:opacity-50 inline-flex items-center justify-center gap-2">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link2 className="w-4 h-4" />}
            {loading ? 'Sending Request...' : 'Request to Link'}
          </button>
        </form>
      </div>
      <div className="mt-6 bg-slate-50 rounded-xl border border-slate-200 p-4">
        <h3 className="text-sm font-medium text-slate-700 mb-2">Two-step linking process</h3>
        <ul className="text-xs text-slate-500 space-y-1.5">
          <li>1. Enter the code from your student's Parent Access page</li>
          <li>2. We send a link request to the student</li>
          <li>3. They must approve the request in their account</li>
          <li>4. Once approved, you can view their progress</li>
          <li>5. Codes expire after 48 hours for security</li>
        </ul>
      </div>
    </div>
  )
}
