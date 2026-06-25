from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessments.models import Assessment, AssessmentAttempt
from app.curriculum.models import Course, Lesson
from app.enrollment.models import StudentCourseEnrollment
from app.mastery.models import MasteryRecord
from app.teaching.models import LessonProgress, TeachingSession
from app.users.models import User
from app.common.types import EnrollmentStatus, LessonProgressStatus, UserRole

from .schemas import (
    AssessmentAnalytics,
    CourseProgressAnalytics,
    StudentProgressAnalytics,
    SystemOverview,
)


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_assessment_analytics(self, course_id: int) -> AssessmentAnalytics:
        result = await self.session.execute(
            select(AssessmentAttempt)
            .join(Assessment, AssessmentAttempt.assessment_id == Assessment.id)
            .where(
                Assessment.course_id == course_id,
                AssessmentAttempt.completed_at.isnot(None),
            )
        )
        attempts = result.scalars().all()

        total = len(attempts)
        if total == 0:
            return AssessmentAnalytics()

        scores = [a.score for a in attempts if a.score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        pass_count = sum(1 for a in attempts if a.passed)
        fail_count = total - pass_count
        pass_rate = (pass_count / total * 100) if total > 0 else 0.0

        time_spent = []
        for a in attempts:
            if a.started_at and a.completed_at:
                diff = (a.completed_at - a.started_at).total_seconds()
                if diff >= 0:
                    time_spent.append(diff)
        avg_time = sum(time_spent) / len(time_spent) if time_spent else None

        return AssessmentAnalytics(
            average_score=round(avg_score, 2),
            total_attempts=total,
            pass_rate=round(pass_rate, 2),
            avg_time_spent_seconds=round(avg_time, 2) if avg_time is not None else None,
            pass_count=pass_count,
            fail_count=fail_count,
        )

    async def get_student_progress_analytics(
        self, student_id: int
    ) -> StudentProgressAnalytics:
        result = await self.session.execute(
            select(LessonProgress).where(LessonProgress.student_id == student_id)
        )
        lessons = result.scalars().all()

        total_lessons = len(lessons)
        completed_lessons = sum(
            1 for lp in lessons if lp.status == LessonProgressStatus.COMPLETED
        )
        completion_rate = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0.0
        )
        total_time_seconds = sum(lp.time_spent_seconds or 0 for lp in lessons)
        total_time_minutes = total_time_seconds / 60.0

        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        lessons_overdue = sum(
            1
            for lp in lessons
            if lp.status == LessonProgressStatus.IN_PROGRESS
            and lp.started_at is not None
            and lp.started_at < cutoff
        )

        mastery_result = await self.session.execute(
            select(func.coalesce(func.avg(MasteryRecord.mastery_level), 0.0)).where(
                MasteryRecord.student_id == student_id
            )
        )
        avg_mastery = float(mastery_result.scalar() or 0.0)

        return StudentProgressAnalytics(
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            completion_rate=round(completion_rate, 2),
            average_mastery=round(avg_mastery, 4),
            total_time_spent_minutes=round(total_time_minutes, 2),
            lessons_overdue=lessons_overdue,
        )

    async def get_course_analytics(self, course_id: int) -> CourseProgressAnalytics:
        total_students = (
            await self.session.scalar(
                select(func.count())
                .select_from(StudentCourseEnrollment)
                .where(StudentCourseEnrollment.course_id == course_id)
            )
            or 0
        )

        active_students = (
            await self.session.scalar(
                select(func.count())
                .select_from(StudentCourseEnrollment)
                .where(
                    StudentCourseEnrollment.course_id == course_id,
                    StudentCourseEnrollment.status == EnrollmentStatus.ACTIVE,
                )
            )
            or 0
        )

        avg_completion = float(
            await self.session.scalar(
                select(func.coalesce(func.avg(LessonProgress.completion_percentage), 0.0))
                .select_from(LessonProgress)
                .join(
                    StudentCourseEnrollment,
                    and_(
                        LessonProgress.student_id == StudentCourseEnrollment.student_id,
                        StudentCourseEnrollment.course_id == course_id,
                    ),
                )
            )
            or 0.0
        )

        avg_mastery = float(
            await self.session.scalar(
                select(func.coalesce(func.avg(MasteryRecord.mastery_level), 0.0))
                .select_from(MasteryRecord)
                .join(
                    StudentCourseEnrollment,
                    and_(
                        MasteryRecord.student_id == StudentCourseEnrollment.student_id,
                        StudentCourseEnrollment.course_id == course_id,
                    ),
                )
            )
            or 0.0
        )

        total_assessments_taken = (
            await self.session.scalar(
                select(func.count())
                .select_from(AssessmentAttempt)
                .join(Assessment, AssessmentAttempt.assessment_id == Assessment.id)
                .where(Assessment.course_id == course_id)
            )
            or 0
        )

        avg_assessment_score = float(
            await self.session.scalar(
                select(func.coalesce(func.avg(AssessmentAttempt.score), 0.0))
                .select_from(AssessmentAttempt)
                .join(Assessment, AssessmentAttempt.assessment_id == Assessment.id)
                .where(
                    Assessment.course_id == course_id,
                    AssessmentAttempt.completed_at.isnot(None),
                )
            )
            or 0.0
        )

        return CourseProgressAnalytics(
            total_students=total_students,
            active_students=active_students,
            average_completion_rate=round(avg_completion, 2),
            average_mastery_score=round(avg_mastery, 4),
            total_assessments_taken=total_assessments_taken,
            average_assessment_score=round(avg_assessment_score, 2),
        )

    async def get_system_overview(self) -> SystemOverview:
        user_counts = await self.session.execute(
            select(User.role, func.count(User.id)).group_by(User.role)
        )
        role_counts = dict(user_counts.all())

        total_courses = (
            await self.session.scalar(
                select(func.count()).select_from(Course)
            )
            or 0
        )

        total_enrollments = (
            await self.session.scalar(
                select(func.count()).select_from(StudentCourseEnrollment)
            )
            or 0
        )

        total_attempts = (
            await self.session.scalar(
                select(func.count()).select_from(AssessmentAttempt)
            )
            or 0
        )

        active_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        active_sessions = (
            await self.session.scalar(
                select(func.count())
                .select_from(TeachingSession)
                .where(TeachingSession.last_activity_at >= active_cutoff)
            )
            or 0
        )

        return SystemOverview(
            total_users=sum(role_counts.values()),
            total_students=role_counts.get(UserRole.STUDENT, 0),
            total_teachers=role_counts.get(UserRole.TEACHER, 0),
            total_courses=total_courses,
            total_enrollments=total_enrollments,
            total_assessment_attempts=total_attempts,
            active_sessions_today=active_sessions,
        )
