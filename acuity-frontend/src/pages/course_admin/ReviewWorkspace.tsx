import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { getCourse, updateProfile, updateCourseStructure, runStage } from '@/services/courseAdmin'
import {
  Bot, Loader2, CheckCircle2, XCircle, ArrowLeft, Save,
  FileText, BookOpen, Users, Sparkles, AlertTriangle, ChevronRight,
  PanelLeft, PanelRight, Eye, Edit3,
} from 'lucide-react'
import type { AdminCourseDetail } from '@/services/types'

export function ReviewWorkspace() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: course, loading, refetch } = useAuthApi(() => getCourse(id!), [id])
  const [activeTab, setActiveTab] = useState<'structure' | 'content' | 'profile'>('structure')
  const [selectedModule, setSelectedModule] = useState<number | null>(null)
  const [selectedLesson, setSelectedLesson] = useState<number | null>(null)
  const [editorContent, setEditorContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [leftPanel, setLeftPanel] = useState(true)
  const [rightPanel, setRightPanel] = useState(true)
  const [editedFields, setEditedFields] = useState<Record<string, boolean>>({})

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-6 h-6 animate-spin text-blue-600" /></div>
  }

  if (!course) {
    return (
      <div className="text-center py-16">
        <Bot className="w-12 h-12 text-slate-200 mx-auto mb-3" />
        <p className="text-sm font-semibold text-slate-700">Course not found</p>
        <Link to="/course-admin/courses" className="text-xs text-blue-600 hover:underline mt-1 inline-block">Back</Link>
      </div>
    )
  }

  const reviewStage = course.stages.find(s => s.stage_name === 'review')
  const generateStage = course.stages.find(s => s.stage_name === 'generate')

  const handleSave = async () => {
    setSaving(true); setError('')
    try {
      if (activeTab === 'profile' && course.teaching_profile) {
        await updateProfile(course.id, course.teaching_profile)
      } else if (activeTab === 'structure' && course.course_structure) {
        await updateCourseStructure(course.id, course.course_structure)
      }
      await refetch()
      setEditedFields({})
    } catch (e: any) { setError(e.message) }
    finally { setSaving(false) }
  }

  const handleCompleteReview = async () => {
    try {
      await runStage(course.id, 'simulate')
      navigate(`/course-admin/courses/${course.id}`)
    } catch (e: any) { setError(e.message) }
  }

  const modules: any[] = (course.course_structure?.modules as any[]) || []
  const selectedMod = selectedModule != null ? modules[selectedModule] : null
  const selectedLess = selectedMod && selectedLesson != null ? (selectedMod.lessons || [])[selectedLesson] : null

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] -m-6 lg:-m-8">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-white border-b border-slate-200 shrink-0">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate(`/course-admin/courses/${course.id}`)} className="p-1 hover:bg-slate-100 rounded">
            <ArrowLeft className="w-4 h-4 text-slate-400" />
          </button>
          <div className="w-6 h-6 rounded bg-indigo-50 flex items-center justify-center">
            <Bot className="w-3 h-3 text-indigo-600" />
          </div>
          <div>
            <span className="text-xs font-semibold text-slate-800">{course.name}</span>
            <span className="text-[10px] text-slate-400 ml-2">Review Workspace</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex border border-slate-200 rounded overflow-hidden">
            <button onClick={() => setLeftPanel(!leftPanel)} className={`p-1.5 ${leftPanel ? 'bg-slate-100' : ''}`} title="Toggle tree"><PanelLeft className="w-3.5 h-3.5 text-slate-500" /></button>
            <button onClick={() => setRightPanel(!rightPanel)} className={`p-1.5 ${rightPanel ? 'bg-slate-100' : ''}`} title="Toggle preview"><PanelRight className="w-3.5 h-3.5 text-slate-500" /></button>
          </div>
          <div className="flex border border-slate-200 rounded overflow-hidden">
            <button onClick={() => setActiveTab('structure')} className={`px-2.5 py-1.5 text-[10px] ${activeTab === 'structure' ? 'bg-blue-50 text-blue-600' : 'text-slate-500 hover:bg-slate-50'}`}>Structure</button>
            <button onClick={() => setActiveTab('content')} className={`px-2.5 py-1.5 text-[10px] ${activeTab === 'content' ? 'bg-blue-50 text-blue-600' : 'text-slate-500 hover:bg-slate-50'}`}>Content</button>
            <button onClick={() => setActiveTab('profile')} className={`px-2.5 py-1.5 text-[10px] ${activeTab === 'profile' ? 'bg-blue-50 text-blue-600' : 'text-slate-500 hover:bg-slate-50'}`}>Profile</button>
          </div>
          <div className="flex items-center gap-1">
            {Object.keys(editedFields).length > 0 && (
              <button onClick={handleSave} disabled={saving}
                className="flex items-center gap-1 px-2.5 py-1.5 bg-blue-600 text-white rounded text-[10px] font-medium hover:bg-blue-700 disabled:opacity-50">
                {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
                Save
              </button>
            )}
            <button onClick={handleCompleteReview} className="flex items-center gap-1 px-2.5 py-1.5 bg-emerald-600 text-white rounded text-[10px] font-medium hover:bg-emerald-700">
              Complete Review <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

      {error && <div className="px-4 py-1.5 bg-red-50 border-b border-red-200 text-[10px] text-red-700">{error}</div>}

      {/* Main workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* LEFT TREE PANEL */}
        {leftPanel && (
          <div className="w-56 border-r border-slate-200 bg-white overflow-y-auto shrink-0">
            {activeTab === 'structure' && (
              <div className="p-3">
                <h3 className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide mb-2">Course Structure</h3>
                {modules.length === 0 ? (
                  <p className="text-[10px] text-slate-400 italic">No modules yet</p>
                ) : (
                  <div className="space-y-0.5">
                    {modules.map((mod, mi) => (
                      <div key={mi}>
                        <button onClick={() => { setSelectedModule(mi); setSelectedLesson(null); setEditorContent(JSON.stringify(mod, null, 2)) }}
                          className={`w-full text-left px-2 py-1.5 rounded text-[10px] ${selectedModule === mi ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-50'}`}>
                          <div className="font-medium truncate">{mod.title || `Module ${mi + 1}`}</div>
                          <div className="text-[9px] text-slate-400">{mod.lessons?.length || 0} lessons</div>
                        </button>
                        {selectedModule === mi && mod.lessons?.length > 0 && (
                          <div className="ml-3 mt-0.5 space-y-0.5 border-l border-slate-200 pl-2">
                            {(mod.lessons as any[]).map((l: any, li: number) => (
                              <button key={li} onClick={() => { setSelectedLesson(li); setEditorContent(JSON.stringify(l, null, 2)) }}
                                className={`w-full text-left px-2 py-1 rounded text-[10px] ${selectedLesson === li ? 'bg-blue-50 text-blue-700' : 'text-slate-500 hover:bg-slate-50'}`}>
                                {l.title || `Lesson ${li + 1}`}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'content' && (
              <div className="p-3">
                <h3 className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide mb-2">Generated Content</h3>
                {generateStage?.output_data ? (
                  <div className="space-y-1">
                    {Object.entries(generateStage.output_data).filter(([k]) => !['course_id'].includes(k)).map(([k, v]) => (
                      <button key={k} onClick={() => setEditorContent(JSON.stringify(v, null, 2))}
                        className="w-full text-left px-2 py-1.5 rounded text-[10px] text-slate-600 hover:bg-slate-50">
                        <span className="font-medium capitalize">{k.replace(/_/g, ' ')}</span>
                        <span className="text-[9px] text-slate-400 ml-1">({Array.isArray(v) ? v.length : typeof v === 'object' ? 'obj' : '1'})</span>
                      </button>
                    ))}
                  </div>
                ) : <p className="text-[10px] text-slate-400 italic">No content generated.</p>}
              </div>
            )}

            {activeTab === 'profile' && (
              <div className="p-3">
                <h3 className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide mb-2">Profile Fields</h3>
                {course.teaching_profile ? (
                  <div className="space-y-0.5">
                    {Object.keys(course.teaching_profile).map(k => (
                      <button key={k} onClick={() => setEditorContent(JSON.stringify((course.teaching_profile as any)[k], null, 2))}
                        className="w-full text-left px-2 py-1.5 rounded text-[10px] text-slate-600 hover:bg-slate-50">
                        <span className="font-medium capitalize">{k.replace(/_/g, ' ')}</span>
                      </button>
                    ))}
                  </div>
                ) : <p className="text-[10px] text-slate-400 italic">No profile data.</p>}
              </div>
            )}
          </div>
        )}

        {/* CENTER EDITOR */}
        <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
          {editorContent ? (
            <div className="flex-1 overflow-y-auto p-4">
              <textarea
                value={editorContent}
                onChange={e => { setEditorContent(e.target.value); setEditedFields(prev => ({ ...prev, editor: true })) }}
                className="w-full h-full min-h-[300px] font-mono text-[11px] p-3 border border-slate-200 rounded bg-white resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
              />
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-xs text-slate-400">
              <div className="text-center">
                <Edit3 className="w-8 h-8 text-slate-200 mx-auto mb-2" />
                <p>Select an item from the left panel to review and edit</p>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT PREVIEW PANEL */}
        {rightPanel && (
          <div className="w-64 border-l border-slate-200 bg-white overflow-y-auto shrink-0">
            {selectedLess ? (
              <div className="p-4">
                <h3 className="text-xs font-semibold text-slate-800 mb-2">{selectedLess.title || 'Lesson Preview'}</h3>
                <div className="text-[10px] text-slate-500 space-y-2">
                  {selectedLess.objectives?.length > 0 && (
                    <div>
                      <div className="font-medium text-slate-700 mb-0.5">Objectives</div>
                      <ul className="list-disc list-inside space-y-0.5">
                        {(selectedLess.objectives as string[]).map((o: string, i: number) => (
                          <li key={i}>{o}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedLess.content_preview && (
                    <div>
                      <div className="font-medium text-slate-700 mb-0.5">Content</div>
                      <p className="text-slate-500">{selectedLess.content_preview as string}</p>
                    </div>
                  )}
                  {selectedLess.estimated_duration_minutes && (
                    <div className="pt-2 border-t border-slate-100">
                      <span className="text-slate-400">Duration: </span>
                      <span className="text-slate-700">{selectedLess.estimated_duration_minutes} min</span>
                    </div>
                  )}
                </div>
              </div>
            ) : selectedMod ? (
              <div className="p-4">
                <h3 className="text-xs font-semibold text-slate-800 mb-2">{selectedMod.title || 'Module Preview'}</h3>
                <div className="text-[10px] text-slate-500 space-y-1">
                  {selectedMod.description && <p>{selectedMod.description}</p>}
                  <div className="pt-1">
                    <span className="text-slate-400">{selectedMod.lessons?.length || 0} lessons</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4">
                <h3 className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide mb-2">Preview</h3>
                <div className="flex items-center justify-center h-32 text-slate-300">
                  <Eye className="w-6 h-6" />
                </div>
              </div>
            )}

            {/* Validation status */}
            {reviewStage?.status === 'completed' && (
              <div className="mx-4 mb-4 p-2 rounded bg-emerald-50 border border-emerald-200">
                <div className="flex items-center gap-1 text-[10px] text-emerald-700">
                  <CheckCircle2 className="w-3 h-3" /> Review completed
                </div>
              </div>
            )}

            {reviewStage?.status === 'failed' && reviewStage?.error_message && (
              <div className="mx-4 mb-4 p-2 rounded bg-red-50 border border-red-200">
                <div className="flex items-start gap-1 text-[10px] text-red-700">
                  <XCircle className="w-3 h-3 shrink-0 mt-0.5" />{reviewStage.error_message}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
