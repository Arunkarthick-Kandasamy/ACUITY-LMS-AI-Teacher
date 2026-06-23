import { useAuthApi } from '@/hooks/useApi'
import { getParentStudents, getParentStudentSessions } from '@/services/parent'
import { getStudentReports } from '@/services/reports'
import { FileText, Download, Calendar, Loader2 } from 'lucide-react'

export function ReportsPage() {
  const { data: students } = useAuthApi(() => getParentStudents(), [])
  const firstStudentId = students?.[0]?.student_id

  const { data: reportsResult, loading } = useAuthApi(
    () => firstStudentId ? getStudentReports(firstStudentId) : Promise.reject(),
    [firstStudentId],
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-navy-600" />
      </div>
    )
  }

  const reports = reportsResult || []

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Reports</h1>
        <p className="text-sm text-slate-500 mt-1">View and download progress reports</p>
      </div>

      <div className="space-y-3">
        {reports.length === 0 ? (
          <div className="bg-white rounded-xl border border-slate-200 p-8 text-center shadow-sm">
            <p className="text-slate-500">No reports available yet.</p>
          </div>
        ) : (
          reports.map((report, i) => (
            <div key={report.report_id || i} className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex gap-3">
                  <div className="w-10 h-10 rounded-lg bg-navy-50 flex items-center justify-center mt-0.5">
                    <FileText className="w-5 h-5 text-navy-600" />
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 capitalize">{report.report_type} Progress Report</h3>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="flex items-center gap-1 text-xs text-slate-400">
                        <Calendar className="w-3 h-3" />
                        {report.generated_at ? new Date(report.generated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A'}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 text-[10px] font-medium text-slate-500 capitalize">{report.report_type}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-2 max-w-lg">{report.summary}</p>
                  </div>
                </div>
                <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
