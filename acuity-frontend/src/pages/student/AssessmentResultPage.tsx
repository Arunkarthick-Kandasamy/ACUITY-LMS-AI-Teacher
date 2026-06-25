import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { getAttemptResult } from '@/services/assessments'
import {
  CheckCircle2, XCircle, ArrowLeft, Trophy, Loader2, AlertCircle, BarChart3,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function AssessmentResultPage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const attemptId = searchParams.get('attempt')

  const { data: result, loading } = useAuthApi(
    () => attemptId ? getAttemptResult(attemptId) : Promise.reject(),
    [attemptId],
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  if (!result) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Result not found.</p>
          <button onClick={() => navigate('/student/assessments')} className="btn-secondary mt-4">
            Back to Assessments
          </button>
        </div>
      </div>
    )
  }

  const correctCount = result.responses.filter(r => r.is_correct).length
  const passThreshold = Math.round(result.passing_score * 100)

  return (
    <div className="max-w-3xl mx-auto">
      <button
        onClick={() => navigate('/student/assessments')}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 mb-4"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Assessments
      </button>

      <div className={cn(
        'bg-white rounded-xl border shadow-sm overflow-hidden',
        result.passed ? 'border-emerald-200' : 'border-red-200'
      )}>
        <div className={cn(
          'p-8 text-center',
          result.passed ? 'bg-emerald-50' : 'bg-red-50'
        )}>
          <div className={cn(
            'w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4',
            result.passed ? 'bg-emerald-100' : 'bg-red-100'
          )}>
            {result.passed
              ? <Trophy className="w-8 h-8 text-emerald-600" />
              : <XCircle className="w-8 h-8 text-red-600" />
            }
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mb-1">
            {result.passed ? 'Assessment Passed!' : 'Assessment Not Passed'}
          </h1>
          <p className="text-sm text-slate-500 mb-4">{result.assessment_title}</p>
          <div className={cn(
            'text-5xl font-bold mb-2',
            result.passed ? 'text-emerald-600' : 'text-red-600'
          )}>
            {Math.round(result.percentage)}%
          </div>
          <p className="text-sm text-slate-500">
            {result.passed
              ? `Great job! You scored above the ${passThreshold}% pass threshold.`
              : `You needed ${passThreshold}% to pass. Review incorrect answers below.`
            }
          </p>
          <div className="flex items-center justify-center gap-6 mt-4 text-xs text-slate-500">
            <span>Score: {Math.round(result.earned_marks)}/{Math.round(result.total_marks)}</span>
            <span>Correct: {correctCount}/{result.responses.length}</span>
            <span>Attempt #{result.attempt_number}</span>
          </div>
        </div>

        <div className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5 text-navy-600" />
            <h2 className="font-semibold text-slate-900">Question Review</h2>
          </div>
          <div className="space-y-4">
            {result.responses.map((r, i) => (
              <div
                key={r.question_id}
                className={cn(
                  'rounded-lg border p-4',
                  r.is_correct ? 'border-emerald-200 bg-emerald-50/50' : 'border-red-200 bg-red-50/50'
                )}
              >
                <div className="flex items-start gap-3">
                  <div className={cn(
                    'w-6 h-6 rounded-full flex items-center justify-center mt-0.5 shrink-0',
                    r.is_correct ? 'bg-emerald-100' : 'bg-red-100'
                  )}>
                    {r.is_correct
                      ? <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      : <XCircle className="w-4 h-4 text-red-600" />
                    }
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-slate-500">Question {i + 1}</span>
                      <span className={cn(
                        'text-xs font-medium',
                        r.is_correct ? 'text-emerald-600' : 'text-red-600'
                      )}>
                        {r.score}/{r.marks} pts
                      </span>
                    </div>
                    <p className="text-sm text-slate-900 mb-2">{r.prompt}</p>
                    <div className="text-xs space-y-1">
                      <p><span className="text-slate-500">Your answer:</span> {r.response || '(no answer)'}</p>
                      {!r.is_correct && (
                        <p><span className="text-slate-500">Correct answer:</span> <span className="text-emerald-600 font-medium">{r.correct_answer}</span></p>
                      )}
                      {r.explanation && (
                        <p className="text-slate-400 mt-1 italic">{r.explanation}</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 border-t border-slate-100 flex items-center justify-between">
          <button onClick={() => navigate('/student/assessments')} className="btn-secondary">
            Back to Assessments
          </button>
          <button onClick={() => navigate('/student/dashboard')} className="btn-primary">
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  )
}
