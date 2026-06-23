import { FileText, Download, Calendar } from 'lucide-react'

const reports = [
  { title: 'Weekly Progress Report', date: 'Jun 21, 2026', type: 'Weekly', summary: 'Open Score improved from 68 to 72. Strong performance in Algebra.' },
  { title: 'Monthly Mastery Summary', date: 'Jun 1, 2026', type: 'Monthly', summary: 'Overall mastery increased 8%. Areas of improvement identified in Trigonometry.' },
  { title: 'Learning Behavior Analysis', date: 'May 15, 2026', type: 'Analysis', summary: 'Peak learning time identified: 10 AM - 12 PM. Recommended study schedule adjusted.' },
  { title: 'Milestone Achievement Report', date: 'May 1, 2026', type: 'Milestone', summary: 'Completed 20 lessons with 78% average accuracy. Good Learner Track recommended.' },
]

export function ReportsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Reports</h1>
        <p className="text-sm text-slate-500 mt-1">View and download progress reports</p>
      </div>

      <div className="space-y-3">
        {reports.map((report, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex gap-3">
                <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center mt-0.5">
                  <FileText className="w-5 h-5 text-navy-600" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">{report.title}</h3>
                  <div className="flex items-center gap-3 mt-1">
                    <span className="flex items-center gap-1 text-xs text-slate-400">
                      <Calendar className="w-3 h-3" />
                      {report.date}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-slate-100 text-[10px] font-medium text-slate-500">{report.type}</span>
                  </div>
                  <p className="text-xs text-slate-500 mt-2 max-w-lg">{report.summary}</p>
                </div>
              </div>
              <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all">
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
