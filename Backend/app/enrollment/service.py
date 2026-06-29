from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.common.types import EnrollmentStatus, PaceStatus
from app.curriculum.models import Course
from app.enrollment.models import StudentCourseEnrollment
from app.enrollment.repository import CourseScheduleRepository, EnrollmentRepository
from app.users.models import StudentProfile
from app.users.repository import StudentProfileRepository


class EnrollmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.enrollment_repo = EnrollmentRepository(session)
        self.schedule_repo = CourseScheduleRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)

    async def _get_student_profile(self, user_id: str) -> StudentProfile:
        profile = await self.student_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise ValidationException(message="User does not have a student profile")
        return profile

    async def _get_course(self, course_id: str) -> Course:
        from app.curriculum.repository import CourseRepository

        repo = CourseRepository(self.session)
        course = await repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        if not course.is_published:
            raise ValidationException(message="Course is not published")
        return course

    async def enroll(self, user_id: str, course_id: str) -> StudentCourseEnrollment:
        profile = await self._get_student_profile(user_id)
        course = await self._get_course(course_id)

        existing = await self.enrollment_repo.find_active_by_student_and_course(
            profile.id, course_id
        )
        if existing is not None:
            raise ConflictException(
                message="Already enrolled in this course", code="ALREADY_ENROLLED"
            )

        now = datetime.now(timezone.utc)
        target_date = date.today() + timedelta(days=course.default_deadline_days)

        enrollment = await self.enrollment_repo.create(
            student_id=profile.id,
            course_id=course_id,
            status=EnrollmentStatus.ACTIVE,
            enrolled_at=now,
            started_at=now,
            target_completion_date=target_date,
        )

        total_lessons = sum(
            len(m.lessons) for m in course.modules if hasattr(m, "lessons")
        ) or 1
        weeks = max(course.default_deadline_days // 7, 1)
        lessons_per_week = max(round(total_lessons / weeks), 1)

        await self.schedule_repo.create(
            enrollment_id=enrollment.id,
            target_lessons_per_week=lessons_per_week,
            current_week=1,
            pace_status=PaceStatus.ON_TRACK,
        )

        return enrollment

    async def list_enrollments(
        self, user_id: str, is_admin: bool = False, is_course_admin: bool = False, student_id: str | None = None
    ) -> list[StudentCourseEnrollment]:
        if (is_admin or is_course_admin) and student_id:
            profile = await self.student_profile_repo.get(student_id)
            if profile is None:
                raise NotFoundException(message="Student profile not found")
            if is_course_admin:
                from app.teacher.repository import TeacherStudentAssignmentRepository
                repo = TeacherStudentAssignmentRepository(self.session)
                link = await repo.find_by_teacher_and_student(user_id, profile.id)
                if link is None:
                    raise ForbiddenException(message="You are not assigned to this student")
            return await self.enrollment_repo.find_by_student(profile.id)
        profile = await self._get_student_profile(user_id)
        return await self.enrollment_repo.find_by_student(profile.id)

    async def get_enrollment(
        self, enrollment_id: str, user_id: str, is_admin: bool = False, is_course_admin: bool = False
    ) -> StudentCourseEnrollment:
        enrollment = await self.enrollment_repo.get(enrollment_id)
        if enrollment is None:
            raise NotFoundException(message="Enrollment not found")

        if not is_admin:
            if is_course_admin:
                from app.teacher.repository import TeacherStudentAssignmentRepository
                repo = TeacherStudentAssignmentRepository(self.session)
                link = await repo.find_by_teacher_and_student(user_id, enrollment.student_id)
                if link is None:
                    raise NotFoundException(message="Enrollment not found")
            else:
                profile = await self._get_student_profile(user_id)
                if enrollment.student_id != profile.id:
                    raise NotFoundException(message="Enrollment not found")

        return enrollment
