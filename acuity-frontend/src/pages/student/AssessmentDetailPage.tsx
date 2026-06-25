import { useParams, useNavigate } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { getAssessmentDetail } from '@/services/assessments'
import { Clock, FileText, Trophy, AlertCircle, Loader2, ArrowLeft, Play } from 'lucide-react'
import { useState } from 'react'

const typeLabels: Record<string, string> = {
  quiz: 'Quiz',
  practice_test: 'Practice Test',
  chapter_test: 'Chapter Test',
  diagnostic: 'Diagnostic',
  final: 'Final Assessment',
}

export function AssessmentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [starting, setStarting] = useState(false)

  const { data: assessment, loading } = useAuthApi(
    () => id ? getAssessmentDetail(id) : Promise.reject(),
    [id],
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Assessment not found.</p>
          <button onClick={() => navigate('/student/assessments')} className="btn-secondary mt-4">
            Back to Assessments
          </button>
        </div>
      </div>
    )
  }

  const handleStart = async () => {
    setStarting(true)
    navigate(`/student/assessments/${id}/attempt`)
  }

  return (
    <div className="max-w-3xl mx-auto">
      <button
        onClick={() => navigate('/student/assessments')}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 mb-4"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Assessments
      </button>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="p-6 border-b border-slate-100">
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium uppercase tracking-wider ${
            assessment.assessment_type === 'quiz' ? 'bg-blue-50 text-blue-700' :
            assessment.assessment_type === 'practice_test' ? 'bg-purple-50 text-purple-700' :
            assessment.assessment_type === 'chapter_test' ? 'bg-amber-50 text-amber-700' :
            assessment.assessment_type === 'diagnostic' ? 'bg-emerald-50 text-emerald-700' :
            'bg-red-50 text-red-700'
          }`}>
            {typeLabels[assessment.assessment_type] || assessment.assessment_type}
          </span>
          <h1 className="text-xl font-semibold text-slate-900 mt-2">{assessment.title}</h1>
          {assessment.description && (
            <p className="text-sm text-slate-500 mt-2">{assessment.description}</p>
          )}
        </div>

        <div className="p-6 space-y-4">
          <h2 className="font-medium text-slate-900">Assessment Details</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <FileText className="w-5 h-5 text-navy-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-slate-900">{assessment.question_count}</div>
              <div className="text-xs text-slate-500">Questions</div>
            </div>
            {assessment.time_limit && (
              <div className="bg-slate-50 rounded-lg p-3 text-center">
                <Clock className="w-5 h-5 text-navy-600 mx-auto mb-1" />
                <div className="text-lg font-bold text-slate-900">{assessment.time_limit}</div>
                <div className="text-xs text-slate-500">Minutes</div>
              </div>
            )}
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <Trophy className="w-5 h-5 text-navy-600 mx-auto mb-1" />
              <div className="text-lg font-bold text-slate-900">{Math.round(assessment.passing_score * 100)}%</div>
              <div className="text-xs text-slate-500">Pass Score</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-slate-900">{assessment.max_attempts}</div>
              <div className="text-xs text-slate-500">Max Attempts</div>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-slate-100 flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Read each question carefully. You cannot pause once started.
          </p>
          <button
            onClick={handleStart}
            disabled={starting}
            className="btn-primary flex items-center gap-2"
          >
            {starting ? 'Starting...' : <><Play className="w-4 h-4" /> Start Assessment</>}
          </button>
        </div>
      </div>
    </div>
  )
}
