import { useState, useCallback, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload, FileText, Loader2, CheckCircle2, XCircle,
  ChevronRight, AlertCircle, Brain, BookOpen, Users, Play,
  ShieldCheck, Sparkles, Clock, AlertTriangle,
  Info, Eye, Edit3, Settings, Bot,
  CheckCircle, Lightbulb, HelpCircle, Clock3, FileType,
  Layers, BarChart3, ArrowRight,
} from 'lucide-react'
import {
  createCourse, getCourse,
  uploadKnowledgeSource, runStage,
  retryStage,
} from '@/services/courseAdmin'
import type { CourseDetail, PipelineStageInfo, KnowledgeSourceInfo } from '@/services/types'
import { STAGE_LABELS, STAGE_ORDER } from '@/services/types'

const WIZARD_STEPS = [
  { key: 'info', label: 'Course Info' },
  { key: 'upload', label: 'Upload Sources' },
  { key: 'validate', label: 'Validate' },
  { key: 'process', label: 'AI Processing' },
  { key: 'curriculum', label: 'Curriculum' },
  { key: 'review', label: 'Review' },
  { key: 'preview', label: 'Preview' },
  { key: 'publish', label: 'Publish' },
]

const STEP_GUIDE: Record<number, string> = {
  0: 'Enter the basic information for your new course. This will be used to initialize the AI training pipeline.',
  1: 'Upload your knowledge sources (PDF, DOCX, TXT). The AI will extract and analyze the content.',
  2: 'Review the extracted content and validate the AI\'s understanding before proceeding.',
  3: 'The AI processes your content to generate a teaching profile, course structure, and lesson content.',
  4: 'Review and refine the generated course structure before content generation.',
  5: 'Review the generated content and make any necessary refinements.',
  6: 'Preview the course through simulation to verify the learning experience.',
  7: 'All stages complete. Deploy your course to make it available to students.',
}

const STEP_HELP: Record<number, { help: string; tips: string[]; fields: string[]; warnings: string[] }> = {
  0: {
    help: 'Course name is required and should be descriptive of the subject matter.',
    tips: ['Use a clear, searchable name', 'Add subject and grade for better AI context'],
    fields: ['Course Name (required)', 'Description', 'Subject', 'Grade Level'],
    warnings: [],
  },
  1: {
    help: 'Upload PDF, DOCX, or TXT files containing your course material.',
    tips: ['Upload textbooks, lecture notes, or syllabi', 'Multiple files can be uploaded at once', 'Files up to 50MB each'],
    fields: ['At least 1 knowledge source'],
    warnings: ['Only PDF, DOCX, and TXT are supported'],
  },
  2: {
    help: 'The AI extracts and validates understanding of your content.',
    tips: ['Review extraction results carefully', 'Check that all content was properly understood'],
    fields: ['Content extraction', 'Knowledge graph validation'],
    warnings: ['Large files may take longer to process'],
  },
  3: {
    help: 'AI generates the teaching profile, course structure, and lesson content.',
    tips: ['This step may take several minutes', 'Progress is saved automatically'],
    fields: ['Teaching profile', 'Course structure', 'Lesson content'],
    warnings: ['Do not close the browser during processing'],
  },
  4: {
    help: 'Review the generated curriculum structure before content generation.',
    tips: ['Verify module order and content', 'Adjust structure if needed'],
    fields: ['Module organization', 'Lesson sequence'],
    warnings: ['Changes after this step may require regeneration'],
  },
  5: {
    help: 'Review the complete generated content and suggest refinements.',
    tips: ['Check for accuracy and completeness', 'Provide feedback for improvements'],
    fields: ['Content review', 'Refinement suggestions'],
    warnings: [],
  },
  6: {
    help: 'Preview your course through AI simulation to verify the learning experience.',
    tips: ['Simulation tests the complete learning path', 'Review student-facing experience'],
    fields: ['Course simulation', 'Learning path verification'],
    warnings: [],
  },
  7: {
    help: 'Your course is ready for deployment. Publishing makes it available to students.',
    tips: ['Verify all stages are complete', 'Review course summary before publishing'],
    fields: [],
    warnings: ['Published courses cannot be easily modified'],
  },
}

const STEP_ICONS: Record<number, typeof Bot> = {
  0: Settings, 1: Upload, 2: ShieldCheck, 3: Brain,
  4: BookOpen, 5: Edit3, 6: Eye, 7: Sparkles,
}

