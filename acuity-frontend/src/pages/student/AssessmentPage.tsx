import { useState, useCallback } from 'react'
import { useAuthApi } from '@/hooks/useApi'
import { getEnrollments } from '@/services/enrollment'
import { getCurriculumTree } from '@/services/progress'
import { getConceptExercises } from '@/services/curriculum'
import { recordAttempt } from '@/services/progress'
import { ArrowLeft, ArrowRight, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AssessmentPage() {
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState<Record<number, string>>({})
  const [submitted, setSubmitted] = useState(false)
  const [score, setScore] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [results, setResults] = useState<Record<number, boolean>>({})
  const [error, setError] = useState('')

  const { data: enrollments } = useAuthApi(() => getEnrollments('active'), [])
  const courseId = enrollments?.[0]?.course_id

  const { data: curriculum } = useAuthApi(
    () => courseId ? getCurriculumTree(courseId) : Promise.reject(),
    [courseId],
  )

  const firstConceptId = curriculum?.modules?.[0]?.lessons?.[0]?.concepts?.[0]?.concept_id
  const { data: exercisesData, loading } = useAuthApi(
    () => firstConceptId ? getConceptExercises(firstConceptId) : Promise.reject(),
    [firstConceptId],
  )

  const questions = (exercisesData || []).map((ex) => ({
    id: ex.exercise_id,
    question: ex.prompt,
    options: ex.options ? Object.values(ex.options) : [],
  }))

  const handleAnswer = (optionIndex: number) => {
    if (submitted || submitting) return
    setAnswers(prev => ({ ...prev, [currentQ]: String(optionIndex) }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    setError('')
    let correctCount = 0
    const resultMap: Record<number, boolean> = {}
    for (let i = 0; i < questions.length; i++) {
      try {
        const res = await recordAttempt(questions[i].id, { response: answers[i] || '' })
        resultMap[i] = res.data.is_correct
        if (res.data.is_correct) correctCount++
      } catch {
        resultMap[i] = false
      }
    }
    setResults(resultMap)
    setScore(Math.round((correctCount / questions.length) * 100))
    setSubmitted(true)
    setSubmitting(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-slate-900">Assessment</h1>
          <p className="text-sm text-slate-500 mt-1">No assessments available yet</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <p className="text-slate-500">Complete a lesson to unlock assessments.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Assessment</h1>
        <p className="text-sm text-slate-500 mt-1">{questions.length} questions</p>
      </div>

      {submitted ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Assessment Complete!</h2>
          <div className="text-4xl font-bold text-navy-800 mb-2">{score}%</div>
          <p className="text-sm text-slate-500 mb-6">
            {score >= 75 ? "Great job! You have a strong understanding." : "Keep practicing! You're making progress."}
          </p>
          <div className="flex items-center justify-center gap-3">
            <button onClick={() => { setSubmitted(false); setAnswers({}); setCurrentQ(0); setScore(0) }} className="btn-secondary">
              Retry
            </button>
            <button onClick={() => window.history.back()} className="btn-primary">
              Back to Dashboard
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex gap-1.5">
              {questions.map((_, i) => (
                <div key={i} className={cn(
                  'w-8 h-1.5 rounded-full transition-all',
                  i === currentQ ? 'bg-navy-800' : i < currentQ ? 'bg-emerald-400' : 'bg-slate-200'
                )} />
              ))}
            </div>
            <span className="text-xs text-slate-400">Question {currentQ + 1} of {questions.length}</span>
          </div>

          <h2 className="text-lg font-medium text-slate-900 mb-6">{questions[currentQ].question}</h2>

          <div className="space-y-3 mb-8">
            {questions[currentQ].options.map((option, i) => (
              <button
                key={i}
                onClick={() => handleAnswer(i)}
                className={cn(
                  'w-full text-left px-4 py-3 rounded-lg border text-sm transition-all',
                  answers[currentQ] === String(i)
                    ? 'border-navy-800 bg-navy-50 text-navy-900 font-medium'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                )}
              >
                {option}
              </button>
            ))}
          </div>

          <div className="flex items-center justify-between">
            <button
              onClick={() => setCurrentQ(prev => Math.max(0, prev - 1))}
              disabled={currentQ === 0}
              className="btn-secondary disabled:opacity-50"
            >
              <ArrowLeft className="w-4 h-4 mr-1" /> Previous
            </button>

            {currentQ < questions.length - 1 ? (
              <button
                onClick={() => setCurrentQ(prev => prev + 1)}
                className="btn-primary"
              >
                Next <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={Object.keys(answers).length < questions.length || submitting}
                className="btn-primary disabled:opacity-50"
              >
                {submitting ? 'Submitting...' : 'Submit'}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
