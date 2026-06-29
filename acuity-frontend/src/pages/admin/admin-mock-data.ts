import type { AdminDashboardStats, AdminUser, Assessment, CourseAnalytics, AssessmentAnalytics, DashboardAnalyticsResponse } from '@/services/types'

export const mockDashboardStats: AdminDashboardStats = {
  total_users: 28450,
  total_students: 24580,
  total_parents: 3200,
  total_admins: 12,
  total_courses: 48,
  active_enrollments: 18750,
  active_sessions_today: 3420,
  completion_rate_avg: 0.78,
}

export const mockUsers: AdminUser[] = [
  { user_id: 'usr_001', email: 'alex.chen@example.com', full_name: 'Alex Chen', role: 'student', is_active: true, created_at: '2025-09-15T08:30:00Z', profile: { grade_level: '10', avg_session_duration_minutes: 42, current_streak_days: 7 } },
  { user_id: 'usr_002', email: 'priya.sharma@example.com', full_name: 'Priya Sharma', role: 'student', is_active: true, created_at: '2025-08-20T10:15:00Z', profile: { grade_level: '12', avg_session_duration_minutes: 38, current_streak_days: 12 } },
  { user_id: 'usr_003', email: 'rajesh.patel@example.com', full_name: 'Rajesh Patel', role: 'parent', is_active: true, created_at: '2025-10-01T14:00:00Z' },
  { user_id: 'usr_004', email: 'sarah.johnson@example.com', full_name: 'Sarah Johnson', role: 'student', is_active: true, created_at: '2025-07-10T09:45:00Z', profile: { grade_level: '8', avg_session_duration_minutes: 35, current_streak_days: 5 } },
  { user_id: 'usr_005', email: 'anita.sharma@example.com', full_name: 'Dr. Anita Sharma', role: 'teacher', is_active: true, created_at: '2025-06-01T11:00:00Z' },
  { user_id: 'usr_006', email: 'arjun.kumar@example.com', full_name: 'Arjun Kumar', role: 'student', is_active: false, created_at: '2025-11-05T16:30:00Z', profile: { grade_level: '11', avg_session_duration_minutes: 28, current_streak_days: 0 } },
  { user_id: 'usr_007', email: 'meera.desai@example.com', full_name: 'Meera Desai', role: 'student', is_active: true, created_at: '2025-09-28T07:20:00Z', profile: { grade_level: '9', avg_session_duration_minutes: 45, current_streak_days: 15 } },
  { user_id: 'usr_008', email: 'vikram.singh@example.com', full_name: 'Vikram Singh', role: 'parent', is_active: true, created_at: '2025-08-15T13:45:00Z' },
  { user_id: 'usr_009', email: 'divya.reddy@example.com', full_name: 'Divya Reddy', role: 'student', is_active: true, created_at: '2025-10-20T10:00:00Z', profile: { grade_level: '10', avg_session_duration_minutes: 52, current_streak_days: 21 } },
  { user_id: 'usr_010', email: 'rohit.verma@example.com', full_name: 'Rohit Verma', role: 'student', is_active: true, created_at: '2025-07-05T15:30:00Z', profile: { grade_level: '12', avg_session_duration_minutes: 40, current_streak_days: 3 } },
  { user_id: 'usr_011', email: 'admin@acuity.com', full_name: 'Admin User', role: 'admin', is_active: true, created_at: '2025-01-01T00:00:00Z' },
  { user_id: 'usr_012', email: 'neha.gupta@example.com', full_name: 'Neha Gupta', role: 'student', is_active: true, created_at: '2025-11-12T09:15:00Z', profile: { grade_level: '7', avg_session_duration_minutes: 32, current_streak_days: 2 } },
  { user_id: 'usr_013', email: 'karan.joshi@example.com', full_name: 'Karan Joshi', role: 'teacher', is_active: true, created_at: '2025-05-20T08:00:00Z' },
  { user_id: 'usr_014', email: 'pavani.rao@example.com', full_name: 'Pavani Rao', role: 'student', is_active: false, created_at: '2025-12-01T11:30:00Z', profile: { grade_level: '6', avg_session_duration_minutes: 25, current_streak_days: 0 } },
  { user_id: 'usr_015', email: 'suresh.nair@example.com', full_name: 'Suresh Nair', role: 'parent', is_active: true, created_at: '2025-09-05T14:20:00Z' },
]

