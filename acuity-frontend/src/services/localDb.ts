import type {
  User, Course, ModuleDetail, Lesson, Concept, Example, Exercise,
  MasteryRecord, Attempt, Enrollment, TeachingSession, Assessment,
  AssessmentQuestion, AssessmentAttemptStart, AssessmentSubmitResponse,
  AssessmentResultResponse, AssessmentResultDetail, LessonProgress,
  CurriculumTree, CurriculumModule, CurriculumLesson, CurriculumConcept,
  ParentStudent, Report, AdminUser, TeacherStudent, TeacherCourse,
  CourseDetail, Module, ConceptDetail, ConceptContent,
  ParentDashboardData, TeacherDashboardData, AssessmentAttemptHistory,
  Misconception, SessionItem, AttemptItem, DashboardStats,
  CourseBrief, CourseAnalytics, StudentProgressAnalytics,
  AssessmentAnalytics, DashboardAnalyticsResponse,
  PacingStatus, AdminDashboardStats,
} from './types'

const DB_KEY = 'acuity_local_db'

interface DbSchema {
  users: User[]
  courses: Course[]
  modules: ModuleDetail[]
  lessons: Lesson[]
  concepts: Concept[]
  examples: Example[]
  exercises: Exercise[]
  enrollments: Enrollment[]
  masteryRecords: MasteryRecord[]
  attempts: Attempt[]
  sessions: TeachingSession[]
  assessments: Assessment[]
  assessmentQuestions: AssessmentQuestion[]
  lessonProgress: LessonProgress[]
  parentStudents: { parentId: string; studentId: string; linkedAt: string }[]
  reports: Report[]
  misconceptions: Misconception[]
  messages: { id: string; from: string; to: string; content: string; created_at: string }[]
  counter: number
}

