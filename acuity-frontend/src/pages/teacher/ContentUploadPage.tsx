import { useState } from 'react'
import { apiRequest } from '@/services/api'
import { Upload, FileText, Loader2, CheckCircle, XCircle, Eye } from 'lucide-react'

export function ContentUploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ upload_id: string; filename: string; status: string } | null>(null)
  const [error, setError] = useState('')
  const [draft, setDraft] = useState<any>(null)
  const [polling, setPolling] = useState(false)

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    setResult(null)
    setDraft(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('http://localhost:8000/api/v1/content/upload', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        body: formData,
      })
      const json = await res.json()
      if (!res.ok) throw new Error(json.error?.message || 'Upload failed')
      setResult(json.data)

      // Poll for completion
      setPolling(true)
      const poll = setInterval(async () => {
        try {
          const pollRes = await apiRequest<any>(`/api/v1/content/jobs/${json.data.upload_id}`)
          if (pollRes.data.status === 'completed' || pollRes.data.status === 'failed') {
            clearInterval(poll)
            setPolling(false)
            if (pollRes.data.draft_id) {
              const draftRes = await apiRequest<any>(`/api/v1/content/drafts/${pollRes.data.draft_id}`)
              setDraft(draftRes.data)
            }
            setResult(prev => prev ? { ...prev, status: pollRes.data.status } : null)
          }
        } catch { clearInterval(poll); setPolling(false) }
      }, 2000)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Upload Content</h1>
        <p className="text-sm text-slate-500 mt-1">Upload PDF, DOCX, or TXT files to auto-generate curriculum.</p>
      </div>

      {!result && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center">
            <FileText className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500 mb-2">Drag and drop or click to browse</p>
            <p className="text-xs text-slate-400 mb-4">PDF, DOCX, or TXT up to 50MB</p>
            <input
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={e => setFile(e.target.files?.[0] || null)}
              className="block mx-auto text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-navy-50 file:text-navy-700 hover:file:bg-navy-100"
            />
          </div>
          {file && (
            <div className="mt-4 flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm text-slate-700">{file.name} ({(file.size / 1024).toFixed(0)} KB)</span>
              <button onClick={handleUpload} disabled={uploading} className="btn-primary text-sm disabled:opacity-50">
                {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          )}
          {error && <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700">{error}</div>}
        </div>
      )}

      {result && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex items-center gap-3 mb-4">
            {result.status === 'completed' ? <CheckCircle className="w-6 h-6 text-emerald-500" /> : polling ? <Loader2 className="w-5 h-5 animate-spin text-navy-600" /> : <XCircle className="w-6 h-6 text-red-500" />}
            <div>
              <p className="font-medium text-slate-900">{result.filename}</p>
              <p className="text-xs text-slate-400 capitalize">{result.status}{polling ? ' - Processing...' : ''}</p>
            </div>
          </div>

          {draft && (
            <div className="border-t border-slate-200 pt-4 mt-4">
              <h3 className="font-medium text-slate-900 mb-2">Generated Curriculum Draft</h3>
              <p className="text-sm text-slate-600 mb-3">{draft.title || 'Untitled Curriculum'}</p>
              {draft.curriculum?.modules?.map((mod: any, i: number) => (
                <div key={i} className="mb-3 p-3 bg-slate-50 rounded-lg">
                  <p className="text-sm font-medium text-slate-700">{mod.title || `Module ${i + 1}`}</p>
                  {mod.lessons?.map((less: any, j: number) => (
                    <p key={j} className="text-xs text-slate-500 ml-4 mt-1">• {less.title}</p>
                  ))}
                </div>
              ))}
              <div className="flex gap-2 mt-4">
                <button className="px-4 py-2 bg-navy-800 text-white rounded-lg text-sm hover:bg-navy-700">Approve & Publish</button>
                <button className="px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-600 hover:bg-slate-50">Edit Draft</button>
              </div>
            </div>
          )}
        </div>
      )}

      {result && !polling && result.status !== 'completed' && result.status !== 'failed' && (
        <button onClick={() => { setResult(null); setFile(null) }} className="text-sm text-navy-600 hover:text-navy-800">
          Upload another file
        </button>
      )}
    </div>
  )
}
