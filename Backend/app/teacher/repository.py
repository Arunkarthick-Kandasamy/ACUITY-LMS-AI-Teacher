from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository

from .models import TeacherCourseAssignment, TeacherStudentAssignment


class TeacherStudentAssignmentRepository(Repository[TeacherStudentAssignment]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(TeacherStudentAssignment, session)

    async def find_by_teacher(
        self, teacher_id: str
    ) -> list[TeacherStudentAssignment]:
        stmt = (
            select(TeacherStudentAssignment)
            .where(TeacherStudentAssignment.teacher_id == teacher_id)
            .order_by(TeacherStudentAssignment.assigned_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_student(
        self, student_id: str
    ) -> list[TeacherStudentAssignment]:
        stmt = select(TeacherStudentAssignment).where(
            TeacherStudentAssignment.student_id == student_id
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_teacher_and_student(
        self, teacher_id: str, student_id: str
    ) -> TeacherStudentAssignment | None:
        stmt = select(TeacherStudentAssignment).where(
            TeacherStudentAssignment.teacher_id == teacher_id,
            TeacherStudentAssignment.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class TeacherCourseAssignmentRepository(Repository[TeacherCourseAssignment]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(TeacherCourseAssignment, session)

    async def find_by_teacher(
        self, teacher_id: str
    ) -> list[TeacherCourseAssignment]:
        stmt = (
            select(TeacherCourseAssignment)
            .where(TeacherCourseAssignment.teacher_id == teacher_id)
            .order_by(TeacherCourseAssignment.assigned_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_course(
        self, course_id: str
    ) -> list[TeacherCourseAssignment]:
        stmt = select(TeacherCourseAssignment).where(
            TeacherCourseAssignment.course_id == course_id
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
