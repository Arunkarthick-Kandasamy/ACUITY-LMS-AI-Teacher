import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Sparkles, BookOpen, BrainCircuit, Users, Shield, BarChart3, Zap, CheckCircle2, Menu, X, Globe, Trophy, Star, Play, Layers, Target, MessageSquare, ChevronRight, Clock, Flame, GraduationCap, Activity, TrendingUp, RefreshCw, Bot, Award, Medal, Laptop, Smartphone, Download, ChevronDown, HelpCircle, School, Search, ExternalLink, Bookmark, Monitor, Apple, Check } from 'lucide-react'
import { cn } from '@/lib/utils'

/* ─── Hook: Animated Counter ─── */
function useCounter(end: number, duration = 2000, startOnView = true) {
  const [count, setCount] = useState(0)
  const ref = useRef<HTMLDivElement>(null)
  const started = useRef(false)

  useEffect(() => {
    if (!startOnView) return
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true
        animate()
      }
    }, { threshold: 0.3 })
    observer.observe(el)
    return () => observer.disconnect()
  }, [end, duration])

  const animate = useCallback(() => {
    let start = 0
    const step = Math.max(1, Math.floor(end / (duration / 16)))
    const timer = setInterval(() => {
      start += step
      if (start >= end) { setCount(end); clearInterval(timer) }
      else setCount(start)
    }, 16)
  }, [end, duration])

  return { count, ref }
}

/* ─── Hook: Live Feed Simulation ─── */
const feedItems = [
  { icon: CheckCircle2, color: 'text-emerald-500 bg-emerald-50', text: 'Alex completed Quadratic Equations', time: 'just now' },
  { icon: Zap, color: 'text-blue-500 bg-blue-50', text: 'Priya scored 92% on Biology quiz', time: '1m ago' },
  { icon: Star, color: 'text-amber-500 bg-amber-50', text: 'Sarah earned "Math Whiz" badge', time: '3m ago' },
  { icon: BrainCircuit, color: 'text-purple-500 bg-purple-50', text: 'AI Tutor helped Ravi with Calculus', time: '5m ago' },
  { icon: Flame, color: 'text-orange-500 bg-orange-50', text: 'Mike reached 7-day learning streak', time: '8m ago' },
  { icon: Trophy, color: 'text-amber-500 bg-amber-50', text: 'Emma topped the weekly leaderboard', time: '12m ago' },
  { icon: BookOpen, color: 'text-green-500 bg-green-50', text: 'David started Physics: Thermodynamics', time: '15m ago' },
  { icon: Activity, color: 'text-blue-500 bg-blue-50', text: 'Ananya improved Algebra score by 15%', time: '20m ago' },
]

const subjectsData = [
  { id: 'math', name: 'Mathematics', icon: '📐', color: 'blue', lessons: 42, total: 60, progress: 70, colorHex: '#1E90FF', students: 1240, desc: 'Algebra, Geometry, Calculus' },
  { id: 'science', name: 'Science', icon: '🔬', color: 'green', lessons: 34, total: 40, progress: 85, colorHex: '#22C55E', students: 980, desc: 'Biology, Chemistry, Physics' },
  { id: 'english', name: 'English', icon: '📖', color: 'purple', lessons: 24, total: 40, progress: 60, colorHex: '#A855F7', students: 1120, desc: 'Literature, Grammar, Writing' },
  { id: 'history', name: 'History', icon: '🌍', color: 'orange', lessons: 18, total: 40, progress: 45, colorHex: '#F97316', students: 760, desc: 'World History, Civics' },
]

const subjectStyles: Record<string, { bg: string; text: string; bar: string; light: string }> = {
  blue: { bg: 'bg-blue-500', text: 'text-blue-600', bar: 'bg-blue-500', light: 'bg-blue-50' },
  green: { bg: 'bg-green-500', text: 'text-green-600', bar: 'bg-green-500', light: 'bg-green-50' },
  purple: { bg: 'bg-purple-500', text: 'text-purple-600', bar: 'bg-purple-500', light: 'bg-purple-50' },
  orange: { bg: 'bg-orange-500', text: 'text-orange-600', bar: 'bg-orange-500', light: 'bg-orange-50' },
}

const roleCards = [
  { icon: BookOpen, title: 'Students', desc: 'Learn at your own pace with an AI tutor. Personalized lessons, instant feedback, and trackable growth.', color: 'blue' },
  { icon: Users, title: 'Parents', desc: 'Stay informed with detailed insights — scores, trends, weak areas, and real-time progress reports.', color: 'green' },
  { icon: Shield, title: 'Educators', desc: 'Manage classes, assign work, track performance, and access analytics from one dashboard.', color: 'purple' },
]

const roleStyles: Record<string, { border: string; bg: string; iconBg: string; icon: string }> = {
  blue: { border: 'border-blue-100', bg: 'bg-blue-50', iconBg: 'bg-blue-100', icon: 'text-blue-600' },
  green: { border: 'border-green-100', bg: 'bg-green-50', iconBg: 'bg-green-100', icon: 'text-green-600' },
  purple: { border: 'border-purple-100', bg: 'bg-purple-50', iconBg: 'bg-purple-100', icon: 'text-purple-600' },
}