function getDb(): DbSchema {
  try {
    const raw = localStorage.getItem(DB_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return initDb()
}

function saveDb(db: DbSchema) {
  localStorage.setItem(DB_KEY, JSON.stringify(db))
}

function id(): string {
  const db = getDb()
  db.counter++
  saveDb(db)
  return `id_${db.counter}`
}

function delay(ms = 200): Promise<void> {
  return new Promise(r => setTimeout(r, ms))
}

function success<T>(data: T) {
  return { status: 'success' as const, data }
}

function seedCourses(): Course[] {
  return [
    { course_id: 'c1', code: 'MATH101', title: 'Mathematics', description: 'Algebra, Geometry, Calculus', total_duration_hours: 40, default_deadline_days: 90, is_published: true, module_count: 4, lesson_count: 20 },
    { course_id: 'c2', code: 'SCI101', title: 'Science', description: 'Biology, Chemistry, Physics', total_duration_hours: 35, default_deadline_days: 90, is_published: true, module_count: 4, lesson_count: 16 },
    { course_id: 'c3', code: 'ENG101', title: 'English', description: 'Literature, Grammar, Writing', total_duration_hours: 30, default_deadline_days: 90, is_published: true, module_count: 4, lesson_count: 16 },
    { course_id: 'c4', code: 'HIS101', title: 'History', description: 'World History, Civics', total_duration_hours: 30, default_deadline_days: 90, is_published: true, module_count: 4, lesson_count: 16 },
  ]
}

function seedModules(): ModuleDetail[] {
  return [
    { module_id: 'm1', title: 'Algebra Basics', order_index: 1, lessons: [
      { lesson_id: 'l1', title: 'Introduction to Algebra', order_index: 1, estimated_duration_minutes: 15, concept_count: 3 },
      { lesson_id: 'l2', title: 'Linear Equations', order_index: 2, estimated_duration_minutes: 20, concept_count: 3 },
      { lesson_id: 'l3', title: 'Quadratic Functions', order_index: 3, estimated_duration_minutes: 25, concept_count: 3 },
      { lesson_id: 'l4', title: 'Polynomials', order_index: 4, estimated_duration_minutes: 20, concept_count: 3 },
      { lesson_id: 'l5', title: 'Exponents & Logarithms', order_index: 5, estimated_duration_minutes: 25, concept_count: 3 },
    ]},
    { module_id: 'm2', title: 'Geometry', order_index: 2, lessons: [
      { lesson_id: 'l6', title: 'Shapes & Angles', order_index: 1, estimated_duration_minutes: 15, concept_count: 3 },
      { lesson_id: 'l7', title: 'Triangles & Theorems', order_index: 2, estimated_duration_minutes: 20, concept_count: 3 },
      { lesson_id: 'l8', title: 'Circles & Area', order_index: 3, estimated_duration_minutes: 20, concept_count: 3 },
      { lesson_id: 'l9', title: 'Coordinate Geometry', order_index: 4, estimated_duration_minutes: 25, concept_count: 3 },
    ]},
    { module_id: 'm3', title: 'Trigonometry', order_index: 3, lessons: [
      { lesson_id: 'l10', title: 'Trigonometry Basics', order_index: 1, estimated_duration_minutes: 20, concept_count: 3 },
      { lesson_id: 'l11', title: 'Trigonometric Identities', order_index: 2, estimated_duration_minutes: 25, concept_count: 3 },
      { lesson_id: 'l12', title: 'Sine & Cosine Rules', order_index: 3, estimated_duration_minutes: 20, concept_count: 3 },
    ]},
    { module_id: 'm4', title: 'Calculus', order_index: 4, lessons: [
      { lesson_id: 'l13', title: 'Introduction to Calculus', order_index: 1, estimated_duration_minutes: 20, concept_count: 3 },
      { lesson_id: 'l14', title: 'Differentiation', order_index: 2, estimated_duration_minutes: 25, concept_count: 3 },
      { lesson_id: 'l15', title: 'Integration', order_index: 3, estimated_duration_minutes: 25, concept_count: 3 },
    ]},
  ]
}

function seedConcepts(): Concept[] {
  const concepts: Concept[] = []
  const titles: Record<string, string[]> = {
    l1: ['Variables & Expressions', 'Simplifying Expressions', 'Evaluating Expressions'],
    l2: ['Solving Linear Equations', 'Graphing Linear Equations', 'Slope & Intercept'],
    l3: ['Quadratic Formula', 'Parabolas', 'Vertex Form'],
    l4: ['Polynomial Operations', 'Factoring', 'Long Division'],
    l5: ['Exponent Rules', 'Logarithm Properties', 'Natural Log'],
    l6: ['Angle Types', 'Angle Relationships', 'Parallel Lines'],
    l7: ['Pythagorean Theorem', 'Congruence', 'Similar Triangles'],
    l8: ['Circle Properties', 'Circumference & Area', 'Arc Length'],
    l9: ['Distance Formula', 'Midpoint Formula', 'Graphing Lines'],
    l10: ['Sin, Cos, Tan', 'Unit Circle', 'Right Triangle Trig'],
    l11: ['Pythagorean Identities', 'Sum & Difference', 'Double Angle'],
    l12: ['Sine Rule', 'Cosine Rule', 'Area of Triangles'],
    l13: ['Limits', 'Continuity', 'Derivative Intro'],
    l14: ['Power Rule', 'Chain Rule', 'Product & Quotient'],
    l15: ['Indefinite Integrals', 'Definite Integrals', 'Area Under Curve'],
  }
  let idx = 0
  for (const [lid, t] of Object.entries(titles)) {
    t.forEach((title, i) => {
      idx++
      concepts.push({
        concept_id: `con_${idx}`,
        lesson_id: lid,
        title,
        description: `Learn about ${title.toLowerCase()}`,
        order_index: i + 1,
        estimated_duration_minutes: 8,
        content_count: 2,
        exercise_count: 3,
        mastery_level: 0,
      })
    })
  }
  return concepts
}

function seedExercises(concepts: Concept[]): Exercise[] {
  const exercises: Exercise[] = []
  let idx = 0
  for (const con of concepts) {
    for (let i = 0; i < 3; i++) {
      idx++
      exercises.push({
        exercise_id: `ex_${idx}`,
        concept_id: con.concept_id,
        question_type: i === 0 ? 'multiple_choice' : i === 1 ? 'true_false' : 'short_answer',
        prompt: i === 0
          ? `Which of the following best describes ${con.title.toLowerCase()}?`
          : i === 1
            ? `True or False: ${con.title} is an important concept in mathematics.`
            : `Explain ${con.title.toLowerCase()} in your own words.`,
        options: i === 0 ? { A: 'First option', B: 'Second option', C: 'Third option', D: 'Fourth option' } : undefined,
        difficulty: (con.order_index % 3) + 1,
        order_index: i + 1,
      })
    }
  }
  return exercises
}

function seedAssessments(): Assessment[] {
  return [
    { id: 'a1', title: 'Algebra Basics Quiz', course_id: 'c1', assessment_type: 'quiz', passing_score: 60, max_attempts: 3, is_published: true, question_count: 5, created_at: new Date().toISOString() },
    { id: 'a2', title: 'Linear Equations Test', course_id: 'c1', assessment_type: 'test', passing_score: 70, max_attempts: 2, is_published: true, question_count: 5, created_at: new Date().toISOString() },
    { id: 'a3', title: 'Geometry Fundamentals', course_id: 'c1', assessment_type: 'quiz', passing_score: 60, max_attempts: 3, is_published: true, question_count: 5, created_at: new Date().toISOString() },
  ]
}

function seedAssessmentQuestions(): AssessmentQuestion[] {
  return [
    { id: 'q1', question_type: 'multiple_choice', prompt: 'What is the value of x + 5 when x = 3?', options: { A: '5', B: '8', C: '3', D: '15' }, difficulty: 1, marks: 1, order_index: 1 },
    { id: 'q2', question_type: 'multiple_choice', prompt: 'Solve: 2x + 4 = 10', options: { A: 'x = 2', B: 'x = 3', C: 'x = 4', D: 'x = 5' }, difficulty: 2, marks: 2, order_index: 2 },
    { id: 'q3', question_type: 'true_false', prompt: 'The slope of a horizontal line is 0.', difficulty: 1, marks: 1, order_index: 3 },
    { id: 'q4', question_type: 'multiple_choice', prompt: 'What is the square root of 144?', options: { A: '10', B: '11', C: '12', D: '13' }, difficulty: 1, marks: 1, order_index: 4 },
    { id: 'q5', question_type: 'short_answer', prompt: 'Factor: x² - 9 (enter your answer using ^ for exponents)', difficulty: 3, marks: 2, order_index: 5 },
  ]
}

function seedUsers(): User[] {
  return [
    { user_id: 'u1', email: 'alex@example.com', full_name: 'Alex Chen', role: 'student' },
    { user_id: 'u2', email: 'parent@example.com', full_name: 'Sarah Chen', role: 'parent' },
    { user_id: 'u3', email: 'admin@acuity.com', full_name: 'Admin User', role: 'admin' },
    { user_id: 'u4', email: 'teacher@acuity.com', full_name: 'Mr. Johnson', role: 'teacher' },
    { user_id: 'u5', email: 'courseadmin@acuity.com', full_name: 'Course Admin', role: 'course_admin' },
    { user_id: 'u6', email: 'student2@example.com', full_name: 'Priya K.', role: 'student' },
    { user_id: 'u7', email: 'student3@example.com', full_name: 'Rahul S.', role: 'student' },
  ]
}

function seedEnrollments(): Enrollment[] {
  return [
    { enrollment_id: 'e1', course_id: 'c1', course_title: 'Mathematics', status: 'active', progress_pct: 35, pace_status: 'on_track', enrolled_at: new Date().toISOString() },
    { enrollment_id: 'e2', course_id: 'c2', course_title: 'Science', status: 'active', progress_pct: 60, pace_status: 'ahead', enrolled_at: new Date().toISOString() },
    { enrollment_id: 'e3', course_id: 'c3', course_title: 'English', status: 'active', progress_pct: 20, pace_status: 'on_track', enrolled_at: new Date().toISOString() },
    { enrollment_id: 'e4', course_id: 'c4', course_title: 'History', status: 'active', progress_pct: 10, pace_status: 'at_risk', enrolled_at: new Date().toISOString() },
  ]
}

function seedMastery(concepts: Concept[]): MasteryRecord[] {
  const records: MasteryRecord[] = []
  concepts.forEach((c, i) => {
    const level = Math.min(1, Math.max(0.1, Math.random() * 0.8 + 0.1))
    records.push({
      record_id: `mr_${i + 1}`,
      student_id: 'u1',
      concept_id: c.concept_id,
      concept_title: c.title,
      mastery_level: level,
      total_attempts: Math.floor(Math.random() * 5) + 1,
      consecutive_correct: Math.floor(Math.random() * 3),
      last_attempted_at: new Date().toISOString(),
      status: level >= 0.7 ? 'mastered' : level >= 0.3 ? 'in_progress' : 'not_started',
    })
  })
  return records
}

function seedSessions(): TeachingSession[] {
  return [
    { session_id: 's1', student_id: 'u1', course_id: 'c1', course_title: 'Mathematics', state: 'active',
      current_concept: { concept_id: 'con_8', title: 'Quadratic Formula', order_index: 1 },
      current_lesson: { lesson_id: 'l3', title: 'Quadratic Functions' },
      context_summary: { concepts_taught_this_session: 3, exercises_answered: 5, session_duration_minutes: 12 },
      started_at: new Date().toISOString(), last_activity_at: new Date().toISOString() },
  ]
}

function seedParentStudents() {
  return [{ parentId: 'u2', studentId: 'u1', linkedAt: new Date().toISOString() }]
}

function seedMisconceptions(): Misconception[] {
  return [
    { misconception_id: 'mc1', concept_id: 'con_15', concept_title: 'Trigonometric Identities', category: 'misapplication', description: 'Confuses sin²θ + cos²θ = 1 with (sinθ + cosθ)² = 1', detected_at: new Date().toISOString(), frequency: 3, is_resolved: false },
    { misconception_id: 'mc2', concept_id: 'con_42', concept_title: 'Chain Rule', category: 'procedural', description: 'Forgets to multiply by derivative of inner function', detected_at: new Date().toISOString(), frequency: 2, is_resolved: false },
  ]
}

function seedReports(): Report[] {
  return [
    { report_id: 'r1', report_type: 'weekly', generated_at: new Date().toISOString(), summary: 'Alex has made good progress in Mathematics this week. Focus on Trigonometric Identities and Chain Rule for improvement.', is_read: false, student_name: 'Alex Chen',
      sections: [
        { heading: 'Weekly Overview', body: 'Alex completed 5 lessons this week with an average score of 78%.' },
        { heading: 'Strengths', body: 'Algebra concepts are well understood with 85% mastery.' },
        { heading: 'Areas for Improvement', body: 'Trigonometry needs more practice, particularly identities.' },
      ],
      metrics: { overall_score: 72, lessons_completed: 5, time_spent_hours: 4.5 },
      recommendations: [
        { priority: 'high', action: 'Practice Trigonometric Identities daily', expected_outcome: 'Improve mastery from 25% to 50%' },
        { priority: 'medium', action: 'Review Chain Rule examples', expected_outcome: 'Build procedural fluency' },
      ],
    },
  ]
}

function initDb(): DbSchema {
  const empty: DbSchema = {
    users: [], courses: [], modules: [], lessons: [], concepts: [],
    examples: [], exercises: [], enrollments: [], masteryRecords: [],
    attempts: [], sessions: [], assessments: [], assessmentQuestions: [],
    lessonProgress: [], parentStudents: [], reports: [], misconceptions: [],
    messages: [], counter: 0,
  }
  const db = empty
  db.users = seedUsers()
  db.courses = seedCourses()
  db.modules = seedModules()
  db.lessons = db.modules.flatMap(m => m.lessons.map(l => ({
    lesson_id: l.lesson_id,
    module_id: m.module_id,
    title: l.title,
    content_url: '',
    order_index: l.order_index,
    estimated_duration_minutes: l.estimated_duration_minutes,
    concept_count: l.concept_count,
  })))
  db.concepts = seedConcepts()
  db.exercises = seedExercises(db.concepts)
  db.assessments = seedAssessments()
  db.assessmentQuestions = seedAssessmentQuestions()
  db.enrollments = seedEnrollments()
  db.masteryRecords = seedMastery(db.concepts)
  db.sessions = seedSessions()
  db.parentStudents = seedParentStudents()
  db.misconceptions = seedMisconceptions()
  db.reports = seedReports()
  db.counter = 100
  saveDb(db)
  return db
}

export function resetDb() {
  localStorage.removeItem(DB_KEY)
  initDb()
}

export const localDb = {
  // Auth
  async login(email: string, _password: string, role: string) {
    await delay()
    const db = getDb()
    let user = db.users.find(u => u.email === email && u.role === role)
    if (!user) {
      user = db.users.find(u => u.email === email)
      if (!user) {
        user = {
          user_id: id(),
          email,
          full_name: email.split('@')[0],
          role: role as any,
          created_at: new Date().toISOString(),
        }
        db.users.push(user)
      }
      saveDb(db)
    }
    return {
      access_token: `local_token_${user.user_id}`,
      refresh_token: `local_refresh_${user.user_id}`,
      token_type: 'bearer',
      expires_in: 86400,
      user,
    }
  },

  async register(email: string, _password: string, fullName: string, role: string) {
    await delay()
    const db = getDb()
    const exists = db.users.find(u => u.email === email)
    if (exists) throw new Error('User already exists')
    const newUser: User = {
      user_id: id(),
      email,
      full_name: fullName,
      role: role as any,
      created_at: new Date().toISOString(),
    }
    db.users.push(newUser)
    saveDb(db)
    return newUser
  },

  async getUsers() {
    await delay()
    return success(getDb().users)
  },

  async getCourses() {
    await delay()
    return success(getDb().courses)
  },

  async getCourse(courseId: string) {
    await delay()
    const db = getDb()
    const course = db.courses.find(c => c.course_id === courseId)
    if (!course) throw new Error('Course not found')
    return success({ ...course, modules: db.modules })
  },

  async getEnrollments(studentId: string, status?: string) {
    await delay()
    const db = getDb()
    let enrollments = db.enrollments
    if (status) enrollments = enrollments.filter(e => e.status === status)
    const withCourses = enrollments.map(e => {
      const course = db.courses.find(c => c.course_id === e.course_id)
      return { ...e, course_title: course?.title || e.course_title }
    })
    return success(withCourses)
  },

  async enroll(courseId: string) {
    await delay()
    const db = getDb()
    const course = db.courses.find(c => c.course_id === courseId)
    const enrollment: Enrollment = {
      enrollment_id: id(),
      course_id: courseId,
      course_title: course?.title || '',
      status: 'active',
      progress_pct: 0,
      pace_status: 'on_track',
      enrolled_at: new Date().toISOString(),
    }
    db.enrollments.push(enrollment)
    saveDb(db)
    return success(enrollment)
  },

  async getCurriculumTree(courseId: string) {
    await delay()
    const db = getDb()
    const course = db.courses.find(c => c.course_id === courseId)
    if (!course) throw new Error('Course not found')
    const modules: CurriculumModule[] = db.modules
      .filter(m => m.module_id.startsWith('m'))
      .map(m => {
        const lessons: CurriculumLesson[] = m.lessons.map(l => ({
          lesson_id: l.lesson_id,
          title: l.title,
          order_index: l.order_index,
          estimated_duration_minutes: l.estimated_duration_minutes,
          status: 'locked',
          concepts: db.concepts
            .filter(c => c.lesson_id === l.lesson_id)
            .map(c => ({
              concept_id: c.concept_id,
              title: c.title,
              order_index: c.order_index,
            })),
        }))
        lessons[0].status = 'active'
        return { module_id: m.module_id, title: m.title, order_index: m.order_index, lesson_count: lessons.length, lessons }
      })
    return success({
      course_id: courseId,
      course_title: course.title,
      course_code: course.code,
      modules,
    })
  },

  async getLessonProgress(lessonId: string) {
    await delay()
    const db = getDb()
    const existing = db.lessonProgress.find(lp => lp.lesson_id === lessonId)
    if (existing) return success(existing)
    const lesson = db.lessons.find(l => l.lesson_id === lessonId)
    return success({
      lesson_id: lessonId,
      lesson_title: lesson?.title,
      status: 'not_started',
      completion_percentage: 0,
      concepts: db.concepts.filter(c => c.lesson_id === lessonId).map(c => ({
        concept_id: c.concept_id,
        title: c.title,
        mastery_level: 0,
        status: 'not_started',
      })),
    })
  },

  async updateLessonProgress(lessonId: string, data: { status?: string; completion_percentage?: number }) {
    await delay()
    const db = getDb()
    let lp = db.lessonProgress.find(p => p.lesson_id === lessonId)
    if (!lp) {
      lp = { lesson_id: lessonId, status: 'in_progress', completion_percentage: 0 }
      db.lessonProgress.push(lp)
    }
    if (data.status) lp.status = data.status
    if (data.completion_percentage !== undefined) lp.completion_percentage = data.completion_percentage
    saveDb(db)
    return success(lp)
  },

  async getCourseMastery(courseId: string, studentId = 'u1') {
    await delay()
    const db = getDb()
    const courseConcepts = db.concepts.filter(c => {
      const lesson = db.lessons.find(l => l.lesson_id === c.lesson_id)
      if (!lesson) return false
      const mod = db.modules.find(m => m.module_id === lesson.module_id)
      return mod?.module_id.startsWith('m')
    })
    const records = db.masteryRecords.filter(r => r.student_id === studentId && courseConcepts.some(cc => cc.concept_id === r.concept_id))
    const total = courseConcepts.length
    const mastered = records.filter(r => r.status === 'mastered').length
    const avg = records.length > 0 ? records.reduce((s, r) => s + r.mastery_level, 0) / records.length : 0
    return success({
      course_id: courseId,
      total_concepts: total,
      mastered_concepts: mastered,
      average_mastery: avg,
      concepts: records,
    })
  },

  async getMasteryOverview(studentId = 'u1') {
    await delay()
    return success(getDb().masteryRecords.filter(r => r.student_id === studentId))
  },

  async getConcept(conceptId: string) {
    await delay()
    const db = getDb()
    const concept = db.concepts.find(c => c.concept_id === conceptId)
    if (!concept) throw new Error('Concept not found')
    const exercises = db.exercises.filter(e => e.concept_id === conceptId)
    const mastery = db.masteryRecords.find(r => r.concept_id === conceptId)
    return success({
      ...concept,
      contents: [{ content_id: `ct_${conceptId}`, content_type: 'text', content: `Learn all about ${concept.title}. This concept covers fundamental ideas that build your understanding step by step.`, order_index: 1 }],
      examples: [
        { example_id: `eg_${conceptId}_1`, content: `Example 1: Let's understand ${concept.title.toLowerCase()} with a simple problem.`, explanation: 'Start with the basics and work your way up.' },
        { example_id: `eg_${conceptId}_2`, content: `Example 2: Another practical application of ${concept.title.toLowerCase()}.`, explanation: 'Practice makes perfect!' },
      ],
      exercise_count: exercises.length,
      mastery: mastery ? { mastery_level: mastery.mastery_level, total_attempts: mastery.total_attempts, consecutive_correct: mastery.consecutive_correct } : undefined,
    })
  },

  async getConceptExercises(conceptId: string) {
    await delay()
    return success(getDb().exercises.filter(e => e.concept_id === conceptId))
  },

  async recordAttempt(exerciseId: string, data: { response: string }, studentId = 'u1') {
    await delay()
    const db = getDb()
    const exercise = db.exercises.find(e => e.exercise_id === exerciseId)
    const isCorrect = Math.random() > 0.3
    const attempt: Attempt = {
      attempt_id: id(),
      exercise_id: exerciseId,
      concept_title: db.concepts.find(c => c.concept_id === exercise?.concept_id)?.title,
      question_type: exercise?.question_type,
      prompt: exercise?.prompt,
      response: data.response,
      is_correct: isCorrect,
      score: isCorrect ? 100 : 40,
      ai_feedback: isCorrect ? 'Great job! Keep it up!' : 'Almost there! Review the concept and try again.',
      attempt_number: (db.attempts.filter(a => a.exercise_id === exerciseId).length) + 1,
      attempted_at: new Date().toISOString(),
    }
    db.attempts.push(attempt)

    if (exercise?.concept_id) {
      let mr = db.masteryRecords.find(r => r.student_id === studentId && r.concept_id === exercise.concept_id)
      if (!mr) {
        mr = { record_id: id(), student_id: studentId, concept_id: exercise.concept_id, concept_title: db.concepts.find(c => c.concept_id === exercise.concept_id)?.title, mastery_level: 0, total_attempts: 0, consecutive_correct: 0 }
        db.masteryRecords.push(mr)
      }
      mr.total_attempts++
      if (isCorrect) {
        mr.consecutive_correct++
        mr.mastery_level = Math.min(1, mr.mastery_level + 0.15)
      } else {
        mr.consecutive_correct = 0
        mr.mastery_level = Math.max(0, mr.mastery_level - 0.05)
      }
      mr.status = mr.mastery_level >= 0.7 ? 'mastered' : mr.mastery_level >= 0.3 ? 'in_progress' : 'not_started'
      mr.last_attempted_at = new Date().toISOString()
    }
    saveDb(db)
    return success(attempt)
  },

  async startSession(courseId: string, studentId = 'u1') {
    await delay()
    const db = getDb()
    const existing = db.sessions.find(s => s.student_id === studentId && s.state === 'active')
    if (existing) return success(existing)
    const session: TeachingSession = {
      session_id: id(),
      student_id: studentId,
      course_id: courseId,
      course_title: db.courses.find(c => c.course_id === courseId)?.title,
      state: 'active',
      current_concept: { concept_id: 'con_1', title: 'Variables & Expressions', order_index: 1 },
      current_lesson: { lesson_id: 'l1', title: 'Introduction to Algebra' },
      context_summary: { concepts_taught_this_session: 0, exercises_answered: 0, session_duration_minutes: 0 },
      started_at: new Date().toISOString(),
      last_activity_at: new Date().toISOString(),
    }
    db.sessions.push(session)
    saveDb(db)
    return success(session)
  },

  async endSession(sessionId: string) {
    await delay()
    const db = getDb()
    const session = db.sessions.find(s => s.session_id === sessionId)
    if (session) {
      session.state = 'ended'
      saveDb(db)
    }
    return success(session)
  },

  async teach(courseId: string, studentInput?: string) {
    await delay(400)
    const db = getDb()
    const course = db.courses.find(c => c.course_id === courseId)
    if (!studentInput) {
      return success({ action: 'teach', content: `Great! Let's start learning ${course?.title || 'this subject'}! I'll teach you step by step. Ready to begin?` })
    }
    const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
    const isGreeting = greetings.some(g => studentInput.toLowerCase().includes(g))
    if (isGreeting) {
      return success({ action: 'teach', content: `Hello there! 😊 Ready to learn some ${course?.title || 'awesome topics'} today? Let me know what you'd like to study!` })
    }
    const encouragements = ['You got this!', 'Amazing effort! 🎉', "That's a great question!", 'Keep up the fantastic work! 🌟']
    return success({
      action: 'teach',
      content: `${encouragements[Math.floor(Math.random() * encouragements.length)]}\n\nLet me explain: ${course?.title || 'the concept'} is all about understanding how things work. Think of it like building blocks - each new idea builds on what you already know!\n\nWould you like to:\n1️⃣ Try a practice exercise?\n2️⃣ Learn something new?\n3️⃣ Review what we covered?`,
    })
  },

  async getAssessments(courseId?: string) {
    await delay()
    const db = getDb()
    let assessments = db.assessments
    if (courseId) assessments = assessments.filter(a => a.course_id === courseId)
    return success(assessments)
  },

  async startAssessment(id: string) {
    await delay()
    const db = getDb()
    const assessment = db.assessments.find(a => a.id === id)
    if (!assessment) throw new Error('Assessment not found')
    const questions = db.assessmentQuestions.slice(0, assessment.question_count)
    return success({
      attempt_id: id(),
      assessment_id: id,
      started_at: new Date().toISOString(),
      attempt_number: 1,
      questions,
    })
  },

  async submitAttempt(attemptId: string, responses: { question_id: string; response: string }[]) {
    await delay()
    const db = getDb()
    const correctAnswers: Record<string, string> = { q1: 'B', q2: 'B', q3: 'true', q4: 'C', q5: '(x-3)(x+3)' }
    let total = 0
    let earned = 0
    const details: AssessmentResultDetail[] = responses.map(r => {
      const question = db.assessmentQuestions.find(q => q.id === r.question_id)
      const isCorrect = r.response.trim().toLowerCase() === (correctAnswers[r.question_id] || '').trim().toLowerCase()
      total += question?.marks || 1
      if (isCorrect) earned += question?.marks || 1
      return {
        question_id: r.question_id,
        prompt: question?.prompt || '',
        question_type: question?.question_type || '',
        marks: question?.marks || 1,
        response: r.response,
        correct_answer: correctAnswers[r.question_id] || '',
        is_correct: isCorrect,
        score: isCorrect ? (question?.marks || 1) : 0,
        feedback: isCorrect ? 'Correct!' : 'Incorrect. Review the material and try again.',
      }
    })
    const percentage = total > 0 ? (earned / total) * 100 : 0
    return success({
      attempt_id: attemptId,
      assessment_id: '',
      score: percentage,
      percentage,
      passed: percentage >= 60,
      total_marks: total,
      earned_marks: earned,
      completed_at: new Date().toISOString(),
      attempt_number: 1,
      responses: details,
    })
  },

  async getAttemptResult(attemptId: string) {
    await delay()
    const db = getDb()
    return success({
      attempt_id: attemptId,
      assessment_id: 'a1',
      assessment_title: 'Algebra Basics Quiz',
      assessment_type: 'quiz',
      passing_score: 60,
      score: 72,
      percentage: 72,
      passed: true,
      attempt_number: 1,
      completed_at: new Date().toISOString(),
      total_marks: 7,
      earned_marks: 5,
      responses: db.assessmentQuestions.slice(0, 5).map((q, i) => ({
        question_id: q.id,
        prompt: q.prompt,
        question_type: q.question_type,
        marks: q.marks,
        response: 'Sample answer',
        correct_answer: 'Correct answer',
        is_correct: i < 4,
        score: i < 4 ? q.marks : 0,
        feedback: i < 4 ? 'Correct!' : 'Incorrect.',
      })),
    })
  },

  async getAssessmentHistory() {
    await delay()
    return success([])
  },

  async getTeacherStudents() {
    await delay()
    const db = getDb()
    const students = db.users.filter(u => u.role === 'student')
    return success(students.map(s => ({
      student_id: s.user_id,
      full_name: s.full_name,
      email: s.email,
      active_courses: db.enrollments.filter(e => e.status === 'active').length,
      overall_mastery_avg: 65 + Math.floor(Math.random() * 25),
      last_active: new Date().toISOString(),
      current_streak_days: Math.floor(Math.random() * 10) + 1,
    })))
  },

  async getTeacherDashboard() {
    await delay()
    const db = getDb()
    const students = db.users.filter(u => u.role === 'student')
    return success({
      total_students: students.length,
      total_courses: db.courses.length,
      students: students.map(s => ({
        student_id: s.user_id,
        full_name: s.full_name,
        email: s.email,
        active_courses: 2,
        overall_mastery_avg: 70,
        last_active: new Date().toISOString(),
        current_streak_days: 5,
      })),
      recent_sessions: db.sessions.map(s => ({
        session_id: s.session_id,
        course_id: s.course_id,
        course_title: s.course_title,
        state: s.state,
        started_at: s.started_at,
        last_activity_at: s.last_activity_at,
      })),
    })
  },

  async getTeacherCourses() {
    await delay()
    return success(getDb().courses.map(c => ({
      course_id: c.course_id,
      title: c.title,
      code: c.code,
      role: 'instructor',
      assigned_at: new Date().toISOString(),
    })))
  },

  async getParentDashboard() {
    await delay()
    const db = getDb()
    const links = db.parentStudents
    const students: ParentStudent[] = links.map(l => {
      const student = db.users.find(u => u.user_id === l.studentId)
      const records = db.masteryRecords.filter(r => r.student_id === l.studentId)
      const avg = records.length > 0 ? records.reduce((s, r) => s + r.mastery_level, 0) / records.length * 100 : 0
      return {
        student_id: l.studentId,
        full_name: student?.full_name || 'Unknown',
        active_courses: db.enrollments.filter(e => e.status === 'active').length,
        overall_mastery_avg: Math.round(avg),
        last_active: new Date().toISOString(),
        current_streak_days: Math.floor(Math.random() * 7) + 2,
      }
    })
    return success({
      students,
      aggregate: {
        total_children: students.length,
        children_with_alerts: 1,
        unread_reports: 1,
        weekly_family_avg_accuracy: 72,
      },
    })
  },

  async getAdminDashboard() {
    await delay()
    const db = getDb()
    return success({
      total_users: db.users.length,
      total_students: db.users.filter(u => u.role === 'student').length,
      total_parents: db.users.filter(u => u.role === 'parent').length,
      total_admins: db.users.filter(u => u.role === 'admin').length,
      total_courses: db.courses.length,
      active_enrollments: db.enrollments.filter(e => e.status === 'active').length,
      active_sessions_today: db.sessions.filter(s => s.state === 'active').length,
      completion_rate_avg: 65,
    })
  },

  async getStudents() {
    await delay()
    const db = getDb()
    return success(db.users.filter(u => u.role === 'student').map(s => ({
      user_id: s.user_id,
      email: s.email,
      full_name: s.full_name,
      role: 'student' as const,
      is_active: true,
      created_at: s.created_at || new Date().toISOString(),
    })))
  },

  async getStudentReports(studentId: string) {
    await delay()
    return success(getDb().reports)
  },

  async getReport(reportId: string) {
    await delay()
    const report = getDb().reports.find(r => r.report_id === reportId)
    if (!report) throw new Error('Report not found')
    return success(report)
  },

  async generateReport(studentId: string) {
    await delay(500)
    const db = getDb()
    const report: Report = {
      report_id: id(),
      report_type: 'weekly',
      generated_at: new Date().toISOString(),
      summary: 'Personalized learning report generated. Great progress this week!',
      is_read: false,
      student_name: db.users.find(u => u.user_id === studentId)?.full_name,
      sections: [{ heading: 'Generated Report', body: 'Your AI-generated learning insights are ready.' }],
      metrics: { overall_score: 72, lessons_completed: 5, time_spent_hours: 3.5 },
      recommendations: [{ priority: 'medium', action: 'Review weak areas', expected_outcome: 'Improved mastery' }],
    }
    db.reports.push(report)
    saveDb(db)
    return success(report)
  },

  async getPacingStatus() {
    await delay()
    const db = getDb()
    return success(db.enrollments.filter(e => e.status === 'active').map(e => ({
      enrollment_id: e.enrollment_id,
      course_id: e.course_id,
      current_week: Math.floor(Math.random() * 6) + 1,
      target_lessons_per_week: 3,
      pace_status: e.pace_status || 'on_track',
    })))
  },

  async getCurrentSession(studentId = 'u1') {
    await delay()
    const db = getDb()
    return success(db.sessions.find(s => s.student_id === studentId && s.state === 'active') || null)
  },

  async getSessionHistory(studentId = 'u1') {
    await delay()
    return success(getDb().sessions.filter(s => s.student_id === studentId))
  },

  async getSession(sessionId: string) {
    await delay()
    const session = getDb().sessions.find(s => s.session_id === sessionId)
    if (!session) throw new Error('Session not found')
    return success(session)
  },

  async getParentStudent(studentId: string) {
    await delay()
    const db = getDb()
    const student = db.users.find(u => u.user_id === studentId)
    return success({
      student_id: studentId,
      full_name: student?.full_name || 'Unknown',
      active_courses: db.enrollments.filter(e => e.status === 'active').length,
      overall_mastery_avg: 72,
      last_active: new Date().toISOString(),
      current_streak_days: 5,
    })
  },

  async getStudentProgressAnalytics(studentId: string) {
    await delay()
    const db = getDb()
    const records = db.masteryRecords.filter(r => r.student_id === studentId)
    const total = records.length
    const mastered = records.filter(r => r.status === 'mastered').length
    return success({
      total_lessons: total,
      completed_lessons: mastered,
      completion_rate: total > 0 ? mastered / total : 0,
      avg_mastery: total > 0 ? records.reduce((s, r) => s + r.mastery_level, 0) / total : 0,
      time_spent_seconds: 3600,
      lessons_overdue: 1,
    })
  },

  async getCourseAnalytics(courseId: string) {
    await delay()
    return success({
      course_id: courseId,
      title: 'Mathematics',
      total_students: 1,
      active_students: 1,
      completion_rate: 0.35,
      avg_mastery: 0.45,
      avg_assessment_score: 72,
      total_assessments: 3,
    })
  },

  async getAssessmentAnalytics(courseId: string) {
    await delay()
    return success({
      average_score: 72,
      total_attempts: 5,
      pass_rate: 0.8,
      avg_time_spent_seconds: 600,
      pass_count: 4,
      fail_count: 1,
    })
  },

  async getSystemOverview() {
    await delay()
    const db = getDb()
    return success({
      total_users: db.users.length,
      total_students: db.users.filter(u => u.role === 'student').length,
      total_admins: db.users.filter(u => u.role === 'admin').length,
      total_parents: db.users.filter(u => u.role === 'parent').length,
      total_courses: db.courses.length,
      active_enrollments: db.enrollments.filter(e => e.status === 'active').length,
      active_sessions_today: db.sessions.filter(s => s.state === 'active').length,
      total_assessment_attempts: db.attempts.length,
      overall_pass_rate: 0.75,
      overall_completion_rate: 0.6,
    })
  },

  async getMisconceptions(studentId: string) {
    await delay()
    return success(getDb().misconceptions)
  },

  async getTeacherStudentProgress(studentId: string) {
    await delay()
    return success({ completionRate: 0.45, avgMastery: 0.62, timeSpentHours: 12 })
  },

  async getTeacherStudentMastery(studentId: string) {
    await delay()
    return success(getDb().masteryRecords.filter(r => r.student_id === studentId))
  },

  async getTeacherStudentSessions(studentId: string) {
    await delay()
    return success(getDb().sessions.filter(s => s.student_id === studentId))
  },

  async getTeacherStudentAttempts(studentId: string) {
    await delay()
    return success(getDb().attempts.filter(a => true))
  },

  async getModuleLessons(moduleId: string) {
    await delay()
    const db = getDb()
    const mod = db.modules.find(m => m.module_id === moduleId)
    if (!mod) return success([])
    return success(mod.lessons.map(l => ({
      ...l,
      module_id: moduleId,
      status: 'active',
      concepts: db.concepts.filter(c => c.lesson_id === l.lesson_id),
    })))
  },

  async getLesson(lessonId: string) {
    await delay()
    const db = getDb()
    const lesson = db.lessons.find(l => l.lesson_id === lessonId)
    if (!lesson) throw new Error('Lesson not found')
    return success({ ...lesson, status: 'active', concepts: db.concepts.filter(c => c.lesson_id === lessonId) })
  },

  async getLessonConcepts(lessonId: string) {
    await delay()
    return success(getDb().concepts.filter(c => c.lesson_id === lessonId))
  },

  async getCourseModules(courseId: string) {
    await delay()
    return success(getDb().modules.map(m => ({
      module_id: m.module_id,
      course_id,
      title: m.title,
      order_index: m.order_index,
      lesson_count: m.lessons.length,
    })))
  },

  async getAttempts() {
    await delay()
    return success(getDb().attempts)
  },

  async getParentStudentCurriculum(studentId: string, courseId: string) {
    return this.getCurriculumTree(courseId)
  },

  async createCourse(data: { code: string; title: string; description?: string }) {
    await delay()
    const db = getDb()
    const course: Course = {
      course_id: id(),
      code: data.code,
      title: data.title,
      description: data.description,
      total_duration_hours: 30,
      default_deadline_days: 90,
      is_published: false,
      created_at: new Date().toISOString(),
    }
    db.courses.push(course)
    saveDb(db)
    return success(course)
  },

  async deleteCourse(courseId: string) {
    await delay()
    const db = getDb()
    db.courses = db.courses.filter(c => c.course_id !== courseId)
    saveDb(db)
    return success({ message: 'Course deleted' })
  },

  async getAdminUsers() {
    await delay()
    const db = getDb()
    return success(db.users.map(u => ({
      user_id: u.user_id,
      email: u.email,
      full_name: u.full_name,
      role: u.role,
      is_active: true,
      created_at: u.created_at || new Date().toISOString(),
    })))
  },

  async getAdminUser(userId: string) {
    await delay()
    const db = getDb()
    const user = db.users.find(u => u.user_id === userId)
    if (!user) throw new Error('User not found')
    return success({
      user_id: user.user_id,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      is_active: true,
      created_at: user.created_at || new Date().toISOString(),
    })
  },

  async getAdminCourseAnalytics(courseId: string) {
    await delay()
    return success({ course_id: courseId, enrollmentCount: 25, avgScore: 78 })
  },

  // Course admin
  async getCourseAdminDashboard() {
    await delay()
    const db = getDb()
    return success({
      total_courses: db.courses.length,
      deployed_count: db.courses.filter(c => c.is_published).length,
      draft_count: db.courses.filter(c => !c.is_published).length,
      total_students: db.users.filter(u => u.role === 'student').length,
      total_published: db.courses.filter(c => c.is_published).length,
      active_sessions: db.sessions.filter(s => s.state === 'active').length,
      pending_review_count: 2,
      failed_stages_count: 0,
      total_concepts_generated: 48,
      total_exercises_generated: 144,
      avg_coverage_pct: 85,
      recent_courses: db.courses.slice(0, 3).map(c => ({
        id: c.course_id,
        name: c.title,
        status: c.is_published ? 'deployed' : 'draft',
        created_at: c.created_at || new Date().toISOString(),
        updated_at: new Date().toISOString(),
      })),
      training_count: 1,
      review_count: 1,
    })
  },

  async listCourseAdminCourses() {
    await delay()
    const db = getDb()
    return success(db.courses.map(c => ({
      id: c.course_id,
      name: c.title,
      description: c.description,
      status: c.is_published ? 'deployed' : 'draft',
      created_at: c.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })))
  },

  async getCourseAdminCourse(courseId: string) {
    await delay()
    const db = getDb()
    const course = db.courses.find(c => c.course_id === courseId)
    if (!course) throw new Error('Course not found')
    return success({
      id: course.course_id,
      name: course.title,
      description: course.description,
      status: course.is_published ? 'deployed' : 'draft',
      course_id: course.course_id,
      knowledge_sources: [],
      stages: [],
      created_at: course.created_at || new Date().toISOString(),
      updated_at: new Date().toISOString(),
    })
  },

  async createCourseAdminCourse(name: string, description?: string) {
    return this.createCourse({ code: name.toUpperCase().slice(0, 3) + Math.floor(Math.random() * 100), title: name, description })
  },

  // Pacing
  async generateSchedule() {
    await delay()
    return success({ enrollment_id: 'e1', current_week: 1, target_lessons_per_week: 3, pace_status: 'on_track' })
  },

  async updatePacing(enrollmentId: string, pace_status: string) {
    await delay()
    const db = getDb()
    const enrollment = db.enrollments.find(e => e.enrollment_id === enrollmentId)
    if (enrollment) {
      enrollment.pace_status = pace_status
      saveDb(db)
    }
    return success({ enrollment_id: enrollmentId, current_week: 1, target_lessons_per_week: 3, pace_status })
  },

  async getParentStudentMisconceptions(studentId: string) {
    return this.getMisconceptions(studentId)
  },

  async getParentStudentSessions(studentId: string) {
    await delay()
    return success(getDb().sessions.filter(s => s.student_id === studentId))
  },

  async getParentStudentRecentActivity(studentId: string) {
    await delay()
    return success(getDb().attempts.slice(0, 10))
  },

  async getParentStudentProgress(studentId: string) {
    return this.getStudentProgressAnalytics(studentId)
  },

  // Link codes
  async generateLinkingCode() {
    await delay()
    const code = Math.random().toString(36).substring(2, 8).toUpperCase()
    return success({ code, expires_at: new Date(Date.now() + 86400000).toISOString() })
  },

  async linkStudent(code: string) {
    await delay()
    const db = getDb()
    const student = db.users.find(u => u.role === 'student')
    if (!student) throw new Error('Student not found')
    db.parentStudents.push({ parentId: 'u2', studentId: student.user_id, linkedAt: new Date().toISOString() })
    saveDb(db)
    return success({ link_id: id(), student_id: student.user_id, full_name: student.full_name, status: 'linked', message: 'Student linked successfully' })
  },
}
