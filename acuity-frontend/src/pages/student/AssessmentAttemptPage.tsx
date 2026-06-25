import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { startAssessment, submitAttempt } from '@/services/assessments'
import { ArrowLeft, ArrowRight, Loader2, AlertCircle, Clock, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AssessmentAttemptPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [timeLeft, setTimeLeft] = useState<number | null>(null)
  const [confirmSubmit, setConfirmSubmit] = useState(false)
  const [submittedAttemptId, setSubmittedAttemptId] = useState<string | null>(null)
  const startTime = useRef(Date.now())

  const { data: attemptData, loading } = useAuthApi(
    () => id ? startAssessment(id) : Promise.reject(),
    [id],
  )

  const questions = attemptData?.questions || []
  const timeLimitSeconds = attemptData?.time_limit_seconds

  useEffect(() => {
    if (timeLimitSeconds && timeLimitSeconds > 0) {
      setTimeLeft(timeLimitSeconds)
    }
  }, [timeLimitSeconds])

  useEffect(() => {
    if (timeLeft === null || timeLeft <= 0) return
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev === null || prev <= 1) {
          clearInterval(timer)
          handleAutoSubmit()
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [timeLeft])

  const handleAutoSubmit = useCallback(async () => {
    if (!attemptData || submittedAttemptId) return
    setSubmitting(true)
    try {
      const responses = questions.map(q => ({
        question_id: q.id,
        response: answers[q.id] || '',
        time_taken_seconds: Math.round((Date.now() - startTime.current) / 1000),
      }))
      const res = await submitAttempt(attemptData.attempt_id, responses)
      setSubmittedAttemptId(res.data.attempt_id)
      navigate(`/student/assessments/${id}/result?attempt=${res.data.attempt_id}`, { replace: true })
    } catch {
      setError('Failed to submit. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }, [attemptData, submittedAttemptId, answers, questions, navigate, id])

  useEffect(() => {
    if (handleAutoSubmit && timeLeft === 0) {
      handleAutoSubmit()
    }
  }, [timeLeft])

  const handleAnswer = (questionId: string, value: string) => {
    if (submitting || submittedAttemptId) return
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  const handleSubmit = async () => {
    if (!attemptData) return
    setSubmitting(true)
    setError('')
    try {
      const responses = questions.map(q => ({
        question_id: q.id,
        response: answers[q.id] || '',
        time_taken_seconds: Math.round((Date.now() - startTime.current) / 1000),
      }))
      const res = await submitAttempt(attemptData.attempt_id, responses)
      setSubmittedAttemptId(res.data.attempt_id)
      navigate(`/student/assessments/${id}/result?attempt=${res.data.attempt_id}`, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  if (!attemptData || questions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <AlertCircle className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">Unable to start assessment.</p>
          <button onClick={() => navigate('/student/assessments')} className="btn-secondary mt-4">
            Back to Assessments
          </button>
        </div>
      </div>
    )
  }

  const question = questions[currentQ]
  const allAnswered = questions.every(q => answers[q.id] && answers[q.id].trim() !== '')
  const answeredCount = Object.keys(answers).length

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm">
        <div className="p-4 border-b border-slate-100">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs text-slate-400">
              Question {currentQ + 1} of {questions.length}
            </span>
            {timeLeft !== null && (
              <span className={cn(
                'flex items-center gap-1 text-xs font-medium',
                timeLeft < 60 ? 'text-red-600' : 'text-slate-500'
              )}>
                <Clock className="w-3.5 h-3.5" />
                {formatTime(timeLeft)}
              </span>
            )}
          </div>

          <div className="flex gap-1">
            {questions.map((_, i) => (
              <div
                key={i}
                className={cn(
                  'h-1.5 flex-1 rounded-full transition-all',
                  answers[questions[i].id] ? 'bg-emerald-400' :
                  i === currentQ ? 'bg-navy-800' : 'bg-slate-200'
                )}
              />
            ))}
          </div>
        </div>

        <div className="p-6">
          <h2 className="text-lg font-medium text-slate-900 mb-6">{question?.prompt}</h2>

          <div className="space-y-3 mb-8">
            {question?.options ? (
              Object.entries(question.options).map(([key, value]) => (
                <button
                  key={key}
                  onClick={() => handleAnswer(question.id, key)}
                  className={cn(
                    'w-full text-left px-4 py-3 rounded-lg border text-sm transition-all',
                    answers[question.id] === key
                      ? 'border-navy-800 bg-navy-50 text-navy-900 font-medium'
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                  )}
                >
                  {value}
                </button>
              ))
            ) : (
              <textarea
                value={answers[question?.id || ''] || ''}
                onChange={(e) => question && handleAnswer(question.id, e.target.value)}
                placeholder="Type your answer..."
                rows={4}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 text-sm focus:border-navy-400 focus:ring-1 focus:ring-navy-400 outline-none resize-none"
              />
            )}
          </div>
        </div>

        <div className="p-4 border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={() => setCurrentQ(prev => Math.max(0, prev - 1))}
            disabled={currentQ === 0}
            className="btn-secondary disabled:opacity-50"
          >
            <ArrowLeft className="w-4 h-4 mr-1" /> Previous
          </button>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400">
              {answeredCount}/{questions.length} answered
            </span>

            {currentQ < questions.length - 1 ? (
              <button
                onClick={() => setCurrentQ(prev => prev + 1)}
                className="btn-primary"
              >
                Next <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            ) : (
              !confirmSubmit ? (
                <button
                  onClick={() => setConfirmSubmit(true)}
                  className="btn-primary"
                >
                  Review & Submit
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setConfirmSubmit(false)}
                    className="btn-secondary text-sm"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSubmit}
                    disabled={submitting}
                    className="btn-primary flex items-center gap-1"
                  >
                    {submitting ? 'Submitting...' : <><CheckCircle2 className="w-4 h-4" /> Confirm Submit</>}
                  </button>
                </div>
              )
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  )
}