/* ─── Exam / Goal Data ─── */
const exams = [
  { id: 'jee', name: 'JEE', full: 'Joint Entrance Examination', icon: '⚙️', students: '15,200+', color: 'blue', desc: 'IIT-JEE Main & Advanced preparation with adaptive practice.' },
  { id: 'neet', name: 'NEET', full: 'National Eligibility cum Entrance Test', icon: '🩺', students: '12,800+', color: 'green', desc: 'Comprehensive biology, chemistry, and physics coverage.' },
  { id: 'cbse', name: 'CBSE', full: 'Central Board of Secondary Education', icon: '📚', students: '18,500+', color: 'purple', desc: 'Class 6-12 curriculum aligned with NCERT standards.' },
  { id: 'state', name: 'State Boards', full: 'State Board Examinations', icon: '🏛️', students: '9,400+', color: 'orange', desc: 'Maharashtra, Tamil Nadu, Karnataka, UP & more.' },
  { id: 'olympiad', name: 'Olympiad', full: 'Science & Math Olympiads', icon: '🏆', students: '6,100+', color: 'amber', desc: 'NSO, IMO, NCO, and other competitive exam prep.' },
  { id: 'upsc', name: 'UPSC', full: 'Union Public Service Commission', icon: '🇮🇳', students: '4,300+', color: 'red', desc: 'Civil services exam preparation with current affairs.' },
]

const examStyles: Record<string, { border: string; bg: string; text: string; dot: string }> = {
  blue: { border: 'border-blue-100', bg: 'bg-blue-50', text: 'text-blue-600', dot: 'bg-blue-500' },
  green: { border: 'border-green-100', bg: 'bg-green-50', text: 'text-green-600', dot: 'bg-green-500' },
  purple: { border: 'border-purple-100', bg: 'bg-purple-50', text: 'text-purple-600', dot: 'bg-purple-500' },
  orange: { border: 'border-orange-100', bg: 'bg-orange-50', text: 'text-orange-600', dot: 'bg-orange-500' },
  amber: { border: 'border-amber-100', bg: 'bg-amber-50', text: 'text-amber-600', dot: 'bg-amber-500' },
  red: { border: 'border-red-100', bg: 'bg-red-50', text: 'text-red-600', dot: 'bg-red-500' },
}

/* ─── Teachers Data ─── */
const teachers = [
  { name: 'Dr. Anita Sharma', subject: 'Physics', icon: '👩‍🔬', students: '12,400', rating: 4.9, exp: '14 years', color: 'blue' },
  { name: 'Prof. Ravi Verma', subject: 'Mathematics', icon: '👨‍🏫', students: '18,200', rating: 4.8, exp: '10 years', color: 'green' },
  { name: 'Ms. Priya Patel', subject: 'Chemistry', icon: '👩‍🔬', students: '9,800', rating: 4.9, exp: '8 years', color: 'purple' },
  { name: 'Dr. Sunil Gupta', subject: 'Biology', icon: '👨‍🔬', students: '14,600', rating: 4.7, exp: '12 years', color: 'orange' },
  { name: 'Ms. Kavita Reddy', subject: 'English Literature', icon: '👩‍🏫', students: '11,300', rating: 4.8, exp: '9 years', color: 'amber' },
  { name: 'Dr. Amit Kumar', subject: 'History & Civics', icon: '👨‍🎓', students: '7,900', rating: 4.6, exp: '15 years', color: 'red' },
]

/* ─── Results / Success Stories Data ─── */
const results = [
  { name: 'Arjun Mehta', achievement: 'JEE Advanced AIR 42', improvement: '+68%', badge: '🏅', color: 'blue', quote: 'The AI practice tests were a game-changer for my preparation.' },
  { name: 'Sneha Patel', achievement: 'NEET Rank 156', improvement: '+55%', badge: '🎯', color: 'green', quote: 'Daily adaptive quizzes helped me identify and fix weak areas.' },
  { name: 'Rahul Kumar', achievement: 'CBSE 12th — 98.4%', improvement: '+42%', color: 'purple', badge: '⭐', quote: 'Concept videos and instant feedback made complex topics easy.' },
  { name: 'Ananya Singh', achievement: 'KVPY Fellow 2025', improvement: '+71%', badge: '🔬', color: 'orange', quote: 'The mentorship and mock tests built my confidence tremendously.' },
]

/* ─── Pricing Data ─── */
const plans = [
  {
    name: 'Free', price: '0', desc: 'Perfect for getting started', popular: false, color: 'gray',
    features: ['5 lessons per month', 'Basic practice questions', 'Community study groups', 'Email support'],
    icon: GraduationCap,
  },
  {
    name: 'Pro', price: '9', desc: 'For serious learners', popular: true, color: 'blue',
    features: ['Unlimited lessons', 'Adaptive AI practice', 'Detailed analytics & reports', 'Priority support', 'Offline access', 'Custom study plans'],
    icon: Zap,
  },
  {
    name: 'School', price: '49', desc: 'For schools & districts', popular: false, color: 'purple',
    features: ['Everything in Pro', 'Teacher dashboard', 'Class management', 'Bulk student accounts', 'Admin analytics', 'Dedicated account manager', 'API access', 'Custom branding'],
    icon: School,
  },
]

/* ─── FAQ Data ─── */
const faqItems = [
  { q: 'Is Acuity really free?', a: 'Yes! Our Free plan gives you access to 5 lessons per month, basic practice questions, and community study groups — no credit card required.' },
  { q: 'How does the AI tutor work?', a: 'Flexi, our AI tutor, analyzes your responses in real-time to identify knowledge gaps and adapts explanations to your learning style. It\'s available 24/7 on web and WhatsApp.' },
  { q: 'Can parents track their child\'s progress?', a: 'Absolutely. Parents get a separate dashboard with detailed insights — time spent, scores by subject, weak areas, improvement trends, and weekly progress reports.' },
  { q: 'Is Acuity aligned with school curricula?', a: 'Yes. Our content is mapped to CBSE, ICSE, and major state board curricula across India, as well as international standards like Common Core and IB.' },
  { q: 'How do study groups work?', a: 'You can create or join study groups based on subject, exam, or grade. Groups include shared whiteboards, resource libraries, and scheduled live sessions.' },
  { q: 'Can teachers use Acuity in the classroom?', a: 'Yes! Our School plan gives teachers tools to assign work, track class performance, create custom quizzes, and access detailed analytics for every student.' },
]

