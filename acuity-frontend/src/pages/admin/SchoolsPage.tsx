import { useState, useEffect } from 'react'
import { apiRequest } from '@/services/api'
import { mockSchools } from './admin-mock-data'
import { Loader2, Plus, CheckCircle2, XCircle, Globe } from 'lucide-react'
import { cn } from '@/lib/utils'

interface School {
  id: string
  name: string
  code: string
  address: string | null
  phone: string | null
  is_active: boolean
  domains: string[]
}

export default function SchoolsPage() {
  const [schools, setSchools] = useState<School[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', code: '', address: '', phone: '', domains: '' })

  useEffect(() => {
    apiRequest('/institutional/schools')
      .then((res: any) => setSchools(res?.data || []))
      .catch(() => setSchools(mockSchools))
      .finally(() => setLoading(false))
  }, [])

  const createSchool = async () => {
    try {
      await apiRequest('/institutional/schools', {
        method: 'POST',
        body: JSON.stringify({
          ...form,
          domains: form.domains.split(',').map((d) => d.trim()).filter(Boolean),
        }),
      })
    } catch {}
    setShowForm(false)
    setForm({ name: '', code: '', address: '', phone: '', domains: '' })
    const res: any = await apiRequest('/institutional/schools').catch(() => ({ data: mockSchools }))
    setSchools(res?.data || mockSchools)
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Schools</h1>
          <p className="text-sm text-gray-500 mt-1">Manage institutional partners and school accounts.</p>
        </div>
        <button onClick={() => setShowForm(!showForm)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all text-sm font-medium shadow-sm">
          <Plus className="w-4 h-4" /> {showForm ? 'Cancel' : 'Add School'}
        </button>
      </div>

      {showForm && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Add New School</h2>
          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">School Name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="e.g. Delhi Public School" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">School Code</label>
              <input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="e.g. DPS_RK" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Address</label>
              <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="e.g. RK Puram, New Delhi" />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500 mb-1 block">Phone</label>
              <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="e.g. +91-11-45678901" />
            </div>
          </div>
          <div className="mb-4">
            <label className="text-xs font-medium text-gray-500 mb-1 block">Domains (comma-separated)</label>
            <input value={form.domains} onChange={(e) => setForm({ ...form, domains: e.target.value })}
              className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
              placeholder="e.g. dpsrkp.edu, dpsdelhi.edu" />
          </div>
          <button onClick={createSchool} disabled={!form.name || !form.code}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-all text-sm font-medium">
            Create School
          </button>
        </div>
      )}

      <div className="grid sm:grid-cols-2 gap-4">
        {schools.length === 0 ? (
          <div className="col-span-2 bg-white rounded-xl border border-gray-200 p-8 text-center">
            <Globe className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-sm text-gray-400">No schools found</p>
          </div>
        ) : (
          schools.map((s) => (
            <div key={s.id} className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm hover:shadow-md transition-all">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900">{s.name}</h3>
                  <p className="text-xs text-gray-400 mt-0.5">Code: {s.code}</p>
                </div>
                <span className={cn('inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium', s.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600')}>
                  {s.is_active ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                  {s.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              {s.address && <p className="text-xs text-gray-500 mb-1">{s.address}</p>}
              {s.phone && <p className="text-xs text-gray-500 mb-2">{s.phone}</p>}
              {s.domains.length > 0 && (
                <div className="flex gap-1.5 flex-wrap mt-2">
                  {s.domains.map((d) => (
                    <span key={d} className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-50 border border-gray-100 rounded text-[10px] text-gray-500">
                      <Globe className="w-3 h-3" /> {d}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
