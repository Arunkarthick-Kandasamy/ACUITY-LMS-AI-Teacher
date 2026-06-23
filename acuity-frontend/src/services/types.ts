export type UserRole = 'admin' | 'student' | 'parent'

export interface User {
  user_id: string
  email: string
  full_name: string
  role: UserRole
  created_at?: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface Course {
  course_id: string
  code: string
  title: string
  description?: string
  total_duration_hours: number
  default_deadline_days: number
  is_published: boolean
  module_count?: number
  lesson_count?: number
  created_at?: string
}

export interface CourseDetail extends Course {
  modules: ModuleDetail[]
}

export interface ModuleDetail {
  module_id: string
  title: string
  order_index: number
  lessons: LessonBrief[]
}

export interface LessonBrief {
  lesson_id: string
  title: string
  order_index: number
  estimated_duration_minutes?: number
  concept_count?: number
}

export interface Module {
  module_id: string
  course_id: string
  title: string
  description?: string
  order_index: number
  estimated_duration_hours?: number
  lesson_count?: number
  created_at?: string
}

export interface Lesson {
  lesson_id: string
  module_id: string
  title: string
  content_url?: string
  order_index: number
  estimated_duration_minutes?: number
  is_required?: boolean
  status?: string
  concept_count?: number
  concepts?: Concept[]
  created_at?: string
}

export interface Concept {
  concept_id: string
  lesson_id?: string
  title: string
  description?: string
  order_index: number
  estimated_duration_minutes?: number
  content_count?: number
  exercise_count?: number
  mastery_level?: number
}

export interface ConceptDetail extends Concept {
  contents: ConceptContent[]
  examples: Example[]
  exercise_count: number
  mastery?: MasteryInfo
}

export interface ConceptContent {
  content_id: string
  content_type: string
  content: string
  order_index: number
  version?: number
  updated_at?: string
}

export interface Example {
  example_id: string
  content: string
  explanation?: string
  order_index?: number
  tags?: string[]
}

export interface Exercise {
  exercise_id: string
  concept_id?: string
  question_type: string
  prompt: string
  options?: Record<string, string>
  difficulty?: number
  order_index?: number
  tags?: string[]
  created_at?: string
}

export interface MasteryRecord {
  record_id: string
  student_id: string
  concept_id: string
  concept_title?: string
  mastery_level: number
  total_attempts: number
  consecutive_correct: number
  last_attempted_at?: string
  status?: 'mastered' | 'in_progress' | 'not_started'
}

export interface MasterySummary {
  course_id: string
  total_concepts: number
  mastered_concepts: number
  average_mastery: number
  concepts: MasteryRecord[]
}

export interface MasteryInfo {
  mastery_level: number
  total_attempts: number
  consecutive_correct: number
}

export interface CurriculumTree {
  course_id: string
  course_title: string
  course_code?: string
  modules: CurriculumModule[]
}

export interface CurriculumModule {
  module_id: string
  title: string
  order_index: number
  lesson_count: number
  lessons?: CurriculumLesson[]
}

export interface CurriculumLesson {
  lesson_id: string
  title: string
  order_index: number
  status?: string
  estimated_duration_minutes?: number
  concepts?: CurriculumConcept[]
}

export interface CurriculumConcept {
  concept_id: string
  title: string
  order_index: number
  mastery_level?: number
}

export interface LessonProgress {
  lesson_id: string
  lesson_title?: string
  status: string
  started_at?: string
  time_spent_seconds?: number
  completion_percentage?: number
  concepts?: ConceptProgress[]
}

export interface ConceptProgress {
  concept_id: string
  title?: string
  mastery_level: number
  status: string
}

export interface Attempt {
  attempt_id: string
  exercise_id: string
  concept_title?: string
  question_type?: string
  prompt?: string
  response?: string
  is_correct: boolean
  score: number
  ai_feedback?: string
  attempt_number?: number
  attempted_at?: string
  time_taken_seconds?: number
}

export interface Enrollment {
  enrollment_id: string
  course_id: string
  course_title: string
  status: string
  progress_pct?: number
  current_concept?: string
  target_completion_date?: string
  pace_status?: string
  enrolled_at?: string
}

export interface TeachingSession {
  session_id: string
  student_id?: string
  course_id: string
  course_title?: string
  state: string
  current_concept?: { concept_id: string; title: string; order_index?: number }
  current_lesson?: { lesson_id: string; title: string }
  context_summary?: {
    concepts_taught_this_session: number
    exercises_answered: number
    session_duration_minutes: number
  }
  started_at?: string
  last_activity_at?: string
  resumed?: boolean
}

export interface PacingStatus {
  enrollment_id: string
  course_id?: string
  schedule_id?: string
  current_week: number
  target_lessons_per_week: number
  pace_status: string
  last_pacing_adjustment_at?: string
}

export interface ParentStudent {
  student_id: string
  full_name: string
  grade_level?: string
  active_courses: number
  overall_mastery_avg: number
  last_active?: string
  current_streak_days?: number
}

export interface ParentDashboardData {
  students: ParentStudent[]
  aggregate: {
    total_children: number
    children_with_alerts: number
    unread_reports: number
    weekly_family_avg_accuracy: number
  }
}

export interface Report {
  report_id: string
  report_type: string
  generated_at: string
  summary: string
  is_read?: boolean
  student_name?: string
  sections?: ReportSection[]
  metrics?: Record<string, number>
  recommendations?: ReportRecommendation[]
}

export interface ReportSection {
  heading: string
  body: string
}

export interface ReportRecommendation {
  priority: string
  action: string
  expected_outcome: string
}

export interface AdminDashboardStats {
  total_users: number
  total_students: number
  total_parents: number
  total_admins: number
  total_courses: number
  active_enrollments: number
  active_sessions_today: number
  completion_rate_avg: number
}

export interface AdminUser {
  user_id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  created_at: string
  profile?: {
    grade_level: string
    avg_session_duration_minutes: number
    current_streak_days: number
  }
  enrollments?: {
    enrollment_id: string
    course_title: string
    status: string
    progress_pct: number
    enrolled_at: string
  }[]
}

export interface ApiResponse<T> {
  status: 'success' | 'error'
  data: T
  meta?: {
    page: number
    per_page: number
    total: number
    total_pages: number
  }
  error?: {
    code: string
    message: string
    details: string[]
  }
}

export interface Misconception {
  misconception_id: string
  concept_id: string
  concept_title: string
  category: string
  description: string
  detected_at: string
  frequency: number
  is_resolved: boolean
  evidence?: { response: string; exercise_prompt: string; expected: string }[]
}