/* ─── Subject Progress Ring ─── */
function ProgressRing({ progress, color, size = 44, stroke = 3.5 }: { progress: number; color: string; size?: number; stroke?: number }) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const [offset, setOffset] = useState(c)
  const circleRef = useRef<SVGCircleElement>(null)

  useEffect(() => {
    const el = circleRef.current
    if (!el) return
    const ob = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setTimeout(() => setOffset(c - (progress / 100) * c), 200)
        ob.disconnect()
      }
    }, { threshold: 0.3 })
    ob.observe(el)
    return () => ob.disconnect()
  }, [progress, c])

  return (
    <svg width={size} height={size} className="-rotate-90 shrink-0">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#f1f5f9" strokeWidth={stroke} />
      <circle ref={circleRef} cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeDasharray={c} strokeDashoffset={offset} style={{ transition: 'stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1)' }} />
    </svg>
  )
}

/* ─── Accordion Item ─── */
function AccordionItem({ q, a, open, onToggle }: { q: string; a: string; open: boolean; onToggle: () => void }) {
  return (
    <div className="border border-gray-100 rounded-xl overflow-hidden transition-all">
      <button onClick={onToggle} className="flex items-center justify-between w-full px-5 py-4 text-left hover:bg-gray-50 transition-colors">
        <span className="text-sm font-medium text-gray-900 pr-4">{q}</span>
        <ChevronDown className={cn('h-4 w-4 text-gray-400 shrink-0 transition-transform duration-200', open && 'rotate-180')} />
      </button>
      <div className={cn('overflow-hidden transition-all duration-300', open ? 'max-h-80' : 'max-h-0')}>
        <p className="px-5 pb-4 text-sm text-gray-500 leading-relaxed">{a}</p>
      </div>
    </div>
  )
}

/* ─── Feature Tabs ─── */
type TabId = 'adaptive' | 'tutor' | 'analytics' | 'collab'
const featureTabs: { id: TabId; label: string; icon: typeof Zap }[] = [
  { id: 'adaptive', label: 'Adaptive Practice', icon: Zap },
  { id: 'tutor', label: 'AI Tutor Flexi', icon: Bot },
  { id: 'analytics', label: 'Analytics', icon: TrendingUp },
  { id: 'collab', label: 'Study Groups', icon: MessageSquare },
]
const featureContent: Record<TabId, { title: string; desc: string; bullets: string[] }> = {
  adaptive: { title: 'Questions that adapt to every student', desc: 'Our AI analyzes each answer to adjust difficulty in real-time — keeping students challenged but not overwhelmed.', bullets: ['Real-time difficulty adjustment', '50,000+ question library', 'K-12 curriculum aligned', 'Instant feedback & explanations'] },
  tutor: { title: '24/7 AI tutor in 300+ languages', desc: 'Flexi helps students with homework, explains concepts, and provides step-by-step guidance — whenever they need it.', bullets: ['Available on WhatsApp & web', '300+ languages supported', 'Step-by-step explanations', 'Concept mastery tracking'] },
  analytics: { title: 'Actionable insights for everyone', desc: 'Track progress, identify gaps, and celebrate growth with detailed reports for students, parents, and teachers.', bullets: ['Live progress dashboards', 'Weak area identification', 'Trend analysis & predictions', 'Exportable reports'] },
  collab: { title: 'Learn together, grow together', desc: 'Form study groups, share resources, and collaborate on problems in real-time with peers.', bullets: ['Live study sessions', 'Resource sharing', 'Group challenges', 'Peer tutoring'] },
}

/* ─── Testimonials Data ─── */
const testimonials = [
  { quote: 'My grades improved from a C to an A in just one semester. The AI tutor explains things in a way that makes sense.', name: 'Priya S.', role: '10th Grade', rating: 5 },
  { quote: 'I can see exactly where my child is excelling and where they need help. The insights are incredible.', name: 'Rajesh M.', role: 'Parent', rating: 5 },
  { quote: 'This platform transformed my classroom. Every student gets personalized content at their level.', name: 'Dr. Anita K.', role: 'Science Teacher', rating: 5 },
  { quote: 'The adaptive practice questions are genius. They always know exactly what I need to work on.', name: 'Arjun P.', role: '12th Grade', rating: 5 },
]

