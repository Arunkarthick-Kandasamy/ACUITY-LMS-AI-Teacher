import { useState, useEffect } from 'react'
import { apiRequest } from '@/services/api'
import { mockConcepts, mockPrereqs } from './admin-mock-data'
import { Loader2, Plus, Trash2, Search } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Concept {
  concept_id: string
  lesson_id: string
  title: string
  order_index: number
}

interface PrerequisiteEdge {
  edge_id: string
  prerequisite_id: string
  prerequisite_title?: string
}

export function KnowledgeGraphPage() {
  const [concepts, setConcepts] = useState<Concept[]>([])
  const [prereqs, setPrereqs] = useState<Map<string, PrerequisiteEdge[]>>(new Map())
  const [selectedConcept, setSelectedConcept] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [prereqId, setPrereqId] = useState('')

  useEffect(() => {
    apiRequest<{ data: Concept[] }>('/api/v1/curriculum/concepts?per_page=500')
      .then(res => setConcepts(Array.isArray(res.data) ? res.data : []))
      .catch(() => setConcepts(mockConcepts))
      .finally(() => setLoading(false))
  }, [])

  const loadPrereqs = async (conceptId: string) => {
    if (mockPrereqs[conceptId]) {
      setPrereqs(prev => new Map(prev).set(conceptId, mockPrereqs[conceptId]))
      return
    }
    try {
      const res = await apiRequest<{ data: { prerequisites: PrerequisiteEdge[] } }>(`/api/v1/knowledge-graph/concepts/${conceptId}/prerequisites`)
      const edges = res.data.prerequisites.map(p => ({ ...p, edge_id: p.edge_id || '' }))
      setPrereqs(prev => new Map(prev).set(conceptId, edges))
    } catch {
      setPrereqs(prev => new Map(prev).set(conceptId, []))
    }
  }

  const handleSelect = (id: string) => {
    setSelectedConcept(id)
    if (!prereqs.has(id)) loadPrereqs(id)
  }

  const addEdge = async () => {
    if (!selectedConcept || !prereqId) return
    try {
      await apiRequest('/api/v1/knowledge-graph/edges', {
        method: 'POST',
        body: JSON.stringify({ concept_id: selectedConcept, prerequisite_id: prereqId }),
      })
      setPrereqId('')
      loadPrereqs(selectedConcept)
    } catch {
      const concept = concepts.find(c => c.concept_id === prereqId)
      setPrereqs(prev => {
        const existing = prev.get(selectedConcept) || []
        return new Map(prev).set(selectedConcept, [...existing, {
          edge_id: `edge_${Date.now()}`,
          prerequisite_id: prereqId,
          prerequisite_title: concept?.title || prereqId,
        }])
      })
      setPrereqId('')
    }
  }

  const deleteEdge = async (edgeId: string) => {
    try {
      await apiRequest(`/api/v1/knowledge-graph/edges/${edgeId}`, { method: 'DELETE' })
    } catch {}
    if (selectedConcept) {
      setPrereqs(prev => {
        const existing = (prev.get(selectedConcept) || []).filter(e => e.edge_id !== edgeId)
        return new Map(prev).set(selectedConcept, existing)
      })
    }
  }

  const filtered = concepts.filter(c => c.title.toLowerCase().includes(search.toLowerCase()))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900">Knowledge Graph</h1>
        <p className="text-sm text-gray-500 mt-1">Manage concept prerequisites and learning dependencies.</p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-3">Concepts</h2>
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input type="text" value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
              placeholder="Search concepts..." />
          </div>
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-5 h-5 animate-spin text-blue-500" /></div>
          ) : (
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {filtered.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">No concepts found</p>
              ) : (
                filtered.map(c => (
                  <button key={c.concept_id} onClick={() => handleSelect(c.concept_id)}
                    className={cn('w-full text-left px-3 py-2 rounded-lg text-sm transition-all', selectedConcept === c.concept_id ? 'bg-gray-900 text-white' : 'hover:bg-gray-100 text-gray-700')}>
                    <span className="text-xs text-gray-400 mr-2">#{c.order_index}</span>
                    {c.title}
                  </button>
                ))
              )}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-3">Prerequisites</h2>
          {selectedConcept ? (
            <>
              <div className="flex gap-2 mb-4">
                <input type="text" value={prereqId} onChange={e => setPrereqId(e.target.value)}
                  className="flex-1 px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                  placeholder="Prerequisite concept ID..." />
                <button onClick={addEdge} disabled={!prereqId}
                  className="inline-flex items-center gap-2 px-3 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-all text-sm">
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              <div className="space-y-2">
                {(prereqs.get(selectedConcept) || []).length === 0 ? (
                  <p className="text-sm text-gray-400 text-center py-4">No prerequisites set for this concept.</p>
                ) : (
                  prereqs.get(selectedConcept)?.map((e: PrerequisiteEdge) => (
                    <div key={e.edge_id || e.prerequisite_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <span className="text-sm text-gray-700">{e.prerequisite_title || e.prerequisite_id}</span>
                        <span className="text-[10px] text-gray-400 ml-2">{e.prerequisite_id}</span>
                      </div>
                      <button onClick={() => deleteEdge(e.edge_id)} className="text-red-400 hover:text-red-600 transition-colors p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center py-12">
              <p className="text-sm text-gray-400">Select a concept to manage its prerequisites.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