const STAGE_META: Record<string, { icon: typeof Bot; color: string; bg: string }> = {
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

function fmtDur(sec?: number | null) {
  if (!sec && sec !== 0) return ''
  if (sec < 60) return `${sec}s`
  return `${Math.floor(sec / 60)}m ${sec % 60}s`
}

function stageStatusIcon(status: string) {
  if (status === 'completed') return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
  if (status === 'in_progress') return <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-500" />
  if (status === 'failed') return <XCircle className="w-3.5 h-3.5 text-red-500" />
  return <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-300" />
}

export function CreateCourse() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [course, setCourse] = useState<CourseDetail | null>(null)
  const [creating, setCreating] = useState(false)
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [subject, setSubject] = useState('')
  const [gradeLevel, setGradeLevel] = useState('')
  const [error, setError] = useState('')
  const [expandedStage, setExpandedStage] = useState<string | null>(null)
  const [publishing, setPublishing] = useState(false)
  const [dropping, setDropping] = useState(false)
  const [uploading, setUploading] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const poll = useCallback(async (id: string) => {
    try {
      const res = await getCourse(id)
      setCourse(res.data)
      const active = res.data.stages.find(s => s.status === 'in_progress')
      if (!active) {
        if (pollRef.current) { clearInterval(pollRef.current); pollRef.current = null }
      }
    } catch { /* ignore */ }
  }, [])

  const startPolling = useCallback((id: string) => {
    if (pollRef.current) clearInterval(pollRef.current)
    pollRef.current = setInterval(() => poll(id), 1500)
  }, [poll])

  const waitForStageCompletion = useCallback(async (id: string, stageName: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const interval = setInterval(async () => {
        try {
          const res = await getCourse(id)
          setCourse(res.data)
          const stage = res.data.stages.find(s => s.stage_name === stageName)
          if (stage?.status === 'completed') {
            clearInterval(interval)
            resolve()
          } else if (stage?.status === 'failed') {
            clearInterval(interval)
            reject(new Error(`${STAGE_LABELS[stageName] || stageName} failed`))
          }
        } catch (e) {
          clearInterval(interval)
          reject(e)
        }
      }, 1500)
    })
  }, [])

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current) }
  }, [])

  const handleCreateAndNext = async () => {
    if (!name.trim()) return
    setError('')
    setCreating(true)
    try {
      const descText = [desc, subject && `Subject: ${subject}`, gradeLevel && `Grade: ${gradeLevel}`].filter(Boolean).join(' | ')
      const res = await createCourse(name.trim(), descText || undefined)
      setCourse(res.data)
      setStep(1)
    } catch (e: any) {
      setError(e.message || 'Failed to create course. Check that the backend server is running.')
    } finally {
      setCreating(false)
    }
  }

  const handleRunStage = async (stageKey: string) => {
    if (!course) return
    setError('')
    try {
      await runStage(course.id, stageKey)
      startPolling(course.id)
      setExpandedStage(stageKey)
    } catch (e: any) { setError(e.message) }
  }

  const handleUpload = async (file: File) => {
    if (!course) return
    setUploading(true)
    setError('')
    try {
      await uploadKnowledgeSource(course.id, file)
      await poll(course.id)
    } catch (e: any) { setError(e.message) }
    finally { setUploading(false) }
  }

  const handleRetry = async (stageKey: string) => {
    if (!course) return
    setError('')
    try { await retryStage(course.id, stageKey); handleRunStage(stageKey) }
    catch (e: any) { setError(e.message) }
  }

  const canContinue = (): boolean => {
    if (!course) return false
    if (step === 1) return course.knowledge_sources.length > 0
    const stageMap: Record<number, string[]> = {
      2: ['validate'],
      3: ['profile', 'structure', 'generate'],
      4: ['structure'],
      5: ['review'],
      6: ['simulate'],
    }
    const needed = stageMap[step]
    if (!needed) return true
    return needed.every(n => course.stages.find(s => s.stage_name === n)?.status === 'completed')
  }

  const handleNext = async () => {
    if (step === 0) {
      await handleCreateAndNext()
      return
    }
    if (step === 1 && course && course.knowledge_sources.length > 0) {
      handleRunStage('extract')
    }
    setStep(Math.min(step + 1, 7))
  }

  const handlePublish = async () => {
    if (!course) return
    setPublishing(true); setError('')
    try {
      await runStage(course.id, 'deploy')
      await waitForStageCompletion(course.id, 'deploy')
      navigate(`/course-admin/courses/${course.id}`)
    } catch (e: any) { setError(e.message) }
    finally { setPublishing(false) }
  }

  const completedStages = course?.stages.filter(s => s.status === 'completed').length || 0
  const totalStages = course?.stages.length || 0
  const progressPct = totalStages ? Math.round((completedStages / totalStages) * 100) : 0
  const hasActiveStage = course?.stages.some(s => s.status === 'in_progress') || false

  const help = STEP_HELP[step] || STEP_HELP[0]
  const Icon = STEP_ICONS[step] || Settings

  // Right panel content per step
  const coverageInfo = (() => {
    if (!course) return null
    const ks = course.knowledge_sources?.length || 0
    const kg = course.knowledge_graph_data ? 'Built' : '—'
    const tp = course.teaching_profile ? 'Generated' : '—'
    const cs = course.course_structure ? 'Generated' : '—'
    if (step === 0) return null
    return { sources: ks, knowledgeGraph: kg, teachingProfile: tp, structure: cs }
  })()

  const formatInfo = step === 1 ? 'PDF, DOCX, TXT (max 50MB)' : null
  const estTime = ['', '1-2 min', '2-5 min', '5-15 min', '—', '2-5 min', '3-5 min', '—'][step]

  const renderWorkspace = () => {
    if (step === 0) {
      return (
        <div className="p-5 space-y-4">
          <div>
            <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 block">Course Name <span className="text-red-400">*</span></label>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Algebra I"
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white" />
          </div>
          <div>
            <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 block">Description</label>
            <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Course overview and objectives" rows={3}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white resize-none" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 block">Subject</label>
              <input value={subject} onChange={e => setSubject(e.target.value)} placeholder="e.g. Mathematics"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white" />
            </div>
            <div>
              <label className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 block">Grade Level</label>
              <input value={gradeLevel} onChange={e => setGradeLevel(e.target.value)} placeholder="e.g. 9-12"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 bg-white" />
            </div>
          </div>
        </div>
      )
    }

    if (step === 1) {
      return (
        <div className="p-5">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${dropping ? 'border-blue-400 bg-blue-50' : 'border-slate-300 bg-slate-50/30'}`}
            onDragOver={e => { e.preventDefault(); setDropping(true) }}
            onDragLeave={() => setDropping(false)}
            onDrop={e => { e.preventDefault(); setDropping(false); Array.from(e.dataTransfer.files).forEach(f => handleUpload(f)) }}
          >
            <Upload className={`w-10 h-10 mx-auto mb-2 ${dropping ? 'text-blue-500' : 'text-slate-300'}`} />
            <p className="text-sm text-slate-500 mb-1">Drop files here or click to upload</p>
            <p className="text-[11px] text-slate-400 mb-4">PDF, DOCX, or TXT (max 50MB each)</p>
            <input type="file" accept=".pdf,.docx,.txt" multiple
              onChange={e => { Array.from(e.target.files || []).forEach(f => handleUpload(f)) }}
              className="text-xs w-full max-w-xs mx-auto file:mr-2 file:py-1.5 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-medium file:bg-blue-600 file:text-white file:cursor-pointer hover:file:bg-blue-700" />
            {uploading && <div className="mt-3 flex items-center justify-center gap-2 text-xs text-blue-600"><Loader2 className="w-3 h-3 animate-spin" /> Uploading...</div>}
          </div>
          {course?.knowledge_sources && course.knowledge_sources.length > 0 && (
            <div className="mt-4 bg-white rounded-lg border border-slate-200 divide-y divide-slate-100">
              <div className="px-3 py-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Uploaded Sources ({course.knowledge_sources.length})</div>
              {course.knowledge_sources.map(s => (
                <div key={s.id} className="flex items-center gap-2.5 px-3 py-2 text-xs">
                  <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <span className="flex-1 truncate text-slate-700">{s.filename}</span>
                  <span className="text-[10px] text-slate-400">{(s.file_size / 1024).toFixed(0)} KB</span>
                  <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${s.status === 'extracted' ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'}`}>{s.status}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )
    }

    if (step >= 2 && step <= 6) {
      if (!course) return null
      return (
        <div className="p-4 space-y-2">
          {course.stages.map(stage => {
            const meta = STAGE_META[stage.stage_name]
            if (!meta) return null
            const Icon = meta.icon
            const isExpanded = expandedStage === stage.stage_name

            if (step === 2 && !['upload', 'extract', 'understand', 'validate'].includes(stage.stage_name)) return null
            if (step === 3 && !['profile', 'structure', 'generate'].includes(stage.stage_name)) return null
            if (step === 4 && stage.stage_name !== 'structure') return null
            if (step === 5 && stage.stage_name !== 'review') return null
            if (step === 6 && !['review', 'simulate'].includes(stage.stage_name)) return null

            const isActive = stage.status === 'in_progress'
            const isCompleted = stage.status === 'completed'
            const isFailed = stage.status === 'failed'
            const isPending = stage.status === 'pending'
            const canRun = (isPending || isFailed) && !hasActiveStage

            return (
              <div key={stage.stage_name}
                className={`rounded-lg border transition-colors ${isActive ? 'border-blue-200 bg-blue-50/50' : isCompleted ? 'border-emerald-200 bg-emerald-50/30' : isFailed ? 'border-red-200 bg-red-50/30' : 'border-slate-100 bg-white'}`}>
                <div className="flex items-center gap-2.5 px-3 py-2.5 cursor-pointer" onClick={() => setExpandedStage(isExpanded ? null : stage.stage_name)}>
                  {stageStatusIcon(stage.status)}
                  <div className={`w-7 h-7 rounded-lg ${meta.bg} flex items-center justify-center shrink-0`}>
                    <Icon className={`w-4 h-4 ${meta.color}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-semibold text-slate-800">{STAGE_LABELS[stage.stage_name] || stage.stage_name}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className={`text-[10px] font-medium capitalize ${isFailed ? 'text-red-500' : isCompleted ? 'text-emerald-600' : 'text-slate-400'}`}>
                        {stage.status.replace(/_/g, ' ')}
                      </span>
                      {stage.duration_seconds != null && <span className="text-[10px] text-slate-400"><Clock className="w-3 h-3 inline mr-0.5" />{fmtDur(stage.duration_seconds)}</span>}
                    </div>
                  </div>
                  {stage.progress_pct > 0 && stage.progress_pct < 100 && (
                    <div className="w-20 bg-slate-200 rounded-full h-1.5">
                      <div className="bg-blue-500 h-1.5 rounded-full transition-all" style={{ width: `${stage.progress_pct}%` }} />
                    </div>
                  )}
                  {canRun && (
                    <button onClick={e => { e.stopPropagation(); handleRunStage(stage.stage_name) }}
                      className="px-2.5 py-1.5 bg-blue-600 text-white rounded-md text-[10px] font-semibold hover:bg-blue-700 transition-colors">Run</button>
                  )}
                  {isFailed && (
                    <button onClick={e => { e.stopPropagation(); handleRetry(stage.stage_name) }}
                      className="px-2.5 py-1.5 bg-red-100 text-red-700 rounded-md text-[10px] font-semibold hover:bg-red-200 transition-colors">Retry</button>
                  )}
                </div>
                {isExpanded && stage.stage_logs && stage.stage_logs.length > 0 && (
                  <div className="px-3 pb-3 border-t border-slate-100">
                    <div className="mt-2 max-h-28 overflow-y-auto space-y-0.5 bg-slate-50 rounded p-2">
                      {stage.stage_logs.map((log, li) => (
                        <div key={li} className="text-[10px] text-slate-600 flex items-start gap-1.5 font-mono">
                          <span className="text-[9px] text-slate-400 shrink-0">{log.ts?.split('T')[1]?.slice(0, 8) || ''}</span>
                          {log.level === 'error' && <AlertCircle className="w-3 h-3 text-red-400 shrink-0 mt-0.5" />}
                          {log.level === 'warning' && <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0 mt-0.5" />}
                          <span>{log.message}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {step === 4 && stage.stage_name === 'structure' && isCompleted && course.course_structure && (
                  <div className="px-3 pb-3 border-t border-slate-100 pt-2">
                    <div className="grid grid-cols-4 gap-2 text-[10px]">
                      <div className="p-2 rounded bg-slate-50"><span className="text-slate-400">Title</span><div className="font-medium text-slate-700 truncate">{course.course_structure.title as string}</div></div>
                      <div className="p-2 rounded bg-slate-50"><span className="text-slate-400">Modules</span><div className="font-medium text-slate-700">{(course.course_structure.modules as any[])?.length || 0}</div></div>
                      <div className="p-2 rounded bg-slate-50"><span className="text-slate-400">Hours</span><div className="font-medium text-slate-700">{course.course_structure.total_duration_hours as string || '—'}</div></div>
                      <div className="p-2 rounded bg-slate-50"><span className="text-slate-400">Audience</span><div className="font-medium text-slate-700 truncate">{course.course_structure.target_audience as string || '—'}</div></div>
                    </div>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )
    }

    if (step === 7) {
      return (
        <div className="p-8 text-center">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-emerald-500" />
          </div>
          <h2 className="text-lg font-bold text-slate-800 mb-1">Ready to Publish</h2>
          <p className="text-sm text-slate-500 mb-6 max-w-md mx-auto">All pipeline stages are complete. Your course is ready to be deployed and made available to students.</p>
          <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto mb-8">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-left">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Course</div>
              <div className="text-sm font-semibold text-slate-700 mt-1">{course?.name}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-left">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Modules</div>
              <div className="text-sm font-semibold text-slate-700 mt-1">{(course?.course_structure?.modules as any[])?.length || 0}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-left">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Concepts</div>
              <div className="text-sm font-semibold text-slate-700 mt-1">{course?.stages.find(s => s.stage_name === 'generate')?.output_data?.concepts_generated as number || 0}</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 text-left">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Exercises</div>
              <div className="text-sm font-semibold text-slate-700 mt-1">{course?.stages.find(s => s.stage_name === 'generate')?.output_data?.total_exercises as number || 0}</div>
            </div>
          </div>
          <button onClick={handlePublish} disabled={publishing}
            className="inline-flex items-center gap-2 px-6 py-3 bg-emerald-600 text-white rounded-xl text-sm font-bold hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-sm">
            {publishing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-5 h-5" />}
            {publishing ? 'Publishing...' : 'Publish Course'}
          </button>
        </div>
      )
    }

    return null
  }

  return (
    <div className="flex flex-col h-screen bg-slate-50">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-2.5 bg-white border-b border-slate-200 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-sm font-bold text-slate-800">AI Course Creator</span>
          <span className="text-[10px] text-slate-400 bg-slate-100 px-2 py-0.5 rounded font-medium">v2.0</span>
        </div>
        <div className="flex items-center gap-2">
          {hasActiveStage && (
            <span className="flex items-center gap-1.5 text-[10px] text-blue-600 bg-blue-50 px-2 py-1 rounded-md font-medium">
              <Loader2 className="w-3 h-3 animate-spin" /> Processing
            </span>
          )}
          <button onClick={() => navigate('/course-admin/dashboard')} className="text-[11px] text-slate-400 hover:text-slate-600 font-medium">Close</button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 px-5 py-1.5 bg-red-50 border-b border-red-200">
          <AlertCircle className="w-3.5 h-3.5 text-red-500 shrink-0" />
          <span className="text-[11px] text-red-700">{error}</span>
        </div>
      )}

      {/* Stepper */}
      <div className="flex items-center gap-0 px-5 py-2.5 bg-white border-b border-slate-200 shrink-0">
        {WIZARD_STEPS.map((s, i) => (
          <div key={s.key} className="flex items-center">
            {i > 0 && <div className={`w-6 h-px ${i <= step ? 'bg-blue-400' : 'bg-slate-200'}`} />}
            <button onClick={() => i <= step && setStep(i)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[10px] font-semibold transition-colors ${
                i === step ? 'text-blue-600 bg-blue-50' : i < step ? 'text-emerald-600' : 'text-slate-400'
              }`}>
              <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[9px] font-bold ${
                i === step ? 'bg-blue-600 text-white' : i < step ? 'bg-emerald-500 text-white' : 'bg-slate-200 text-slate-500'
              }`}>
                {i < step ? '✓' : i + 1}
              </div>
              <span>{s.label}</span>
            </button>
          </div>
        ))}
        <div className="ml-auto text-[10px] text-slate-400 font-medium">Step {step + 1} / 8</div>
      </div>

      {/* Main 3-panel content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel (30%) */}
        <div className="w-[30%] bg-white border-r border-slate-200 overflow-y-auto p-4 space-y-4">
          {/* Course Progress */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <BarChart3 className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Course Progress</span>
            </div>
            {course ? (
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[10px] text-slate-500">{completedStages} of {totalStages} stages</span>
                  <span className="text-[10px] font-bold text-blue-600">{progressPct}%</span>
                </div>
                <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
                </div>
              </div>
            ) : (
              <p className="text-[10px] text-slate-400">Not started</p>
            )}
          </div>

          {/* Step Guide */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Lightbulb className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Step Guide</span>
            </div>
            <p className="text-[11px] text-slate-600 leading-relaxed">{STEP_GUIDE[step]}</p>
          </div>

          {/* AI Readiness */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <Brain className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">AI Readiness</span>
            </div>
            <div className="space-y-1.5">
              {!course && step === 0 && (
                <div className="flex items-center gap-2 text-[10px] text-slate-400">
                  <div className="w-3 h-3 rounded-full border-2 border-slate-300 shrink-0" />
                  Waiting for course creation
                </div>
              )}
              {course && STAGE_ORDER.map(s => {
                const st = course.stages.find(st => st.stage_name === s)
                const done = st?.status === 'completed'
                const active = st?.status === 'in_progress'
                return (
                  <div key={s} className="flex items-center gap-2 text-[10px]">
                    {done ? <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" /> :
                     active ? <Loader2 className="w-3 h-3 animate-spin text-blue-500 shrink-0" /> :
                     <div className="w-3 h-3 rounded-full border-2 border-slate-300 shrink-0" />}
                    <span className={`${done ? 'text-slate-700' : active ? 'text-blue-600' : 'text-slate-400'}`}>
                      {STAGE_LABELS[s] || s}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Completion Status */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <CheckCircle className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Completion Status</span>
            </div>
            <div className="space-y-1.5">
              {WIZARD_STEPS.slice(0, 7).map((s, i) => {
                const st = course?.stages.find(st => st.stage_name === s.key)
                const done = st?.status === 'completed' || (step > i && i > 0)
                const current = step === i
                return (
                  <div key={s.key} className="flex items-center gap-2 text-[10px]">
                    {done ? <CheckCircle2 className="w-3 h-3 text-emerald-500 shrink-0" /> :
                     current ? <Loader2 className="w-3 h-3 animate-spin text-blue-500 shrink-0" /> :
                     <div className="w-3 h-3 rounded-full border-2 border-slate-300 shrink-0" />}
                    <span className={done ? 'text-slate-700' : current ? 'text-blue-600' : 'text-slate-400'}>{s.label}</span>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Validation Summary */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <ShieldCheck className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Validation Summary</span>
            </div>
            <div className="text-[10px] text-slate-500 space-y-1">
              {!course && step === 0 && <p>Create a course to begin</p>}
              {course && course.stages.filter(s => s.status === 'failed').length > 0 && (
                <div className="flex items-center gap-1.5 text-red-500">
                  <XCircle className="w-3 h-3" />
                  {course.stages.filter(s => s.status === 'failed').length} stage(s) failed
                </div>
              )}
              {course && course.stages.filter(s => s.status === 'in_progress').length > 0 && (
                <div className="flex items-center gap-1.5 text-blue-500">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Processing in progress
                </div>
              )}
              {course && course.stages.every(s => s.status === 'completed') && (
                <div className="flex items-center gap-1.5 text-emerald-600">
                  <CheckCircle2 className="w-3 h-3" />
                  All validations passed
                </div>
              )}
              {course && course.stages.every(s => s.status === 'pending' || s.status === 'completed') && course.stages.some(s => s.status === 'pending') && (
                <div className="flex items-center gap-1.5 text-slate-400">
                  <Info className="w-3 h-3" />
                  Pending stages require action
                </div>
              )}
              {course && step === 1 && course.knowledge_sources.length === 0 && (
                <div className="flex items-center gap-1.5 text-amber-500">
                  <AlertTriangle className="w-3 h-3" />
                  Upload at least 1 source
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Center Panel (50%) */}
        <div className="w-[50%] overflow-y-auto bg-slate-50">
          <div className="flex items-center gap-2 px-5 py-3 bg-white border-b border-slate-100 sticky top-0 z-10">
            <div className="w-7 h-7 rounded-lg bg-blue-50 flex items-center justify-center">
              <Icon className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-800">{WIZARD_STEPS[step].label}</h2>
              <p className="text-[10px] text-slate-400">{STEP_GUIDE[step]?.slice(0, 60)}...</p>
            </div>
          </div>
          {renderWorkspace()}
        </div>

        {/* Right Panel (20%) */}
        <div className="w-[20%] bg-white border-l border-slate-200 overflow-y-auto p-4 space-y-4">
          {/* Contextual Help */}
          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Help</span>
            </div>
            <p className="text-[10px] text-slate-600 leading-relaxed">{help.help}</p>
          </div>

          {/* Required Fields */}
          {help.fields.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Info className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Required</span>
              </div>
              <ul className="space-y-1">
                {help.fields.map((f, i) => (
                  <li key={i} className="text-[10px] text-slate-600 flex items-start gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1 shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Tips */}
          {help.tips.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Tips</span>
              </div>
              <ul className="space-y-1">
                {help.tips.map((t, i) => (
                  <li key={i} className="text-[10px] text-slate-600 flex items-start gap-1.5">
                    <ArrowRight className="w-2.5 h-2.5 text-amber-400 mt-0.5 shrink-0" />
                    {t}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {help.warnings.length > 0 && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Warnings</span>
              </div>
              <ul className="space-y-1">
                {help.warnings.map((w, i) => (
                  <li key={i} className="text-[10px] text-amber-700 flex items-start gap-1.5">
                    <AlertTriangle className="w-2.5 h-2.5 text-amber-500 mt-0.5 shrink-0" />
                    {w}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Supported Formats */}
          {formatInfo && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <FileType className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Supported Formats</span>
              </div>
              <p className="text-[10px] text-slate-600">{formatInfo}</p>
            </div>
          )}

          {/* Estimated Time */}
          {estTime && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Clock3 className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Est. Processing</span>
              </div>
              <p className="text-[10px] text-slate-600">{estTime}</p>
            </div>
          )}

          {/* Knowledge Coverage */}
          {coverageInfo && (
            <div>
              <div className="flex items-center gap-1.5 mb-2">
                <Layers className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">Coverage</span>
              </div>
              <div className="space-y-1">
                <div className="flex justify-between text-[10px]"><span className="text-slate-500">Sources</span><span className="text-slate-700 font-medium">{coverageInfo.sources}</span></div>
                <div className="flex justify-between text-[10px]"><span className="text-slate-500">Knowledge Graph</span><span className="text-slate-700 font-medium">{coverageInfo.knowledgeGraph}</span></div>
                <div className="flex justify-between text-[10px]"><span className="text-slate-500">Profile</span><span className="text-slate-700 font-medium">{coverageInfo.teachingProfile}</span></div>
                <div className="flex justify-between text-[10px]"><span className="text-slate-500">Structure</span><span className="text-slate-700 font-medium">{coverageInfo.structure}</span></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Bottom navigation */}
      <div className="flex items-center justify-between px-5 py-3 bg-white border-t border-slate-200 shrink-0">
        <div className="flex items-center gap-2">
          {step > 0 && (
            <button onClick={() => setStep(step - 1)}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-slate-200 rounded-lg text-[11px] font-semibold text-slate-600 hover:bg-slate-50 transition-colors">
              <ChevronRight className="w-3.5 h-3.5 rotate-180" /> Back
            </button>
          )}
        </div>
        <div className="flex items-center gap-3">
          {step < 7 && (
            <>
              {!canContinue() && course && (
                <span className="text-[10px] text-amber-600">
                  {step === 1 ? 'Upload at least one source' :
                   step === 2 ? 'Complete validation' :
                   step === 3 ? 'Complete AI processing' :
                   step === 4 ? 'Complete curriculum' :
                   step === 5 ? 'Complete review' :
                   step === 6 ? 'Complete preview' : 'Fill required fields'}
                </span>
              )}
              {!name.trim() && step === 0 && (
                <span className="text-[10px] text-amber-600">Enter a course name</span>
              )}
              <button onClick={handleNext}
                disabled={step === 0 ? !name.trim() || creating : !canContinue()}
                className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white rounded-lg text-[11px] font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                {creating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : null}
                {creating ? 'Creating...' : step === 6 ? 'Continue to Publish' : 'Next'}
                {!creating && <ChevronRight className="w-3.5 h-3.5" />}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
