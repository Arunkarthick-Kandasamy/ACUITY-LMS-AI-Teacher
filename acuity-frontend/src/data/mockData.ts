export const studentProfile = {
  id: 's1',
  name: 'Abinaya',
  grade: '10th Grade',
  avatar: 'AB',
  subject: 'Mathematics',
  currentLesson: 'Quadratic Functions',
  openScore: 72,
  track: 'Support' as const,
  strengths: ['Linear Equations', 'Basic Algebra', 'Fractions'],
  improvements: ['Trigonometric Identities', 'Chain Rule'],
  learningPace: 'Moderate',
  peakLearningTime: '10:00 AM - 12:00 PM',
}

export const openScoreData = {
  overall: 72,
  parameters: {
    correctness: 78,
    responseTime: 65,
    retries: 70,
    skips: 75,
  },
  history: [
    { lesson: 'L1', score: 45 },
    { lesson: 'L2', score: 52 },
    { lesson: 'L3', score: 48 },
    { lesson: 'L4', score: 63 },
    { lesson: 'L5', score: 71 },
    { lesson: 'L6', score: 68 },
    { lesson: 'L7', score: 82 },
    { lesson: 'L8', score: 78 },
  ],
}

export const lessons = [
  { id: 1, title: 'Introduction to Algebra', status: 'completed' as const, score: 85, xp: 100 },
  { id: 2, title: 'Linear Equations', status: 'completed' as const, score: 78, xp: 150 },
  { id: 3, title: 'Quadratic Functions', status: 'active' as const, score: null, xp: 200 },
  { id: 4, title: 'Polynomials', status: 'locked' as const, score: null, xp: 250 },
  { id: 5, title: 'Exponents & Logarithms', status: 'locked' as const, score: null, xp: 300 },
  { id: 6, title: 'Trigonometry Basics', status: 'locked' as const, score: null, xp: 350 },
]

export const chatHistory = [
  { id: 1, role: 'ai' as const, content: "Hi Abinaya! Ready to learn Quadratic Functions today?", time: '10:30 AM' },
  { id: 2, role: 'user' as const, content: "Yes! I've been practicing linear equations.", time: '10:31 AM' },
  { id: 3, role: 'ai' as const, content: "Great! A quadratic function is written as f(x) = ax² + bx + c. The graph forms a U-shaped curve called a parabola.", time: '10:31 AM' },
  { id: 4, role: 'ai' as const, content: "The value of 'a' determines whether the parabola opens upward (a > 0) or downward (a < 0). Can you tell me what happens when a = 0?", time: '10:32 AM' },
]

export const parentData = {
  studentName: 'Abinaya',
  grade: '10th Grade',
  overallMastery: 72,
  currentTrack: 'Support (Weak Learner)',
  trackReason: 'Open Score of 72 — needs foundational reinforcement',
  timeSpentThisWeek: 14.5,
  previousWeekTime: 12,
  moduleType: 'Simplified, step-by-step with examples',
  weeklyScores: [
    { day: 'Mon', score: 65 },
    { day: 'Tue', score: 70 },
    { day: 'Wed', score: 68 },
    { day: 'Thu', score: 78 },
    { day: 'Fri', score: 75 },
    { day: 'Sat', score: 82 },
    { day: 'Sun', score: 80 },
  ],
  alerts: [
    { id: 1, type: 'warning' as const, message: 'Response time slowing down in Trigonometry', date: '2 days ago' },
    { id: 2, type: 'success' as const, message: 'Accuracy improved 15% in Algebra this week!', date: '3 days ago' },
    { id: 3, type: 'info' as const, message: 'Peak learning time identified: 10 AM - 12 PM', date: '5 days ago' },
  ],
  weakTopics: [
    { topic: 'Trigonometric Identities', mastery: 25 },
    { topic: 'Chain Rule', mastery: 30 },
    { topic: 'Integration', mastery: 35 },
  ],
  strongTopics: [
    { topic: 'Linear Equations', mastery: 95 },
    { topic: 'Basic Algebra', mastery: 92 },
    { topic: 'Statistics', mastery: 88 },
  ],
}

export const adminData = {
  totalStudents: 1248,
  totalParents: 892,
  activeToday: 456,
  avgOpenScore: 68.5,
  students: [
    { id: 's1', name: 'Abinaya', grade: '10th', score: 72, track: 'Support', lessons: 24, lastActive: '2 hours ago' },
    { id: 's2', name: 'Arjun M.', grade: '9th', score: 88, track: 'Good', lessons: 31, lastActive: '5 mins ago' },
    { id: 's3', name: 'Priya K.', grade: '11th', score: 45, track: 'Support', lessons: 12, lastActive: '1 hour ago' },
    { id: 's4', name: 'Rahul S.', grade: '10th', score: 92, track: 'Good', lessons: 45, lastActive: 'Just now' },
    { id: 's5', name: 'Divya L.', grade: '12th', score: 61, track: 'Support', lessons: 18, lastActive: '30 mins ago' },
    { id: 's6', name: 'Karthik R.', grade: '9th', score: 79, track: 'Good', lessons: 28, lastActive: '3 hours ago' },
  ],
  trackDistribution: { good: 487, support: 761 },
  weeklyEnrollments: [
    { week: 'W1', count: 45 },
    { week: 'W2', count: 62 },
    { week: 'W3', count: 58 },
    { week: 'W4', count: 78 },
    { week: 'W5', count: 92 },
    { week: 'W6', count: 105 },
    { week: 'W7', count: 120 },
    { week: 'W8', count: 145 },
  ],
}
