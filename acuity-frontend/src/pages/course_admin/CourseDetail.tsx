import { useState } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { getCourse, deleteCourse, runStage } from '@/services/courseAdmin'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  Bot, Loader2, CheckCircle2, XCircle, AlertCircle, Clock, Brain,
  Upload, FileText, BookOpen, Users, Sparkles, Play, ShieldCheck,
  ArrowLeft, Edit3, Trash2, ExternalLink, ChevronRight, AlertTriangle,
  Info, BarChart3, Layers, GitBranch, Settings, Activity,
  GraduationCap, ClipboardCheck,
} from 'lucide-react'
import type { PipelineStageInfo } from '@/services/types'
import { STAGE_LABELS, STAGE_ORDER } from '@/services/types'

const stageMeta: Record<string, { icon: typeof Bot; color: string; bg: string }> = {
  upload: { icon: Upload, color: 'text-blue-600', bg: 'bg-blue-50' },
  extract: { icon: FileText, color: 'text-purple-600', bg: 'bg-purple-50' },
  understand: { icon: Brain, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  validate: { icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  profile: { icon: Users, color: 'text-amber-600', bg: 'bg-amber-50' },
  structure: { icon: BookOpen, color: 'text-orange-600', bg: 'bg-orange-50' },
  generate: { icon: Sparkles, color: 'text-pink-600', bg: 'bg-pink-50' },
  review: { icon: ShieldCheck, color: 'text-teal-600', bg: 'bg-teal-50' },
  simulate: { icon: Play, color: 'text-cyan-600', bg: 'bg-cyan-50' },
  deploy: { icon: Bot, color: 'text-emerald-600', bg: 'bg-emerald-50' },
}

const TABS = [
  { key: 'overview', label: 'Overview', icon: Info },
  { key: 'curriculum', label: 'Curriculum', icon: BookOpen },
  { key: 'sources', label: 'Sources', icon: FileText },
  { key: 'pipeline', label: 'Processing', icon: Layers },
  { key: 'analytics', label: 'Analytics', icon: BarChart3 },
  { key: 'settings', label: 'Settings', icon: Settings },
]

function fmtDur(sec?: number | null) {
  if (!sec && sec !== 0) return '—'
  if (sec < 60) return `${sec}s`
  return `${Math.floor(sec / 60)}m ${sec % 60}s`
}

export function CourseDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: course, loading, refetch } = useAuthApi(() => getCourse(id!), [id])
  const [activeTab, setActiveTab] = useState('overview')
  const [expandedStage, setExpandedStage] = useState<string | null>(null)

  const handleDelete = async () => {
    if (!confirm(`Delete "${course?.name}"? This cannot be undone.`)) return
    try { await deleteCourse(course!.id); navigate('/course-admin/courses') }
    catch { alert('Failed to delete') }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-5 h-5 animate-spin text-blue-600" /></div>
  }

  if (!course) {
    return (
      <div className="text-center py-16">
        <Bot className="w-12 h-12 text-slate-200 mx-auto mb-3" />
        <p className="text-sm font-semibold text-slate-700">Course not found</p>
        <Link to="/course-admin/courses" className="text-[10px] text-blue-600 hover:underline mt-1 inline-block">Back to Courses</Link>
      </div>
    )
  }

  const completed = course.stages.filter(s => s.status === 'completed').length
  const total = course.stages.length
  const pct = total > 0 ? Math.round((completed / total) * 100) : 0

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/course-admin/courses')} className="p-1.5 hover:bg-slate-100 rounded">
            <ArrowLeft className="w-4 h-4 text-slate-400" />
          </button>
          <div className="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center">
            <GraduationCap className="w-4 h-4 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-slate-900">{course.name}</h1>
            <div className="flex items-center gap-3 text-[10px] text-slate-400 mt-0.5">
              <span className="capitalize">{course.status}</span>
              <span>{completed}/{total} stages</span>
              <span>{new Date(course.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/course-admin/create?edit=${course.id}`} className="flex items-center gap-1 px-2.5 py-1.5 border border-slate-200 rounded text-[10px] text-slate-600 hover:bg-slate-50">
            <Edit3 className="w-3 h-3" />Edit
          </Link>
          {course.status !== 'deployed' && (
            <button onClick={handleDelete} className="flex items-center gap-1 px-2.5 py-1.5 border border-red-200 rounded text-[10px] text-red-600 hover:bg-red-50">
              <Trash2 className="w-3 h-3" />Delete
            </button>
          )}
          {course.course_id && (
            <Link to="/course-admin/courses" className="flex items-center gap-1 px-2.5 py-1.5 bg-emerald-50 text-emerald-700 rounded text-[10px] hover:bg-emerald-100">
              <ExternalLink className="w-3 h-3" />View Published
            </Link>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-4">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide">Course Progress</h2>
          <Link to={`/course-admin/create?edit=${course.id}`} className="text-[10px] text-blue-600 hover:underline flex items-center gap-0.5">
            Continue Training <ChevronRight className="w-3 h-3" />
          </Link>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-2 mb-3">
          <div className={`h-2 rounded-full transition-all ${pct === 100 ? 'bg-emerald-400' : 'bg-blue-500'}`} style={{ width: `${pct}%` }} />
        </div>
        <div className="flex items-center gap-0.5">
          {STAGE_ORDER.map(key => {
            const s = course.stages.find(st => st.stage_name === key)
            const map: Record<string, string> = {
              completed: 'bg-emerald-400', in_progress: 'bg-blue-400 animate-pulse',
              failed: 'bg-red-400', pending: 'bg-slate-200',
            }
            return <div key={key} className={`flex-1 h-1.5 rounded-sm ${map[s?.status || 'pending']}`} title={`${STAGE_LABELS[key]}: ${s?.status || 'pending'}`} />
          })}
        </div>
        <div className="flex items-center justify-between mt-1.5 text-[9px] text-slate-400">
          <span>{course.status === 'deployed' ? 'Published' : course.status}</span>
          <span>{completed}/{total} stages complete</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
        <div className="flex border-b border-slate-100 overflow-x-auto">
          {TABS.map(t => (
            <button key={t.key} onClick={() => setActiveTab(t.key)}
              className={`flex items-center gap-1.5 px-3 py-2 text-[10px] font-medium whitespace-nowrap transition-colors ${activeTab === t.key ? 'text-blue-600 border-b-2 border-blue-500' : 'text-slate-500 hover:text-slate-700'}`}>
              <t.icon className="w-3 h-3" />{t.label}
            </button>
          ))}
        </div>

        <div className="p-4">
          {/* Overview */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-3 gap-4">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Knowledge Sources</div>
                <div className="text-lg font-semibold text-slate-800">{course.knowledge_sources.length}</div>
                <div className="text-[10px] text-slate-400">{course.knowledge_sources.filter(s => s.status === 'extracted').length} extracted</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Concepts</div>
                <div className="text-lg font-semibold text-slate-800">{(course.knowledge_graph_data?.concepts as any[])?.length || 0}</div>
                <div className="text-[10px] text-slate-400">from knowledge graph</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Status</div>
                <div className="text-lg font-semibold text-slate-800 capitalize">{course.status}</div>
                <div className="text-[10px] text-slate-400">{course.course_id ? 'Published' : 'Not published'}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Teaching Style</div>
                <div className="text-sm font-semibold text-slate-800 capitalize">{course.teaching_profile?.teaching_style as string || '—'}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Modules</div>
                <div className="text-lg font-semibold text-slate-800">{(course.course_structure?.modules as any[])?.length || 0}</div>
              </div>
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-1">Effectiveness</div>
                <div className="text-lg font-semibold text-slate-800">{course.simulation_results ? `${Math.round(((course.simulation_results.estimated_effectiveness as number) || 0) * 100)}%` : '—'}</div>
              </div>
            </div>
          )}

          {/* Curriculum */}
          {activeTab === 'curriculum' && (
            <div>
              {course.course_structure ? (
                <div>
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    <div className="p-3 rounded bg-orange-50 border border-orange-100">
                      <div className="text-[10px] text-orange-500 uppercase tracking-wide">Title</div>
                      <div className="text-xs font-semibold text-slate-800 mt-0.5">{course.course_structure.title as string}</div>
                    </div>
                    <div className="p-3 rounded bg-orange-50 border border-orange-100">
                      <div className="text-[10px] text-orange-500 uppercase tracking-wide">Modules</div>
                      <div className="text-xs font-semibold text-slate-800 mt-0.5">{(course.course_structure.modules as any[])?.length || 0}</div>
                    </div>
                    <div className="p-3 rounded bg-orange-50 border border-orange-100">
                      <div className="text-[10px] text-orange-500 uppercase tracking-wide">Duration</div>
                      <div className="text-xs font-semibold text-slate-800 mt-0.5">{course.course_structure.total_duration_hours as string || '—'} hrs</div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {((course.course_structure.modules || []) as any[]).map((mod: any, i: number) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-medium text-slate-700">{mod.title || `Module ${i + 1}`}</span>
                          <span className="text-[10px] text-slate-400">{mod.lessons?.length || 0} lessons</span>
                        </div>
                        {mod.lessons?.length > 0 && (
                          <div className="mt-1.5 flex flex-wrap gap-1">
                            {(mod.lessons as any[]).map((l: any, li: number) => (
                              <span key={li} className="text-[9px] px-1.5 py-0.5 rounded bg-white border border-slate-200 text-slate-500">{l.title || l}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : <p className="text-xs text-slate-400 italic">Curriculum not yet generated. Run the pipeline to generate.</p>}
            </div>
          )}

          {/* Sources */}
          {activeTab === 'sources' && (
            <div>
              {course.knowledge_sources.length > 0 ? (
                <div className="space-y-1">
                  {course.knowledge_sources.map(s => (
                    <div key={s.id} className="flex items-center gap-2.5 p-2.5 rounded bg-slate-50 border border-slate-100">
                      <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-medium text-slate-700 truncate">{s.filename}</div>
                        <div className="text-[10px] text-slate-400">{(s.file_size / 1024).toFixed(0)} KB</div>
                      </div>
                      <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${s.status === 'extracted' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{s.status}</span>
                    </div>
                  ))}
                </div>
              ) : <p className="text-xs text-slate-400 italic">No knowledge sources uploaded.</p>}
            </div>
          )}

          {/* Processing Pipeline */}
          {activeTab === 'pipeline' && (
            <div className="space-y-1">
              {STAGE_ORDER.map(key => {
                const stage = course.stages.find(s => s.stage_name === key)
                if (!stage) return null
                const meta = stageMeta[key]
                const Icon = meta.icon
                const isExpanded = expandedStage === key
                const isActive = stage.status === 'in_progress'
                const isCompleted = stage.status === 'completed'
                const isFailed = stage.status === 'failed'

                return (
                  <div key={key} className={`border rounded-lg transition-colors ${isCompleted ? 'border-emerald-200' : isActive ? 'border-blue-200 bg-blue-50/30' : isFailed ? 'border-red-200 bg-red-50/30' : 'border-slate-200'}`}>
                    <div className="flex items-center gap-2.5 px-3 py-2 cursor-pointer" onClick={() => setExpandedStage(isExpanded ? null : key)}>
                      <div className="relative">
                        {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
                        {isActive && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
                        {isFailed && <XCircle className="w-4 h-4 text-red-500" />}
                        {stage.status === 'pending' && <div className="w-4 h-4 rounded-full border-2 border-slate-300" />}
                      </div>
                      <div className={`w-6 h-6 rounded ${meta.bg} flex items-center justify-center shrink-0`}>
                        <Icon className={`w-3.5 h-3.5 ${meta.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-medium text-slate-800">{STAGE_LABELS[key] || key}</div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className={`text-[10px] ${isFailed ? 'text-red-500' : isCompleted ? 'text-emerald-600' : 'text-slate-400'}`}>
                            {stage.status.replace(/_/g, ' ')}
                          </span>
                          {stage.duration_seconds != null && <span className="text-[10px] text-slate-400"><Clock className="w-3 h-3 inline mr-0.5" />{fmtDur(stage.duration_seconds)}</span>}
                          {stage.retry_count ? <span className="text-[10px] text-slate-400">retry #{stage.retry_count}</span> : null}
                        </div>
                      </div>
                      {stage.progress_pct > 0 && stage.progress_pct < 100 && (
                        <div className="w-12 bg-slate-200 rounded-full h-1.5">
                          <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${stage.progress_pct}%` }} />
                        </div>
                      )}
                    </div>

                    {isExpanded && (
                      <div className="px-3 pb-3 border-t border-slate-100 pt-2 text-xs space-y-2">
                        {stage.error_message && (
                          <div className="p-2 rounded bg-red-50 border border-red-200 text-red-700 flex items-start gap-1 text-[10px]">
                            <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />{stage.error_message}
                          </div>
                        )}
                        {stage.stage_logs && stage.stage_logs.length > 0 && (
                          <div>
                            <div className="text-[9px] font-medium text-slate-500 uppercase tracking-wide mb-1">Logs</div>
                            <div className="max-h-32 overflow-y-auto space-y-0.5 bg-slate-50 p-2 rounded">
                              {stage.stage_logs.map((log, li) => (
                                <div key={li} className="text-[10px] text-slate-600 flex items-start gap-1.5">
                                  <span className="text-[9px] text-slate-400 shrink-0 font-mono">{log.ts?.split('T')[1]?.slice(0, 8) || ''}</span>
                                  {log.level === 'error' && <XCircle className="w-3 h-3 text-red-400 shrink-0 mt-0.5" />}
                                  {log.level === 'warning' && <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />}
                                  <span>{log.message}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}

          {/* Analytics */}
          {activeTab === 'analytics' && (
            <div className="grid grid-cols-2 gap-4">
              {course.knowledge_graph_data && (
                <div className="p-4 rounded-lg bg-indigo-50 border border-indigo-100">
                  <h3 className="text-[10px] font-semibold text-indigo-700 uppercase tracking-wide mb-3">Knowledge Graph</h3>
                  <div className="text-[10px] text-indigo-600 space-y-2">
                    <div className="flex justify-between"><span>Domain</span><span className="font-medium text-slate-700">{course.knowledge_graph_data.subject_domain as string || '—'}</span></div>
                    <div className="flex justify-between"><span>Grade Level</span><span className="font-medium text-slate-700">{course.knowledge_graph_data.estimated_grade_level as string || '—'}</span></div>
                    <div className="flex justify-between"><span>Concepts</span><span className="font-medium text-slate-700">{(course.knowledge_graph_data.concepts as any[])?.length || 0}</span></div>
                    <div className="flex justify-between"><span>Relationships</span><span className="font-medium text-slate-700">{(course.knowledge_graph_data.relationships as any[])?.length || 0}</span></div>
                  </div>
                </div>
              )}
              {course.teaching_profile && (
                <div className="p-4 rounded-lg bg-amber-50 border border-amber-100">
                  <h3 className="text-[10px] font-semibold text-amber-700 uppercase tracking-wide mb-3">Teaching Profile</h3>
                  <div className="text-[10px] text-amber-600 space-y-2">
                    <div className="flex justify-between"><span>Style</span><span className="font-medium text-slate-700 capitalize">{course.teaching_profile.teaching_style as string}</span></div>
                    <div className="flex justify-between"><span>Depth</span><span className="font-medium text-slate-700 capitalize">{course.teaching_profile.explanation_depth as string}</span></div>
                    <div className="flex justify-between"><span>Assessment</span><span className="font-medium text-slate-700 capitalize">{course.teaching_profile.assessment_style as string}</span></div>
                    <div className="flex justify-between"><span>Difficulty Curve</span><span className="font-medium text-slate-700">{course.teaching_profile.difficulty_curve as number}/5</span></div>
                  </div>
                </div>
              )}
              {course.simulation_results && (
                <div className="p-4 rounded-lg bg-cyan-50 border border-cyan-100">
                  <h3 className="text-[10px] font-semibold text-cyan-700 uppercase tracking-wide mb-3">Simulation</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Effectiveness', value: (course.simulation_results.estimated_effectiveness as number || 0) * 100, color: 'bg-emerald-500' },
                      { label: 'Engagement', value: (course.simulation_results.engagement_score as number || 0) * 100, color: 'bg-blue-500' },
                      { label: 'Clarity', value: (course.simulation_results.clarity_score as number || 0) * 100, color: 'bg-purple-500' },
                    ].map(m => (
                      <div key={m.label}>
                        <div className="flex justify-between text-[10px] mb-0.5"><span className="text-slate-500">{m.label}</span><span className="font-medium text-slate-700">{Math.round(m.value)}%</span></div>
                        <div className="w-full bg-slate-200 rounded-full h-1.5">
                          <div className={`${m.color} h-1.5 rounded-full`} style={{ width: `${m.value}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {course.knowledge_sources.length > 0 && (
                <div className="p-4 rounded-lg bg-purple-50 border border-purple-100">
                  <h3 className="text-[10px] font-semibold text-purple-700 uppercase tracking-wide mb-3">Content Stats</h3>
                  <div className="text-[10px] text-purple-600 space-y-2">
                    <div className="flex justify-between"><span>Sources</span><span className="font-medium text-slate-700">{course.knowledge_sources.length}</span></div>
                    <div className="flex justify-between"><span>Extracted</span><span className="font-medium text-slate-700">{course.knowledge_sources.filter(s => s.status === 'extracted').length}</span></div>
                    <div className="flex justify-between"><span>Total Size</span><span className="font-medium text-slate-700">{(course.knowledge_sources.reduce((a, s) => a + s.file_size, 0) / 1024).toFixed(0)} KB</span></div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Settings */}
          {activeTab === 'settings' && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
                <h3 className="text-[10px] font-semibold text-slate-700 uppercase tracking-wide mb-3">Course Details</h3>
                <div className="text-xs space-y-2">
                  <div className="flex justify-between"><span className="text-slate-500">Name</span><span className="text-slate-700 font-medium">{course.name}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Description</span><span className="text-slate-700">{course.description || '—'}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Status</span><span className="text-slate-700 capitalize">{course.status}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Created</span><span className="text-slate-700">{new Date(course.created_at).toLocaleDateString()}</span></div>
                  <div className="flex justify-between"><span className="text-slate-500">Updated</span><span className="text-slate-700">{new Date(course.updated_at).toLocaleDateString()}</span></div>
                </div>
              </div>
              {course.course_id && (
                <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  <div>
                    <span className="text-xs font-medium text-emerald-800">Published</span>
                    <span className="text-[10px] text-emerald-600 ml-2">This course is published and available.</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
