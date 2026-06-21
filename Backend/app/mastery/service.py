from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Integer, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.curriculum.models import Exercise
from app.mastery.models import MasteryRecord
from app.mastery.repository import MasteryRecordRepository
from app.teaching.models import Attempt
from app.users.models import StudentProfile
from app.users.repository import StudentProfileRepository


class MasteryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.mastery_repo = MasteryRecordRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)

    async def _get_student_profile(self, user_id: str) -> StudentProfile:
        profile = await self.student_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="Student profile not found")
        return profile

    async def recalculate_mastery(self, student_id: str, concept_id: str) -> MasteryRecord:
        stmt = (
            select(
                func.count(Attempt.id),
                func.avg(Attempt.score),
                func.sum(cast(Attempt.is_correct, Integer)),
                func.max(Attempt.attempted_at),
            )
            .where(Attempt.student_id == student_id)
            .join(Exercise, Attempt.exercise_id == Exercise.id)
            .where(Exercise.concept_id == concept_id)
        )

        result = await self.session.execute(stmt)
        row = result.one()

        total_attempts = row[0] or 0
        avg_score = row[1] or 0.0
        correct_count = row[2] or 0
        last_attempted = row[3]

        existing = await self.mastery_repo.find_by_student_and_concept(
            student_id, concept_id
        )

        if total_attempts == 0:
            mastery_level = 0.0
            consecutive_correct = 0
        else:
            mastery_level = round(float(avg_score), 4)
            consecutive_correct = int(correct_count)

        now = datetime.now(timezone.utc)

        if existing:
            updated = await self.mastery_repo.update(
                existing.id,
                mastery_level=mastery_level,
                last_attempted_at=last_attempted or now,
                total_attempts=total_attempts,
                consecutive_correct=consecutive_correct,
            )
            if updated is None:
                raise NotFoundException(message="Mastery record not found")
            return updated

        return await self.mastery_repo.create(
            student_id=student_id,
            concept_id=concept_id,
            mastery_level=mastery_level,
            total_attempts=total_attempts,
            consecutive_correct=consecutive_correct,
            last_attempted_at=last_attempted or now,
        )

    async def get_overview(self, user_id: str) -> list[MasteryRecord]:
        profile = await self._get_student_profile(user_id)
        return await self.mastery_repo.find_by_student(profile.id)

    async def get_by_concept(
        self, concept_id: str, user_id: str
    ) -> MasteryRecord | None:
        profile = await self._get_student_profile(user_id)
        return await self.mastery_repo.find_by_student_and_concept(
            profile.id, concept_id
        )

    async def get_course_summary(
        self, course_id: str, user_id: str
    ) -> list[MasteryRecord]:
        profile = await self._get_student_profile(user_id)
        return await self.mastery_repo.find_by_student_and_course(
            profile.id, course_id
        )
