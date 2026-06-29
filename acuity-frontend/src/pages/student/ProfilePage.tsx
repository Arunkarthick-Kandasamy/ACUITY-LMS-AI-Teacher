import { useState } from 'react'
import { authStore } from '@/store/authStore'
import { useNavigate } from 'react-router-dom'
import { apiRequest } from '@/services/api'
import { User, Mail, BookOpen, Calendar, Download, Trash2, Loader2, CheckCircle } from 'lucide-react'

export function ProfilePage() {
  const navigate = useNavigate()
  const user = authStore.user
  const [exporting, setExporting] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [deleteConfirmText, setDeleteConfirmText] = useState('')

  const handleExport = async () => {
    setExporting(true)
    try {
      const res = await apiRequest<any>('/api/v1/auth/export-data')
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `acuity-export-${user?.user_id || 'data'}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch { }
    setExporting(false)
  }

  const handleDelete = async () => {
    if (deleteConfirmText !== 'DELETE') return
    setDeleting(true)
    try {
      await apiRequest('/api/v1/auth/delete-account', { method: 'POST' })
      await authStore.logout()
      navigate('/')
    } catch { }
    setDeleting(false)
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">My Profile</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your learning preferences</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-slate-100">
          <div className="w-16 h-16 rounded-full bg-navy-800 flex items-center justify-center text-xl font-bold text-white">
            {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{user?.full_name || 'Student'}</h2>
            <p className="text-sm text-slate-500 capitalize">{user?.role || 'Student'}</p>
          </div>
        </div>

        <div className="space-y-4">
          {[
            { icon: User, label: 'Name', value: user?.full_name || 'N/A' },
            { icon: Mail, label: 'Email', value: user?.email || 'N/A' },
            { icon: BookOpen, label: 'Role', value: user?.role || 'N/A' },
            { icon: Calendar, label: 'Member Since', value: user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A' },
          ].map((item) => {
            const Icon = item.icon
            return (
              <div key={item.label} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-slate-500" />
                </div>
                <div className="flex-1">
                  <div className="text-xs text-slate-400">{item.label}</div>
                  <div className="text-sm font-medium text-slate-800 capitalize">{item.value}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Privacy & Data */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <h2 className="font-semibold text-slate-900 mb-4">Privacy & Data</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50">
            <div>
              <p className="text-sm font-medium text-slate-700">Export My Data</p>
              <p className="text-xs text-slate-400">Download all your data in JSON format (GDPR Right to Access)</p>
            </div>
            <button onClick={handleExport} disabled={exporting} className="px-3 py-2 bg-navy-800 text-white rounded-lg text-sm hover:bg-navy-700 disabled:opacity-50 inline-flex items-center gap-1">
              {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
              {exporting ? 'Exporting...' : 'Export'}
            </button>
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg bg-red-50 border border-red-100">
            <div>
              <p className="text-sm font-medium text-red-800">Delete Account</p>
              <p className="text-xs text-red-600">Permanently delete your account and all associated data</p>
            </div>
            <button onClick={() => setShowDeleteConfirm(true)} className="px-3 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 inline-flex items-center gap-1">
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-xl max-w-md w-full p-6">
            <Trash2 className="w-10 h-10 text-red-500 mx-auto mb-3" />
            <h2 className="text-lg font-semibold text-slate-900 text-center mb-2">Delete Account?</h2>
            <p className="text-sm text-slate-500 text-center mb-4">
              This action is permanent and cannot be undone. All your data will be deleted.
            </p>
            <p className="text-xs text-slate-400 text-center mb-4">
              Type <strong>DELETE</strong> to confirm.
            </p>
            <input
              type="text"
              value={deleteConfirmText}
              onChange={e => setDeleteConfirmText(e.target.value)}
              className="input-field text-center mb-4"
              placeholder="Type DELETE"
            />
            <div className="flex gap-3">
              <button onClick={() => { setShowDeleteConfirm(false); setDeleteConfirmText('') }} className="btn-secondary flex-1">Cancel</button>
              <button onClick={handleDelete} disabled={deleteConfirmText !== 'DELETE' || deleting} className="px-4 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:opacity-50 flex-1 text-sm font-medium">
                {deleting ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Delete Account'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