/* ═══════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════ */
export function LandingPage() {
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [selectedSubject, setSelectedSubject] = useState(subjectsData[0])
  const [activeTab, setActiveTab] = useState<TabId>('adaptive')
  const [testimonialIdx, setTestimonialIdx] = useState(0)
  const [feed, setFeed] = useState(feedItems.slice(0, 4))
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)
  const feedIdx = useRef(4)

  /* Live feed rotation */
  useEffect(() => {
    const t = setInterval(() => {
      setFeed(prev => {
        const next = [...prev.slice(1), feedItems[feedIdx.current % feedItems.length]]
        feedIdx.current++
        return next
      })
    }, 4000)
    return () => clearInterval(t)
  }, [])

  /* Testimonial rotation */
  useEffect(() => {
    const t = setInterval(() => setTestimonialIdx(i => (i + 1) % testimonials.length), 5000)
    return () => clearInterval(t)
  }, [])

  const t = testimonials[testimonialIdx]

  /* Counters */
  const students = useCounter(50240)
  const lessons = useCounter(12850)
  const schools = useCounter(1120)
  const ratings = useCounter(97)

  return (
    <div className="min-h-screen bg-white">
      {/* ═══ Nav ═══ */}
      <nav className="sticky top-0 z-50 border-b border-gray-100 bg-white/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold shadow-sm">A</div>
            <span className="text-sm font-semibold text-gray-900">Acuity</span>
          </div>
          <div className="hidden md:flex items-center gap-1">
            {['Dashboard', 'Courses', 'For Schools'].map(item => (
              <button key={item} className="text-sm text-gray-500 hover:text-gray-800 px-3 py-2 rounded-lg hover:bg-gray-50 transition-all font-medium">{item}</button>
            ))}
          </div>
          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/login')} className="text-sm text-gray-600 hover:text-gray-900 font-medium px-4 py-2 rounded-lg hover:bg-gray-50 transition-all hidden sm:inline">Sign In</button>
            <button onClick={() => navigate('/login?register=true')} className="text-sm bg-gray-900 text-white px-5 py-2 rounded-lg hover:bg-gray-800 transition-all shadow-sm font-medium flex items-center gap-1.5">
              Get Started <ArrowRight className="h-3.5 w-3.5" />
            </button>
            <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden p-2 -mr-2 rounded-lg hover:bg-gray-100 transition-colors">
              {mobileOpen ? <X className="h-4.5 w-4.5 text-gray-500" /> : <Menu className="h-4.5 w-4.5 text-gray-500" />}
            </button>
          </div>
        </div>
        {mobileOpen && (
          <div className="md:hidden border-t border-gray-100 bg-white px-4 py-2 space-y-1">
            {['Dashboard', 'Courses', 'For Schools'].map(item => (
              <button key={item} className="block w-full text-left text-sm text-gray-600 px-3 py-2 rounded-lg hover:bg-gray-50">{item}</button>
            ))}
            <button onClick={() => navigate('/login')} className="block w-full text-left text-sm text-gray-600 px-3 py-2 rounded-lg hover:bg-gray-50">Sign In</button>
          </div>
        )}
      </nav>

      {/* ═══ Hero Section: Dynamic Dashboard Preview ═══ */}
      <section className="relative overflow-hidden border-b border-gray-100">
        <div className="absolute inset-0 bg-gradient-to-b from-blue-50/50 via-white to-white" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-b from-blue-100/20 to-transparent rounded-full blur-3xl" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 pt-12 sm:pt-16 pb-16 sm:pb-20">
          <div className="grid lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 mb-5">
                <Activity className="h-3.5 w-3.5 text-blue-500" />
                <span className="text-xs font-medium text-blue-600">Live Dashboard — {new Date().toLocaleDateString()}</span>
              </div>
              <h1 className="text-4xl sm:text-5xl font-bold text-gray-900 leading-[1.08] tracking-tight mb-3">
                Your Learning<br />
                <span className="bg-gradient-to-r from-blue-600 to-blue-500 bg-clip-text text-transparent">Command Center</span>
              </h1>
              <p className="text-base sm:text-lg text-gray-400 leading-relaxed max-w-lg mb-6">
                One dashboard to track progress, discover lessons, and master subjects — powered by AI that adapts to you.
              </p>
              <div className="flex items-center gap-3 flex-wrap mb-8">
                <button onClick={() => navigate('/login?register=true')} className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-all shadow-sm font-medium text-sm">
                  Start Learning Free <ArrowRight className="h-4 w-4" />
                </button>
                <button onClick={() => navigate('/courses')} className="inline-flex items-center gap-2 px-6 py-3 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 hover:border-gray-300 transition-all font-medium text-sm">
                  <Play className="h-4 w-4" /> Watch Demo
                </button>
              </div>
              <div className="flex items-center gap-4 sm:gap-6 text-xs text-gray-400">
                <span className="flex items-center gap-1.5"><CheckCircle2 className="h-3.5 w-3.5 text-green-500" /> Free forever</span>
                <span className="flex items-center gap-1.5"><Globe className="h-3.5 w-3.5 text-blue-500" /> 300+ languages</span>
                <span className="flex items-center gap-1.5"><Trophy className="h-3.5 w-3.5 text-amber-500" /> K-12 aligned</span>
              </div>
            </div>

            {/* Live Dashboard Preview */}
            <div className="relative">
              <div className="rounded-2xl border border-gray-200 bg-white shadow-xl shadow-gray-200/50 overflow-hidden">
                <div className="flex items-center justify-between px-4 h-9 bg-gray-50 border-b border-gray-100">
                  <div className="flex gap-1.5"><div className="h-2.5 w-2.5 rounded-full bg-red-400" /><div className="h-2.5 w-2.5 rounded-full bg-amber-400" /><div className="h-2.5 w-2.5 rounded-full bg-green-400" /></div>
                  <span className="text-[10px] text-gray-400 font-medium">student.acuity.com/dashboard</span>
                  <RefreshCw className="h-3 w-3 text-gray-300 animate-spin-slow" />
                </div>
                <div className="p-5 space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-bold">A</div>
                      <div><p className="text-sm font-semibold text-gray-900">Alex Chen</p><p className="text-xs text-gray-400">Grade 10 &middot; Lincoln High</p></div>
                    </div>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 text-[10px] font-medium text-green-600"><span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" /> Active Now</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {[{ label: 'Streak', value: '🔥 7 days', up: true }, { label: 'This Week', value: '12 hrs', up: true }, { label: 'Mastery', value: '78%', up: true }].map(s => (
                      <div key={s.label} className="rounded-lg bg-gray-50 px-3 py-2 text-center">
                        <p className="text-[10px] text-gray-400">{s.label}</p>
                        <p className="text-sm font-bold text-gray-900">{s.value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="space-y-2">
                    {subjectsData.slice(0, 3).map(sub => (
                      <div key={sub.id} className="flex items-center gap-3">
                        <span className="text-xs w-16 text-gray-500 font-medium truncate">{sub.name}</span>
                        <div className="flex-1 h-2 rounded-full bg-gray-100 overflow-hidden">
                          <div className={cn('h-full rounded-full transition-all duration-1000', subjectStyles[sub.color].bar)} style={{ width: `${sub.progress}%` }} />
                        </div>
                        <span className={cn('text-[10px] font-semibold w-8 text-right', subjectStyles[sub.color].text)}>{sub.progress}%</span>
                      </div>
                    ))}
                  </div>
                  <div className="rounded-lg bg-gray-50 p-3">
                    <div className="flex items-center gap-2 text-[10px] text-gray-500 mb-2"><Activity className="h-3 w-3 text-blue-500" /> Live Activity</div>
                    <div className="space-y-1.5 h-20 overflow-hidden">
                      {feed.slice(0, 3).map((item, i) => (
                        <div key={i} className="flex items-center gap-2 text-[11px]">
                          <div className={cn('flex h-5 w-5 items-center justify-center rounded', item.color.split(' ')[1])}><item.icon className={cn('h-3 w-3', item.color.split(' ')[0])} /></div>
                          <span className="text-gray-600 truncate flex-1">{item.text}</span>
                          <span className="text-gray-400 shrink-0">{item.time}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              <div className="absolute -bottom-3 -right-3 w-48 h-48 bg-blue-100/20 rounded-full blur-3xl pointer-events-none" />
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Live Stats Counters ═══ */}
      <section className="border-b border-gray-100 bg-gray-50/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-10">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8" ref={students.ref}>
            {[
              { value: students.count, label: 'Active Students', suffix: '+', icon: Users },
              { value: lessons.count, label: 'Lessons Completed', suffix: '+', icon: BookOpen },
              { value: schools.count, label: 'Schools', suffix: '+', icon: GraduationCap },
              { value: ratings.count, label: 'Mastery Rate', suffix: '%', icon: TrendingUp },
            ].map((stat, i) => {
              const Icon = stat.icon
              return (
                <div key={i} className="text-center group">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600 mx-auto mb-3 group-hover:scale-110 transition-transform"><Icon className="h-5 w-5" /></div>
                  <p className="text-2xl sm:text-3xl font-bold text-gray-900 tabular-nums">{stat.value.toLocaleString()}{stat.suffix}</p>
                  <p className="text-sm text-gray-400 mt-1">{stat.label}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ═══ Exam / Goal Selector (Unacademy pattern) ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">What Are You Preparing For?</h2>
            <p className="text-sm text-gray-400 mt-2">Choose your goal and get a personalized learning path.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {exams.map(exam => {
              const s = examStyles[exam.color]
              return (
                <button key={exam.id} onClick={() => navigate('/login?register=true')}
                  className={cn('group relative rounded-xl border p-5 text-left transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 bg-white', s.border)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className={cn('flex h-10 w-10 items-center justify-center rounded-lg text-base', s.bg)}>{exam.icon}</div>
                    <span className={cn('flex items-center gap-1 text-[10px] font-medium', s.text)}>
                      <Users className="h-3 w-3" /> {exam.students}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-gray-900 mb-0.5">{exam.name}</h3>
                  <p className="text-[11px] text-gray-400 mb-2">{exam.full}</p>
                  <p className="text-xs text-gray-500 leading-relaxed">{exam.desc}</p>
                  <div className="mt-3 flex items-center gap-1.5 text-xs font-medium text-gray-700 group-hover:text-blue-600 transition-colors">
                    Explore Path <ChevronRight className="h-3 w-3" />
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </section>

      {/* ═══ Interactive Subject Explorer ═══ */}
      <section className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Explore Subjects</h2>
            <p className="text-sm text-gray-400 mt-2">Click on a subject to see detailed progress and stats.</p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
            {subjectsData.map(sub => {
              const active = selectedSubject.id === sub.id
              const s = subjectStyles[sub.color]
              return (
                <button key={sub.id} onClick={() => setSelectedSubject(sub)}
                  className={cn('flex items-center gap-3 rounded-xl border p-3.5 transition-all', active ? 'border-gray-300 bg-white shadow-sm' : 'border-gray-100 bg-gray-50/50 hover:bg-white hover:border-gray-200')}
                >
                  <div className={cn('flex h-9 w-9 items-center justify-center rounded-lg text-base shrink-0', s.light)}>{sub.icon}</div>
                  <div className="text-left flex-1 min-w-0">
                    <p className={cn('text-sm font-semibold truncate', active ? 'text-gray-900' : 'text-gray-600')}>{sub.name}</p>
                    <p className="text-[10px] text-gray-400">{sub.students.toLocaleString()} students</p>
                  </div>
                  <ProgressRing progress={sub.progress} color={sub.colorHex} size={32} stroke={3} />
                </button>
              )
            })}
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-6 transition-all duration-300">
            <div className="grid sm:grid-cols-2 gap-6 items-center">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className={cn('flex h-10 w-10 items-center justify-center rounded-lg text-lg', subjectStyles[selectedSubject.color].light)}>{selectedSubject.icon}</div>
                  <div><h3 className="text-lg font-semibold text-gray-900">{selectedSubject.name}</h3><p className="text-xs text-gray-400">{selectedSubject.desc}</p></div>
                </div>
                <div className="space-y-3 mt-4">
                  <div className="flex justify-between text-sm"><span className="text-gray-500">Progress</span><span className={cn('font-semibold', subjectStyles[selectedSubject.color].text)}>{selectedSubject.progress}%</span></div>
                  <div className="h-2 rounded-full bg-gray-100 overflow-hidden"><div className={cn('h-full rounded-full transition-all duration-1000', subjectStyles[selectedSubject.color].bar)} style={{ width: `${selectedSubject.progress}%` }} /></div>
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    {[{ label: 'Lessons', value: `${selectedSubject.lessons}/${selectedSubject.total}` }, { label: 'Students', value: selectedSubject.students.toLocaleString() }, { label: 'Completion', value: `${selectedSubject.progress}%` }].map(d => (
                      <div key={d.label} className="rounded-lg bg-gray-50 px-3 py-2.5 text-center"><p className="text-xs text-gray-400">{d.label}</p><p className="text-sm font-bold text-gray-900">{d.value}</p></div>
                    ))}
                  </div>
                </div>
              </div>
              <div className="rounded-xl bg-gray-50 p-5">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Recommended for you</p>
                <div className="space-y-2">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-white border border-gray-100 hover:border-gray-200 transition-colors cursor-pointer">
                      <Play className={cn('h-4 w-4', subjectStyles[selectedSubject.color].text)} />
                      <div className="flex-1"><p className="text-sm font-medium text-gray-800">Lesson {i}: Core Concepts</p><p className="text-xs text-gray-400">{10 + i * 5} min</p></div>
                      <ChevronRight className="h-4 w-4 text-gray-300" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Live Feed Section ═══ */}
      <section className="py-16 sm:py-20 bg-gray-50/70 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid lg:grid-cols-3 gap-8 items-start">
            <div className="lg:col-span-1">
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Live Across<br />the Platform</h2>
              <p className="text-sm text-gray-400 mt-2">Real-time activity from students learning right now.</p>
              <div className="flex items-center gap-2 mt-4 text-xs text-green-600"><span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" /> {Math.floor(120 + Math.random() * 80)} active now</div>
            </div>
            <div className="lg:col-span-2">
              <div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-4"><Activity className="h-3.5 w-3.5 text-blue-500" /> Live Activity Feed <span className="text-gray-300">—</span> <span className="text-green-500 font-medium">updating live</span></div>
                <div className="space-y-1">
                  {feed.map((item, i) => (
                    <div key={i} className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-gray-50 transition-colors">
                      <div className={cn('flex h-8 w-8 items-center justify-center rounded-lg', item.color.split(' ')[1])}><item.icon className={cn('h-4 w-4', item.color.split(' ')[0])} /></div>
                      <div className="flex-1"><p className="text-sm text-gray-700">{item.text}</p></div>
                      <span className="text-[10px] text-gray-400 shrink-0">{item.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Personalized Demo Booking (BYJU'S pattern) ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 mb-4">
                <Sparkles className="h-3.5 w-3.5 text-blue-500" />
                <span className="text-xs font-medium text-blue-600">Free Demo Class</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight mb-3">See Acuity in Action</h2>
              <p className="text-sm text-gray-400 leading-relaxed mb-6">Book a free 1-on-1 demo with our learning advisors. We'll show you exactly how Acuity works for your grade and goals.</p>
              <div className="space-y-3">
                {[
                  { icon: CheckCircle2, text: 'Personalized platform walkthrough' },
                  { icon: CheckCircle2, text: 'Sample AI tutoring session' },
                  { icon: CheckCircle2, text: 'Curriculum alignment check' },
                  { icon: CheckCircle2, text: 'No commitment, free forever' },
                ].map((item, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm text-gray-600">
                    <item.icon className="h-4 w-4 text-green-500 shrink-0" />
                    {item.text}
                  </div>
                ))}
              </div>
            </div>
            <div className="rounded-xl border border-gray-200 bg-white p-6 sm:p-8 shadow-sm">
              <h3 className="text-base font-semibold text-gray-900 mb-4">Book Your Free Demo</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Full Name</label>
                  <input type="text" placeholder="e.g. Priya Sharma" className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all placeholder:text-gray-300" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Email Address</label>
                  <input type="email" placeholder="priya@example.com" className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all placeholder:text-gray-300" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Phone Number</label>
                  <input type="tel" placeholder="+91 98765 43210" className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all placeholder:text-gray-300" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Grade / Class</label>
                  <select className="w-full px-3.5 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all bg-white text-gray-500">
                    <option>Select grade</option>
                    {[6,7,8,9,10,11,12].map(g => <option key={g}>Class {g}</option>)}
                  </select>
                </div>
                <button className="w-full inline-flex items-center justify-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-all font-medium text-sm mt-1">
                  Book Free Demo <ArrowRight className="h-4 w-4" />
                </button>
                <p className="text-[10px] text-gray-400 text-center">Free &middot; No spam &middot; 30-min session</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Interactive Feature Tabs ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10"><h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Platform Features</h2><p className="text-sm text-gray-400 mt-2">Click through to explore each capability.</p></div>
          <div className="flex flex-wrap justify-center gap-1 mb-8">
            {featureTabs.map(tab => {
              const Icon = tab.icon
              return (
                <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                  className={cn('flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all', activeTab === tab.id ? 'bg-gray-900 text-white shadow-sm' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100')}
                ><Icon className="h-4 w-4" /> {tab.label}</button>
              )
            })}
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-6 sm:p-8 shadow-sm">
            <div className="grid sm:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{featureContent[activeTab].title}</h3>
                <p className="text-sm text-gray-400 mb-5">{featureContent[activeTab].desc}</p>
                <ul className="space-y-2.5">
                  {featureContent[activeTab].bullets.map((b, i) => (
                    <li key={i} className="flex items-center gap-2.5 text-sm text-gray-600"><CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />{b}</li>
                  ))}
                </ul>
              </div>
              <div className="rounded-xl bg-gray-50 p-6 flex items-center justify-center min-h-[200px]">
                <div className="text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-100 text-blue-600 mx-auto mb-3">
                    {activeTab === 'adaptive' && <Zap className="h-8 w-8" />}
                    {activeTab === 'tutor' && <Bot className="h-8 w-8" />}
                    {activeTab === 'analytics' && <BarChart3 className="h-8 w-8" />}
                    {activeTab === 'collab' && <Users className="h-8 w-8" />}
                  </div>
                  <p className="text-sm font-semibold text-gray-900">{featureContent[activeTab].title}</p>
                  <p className="text-xs text-gray-400 mt-1">Click the tab to explore</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Teacher / Educator Showcase (Unacademy pattern) ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Learn from the Best</h2>
            <p className="text-sm text-gray-400 mt-2">Expert educators with years of experience in their fields.</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {teachers.map((teacher, i) => {
              const s = examStyles[teacher.color] || examStyles.blue
              return (
                <div key={i} className="group rounded-xl border border-gray-200 bg-white p-5 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={cn('flex h-11 w-11 items-center justify-center rounded-full text-base shrink-0', s.bg)}>{teacher.icon}</div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-gray-900 truncate">{teacher.name}</p>
                      <p className="text-xs text-gray-400">{teacher.subject}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500 mt-3 pt-3 border-t border-gray-50">
                    <span className="flex items-center gap-1"><Users className="h-3 w-3" /> {teacher.students} students</span>
                    <span className="flex items-center gap-1"><Star className="h-3 w-3 fill-amber-400 text-amber-400" /> {teacher.rating}</span>
                    <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {teacher.exp}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ═══ Results / Report Cards (Vedantu pattern) ═══ */}
      <section className="py-16 sm:py-20 bg-gray-50/70 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Student Success Stories</h2>
            <p className="text-sm text-gray-400 mt-2">Real results from real students who used Acuity to achieve their goals.</p>
          </div>
          <div className="grid sm:grid-cols-2 gap-5">
            {results.map((r, i) => (
              <div key={i} className="group rounded-xl border border-gray-200 bg-white p-6 hover:shadow-md hover:-translate-y-0.5 transition-all duration-200">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className={cn('flex h-10 w-10 items-center justify-center rounded-full text-base', examStyles[r.color]?.bg || 'bg-blue-50')}>{r.badge}</div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{r.name}</p>
                      <p className={cn('text-xs font-medium', examStyles[r.color]?.text || 'text-blue-600')}>{r.achievement}</p>
                    </div>
                  </div>
                  <span className={cn('inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full', examStyles[r.color]?.bg || 'bg-blue-50', examStyles[r.color]?.text || 'text-blue-600')}>
                    <TrendingUp className="h-3 w-3" /> {r.improvement}
                  </span>
                </div>
                <p className="text-sm text-gray-500 leading-relaxed">&ldquo;{r.quote}&rdquo;</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ Role Cards ═══ */}
      <section className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10"><h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Designed for Everyone</h2><p className="text-sm text-gray-400 mt-2">Students, parents, and educators — all connected.</p></div>
          <div className="grid sm:grid-cols-3 gap-5">
            {roleCards.map((item, i) => {
              const Icon = item.icon; const s = roleStyles[item.color]
              return (
                <div key={i} className={cn('group rounded-xl border p-6 transition-all duration-200 hover:shadow-md hover:-translate-y-0.5', s.border, s.bg)}>
                  <div className={cn('flex h-11 w-11 items-center justify-center rounded-lg mb-4 transition-transform group-hover:scale-110', s.iconBg)}><Icon className={cn('h-5.5 w-5.5', s.icon)} /></div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-1.5">{item.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{item.desc}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ═══ Animated Testimonials ═══ */}
      <section className="py-16 sm:py-20 bg-gray-50/70 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10"><h2 className="text-2xl sm:text-3xl font-bold text-gray-900">What People Say</h2><p className="text-sm text-gray-400 mt-2">Real stories from real learners.</p></div>
          <div className="max-w-2xl mx-auto">
            <div className="rounded-xl border border-gray-200 bg-white p-8 shadow-sm text-center transition-all duration-500">
              <div className="flex justify-center gap-1 mb-4">{Array.from({ length: t.rating }).map((_, i) => <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" />)}</div>
              <p className="text-base sm:text-lg text-gray-700 leading-relaxed italic">&ldquo;{t.quote}&rdquo;</p>
              <div className="mt-6 pt-4 border-t border-gray-100">
                <p className="text-sm font-semibold text-gray-900">{t.name}</p>
                <p className="text-xs text-gray-400">{t.role}</p>
              </div>
              <div className="flex justify-center gap-2 mt-4">
                {testimonials.map((_, i) => (
                  <button key={i} onClick={() => setTestimonialIdx(i)} className={cn('h-2 rounded-full transition-all', i === testimonialIdx ? 'w-6 bg-gray-900' : 'w-2 bg-gray-300 hover:bg-gray-400')} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Pricing / Subscription (edX / Coursera pattern) ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Simple, Transparent Pricing</h2>
            <p className="text-sm text-gray-400 mt-2">Start free, upgrade when you need more.</p>
          </div>
          <div className="grid sm:grid-cols-3 gap-5 max-w-4xl mx-auto">
            {plans.map((plan, i) => {
              const Icon = plan.icon
              return (
                <div key={i} className={cn('relative rounded-xl border p-6 transition-all duration-200 hover:shadow-md', plan.popular ? 'border-blue-200 bg-blue-50/30 shadow-sm' : 'border-gray-200 bg-white')}>
                  {plan.popular && (
                    <div className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-blue-500 text-white text-[10px] font-semibold rounded-full shadow-sm">Most Popular</div>
                  )}
                  <div className={cn('flex h-10 w-10 items-center justify-center rounded-lg mb-4', plan.popular ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600')}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-1">{plan.name}</h3>
                  <div className="flex items-baseline gap-1 mb-1">
                    <span className="text-2xl font-bold text-gray-900">${plan.price}</span>
                    <span className="text-xs text-gray-400">/month</span>
                  </div>
                  <p className="text-xs text-gray-400 mb-4">{plan.desc}</p>
                  <ul className="space-y-2 mb-6">
                    {plan.features.map((f, j) => (
                      <li key={j} className="flex items-center gap-2 text-xs text-gray-600">
                        <Check className="h-3.5 w-3.5 text-green-500 shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  <button onClick={() => navigate('/login?register=true')}
                    className={cn('w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all', plan.popular ? 'bg-blue-500 text-white hover:bg-blue-600 shadow-sm' : 'border border-gray-200 text-gray-700 hover:bg-gray-50')}
                  >
                    {plan.name === 'Free' ? 'Get Started' : 'Start Free Trial'}
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* ═══ FAQ Accordion (Coursera pattern) ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-10">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">Frequently Asked Questions</h2>
            <p className="text-sm text-gray-400 mt-2">Everything you need to know about Acuity.</p>
          </div>
          <div className="max-w-2xl mx-auto space-y-2.5">
            {faqItems.map((item, i) => (
              <AccordionItem key={i} q={item.q} a={item.a} open={expandedFaq === i} onToggle={() => setExpandedFaq(expandedFaq === i ? null : i)} />
            ))}
          </div>
        </div>
      </section>

      {/* ═══ App Download CTA (Duolingo / Unacademy pattern) ═══ */}
      <section className="py-16 sm:py-20 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-10 items-center">
            <div>
              <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-tight mb-3">Learn Anytime,<br />Anywhere</h2>
              <p className="text-sm text-gray-400 leading-relaxed mb-6">Take Acuity with you. Download the app and keep learning on the go — offline lessons, mobile practice, and AI tutor in your pocket.</p>
              <div className="flex flex-col sm:flex-row gap-3 mb-6">
                <button className="inline-flex items-center gap-3 px-5 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-all shadow-sm">
                  <Apple className="h-5 w-5" />
                  <div className="text-left">
                    <p className="text-[10px] text-gray-400 leading-tight">Download on the</p>
                    <p className="text-sm font-semibold leading-tight">App Store</p>
                  </div>
                </button>
                <button className="inline-flex items-center gap-3 px-5 py-3 bg-gray-900 text-white rounded-xl hover:bg-gray-800 transition-all shadow-sm">
                  <Smartphone className="h-5 w-5" />
                  <div className="text-left">
                    <p className="text-[10px] text-gray-400 leading-tight">Get it on</p>
                    <p className="text-sm font-semibold leading-tight">Google Play</p>
                  </div>
                </button>
              </div>
              <div className="flex items-center gap-6 text-xs text-gray-400">
                <span className="flex items-center gap-1.5"><Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> 4.8 App Store</span>
                <span className="flex items-center gap-1.5"><Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" /> 4.7 Play Store</span>
                <span className="flex items-center gap-1.5"><Download className="h-3.5 w-3.5" /> 100K+ downloads</span>
              </div>
            </div>
            <div className="flex justify-center">
              <div className="relative w-56 h-[360px] rounded-[2rem] border-[3px] border-gray-200 bg-gray-50 overflow-hidden shadow-xl">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-5 bg-gray-200 rounded-b-xl" />
                <div className="absolute top-6 left-0 right-0 bottom-0 flex flex-col items-center justify-center p-5">
                  <div className="h-10 w-10 rounded-xl bg-blue-500 flex items-center justify-center text-white text-sm font-bold mb-3 shadow-sm">A</div>
                  <p className="text-xs font-semibold text-gray-900 mb-1">Acuity Learning</p>
                  <p className="text-[10px] text-gray-400 mb-4">Your AI learning companion</p>
                  <div className="w-full space-y-2">
                    <div className="h-2 rounded-full bg-blue-100 overflow-hidden"><div className="h-full w-3/4 rounded-full bg-blue-500" /></div>
                    <div className="h-2 rounded-full bg-green-100 overflow-hidden"><div className="h-full w-4/5 rounded-full bg-green-500" /></div>
                    <div className="h-2 rounded-full bg-purple-100 overflow-hidden"><div className="h-full w-3/5 rounded-full bg-purple-500" /></div>
                  </div>
                  <p className="text-[10px] text-gray-400 mt-4 text-center">Math &middot; Science &middot; English</p>
                  <div className="flex gap-1 mt-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-300" />
                    <span className="h-1.5 w-1.5 rounded-full bg-gray-300" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ CTA ═══ */}
      <section className="py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="relative overflow-hidden rounded-2xl bg-gray-900 px-8 py-14 sm:px-14 sm:py-18 text-center">
            <div className="absolute -top-20 -right-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-20 -left-20 w-72 h-72 bg-blue-500/5 rounded-full blur-3xl" />
            <div className="relative">
              <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">Start Your Learning Journey</h2>
              <p className="text-gray-400 text-sm mb-6 max-w-md mx-auto">Join 50,000+ students getting a personalized, AI-powered education — free forever.</p>
              <button onClick={() => navigate('/login?register=true')} className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 rounded-xl hover:bg-gray-100 transition-all font-medium text-sm shadow-sm">
                Create Free Account <ArrowRight className="h-4 w-4" />
              </button>
              <p className="text-gray-500 text-xs mt-4">No credit card &middot; No contracts &middot; Free forever</p>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ Footer ═══ */}
      <footer className="border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2"><div className="h-6 w-6 rounded bg-gray-900 flex items-center justify-center text-white text-[9px] font-bold">A</div><span className="text-xs font-semibold text-gray-700">Acuity Learning Hub</span></div>
            <div className="flex items-center gap-6 text-xs text-gray-400">
              <button className="hover:text-gray-600 transition-colors">Privacy</button>
              <button className="hover:text-gray-600 transition-colors">Terms</button>
              <button className="hover:text-gray-600 transition-colors">Contact</button>
            </div>
            <p className="text-xs text-gray-400">&copy; 2026 Acuity Learning Hub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
