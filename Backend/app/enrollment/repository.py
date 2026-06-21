from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.enrollment.models import CourseSchedule, StudentCourseEnrollment


class EnrollmentRepository(Repository[StudentCourseEnrollment]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(StudentCourseEnrollment, session)

    async def find_by_student(self, student_id: str) -> list[StudentCourseEnrollment]:
        stmt = (
            select(StudentCourseEnrollment)
            .where(StudentCourseEnrollment.student_id == student_id)
            .order_by(StudentCourseEnrollment.enrolled_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_active_by_student_and_course(
        self, student_id: str, course_id: str
    ) -> StudentCourseEnrollment | None:
        from app.common.types import EnrollmentStatus

        stmt = select(StudentCourseEnrollment).where(
            StudentCourseEnrollment.student_id == student_id,
            StudentCourseEnrollment.course_id == course_id,
            StudentCourseEnrollment.status == EnrollmentStatus.ACTIVE,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class CourseScheduleRepository(Repository[CourseSchedule]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(CourseSchedule, session)

    async def find_by_enrollment(self, enrollment_id: str) -> CourseSchedule | None:
        stmt = select(CourseSchedule).where(CourseSchedule.enrollment_id == enrollment_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
