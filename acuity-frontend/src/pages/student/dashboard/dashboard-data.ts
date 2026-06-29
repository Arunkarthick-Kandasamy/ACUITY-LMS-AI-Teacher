export interface Subject {
  id: string
  name: string
  icon: string
  color: string
  colorHex: string
  progress: number
  lessonsCompleted: number
  totalLessons: number
  description: string
}

export interface Activity {
  id: string
  type: 'quiz' | 'lesson' | 'badge' | 'practice'
  description: string
  subject: string
  timestamp: string
  score?: number
}

export interface RecommendedLesson {
  id: string
  title: string
  subject: string
  subjectColor: string
  duration: string
}

export const student = {
  name: 'Alex Chen',
  initials: 'AC',
  streak: 7,
  weeklyHours: 12,
}

export const subjects: Subject[] = [
  {
    id: 'math', name: 'Mathematics', icon: '📐',
    color: 'blue', colorHex: '#1E90FF',
    progress: 70, lessonsCompleted: 42, totalLessons: 60,
    description: 'Algebra, Geometry, Calculus',
  },
  {
    id: 'science', name: 'Science', icon: '🔬',
    color: 'green', colorHex: '#22C55E',
    progress: 85, lessonsCompleted: 34, totalLessons: 40,
    description: 'Biology, Chemistry, Physics',
  },
  {
    id: 'english', name: 'English', icon: '📖',
    color: 'purple', colorHex: '#A855F7',
    progress: 60, lessonsCompleted: 24, totalLessons: 40,
    description: 'Literature, Grammar, Writing',
  },
  {
    id: 'history', name: 'History', icon: '🌍',
    color: 'orange', colorHex: '#F97316',
    progress: 45, lessonsCompleted: 18, totalLessons: 40,
    description: 'World History, Civics',
  },
]

export const recentActivity: Activity[] = [
  { id: 'a1', type: 'quiz', description: 'Quadratic Functions', subject: 'Mathematics', timestamp: '2 hours ago', score: 88 },
  { id: 'a2', type: 'lesson', description: 'Photosynthesis & Cellular Respiration', subject: 'Science', timestamp: '5 hours ago' },
  { id: 'a3', type: 'badge', description: 'Math Whiz — Level 2', subject: 'Mathematics', timestamp: '1 day ago' },
  { id: 'a4', type: 'practice', description: 'Grammar: Parts of Speech', subject: 'English', timestamp: '2 days ago', score: 92 },
]

export const recommendedLessons: RecommendedLesson[] = [
  { id: 'r1', title: 'Solving Quadratic Equations', subject: 'Mathematics', subjectColor: '#1E90FF', duration: '12 min' },
  { id: 'r2', title: 'Cell Division & Mitosis', subject: 'Science', subjectColor: '#22C55E', duration: '15 min' },
  { id: 'r3', title: 'Shakespeare: Hamlet Act II', subject: 'English', subjectColor: '#A855F7', duration: '10 min' },
]