export const mockAssessments: Assessment[] = [
  { id: 'assess_001', title: 'Quadratic Equations Quiz', description: 'Test your understanding of quadratic equations', course_id: 'course_001', assessment_type: 'quiz', passing_score: 0.7, time_limit: 30, max_attempts: 3, is_published: true, question_count: 15, created_at: '2025-11-01T10:00:00Z', updated_at: '2025-11-10T14:00:00Z' },
  { id: 'assess_002', title: 'Thermodynamics Chapter Test', description: 'Comprehensive test on thermodynamics concepts', course_id: 'course_002', assessment_type: 'chapter_test', passing_score: 0.6, time_limit: 60, max_attempts: 2, is_published: true, question_count: 25, created_at: '2025-10-15T08:30:00Z', updated_at: '2025-11-05T12:00:00Z' },
  { id: 'assess_003', title: 'Cell Biology Diagnostic', description: 'Identify your strengths and weaknesses in cell biology', course_id: 'course_003', assessment_type: 'diagnostic', passing_score: 0.5, time_limit: 45, max_attempts: 1, is_published: true, question_count: 30, created_at: '2025-11-20T09:00:00Z', updated_at: '2025-11-25T16:00:00Z' },
  { id: 'assess_004', title: 'Grammar Practice Test', description: 'Practice English grammar fundamentals', course_id: 'course_004', assessment_type: 'practice_test', passing_score: 0.7, time_limit: 20, max_attempts: 5, is_published: false, question_count: 20, created_at: '2025-12-01T11:00:00Z', updated_at: '2025-12-05T09:00:00Z' },
  { id: 'assess_005', title: 'World War II Final Exam', description: 'Final assessment for the World History module', course_id: 'course_005', assessment_type: 'final', passing_score: 0.8, time_limit: 90, max_attempts: 2, is_published: true, question_count: 40, created_at: '2025-09-10T07:00:00Z', updated_at: '2025-10-01T10:00:00Z' },
  { id: 'assess_006', title: 'Algebra Mid-Term', description: 'Mid-term assessment covering algebra topics', course_id: 'course_001', assessment_type: 'chapter_test', passing_score: 0.65, time_limit: 60, max_attempts: 2, is_published: true, question_count: 20, created_at: '2025-08-15T13:00:00Z', updated_at: '2025-09-01T08:00:00Z' },
  { id: 'assess_007', title: 'Periodic Table Quiz', description: 'Quick quiz on the periodic table elements', course_id: 'course_002', assessment_type: 'quiz', passing_score: 0.75, time_limit: 15, max_attempts: 3, is_published: true, question_count: 10, created_at: '2025-12-10T10:30:00Z', updated_at: '2025-12-12T14:00:00Z' },
  { id: 'assess_008', title: 'Poetry Analysis Assignment', description: 'Analyze and interpret classic poems', course_id: 'course_004', assessment_type: 'final', passing_score: 0.7, time_limit: undefined, max_attempts: 1, is_published: false, question_count: 8, created_at: '2025-11-25T09:00:00Z', updated_at: '2025-11-28T11:00:00Z' },
  { id: 'assess_009', title: 'Newton\'s Laws Diagnostic', description: 'Diagnostic test on Newtonian mechanics', course_id: 'course_002', assessment_type: 'diagnostic', passing_score: 0.5, time_limit: 30, max_attempts: 1, is_published: true, question_count: 15, created_at: '2025-10-05T08:00:00Z', updated_at: '2025-10-10T12:00:00Z' },
  { id: 'assess_010', title: 'Civil Rights Movement Quiz', description: 'Test your knowledge of the civil rights movement', course_id: 'course_005', assessment_type: 'quiz', passing_score: 0.7, time_limit: 20, max_attempts: 3, is_published: true, question_count: 12, created_at: '2025-12-05T14:00:00Z', updated_at: '2025-12-08T16:00:00Z' },
]

