import { studentProfile } from '@/data/mockData'
import { User, Mail, BookOpen, Calendar } from 'lucide-react'

export function ProfilePage() {
  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">My Profile</h1>
        <p className="text-sm text-slate-500 mt-1">Manage your learning preferences</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center gap-4 mb-6 pb-6 border-b border-slate-100">
          <div className="w-16 h-16 rounded-full bg-navy-800 flex items-center justify-center text-xl font-bold text-white">
            {studentProfile.avatar}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-900">{studentProfile.name}</h2>
            <p className="text-sm text-slate-500">Grade {studentProfile.grade}</p>
          </div>
        </div>

        <div className="space-y-4">
          {[
            { icon: User, label: 'Name', value: studentProfile.name },
            { icon: Mail, label: 'Email', value: 'abinaya@example.com' },
            { icon: BookOpen, label: 'Subject', value: studentProfile.subject },
            { icon: Calendar, label: 'Grade', value: studentProfile.grade },
          ].map((item) => {
            const Icon = item.icon
            return (
              <div key={item.label} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-slate-500" />
                </div>
                <div className="flex-1">
                  <div className="text-xs text-slate-400">{item.label}</div>
                  <div className="text-sm font-medium text-slate-800">{item.value}</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
