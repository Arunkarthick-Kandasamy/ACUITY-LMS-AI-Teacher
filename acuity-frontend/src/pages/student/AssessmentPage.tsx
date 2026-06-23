import { useState } from 'react'
import { ArrowLeft, ArrowRight, CheckCircle2, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'

const questions = [
  { id: 1, question: 'What is the value of x in the equation 2x + 5 = 13?', options: ['x = 3', 'x = 4', 'x = 5', 'x = 6'], correct: 1 },
  { id: 2, question: 'Simplify: 3(x + 2) - 2x', options: ['x + 6', 'x + 5', '3x + 6', '5x + 6'], correct: 0 },
  { id: 3, question: 'What is the slope of the line y = 2x + 3?', options: ['2', '3', '-2', '1/2'], correct: 0 },
]

export function AssessmentPage() {
  const [currentQ, setCurrentQ] = useState(0)
  const [answers, setAnswers] = useState<Record<number, number>>({})
  const [submitted, setSubmitted] = useState(false)

  const handleAnswer = (optionIndex: number) => {
    if (submitted) return
    setAnswers(prev => ({ ...prev, [currentQ]: optionIndex }))
  }

  const handleSubmit = () => {
    setSubmitted(true)
  }

  const score = submitted
    ? Math.round((Object.entries(answers).filter(([q, a]) => a === questions[Number(q)].correct).length / questions.length) * 100)
    : 0

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Assessment</h1>
        <p className="text-sm text-slate-500 mt-1">Quadratic Functions · 3 questions</p>
      </div>

      {submitted ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-8 h-8 text-emerald-600" />
          </div>
          <h2 className="text-xl font-semibold text-slate-900 mb-2">Assessment Complete!</h2>
          <div className="text-4xl font-bold text-navy-800 mb-2">{score}%</div>
          <p className="text-sm text-slate-500 mb-6">
            {score >= 75 ? 'Great job! You have a strong understanding.' : 'Keep practicing! You\'re making progress.'}
          </p>
          <div className="flex items-center justify-center gap-3">
            <button onClick={() => { setSubmitted(false); setAnswers({}); setCurrentQ(0) }} className="btn-secondary">
              Retry
            </button>
            <button onClick={() => window.history.back()} className="btn-primary">
              Back to Dashboard
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          {/* Progress */}
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
                  answers[currentQ] === i
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
                disabled={Object.keys(answers).length < questions.length}
                className="btn-primary disabled:opacity-50"
              >
                Submit
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