export const mockConcepts = [
  { concept_id: 'con_001', lesson_id: 'lesson_001', title: 'Linear Equations', order_index: 1 },
  { concept_id: 'con_002', lesson_id: 'lesson_001', title: 'Quadratic Formula', order_index: 2 },
  { concept_id: 'con_003', lesson_id: 'lesson_001', title: 'Polynomial Factorization', order_index: 3 },
  { concept_id: 'con_004', lesson_id: 'lesson_002', title: 'Newton\'s Laws of Motion', order_index: 1 },
  { concept_id: 'con_005', lesson_id: 'lesson_002', title: 'Kinematics', order_index: 2 },
  { concept_id: 'con_006', lesson_id: 'lesson_002', title: 'Work-Energy Theorem', order_index: 3 },
  { concept_id: 'con_007', lesson_id: 'lesson_003', title: 'Cell Structure', order_index: 1 },
  { concept_id: 'con_008', lesson_id: 'lesson_003', title: 'DNA Replication', order_index: 2 },
  { concept_id: 'con_009', lesson_id: 'lesson_003', title: 'Photosynthesis', order_index: 3 },
  { concept_id: 'con_010', lesson_id: 'lesson_004', title: 'Subject-Verb Agreement', order_index: 1 },
  { concept_id: 'con_011', lesson_id: 'lesson_004', title: 'Tense Consistency', order_index: 2 },
  { concept_id: 'con_012', lesson_id: 'lesson_005', title: 'World War I Causes', order_index: 1 },
  { concept_id: 'con_013', lesson_id: 'lesson_005', title: 'Treaty of Versailles', order_index: 2 },
  { concept_id: 'con_014', lesson_id: 'lesson_003', title: 'Mitosis & Meiosis', order_index: 4 },
]

export const mockPrereqs: Record<string, { edge_id: string; prerequisite_id: string; prerequisite_title: string }[]> = {
  con_002: [{ edge_id: 'edge_001', prerequisite_id: 'con_001', prerequisite_title: 'Linear Equations' }],
  con_003: [{ edge_id: 'edge_002', prerequisite_id: 'con_001', prerequisite_title: 'Linear Equations' }, { edge_id: 'edge_003', prerequisite_id: 'con_002', prerequisite_title: 'Quadratic Formula' }],
  con_005: [{ edge_id: 'edge_004', prerequisite_id: 'con_004', prerequisite_title: 'Newton\'s Laws of Motion' }],
  con_006: [{ edge_id: 'edge_005', prerequisite_id: 'con_004', prerequisite_title: 'Newton\'s Laws of Motion' }, { edge_id: 'edge_006', prerequisite_id: 'con_005', prerequisite_title: 'Kinematics' }],
  con_008: [{ edge_id: 'edge_007', prerequisite_id: 'con_007', prerequisite_title: 'Cell Structure' }],
  con_009: [{ edge_id: 'edge_008', prerequisite_id: 'con_007', prerequisite_title: 'Cell Structure' }, { edge_id: 'edge_009', prerequisite_id: 'con_008', prerequisite_title: 'DNA Replication' }],
  con_014: [{ edge_id: 'edge_010', prerequisite_id: 'con_007', prerequisite_title: 'Cell Structure' }, { edge_id: 'edge_011', prerequisite_id: 'con_008', prerequisite_title: 'DNA Replication' }],
}

export const mockModerationItems = [
  { id: 'mod_001', content_id: 'content_001', content_type: 'Lesson Video', uploader_name: 'Dr. Anita Sharma', status: 'pending', flag_reason: 'Inappropriate language detected', created_at: '2025-12-10T09:30:00Z', review_notes: null },
  { id: 'mod_002', content_id: 'content_002', content_type: 'Assessment Question', uploader_name: 'Prof. Ravi Verma', status: 'pending', flag_reason: 'Possible copyright violation', created_at: '2025-12-11T14:15:00Z', review_notes: null },
  { id: 'mod_003', content_id: 'content_003', content_type: 'Study Material', uploader_name: 'Ms. Priya Patel', status: 'approved', flag_reason: null, created_at: '2025-12-08T11:00:00Z', review_notes: null },
  { id: 'mod_004', content_id: 'content_004', content_type: 'User Profile', uploader_name: 'Alex Chen', status: 'rejected', flag_reason: 'Inappropriate profile picture', created_at: '2025-12-09T16:45:00Z', review_notes: 'Profile picture removed. User notified.' },
  { id: 'mod_005', content_id: 'content_005', content_type: 'Lesson Video', uploader_name: 'Dr. Sunil Gupta', status: 'pending', flag_reason: 'Audio quality issues', created_at: '2025-12-12T08:00:00Z', review_notes: null },
  { id: 'mod_006', content_id: 'content_006', content_type: 'Discussion Post', uploader_name: 'Divya Reddy', status: 'pending', flag_reason: 'Reported by multiple users', created_at: '2025-12-12T10:20:00Z', review_notes: null },
  { id: 'mod_007', content_id: 'content_007', content_type: 'Assessment Question', uploader_name: 'Ms. Kavita Reddy', status: 'approved', flag_reason: null, created_at: '2025-12-07T13:30:00Z', review_notes: null },
  { id: 'mod_008', content_id: 'content_008', content_type: 'Study Material', uploader_name: 'Karan Joshi', status: 'pending', flag_reason: 'Factual accuracy concern', created_at: '2025-12-12T15:00:00Z', review_notes: null },
]

