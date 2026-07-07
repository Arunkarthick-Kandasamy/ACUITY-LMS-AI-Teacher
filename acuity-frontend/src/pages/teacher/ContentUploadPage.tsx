import { useState } from 'react'
import { Upload, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react'

export function ContentUploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<{ filename: string; status: string } | null>(null)
  const [error, setError] = useState('')

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    setResult(null)
    await new Promise(r => setTimeout(r, 1500))
    setResult({ filename: file.name, status: 'completed' })
    setUploading(false)
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
            <input type="file" accept=".pdf,.docx,.txt" onChange={e => setFile(e.target.files?.[0] || null)} className="block mx-auto text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-navy-50 file:text-navy-700 hover:file:bg-navy-100" />
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
            {result.status === 'completed' ? <CheckCircle className="w-6 h-6 text-emerald-500" /> : <XCircle className="w-6 h-6 text-red-500" />}
            <div>
              <p className="font-medium text-slate-900">{result.filename}</p>
              <p className="text-xs text-slate-400 capitalize">{result.status}</p>
            </div>
          </div>
          <button onClick={() => { setResult(null); setFile(null) }} className="text-sm text-navy-600 hover:text-navy-800">Upload another file</button>
        </div>
      )}
    </div>
  )
}
