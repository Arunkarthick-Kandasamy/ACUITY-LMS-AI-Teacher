import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, ArrowRight, BookOpen, Sparkles } from 'lucide-react'
import { authStore } from '@/store/authStore'
import { enroll } from '@/services/enrollment'
import { getCourses } from '@/services/curriculum'

const grades = ['6th', '7th', '8th', '9th', '10th', '11th', '12th']
const subjects = ['Mathematics', 'Science', 'English', 'Social Studies', 'Computer Science']
const interests = ['Algebra', 'Geometry', 'Trigonometry', 'Calculus', 'Statistics', 'Physics', 'Chemistry', 'Biology']

export function StudentOnboarding() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [grade, setGrade] = useState('')
  const [subject, setSubject] = useState('')
  const [selectedInterests, setSelectedInterests] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const toggleInterest = (interest: string) => {
    setSelectedInterests(prev =>
      prev.includes(interest) ? prev.filter(i => i !== interest) : [...prev, interest]
    )
  }

  const handleComplete = async () => {
    setLoading(true)
    try {
      const res = await getCourses({ is_published: true, per_page: 1 })
      const course = res.data?.[0]
      if (course) {
        await enroll(course.course_id)
      }
    } catch {}
    navigate('/student/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <GraduationCap className="w-8 h-8 text-navy-800" />
            <span className="text-xl font-bold text-navy-800">Acuity</span>
          </div>
          <h1 className="text-xl font-semibold text-slate-900">Welcome! Let's set up your profile</h1>
          <p className="text-sm text-slate-500 mt-1">Step {step} of 3</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex gap-2 mb-6">
            {[1, 2, 3].map(s => (
              <div key={s} className={`flex-1 h-1.5 rounded-full ${s <= step ? 'bg-navy-800' : 'bg-slate-200'}`} />
            ))}
          </div>

          {step === 1 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-slate-700">
                <BookOpen className="w-5 h-5 text-navy-600" />
                <h2 className="font-semibold">What grade are you in?</h2>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {grades.map(g => (
                  <button
                    key={g}
                    onClick={() => setGrade(g)}
                    className={`px-4 py-3 rounded-lg text-sm font-medium border transition-all ${
                      grade === g
                        ? 'bg-navy-800 text-white border-navy-800'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    {g}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setStep(2)}
                disabled={!grade}
                className="btn-primary w-full mt-2 disabled:opacity-50"
              >
                Next <ArrowRight className="w-4 h-4 ml-1" />
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-slate-700">
                <BookOpen className="w-5 h-5 text-navy-600" />
                <h2 className="font-semibold">Which subject interests you most?</h2>
              </div>
              <div className="space-y-2">
                {subjects.map(s => (
                  <button
                    key={s}
                    onClick={() => setSubject(s)}
                    className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium border transition-all ${
                      subject === s
                        ? 'bg-navy-800 text-white border-navy-800'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button onClick={() => setStep(1)} className="btn-secondary flex-1">
                  Back
                </button>
                <button
                  onClick={() => setStep(3)}
                  disabled={!subject}
                  className="btn-primary flex-1 disabled:opacity-50"
                >
                  Next <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-slate-700">
                <Sparkles className="w-5 h-5 text-navy-600" />
                <h2 className="font-semibold">Pick topics you like (optional)</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {interests.map(interest => (
                  <button
                    key={interest}
                    onClick={() => toggleInterest(interest)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                      selectedInterests.includes(interest)
                        ? 'bg-navy-800 text-white border-navy-800'
                        : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    {interest}
                  </button>
                ))}
              </div>
              <div className="flex gap-2">
                <button onClick={() => setStep(2)} className="btn-secondary flex-1">
                  Back
                </button>
                <button onClick={handleComplete} disabled={loading} className="btn-primary flex-1 disabled:opacity-50">
                  {loading ? 'Setting up...' : 'Start Learning'} <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
