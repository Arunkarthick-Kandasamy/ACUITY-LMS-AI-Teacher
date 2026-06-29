
from pydantic import BaseModel


class AssessmentAnalytics(BaseModel):
    average_score: float = 0.0
    total_attempts: int = 0
    pass_rate: float = 0.0
    avg_time_spent_seconds: float | None = None
    pass_count: int = 0
    fail_count: int = 0

class StudentProgressAnalytics(BaseModel):
    total_lessons: int = 0
    completed_lessons: int = 0
    completion_rate: float = 0.0
    average_mastery: float = 0.0
    total_time_spent_minutes: float = 0.0
    lessons_overdue: int = 0

class CourseProgressAnalytics(BaseModel):
    total_students: int = 0
    active_students: int = 0
    average_completion_rate: float = 0.0
    average_mastery_score: float = 0.0
    total_assessments_taken: int = 0
    average_assessment_score: float = 0.0

class SystemOverview(BaseModel):
    total_users: int = 0
    total_students: int = 0
    total_teachers: int = 0
    total_courses: int = 0
    total_enrollments: int = 0
    total_assessment_attempts: int = 0
    active_sessions_today: int = 0

class DashboardAnalyticsResponse(BaseModel):
    assessments: AssessmentAnalytics
    progress: StudentProgressAnalytics
    course: CourseProgressAnalytics | None = None
    overview: SystemOverview | None = None
