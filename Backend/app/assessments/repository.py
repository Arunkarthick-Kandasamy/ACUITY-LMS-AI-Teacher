from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.assessments.models import (
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResponse,
    QuestionBank,
)


class AssessmentRepository(Repository[Assessment]):
    def __init__(self, session) -> None:
        super().__init__(Assessment, session)

    async def find_by_course(self, course_id: str) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .where(Assessment.course_id == course_id)
            .order_by(Assessment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_published_by_course(self, course_id: str) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .where(Assessment.course_id == course_id, Assessment.is_published.is_(True))
            .order_by(Assessment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_published(self) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .where(Assessment.is_published.is_(True))
            .order_by(Assessment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class AssessmentQuestionRepository(Repository[AssessmentQuestion]):
    def __init__(self, session) -> None:
        super().__init__(AssessmentQuestion, session)

    async def find_by_assessment(self, assessment_id: str) -> list[AssessmentQuestion]:
        stmt = (
            select(AssessmentQuestion)
            .where(AssessmentQuestion.assessment_id == assessment_id)
            .order_by(AssessmentQuestion.order_index)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete_by_assessment(self, assessment_id: str) -> None:
        questions = await self.find_by_assessment(assessment_id)
        for q in questions:
            await self.session.delete(q)


class AssessmentAttemptRepository(Repository[AssessmentAttempt]):
    def __init__(self, session) -> None:
        super().__init__(AssessmentAttempt, session)

    async def find_by_assessment_and_student(
        self, assessment_id: str, student_id: str
    ) -> list[AssessmentAttempt]:
        stmt = (
            select(AssessmentAttempt)
            .where(
                AssessmentAttempt.assessment_id == assessment_id,
                AssessmentAttempt.student_id == student_id,
            )
            .order_by(AssessmentAttempt.attempt_number.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_student(
        self, student_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[AssessmentAttempt], int]:
        return await self.find(
            AssessmentAttempt.student_id == student_id,
            offset=offset,
            limit=limit,
            order_by=AssessmentAttempt.started_at.desc(),
        )

    async def count_by_student(self, student_id: str) -> int:
        return await self.count(AssessmentAttempt.student_id == student_id)

    async def get_max_attempt_number(
        self, assessment_id: str, student_id: str
    ) -> int:
        from sqlalchemy import func

        stmt = select(func.coalesce(func.max(AssessmentAttempt.attempt_number), 0)).where(
            AssessmentAttempt.assessment_id == assessment_id,
            AssessmentAttempt.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0


class AssessmentResponseRepository(Repository[AssessmentResponse]):
    def __init__(self, session) -> None:
        super().__init__(AssessmentResponse, session)

    async def find_by_attempt(self, attempt_id: str) -> list[AssessmentResponse]:
        stmt = select(AssessmentResponse).where(
            AssessmentResponse.attempt_id == attempt_id
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class QuestionBankRepository(Repository[QuestionBank]):
    def __init__(self, session) -> None:
        super().__init__(QuestionBank, session)

    async def find_by_course(self, course_id: str) -> list[QuestionBank]:
        stmt = (
            select(QuestionBank)
            .where(QuestionBank.course_id == course_id)
            .order_by(QuestionBank.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_concept(self, concept_id: str) -> list[QuestionBank]:
        stmt = (
            select(QuestionBank)
            .where(QuestionBank.concept_id == concept_id)
            .order_by(QuestionBank.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
