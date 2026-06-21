from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException, ValidationException
from app.common.types import PaceStatus
from app.curriculum.repository import CourseRepository
from app.enrollment.models import CourseSchedule, StudentCourseEnrollment
from app.enrollment.repository import CourseScheduleRepository, EnrollmentRepository
from app.users.models import StudentProfile
from app.users.repository import StudentProfileRepository


class PacingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.schedule_repo = CourseScheduleRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.course_repo = CourseRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)

    async def _get_student_profile(self, user_id: str) -> StudentProfile:
        profile = await self.student_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="Student profile not found")
        return profile

    async def _get_enrollment(self, enrollment_id: str, student_id: str) -> StudentCourseEnrollment:
        enrollment = await self.enrollment_repo.get(enrollment_id)
        if enrollment is None or enrollment.student_id != student_id:
            raise NotFoundException(message="Enrollment not found")
        return enrollment

    async def generate_schedule(
        self, enrollment_id: str, user_id: str
    ) -> CourseSchedule:
        profile = await self._get_student_profile(user_id)
        enrollment = await self._get_enrollment(enrollment_id, profile.id)

        existing = await self.schedule_repo.find_by_enrollment(enrollment_id)
        if existing is not None:
            raise ValidationException(
                message="Schedule already exists for this enrollment"
            )

        course = await self.course_repo.get(enrollment.course_id)
        if course is None:
            raise NotFoundException(message="Course not found")

        total_lessons = sum(
            len(m.lessons) for m in course.modules if hasattr(m, "lessons")
        ) or 1
        weeks = max(course.default_deadline_days // 7, 1)
        lessons_per_week = max(round(total_lessons / weeks), 1)

        return await self.schedule_repo.create(
            enrollment_id=enrollment_id,
            target_lessons_per_week=lessons_per_week,
            current_week=1,
            pace_status=PaceStatus.ON_TRACK,
        )

    async def get_pacing_status(self, user_id: str) -> list[dict]:
        profile = await self._get_student_profile(user_id)
        enrollments = await self.enrollment_repo.find_by_student(profile.id)

        result = []
        for enrollment in enrollments:
            schedule = await self.schedule_repo.find_by_enrollment(enrollment.id)
            if schedule is None:
                continue

            course = await self.course_repo.get(enrollment.course_id)
            course_title = course.title if course else "Unknown"

            result.append({
                "enrollment_id": enrollment.id,
                "course_id": enrollment.course_id,
                "course_title": course_title,
                "schedule_id": schedule.id,
                "current_week": schedule.current_week,
                "target_lessons_per_week": schedule.target_lessons_per_week,
                "pace_status": schedule.pace_status,
                "last_pacing_adjustment_at": schedule.last_pacing_adjustment_at,
            })

        return result

    async def update_pacing_status(
        self, user_id: str, enrollment_id: str, pace_status: PaceStatus
    ) -> CourseSchedule:
        profile = await self._get_student_profile(user_id)
        enrollment = await self._get_enrollment(enrollment_id, profile.id)

        schedule = await self.schedule_repo.find_by_enrollment(enrollment.id)
        if schedule is None:
            raise NotFoundException(message="Course schedule not found")

        updated = await self.schedule_repo.update(
            schedule.id,
            pace_status=pace_status,
            last_pacing_adjustment_at=datetime.now(timezone.utc),
        )
        if updated is None:
            raise NotFoundException(message="Course schedule not found")
        return updated
