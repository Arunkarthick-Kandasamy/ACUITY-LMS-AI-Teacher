from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.common.types import LessonProgressStatus
from app.curriculum.models import Course, Lesson
from app.curriculum.repository import CourseRepository, LessonRepository
from app.progress.repository import AttemptRepository, LessonProgressRepository
from app.teaching.models import Attempt, LessonProgress
from app.users.models import StudentProfile
from app.users.repository import StudentProfileRepository


class ProgressService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.progress_repo = LessonProgressRepository(session)
        self.attempt_repo = AttemptRepository(session)
        self.lesson_repo = LessonRepository(session)
        self.course_repo = CourseRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)

    async def _get_student_profile(self, user_id: str) -> StudentProfile:
        profile = await self.student_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="Student profile not found")
        return profile

    async def _get_lesson(self, lesson_id: str) -> Lesson:
        lesson = await self.lesson_repo.get(lesson_id)
        if lesson is None:
            raise NotFoundException(message="Lesson not found")
        return lesson

    async def get_curriculum_tree(self, course_id: str) -> Course:
        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")
        return course

    async def get_lesson_progress(
        self, lesson_id: str, user_id: str
    ) -> LessonProgress | None:
        profile = await self._get_student_profile(user_id)
        return await self.progress_repo.find_by_student_and_lesson(profile.id, lesson_id)

    async def update_lesson_progress(
        self, lesson_id: str, user_id: str, **kwargs
    ) -> LessonProgress:
        profile = await self._get_student_profile(user_id)
        lesson = await self._get_lesson(lesson_id)

        existing = await self.progress_repo.find_by_student_and_lesson(
            profile.id, lesson_id
        )

        now = datetime.now(timezone.utc)

        if existing is None:
            progress_kwargs = {
                "student_id": profile.id,
                "lesson_id": lesson_id,
                "status": LessonProgressStatus.IN_PROGRESS,
                "time_spent_seconds": 0,
                "completion_percentage": 0.0,
            }

            if kwargs.get("status") == LessonProgressStatus.IN_PROGRESS:
                progress_kwargs["started_at"] = now

            progress_kwargs.update(
                {k: v for k, v in kwargs.items() if v is not None}
            )

            if progress_kwargs.get("status") == LessonProgressStatus.COMPLETED:
                progress_kwargs["completed_at"] = now
                progress_kwargs["completion_percentage"] = 100.0
                if progress_kwargs.get("started_at") is None:
                    progress_kwargs["started_at"] = now

            return await self.progress_repo.create(**progress_kwargs)

        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if update_data.get("status") == LessonProgressStatus.COMPLETED:
            update_data["completed_at"] = now
            update_data["completion_percentage"] = 100.0
            if existing.started_at is None:
                update_data["started_at"] = now
        elif update_data.get("status") == LessonProgressStatus.IN_PROGRESS:
            if existing.started_at is None:
                update_data["started_at"] = now

        updated = await self.progress_repo.update(lesson.id, **update_data)
        if updated is None:
            raise NotFoundException(message="Lesson progress not found")
        return updated

    async def record_attempt(
        self, user_id: str, exercise_id: str, **kwargs
    ) -> Attempt:
        profile = await self._get_student_profile(user_id)

        from sqlalchemy import func, select

        stmt = select(func.coalesce(func.max(Attempt.attempt_number), 0)).where(
            Attempt.student_id == profile.id,
            Attempt.exercise_id == exercise_id,
        )
        result = await self.session.execute(stmt)
        max_number = result.scalar() or 0

        attempt_number = kwargs.pop("attempt_number", max_number + 1)
        teaching_session_id = kwargs.pop("teaching_session_id", None)

        attempt = await self.attempt_repo.create(
            student_id=profile.id,
            exercise_id=exercise_id,
            teaching_session_id=teaching_session_id,
            attempt_number=attempt_number,
            attempted_at=datetime.now(timezone.utc),
            **kwargs,
        )

        from app.curriculum.models import Exercise as ExerciseModel
        from app.mastery.service import MasteryService

        stmt = select(ExerciseModel.concept_id).where(ExerciseModel.id == exercise_id)
        result = await self.session.execute(stmt)
        concept_id = result.unique().scalar_one_or_none()

        if concept_id is not None:
            mastery_service = MasteryService(self.session)
            await mastery_service.recalculate_mastery(profile.id, concept_id)

        return attempt

    async def get_attempt_history(
        self, user_id: str, page: int = 1, per_page: int = 20
    ) -> tuple[list[Attempt], int]:
        profile = await self._get_student_profile(user_id)
        offset = (page - 1) * per_page
        return await self.attempt_repo.find_by_student(
            profile.id, offset=offset, limit=per_page
        )
