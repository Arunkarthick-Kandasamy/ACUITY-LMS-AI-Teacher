import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authStore } from '@/store/authStore'
import { resetDb } from '@/services/localDb'
import { Trash2, AlertTriangle, CheckCircle } from 'lucide-react'

export function SettingsPage() {
  const navigate = useNavigate()
  const [confirming, setConfirming] = useState(false)
  const [done, setDone] = useState(false)

  const handleReset = () => {
    resetDb()
    localStorage.removeItem('acuity_current_user')
    localStorage.removeItem('acuity_xp')
    localStorage.removeItem('acuity_level')
    localStorage.removeItem('acuity_streak')
    localStorage.removeItem('acuity_last_active')
    authStore.logout()
    setDone(true)
    setTimeout(() => navigate('/login', { replace: true }), 1500)
  }

  return (
    <div className="max-w-lg mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your app preferences and data.</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="font-semibold text-slate-900 mb-1">Reset All Data</h2>
        <p className="text-sm text-slate-500 mb-4">Clear all local data, progress, and reset the database to its default state. This cannot be undone.</p>

        {done ? (
          <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 rounded-lg p-3">
            <CheckCircle className="w-5 h-5" />
            <span className="text-sm font-medium">Data reset! Redirecting to login...</span>
          </div>
        ) : confirming ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-700 mb-3">
              <AlertTriangle className="w-5 h-5" />
              <span className="text-sm font-semibold">Are you sure?</span>
            </div>
            <p className="text-xs text-red-600 mb-4">This will delete ALL your progress, XP, badges, and settings. You'll be logged out immediately.</p>
            <div className="flex gap-3">
              <button onClick={handleReset} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all text-sm font-medium">Yes, Reset Everything</button>
              <button onClick={() => setConfirming(false)} className="px-4 py-2 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-all text-sm font-medium">Cancel</button>
            </div>
          </div>
        ) : (
          <button onClick={() => setConfirming(true)} className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 text-red-700 border border-red-200 rounded-lg hover:bg-red-100 transition-all text-sm font-medium">
            <Trash2 className="w-4 h-4" /> Reset All Data
          </button>
        )}
      </div>
    </div>
  )
}
