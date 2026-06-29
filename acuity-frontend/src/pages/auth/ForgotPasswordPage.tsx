import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, ArrowLeft, Mail, CheckCircle } from 'lucide-react'
import { apiRequest } from '@/services/api'

export function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await apiRequest('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
      })
      setSent(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (sent) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8">
            <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
            <h1 className="text-xl font-semibold text-slate-900 mb-2">Check your email</h1>
            <p className="text-sm text-slate-600 mb-6">
              If an account exists for <strong>{email}</strong>, we've sent a password reset link.
            </p>
            <button onClick={() => navigate('/login')} className="text-sm text-navy-700 hover:text-navy-900 font-medium">
              ← Back to sign in
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <GraduationCap className="w-8 h-8 text-navy-800" />
            <span className="text-2xl font-bold text-navy-800">Acuity</span>
          </div>
          <h1 className="text-xl font-semibold text-slate-900">Reset your password</h1>
          <p className="text-sm text-slate-500 mt-1">
            Enter your email and we'll send you a reset link.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">{error}</div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-navy-800/20 focus:border-navy-800"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-50">
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        </div>

        <p className="text-center mt-6">
          <button onClick={() => navigate('/login')} className="inline-flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600">
            <ArrowLeft className="w-3 h-3" />
            Back to sign in
          </button>
        </p>
      </div>
    </div>
  )
}
