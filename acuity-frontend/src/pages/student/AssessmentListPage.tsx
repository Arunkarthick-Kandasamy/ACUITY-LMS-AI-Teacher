import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthApi } from '@/hooks/useApi'
import { getAvailableAssessments } from '@/services/assessments'
import { ClipboardCheck, Clock, FileText, Trophy, Loader2, ArrowRight } from 'lucide-react'

const typeLabels: Record<string, string> = {
  quiz: 'Quiz',
  practice_test: 'Practice Test',
  chapter_test: 'Chapter Test',
  diagnostic: 'Diagnostic',
  final: 'Final Assessment',
}

const typeColors: Record<string, string> = {
  quiz: 'bg-blue-50 text-blue-700',
  practice_test: 'bg-purple-50 text-purple-700',
  chapter_test: 'bg-amber-50 text-amber-700',
  diagnostic: 'bg-emerald-50 text-emerald-700',
  final: 'bg-red-50 text-red-700',
}

export function AssessmentListPage() {
  const navigate = useNavigate()
  const { data: assessments, loading } = useAuthApi(() => getAvailableAssessments(), [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Assessments</h1>
        <p className="text-sm text-slate-500 mt-1">Test your knowledge and track your progress</p>
      </div>

      {(!assessments || assessments.length === 0) ? (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-8 text-center">
          <ClipboardCheck className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <p className="text-slate-500">No assessments available yet.</p>
          <p className="text-xs text-slate-400 mt-1">Complete lessons to unlock assessments.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {assessments.map((a) => (
            <div
              key={a.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 hover:border-navy-300 transition-all cursor-pointer"
              onClick={() => navigate(`/student/assessments/${a.id}`)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wider ${typeColors[a.assessment_type] || 'bg-slate-100 text-slate-600'}`}>
                      {typeLabels[a.assessment_type] || a.assessment_type}
                    </span>
                    {a.max_attempts > 1 && (
                      <span className="text-[10px] text-slate-400">{a.max_attempts} attempts</span>
                    )}
                  </div>
                  <h2 className="font-medium text-slate-900">{a.title}</h2>
                  {a.description && (
                    <p className="text-sm text-slate-500 mt-1 line-clamp-2">{a.description}</p>
                  )}
                  <div className="flex items-center gap-4 mt-3 text-xs text-slate-400">
                    <span className="flex items-center gap-1">
                      <FileText className="w-3.5 h-3.5" />
                      {a.question_count} questions
                    </span>
                    {a.time_limit && (
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {a.time_limit} min
                      </span>
                    )}
                    <span className="flex items-center gap-1">
                      <Trophy className="w-3.5 h-3.5" />
                      {Math.round(a.passing_score * 100)}% to pass
                    </span>
                  </div>
                </div>
                <ArrowRight className="w-5 h-5 text-slate-300 mt-1 shrink-0" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