export const mockSchools = [
  { id: 'sch_001', name: 'Delhi Public School', code: 'DPS_RK', address: 'RK Puram, New Delhi', phone: '+91-11-45678901', is_active: true, domains: ['dpsrkp.edu', 'dpsdelhi.edu'] },
  { id: 'sch_002', name: 'National Public School', code: 'NPS_IN', address: 'Indiranagar, Bangalore', phone: '+91-80-23456789', is_active: true, domains: ['npsindiranagar.edu'] },
  { id: 'sch_003', name: 'DAV Public School', code: 'DAV_PT', address: 'Patna, Bihar', phone: '+91-612-3456789', is_active: true, domains: ['davpatna.edu'] },
  { id: 'sch_004', name: 'St. Mary\'s Convent', code: 'SMC_KL', address: 'Kochi, Kerala', phone: '+91-484-2345678', is_active: false, domains: ['stmaryskochi.edu'] },
  { id: 'sch_005', name: 'Chinmaya Vidyalaya', code: 'CHN_MN', address: 'Mumbai, Maharashtra', phone: '+91-22-34567890', is_active: true, domains: ['chinmayamumbai.edu'] },
  { id: 'sch_006', name: 'Sri Chaitanya School', code: 'SCS_HYD', address: 'Hyderabad, Telangana', phone: '+91-40-45678901', is_active: true, domains: ['srichaitanyahyderabad.edu', 'srichaitanya.in'] },
  { id: 'sch_007', name: 'The Lawrence School', code: 'LAW_OO', address: 'Ooty, Tamil Nadu', phone: '+91-423-3456789', is_active: true, domains: ['lawrenceschoolooty.edu'] },
  { id: 'sch_008', name: 'Cathedral & John Connon', code: 'CJC_MN', address: 'Mumbai, Maharashtra', phone: '+91-22-23456789', is_active: true, domains: ['cathedralconnon.edu'] },
]

export const mockSystemOverview: DashboardAnalyticsResponse = {
  total_users: 28450,
  total_students: 24580,
  total_admins: 12,
  total_parents: 3200,
  total_courses: 48,
  active_enrollments: 18750,
  active_sessions_today: 3420,
  total_assessment_attempts: 156890,
  overall_pass_rate: 74.5,
  overall_completion_rate: 68.2,
}

export const mockCourseAnalytics: CourseAnalytics = {
  course_id: 'course_001',
  title: 'Mathematics',
  total_students: 5200,
  active_students: 3850,
  completion_rate: 71.3,
  avg_mastery: 0.78,
  avg_assessment_score: 76.4,
  total_assessments: 24,
}

export const mockAssessmentAnalytics: AssessmentAnalytics = {
  average_score: 72.5,
  total_attempts: 8450,
  pass_rate: 68.3,
  avg_time_spent_seconds: 1860,
  pass_count: 5770,
  fail_count: 2680,
}

export const mockCourses = [
  { course_id: 'course_001', title: 'Mathematics' },
  { course_id: 'course_002', title: 'Science' },
  { course_id: 'course_003', title: 'Biology' },
  { course_id: 'course_004', title: 'English' },
  { course_id: 'course_005', title: 'History' },
]
