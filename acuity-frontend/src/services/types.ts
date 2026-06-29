export type UserRole = 'admin' | 'course_admin' | 'student' | 'parent' | 'teacher'

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

export interface Assessment {
  id: string
  title: string
  description?: string
  lesson_id?: string
  module_id?: string
  course_id: string
  assessment_type: string
  passing_score: number
  time_limit?: number
  max_attempts: number
  is_published: boolean
  question_count: number
  created_at?: string
  updated_at?: string
}

export interface AssessmentQuestion {
  id: string
  question_type: string
  prompt: string
  options?: Record<string, string>
  difficulty: number
  marks: number
  order_index: number
}

export interface AssessmentAttemptStart {
  attempt_id: string
  assessment_id: string
  started_at: string
  attempt_number: number
  questions: AssessmentQuestion[]
  time_limit?: number
  time_limit_seconds?: number
}

export interface AssessmentSubmitResponse {
  attempt_id: string
  assessment_id: string
  score: number
  percentage: number
  passed: boolean
  total_marks: number
  earned_marks: number
  completed_at: string
}

export interface AssessmentResultResponse {
  attempt_id: string
  assessment_id: string
  assessment_title: string
  assessment_type: string
  passing_score: number
  score: number
  percentage: number
  passed: boolean
  attempt_number: number
  started_at?: string
  completed_at?: string
  total_marks: number
  earned_marks: number
  responses: AssessmentResultDetail[]
}

export interface AssessmentResultDetail {
  question_id: string
  prompt: string
  question_type: string
  marks: number
  response: string
  correct_answer: string
  is_correct: boolean
  score: number
  feedback?: string
  explanation?: string
}

export interface TeacherStudent {
  student_id: string
  full_name: string
  email: string
  grade_level?: string
  active_courses: number
  overall_mastery_avg: number
  last_active?: string
  current_streak_days: number
  assigned_at?: string
}

export interface TeacherCourse {
  course_id: string
  title: string
  code: string
  role: string
  assigned_at?: string
}

export interface TeacherDashboardData {
  total_students: number
  total_courses: number
  students: TeacherStudent[]
  recent_sessions: SessionItem[]
}

export interface SessionItem {
  session_id: string
  course_id: string
  course_title?: string
  state: string
  started_at?: string
  last_activity_at?: string
}

export interface AttemptItem {
  attempt_id: string
  exercise_id: string
  is_correct: boolean
  score: number
  attempted_at?: string
  concept_title?: string
}

export interface AssessmentAttemptHistory {
  attempt_id: string
  assessment_id: string
  assessment_title: string
  assessment_type: string
  score: number
  percentage: number
  passed: boolean
  attempt_number: number
  started_at?: string
  completed_at?: string
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

export interface AssessmentAnalytics {
  average_score: number
  total_attempts: number
  pass_rate: number
  avg_time_spent_seconds: number
  pass_count: number
  fail_count: number
}

export interface StudentProgressAnalytics {
  total_lessons: number
  completed_lessons: number
  completion_rate: number
  avg_mastery: number
  time_spent_seconds: number
  lessons_overdue: number
}

export interface CourseAnalytics {
  course_id: string
  title: string
  total_students: number
  active_students: number
  completion_rate: number
  avg_mastery: number
  avg_assessment_score: number
  total_assessments: number
}

export interface DashboardAnalyticsResponse {
  total_users: number
  total_students: number
  total_admins: number
  total_parents: number
  total_courses: number
  active_enrollments: number
  active_sessions_today: number
  total_assessment_attempts: number
  overall_pass_rate: number
  overall_completion_rate: number
}

// -----------------------------------------------------------------------
// Course (Course Admin) types
// -----------------------------------------------------------------------

export interface StageLogEntry {
  ts: string
  message: string
  level: string
}

export interface StageProgress {
  completed: number
  total: number
  pct: number
}

export interface CourseBrief {
  id: string
  name: string
  description?: string
  status: string
  course_id?: string
  stage_progress?: StageProgress
  created_at: string
  updated_at: string
}

export interface PipelineStageInfo {
  id: string
  stage_name: string
  status: string
  progress_pct: number
  error_message?: string
  output_data?: Record<string, unknown>
  stage_logs: StageLogEntry[]
  retry_count: number
  started_at?: string
  completed_at?: string
  duration_seconds?: number
  created_at: string
}

export interface KnowledgeSourceInfo {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: string
  error_message?: string
  created_at: string
}

export interface CourseDetail {
  id: string
  name: string
  description?: string
  status: string
  course_id?: string
  stage_progress?: StageProgress
  knowledge_sources: KnowledgeSourceInfo[]
  knowledge_graph_data?: Record<string, unknown>
  teaching_profile?: Record<string, unknown>
  course_structure?: Record<string, unknown>
  simulation_results?: Record<string, unknown>
  error_message?: string
  stages: PipelineStageInfo[]
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  total_courses: number
  deployed_count: number
  training_count: number
  draft_count: number
  review_count: number
  total_students: number
  total_published: number
  active_sessions: number
  pending_review_count: number
  failed_stages_count: number
  total_concepts_generated: number
  total_exercises_generated: number
  avg_coverage_pct: number
  recent_courses: CourseBrief[]
}

export const STAGE_LABELS: Record<string, string> = {
  upload: 'Upload Knowledge Source',
  extract: 'Extract Text Content',
  understand: 'AI Understands & Builds Knowledge Graph',
  validate: 'Validate Understanding',
  profile: 'Generate Teaching Profile',
  structure: 'Generate Course Structure',
  generate: 'Generate Lesson Content & Assessments',
  review: 'Review & Refine',
  simulate: 'Simulation & Testing',
  deploy: 'Deploy & Publish',
}

export const STAGE_ORDER = [
  'upload', 'extract', 'understand', 'validate',
  'profile', 'structure', 'generate',
  'review', 'simulate', 'deploy',
]
