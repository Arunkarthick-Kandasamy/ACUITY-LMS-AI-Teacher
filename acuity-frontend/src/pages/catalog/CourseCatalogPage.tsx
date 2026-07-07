import { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { GraduationCap, Search, Clock, BookOpen, Layers, ArrowRight, ChevronLeft, ChevronRight } from 'lucide-react'
import { localDb } from '@/services/localDb'
import type { Course } from '@/services/types'

export function CourseCatalogPage() {
  const navigate = useNavigate()
  const [courses, setCourses] = useState<Course[]>([])
  const [page, setPage] = useState(1)
  const [perPage] = useState(12)
  const [search, setSearch] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [loading, setLoading] = useState(true)

  const fetchCourses = useCallback(async () => {
    setLoading(true)
    const res = await localDb.getCourses()
    setCourses(res.data)
    setLoading(false)
  }, [])

  useEffect(() => { fetchCourses() }, [fetchCourses])

  const filtered = courses.filter(c =>
    !search || c.title.toLowerCase().includes(search.toLowerCase()) || c.code.toLowerCase().includes(search.toLowerCase())
  )

  const paged = filtered.slice((page - 1) * perPage, page * perPage)
  const totalPages = Math.ceil(filtered.length / perPage)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setSearch(searchInput)
    setPage(1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white">
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-6 h-6 text-navy-800" />
            <span className="text-lg font-bold text-navy-800">Acuity</span>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={() => navigate('/login')} className="text-sm text-slate-600 hover:text-slate-900 font-medium px-4 py-2">Sign In</button>
            <button onClick={() => navigate('/login?register=true')} className="text-sm bg-navy-800 text-white px-4 py-2 rounded-lg hover:bg-navy-700 transition-all shadow-sm font-medium">Get Started</button>
          </div>
        </div>
      </nav>

      <section className="max-w-6xl mx-auto px-4 pt-12 pb-8">
        <h1 className="text-3xl font-bold text-navy-900 mb-2">Course Catalog</h1>
        <p className="text-slate-600">Explore our AI-powered courses and start learning today.</p>
      </section>

      <section className="max-w-6xl mx-auto px-4 pb-8">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input type="text" value={searchInput} onChange={(e) => setSearchInput(e.target.value)} placeholder="Search courses..." className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-navy-800/20 focus:border-navy-800" />
          </div>
          <button type="submit" className="px-5 py-2.5 bg-navy-800 text-white rounded-xl hover:bg-navy-700 transition-all text-sm font-medium shadow-sm">Search</button>
        </form>
      </section>

      <section className="max-w-6xl mx-auto px-4 pb-12">
        {loading ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl border border-slate-200 p-6 animate-pulse">
                <div className="h-5 bg-slate-200 rounded w-3/4 mb-3" />
                <div className="h-4 bg-slate-200 rounded w-full mb-2" />
                <div className="h-4 bg-slate-200 rounded w-2/3 mb-4" />
                <div className="flex gap-4"><div className="h-4 bg-slate-200 rounded w-20" /><div className="h-4 bg-slate-200 rounded w-20" /></div>
              </div>
            ))}
          </div>
        ) : paged.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-12 h-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-600 mb-1">No courses found</h3>
            <p className="text-sm text-slate-400">Try a different search term or check back later.</p>
          </div>
        ) : (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {paged.map((course) => (
                <div key={course.course_id} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-all flex flex-col">
                  <div className="flex-1">
                    <h3 className="font-semibold text-navy-900 mb-2 leading-snug">{course.title}</h3>
                    {course.description && <p className="text-sm text-slate-600 mb-4 line-clamp-2">{course.description}</p>}
                    <div className="flex flex-wrap gap-4 text-xs text-slate-500 mb-4">
                      <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" />{course.total_duration_hours}h</span>
                      <span className="flex items-center gap-1"><Layers className="w-3.5 h-3.5" />{course.module_count || 4} modules</span>
                      <span className="flex items-center gap-1"><BookOpen className="w-3.5 h-3.5" />{course.lesson_count || 12} lessons</span>
                    </div>
                  </div>
                  <button onClick={() => navigate('/login?register=true')} className="inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 bg-navy-800 text-white rounded-lg hover:bg-navy-700 transition-all text-sm font-medium shadow-sm">
                    Start Learning <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="p-2 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-30 disabled:pointer-events-none"><ChevronLeft className="w-4 h-4" /></button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                  <button key={p} onClick={() => setPage(p)} className={`w-9 h-9 rounded-lg text-sm font-medium transition-all ${p === page ? 'bg-navy-800 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100'}`}>{p}</button>
                ))}
                <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} className="p-2 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 disabled:opacity-30 disabled:pointer-events-none"><ChevronRight className="w-4 h-4" /></button>
              </div>
            )}
          </>
        )}
      </section>

      <footer className="border-t border-slate-200 py-6 text-center text-xs text-slate-400">&copy; 2026 Acuity Learning Hub. All rights reserved.</footer>
    </div>
  )
}
