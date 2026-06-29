import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Eye, EyeOff, ArrowRight, Sparkles, CheckCircle2, BookOpen, Users, School, GraduationCap, ChevronLeft } from 'lucide-react'
import { cn } from '@/lib/utils'
import { authStore, type UserRole } from '@/store/authStore'
import { ApiError } from '@/services/api'

const roleToPath: Record<string, string> = {
  student: '/student/dashboard',
  parent: '/parent/dashboard',
  admin: '/admin/dashboard',
  course_admin: '/course-admin/dashboard',
  teacher: '/teacher/dashboard',
}

const roles: { value: UserRole; label: string; icon: typeof BookOpen; desc: string }[] = [
  { value: 'student', label: 'Student', icon: BookOpen, desc: 'Learn with AI' },
  { value: 'parent', label: 'Parent', icon: Users, desc: 'Track progress' },
  { value: 'admin', label: 'Admin', icon: School, desc: 'Manage system' },
  { value: 'course_admin', label: 'Course Admin', icon: GraduationCap, desc: 'Manage courses' },
]

export function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const isRegister = searchParams.get('register') === 'true'
  const [showPassword, setShowPassword] = useState(false)
  const [selectedRole, setSelectedRole] = useState<UserRole>('student')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegister) {
        await authStore.register(email, password, name, selectedRole)
        await authStore.login(email, password, selectedRole)
      } else {
        await authStore.login(email, password, selectedRole)
      }
      const user = authStore.user
      navigate(roleToPath[user?.role || selectedRole] || '/')
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError('An unexpected error occurred. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Left panel — Form */}
      <div className="flex-1 flex items-center justify-center p-4 sm:p-8">
        <div className="w-full max-w-sm">
          {/* Logo */}
          <button onClick={() => navigate('/')} className="flex items-center gap-2 mb-8">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">A</div>
            <span className="text-sm font-semibold text-gray-900">Acuity</span>
          </button>

          <div className="mb-8">
            <h1 className="text-xl font-semibold text-gray-900">{isRegister ? 'Create your account' : 'Welcome back'}</h1>
            <p className="text-sm text-gray-400 mt-1">{isRegister ? 'Start your personalized learning journey' : 'Sign in to continue learning'}</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-100 text-sm text-red-600 flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-red-500 shrink-0" />
                {error}
              </div>
            )}

            {isRegister && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">Full name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="block w-full h-10 rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                  placeholder="Alex Chen"
                  required
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full h-10 rounded-lg border border-gray-200 bg-white px-3.5 text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full h-10 rounded-lg border border-gray-200 bg-white px-3.5 pr-10 text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1 rounded-md transition-colors"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            {/* Role selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">I am a</label>
              <div className="grid grid-cols-4 gap-2">
                {roles.map((role) => {
                  const Icon = role.icon
                  const active = selectedRole === role.value
                  return (
                    <button
                      key={role.value}
                      type="button"
                      onClick={() => setSelectedRole(role.value)}
                      className={cn(
                        'flex flex-col items-center gap-1.5 px-2 py-3 rounded-lg border text-sm font-medium transition-all',
                        active
                          ? 'bg-blue-50 border-blue-200 text-blue-700 shadow-sm'
                          : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300 hover:text-gray-700'
                      )}
                    >
                      <Icon className={cn('h-4 w-4', active ? 'text-blue-500' : 'text-gray-400')} />
                      <span className="text-[11px] font-semibold">{role.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {!isRegister && (
              <div className="text-right">
                <button
                  type="button"
                  onClick={() => navigate('/forgot-password')}
                  className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
                >
                  Forgot password?
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex items-center justify-center gap-2 w-full h-10 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                  Please wait...
                </span>
              ) : isRegister ? 'Create Account' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button
              onClick={() => navigate(isRegister ? '/login' : '/login?register=true')}
              className="text-sm text-gray-500 hover:text-gray-800 font-medium transition-colors"
            >
              {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
              <span className="text-blue-600 hover:text-blue-700">{isRegister ? 'Sign in' : 'Register'}</span>
            </button>
          </div>

          <div className="mt-6 text-center">
            <button onClick={() => navigate('/')} className="inline-flex items-center gap-1 text-xs text-gray-400 hover:text-gray-600 transition-colors">
              <ChevronLeft className="h-3 w-3" /> Back to home
            </button>
          </div>
        </div>
      </div>

      {/* Right panel — Branding */}
      <div className="hidden lg:flex lg:w-[480px] xl:w-[560px] bg-gradient-to-br from-blue-500 to-blue-600 p-10 flex-col justify-between relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-white/[0.03] rounded-full blur-2xl" />

        <div className="relative">
          <div className="flex items-center gap-2 text-white/90">
            <div className="h-7 w-7 rounded-lg bg-white/20 flex items-center justify-center text-white text-xs font-bold">A</div>
            <span className="text-sm font-semibold">Acuity</span>
          </div>
        </div>

        <div className="relative space-y-8">
          <div>
            <h2 className="text-2xl font-bold text-white leading-snug">Personalized AI learning<br />for every student.</h2>
            <p className="text-blue-100 text-sm mt-3 leading-relaxed max-w-sm">Adaptive lessons, instant feedback, and intelligent tutoring — all in one platform.</p>
          </div>

          <div className="space-y-4">
            {[
              { icon: Sparkles, text: 'AI-powered adaptive learning' },
              { icon: CheckCircle2, text: 'K-12 curriculum aligned' },
              { icon: ArrowRight, text: 'Free forever for students' },
            ].map((item, i) => {
              const Icon = item.icon
              return (
                <div key={i} className="flex items-center gap-3 text-sm text-blue-50">
                  <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/10">
                    <Icon className="h-3.5 w-3.5" />
                  </div>
                  {item.text}
                </div>
              )
            })}
          </div>
        </div>

        <div className="relative flex items-center gap-4">
          <div className="flex -space-x-2">
            {['#1E90FF', '#22C55E', '#A855F7', '#F97316'].map((color, i) => (
              <div key={i} className="h-8 w-8 rounded-full border-2 border-blue-500" style={{ backgroundColor: color }} />
            ))}
          </div>
          <div>
            <p className="text-sm font-semibold text-white">Trusted by 50K+ students</p>
            <p className="text-xs text-blue-200/70">Across 1,000+ schools</p>
          </div>
        </div>
      </div>
    </div>
  )
}
