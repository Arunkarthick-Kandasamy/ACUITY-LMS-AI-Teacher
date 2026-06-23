import { useNavigate } from 'react-router-dom'
import { GraduationCap, ArrowRight, Sparkles, BookOpen, BrainCircuit, Users, Shield } from 'lucide-react'

export function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white">
      {/* Nav */}
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-navy-800" />
            <span className="text-lg font-bold text-navy-800">Acuity</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/login')} className="text-sm text-slate-600 hover:text-slate-900 font-medium px-4 py-2">
              Sign In
            </button>
            <button onClick={() => navigate('/login?register=true')} className="text-sm bg-navy-800 text-white px-4 py-2 rounded-lg hover:bg-navy-700 transition-all shadow-sm font-medium">
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-4 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-navy-50 border border-navy-200 mb-6">
          <Sparkles className="w-3.5 h-3.5 text-navy-600" />
          <span className="text-xs font-medium text-navy-600">AI-Powered Personalized Learning</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-navy-900 leading-tight mb-4">
          Where Accuracy<br />Meets Knowledge
        </h1>
        <p className="text-lg text-slate-600 max-w-xl mx-auto mb-8 leading-relaxed">
          An AI-powered platform that adapts to each student's unique learning pace, 
          delivering personalized lessons and real-time feedback at scale.
        </p>
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => navigate('/login?register=true')}
            className="inline-flex items-center gap-2 px-6 py-3 bg-navy-800 text-white rounded-xl hover:bg-navy-700 transition-all shadow-md font-medium"
          >
            Start Learning
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => navigate('/login')}
            className="inline-flex items-center gap-2 px-6 py-3 border border-slate-300 rounded-xl text-slate-700 hover:bg-slate-50 transition-all font-medium"
          >
            Watch Demo
          </button>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-navy-900 mb-12">How Acuity Works</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: BrainCircuit, title: 'AI Assesses', desc: 'Student completes a gamified module. AI analyzes correctness, speed, retries, and skips to generate an Open Score.' },
            { icon: BookOpen, title: 'AI Adapts', desc: 'Based on the score, the system classifies the learner and delivers personalized content — advanced or foundational.' },
            { icon: Users, title: 'AI Improves', desc: 'After each lesson, the score updates. The system continuously adapts, tracks progress, and provides insights.' },
          ].map((item, i) => {
            const Icon = item.icon
            return (
              <div key={i} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow">
                <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-navy-700" />
                </div>
                <h3 className="font-semibold text-navy-900 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{item.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* Roles */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-navy-900 mb-12">For Everyone in Education</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {[
            { icon: BookOpen, title: 'Students', desc: 'Learn at your own pace with an AI tutor that adapts to you. Get personalized lessons, instant feedback, and track your growth.', color: 'bg-emerald-50 border-emerald-200', iconBg: 'bg-emerald-100 text-emerald-700' },
            { icon: Users, title: 'Parents', desc: 'Stay informed with detailed insights — scores, trends, weak areas, learning behavior, and real-time progress reports.', color: 'bg-blue-50 border-blue-200', iconBg: 'bg-blue-100 text-blue-700' },
            { icon: Shield, title: 'Admin', desc: 'Monitor platform usage, track student performance, manage users, and access system-wide analytics from one dashboard.', color: 'bg-purple-50 border-purple-200', iconBg: 'bg-purple-100 text-purple-700' },
          ].map((item, i) => {
            const Icon = item.icon
            return (
              <div key={i} className={`rounded-xl border p-6 ${item.color}`}>
                <div className={`w-10 h-10 rounded-lg ${item.iconBg} flex items-center justify-center mb-4`}>
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-navy-900 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{item.desc}</p>
              </div>
            )
          })}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-6xl mx-auto px-4 py-16 text-center">
        <div className="bg-navy-900 rounded-2xl p-12">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">
            Ready to Transform Learning?
          </h2>
          <p className="text-navy-200 mb-6 max-w-lg mx-auto text-sm">
            Join thousands of students getting personalized AI-powered education.
          </p>
          <button
            onClick={() => navigate('/login?register=true')}
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-navy-900 rounded-xl hover:bg-slate-100 transition-all font-medium shadow-md"
          >
            Get Started Free
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">
        &copy; 2026 Acuity Learning Hub. All rights reserved.
      </footer>
    </div>
  )
}
