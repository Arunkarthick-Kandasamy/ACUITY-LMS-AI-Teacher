from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, NotFoundException, ValidationException
from app.common.types import SessionState
from app.curriculum.repository import ConceptRepository, CourseRepository, LessonRepository
from app.teaching.models import TeachingSession
from app.teaching_sessions.repository import TeachingSessionRepository
from app.users.models import StudentProfile
from app.users.repository import StudentProfileRepository


class SessionContext:
    def __init__(self, session: TeachingSession) -> None:
        self.session_id = session.id
        self.current_lesson_id = session.current_lesson_id
        self.current_concept_id = session.current_concept_id
        self.state = session.state
        self.context = session.context
        self.last_activity_at = session.last_activity_at


class SessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.session_repo = TeachingSessionRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)
        self.course_repo = CourseRepository(session)
        self.lesson_repo = LessonRepository(session)
        self.concept_repo = ConceptRepository(session)

    async def _get_student_profile(self, user_id: str) -> StudentProfile:
        profile = await self.student_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundException(message="Student profile not found")
        return profile

    async def _get_session_owned(
        self, session_id: str, profile_id: str
    ) -> TeachingSession:
        session = await self.session_repo.get(session_id)
        if session is None or session.student_id != profile_id:
            raise NotFoundException(message="Session not found")
        return session

    async def start_session(
        self,
        user_id: str,
        course_id: str,
        lesson_id: str | None = None,
        concept_id: str | None = None,
    ) -> TeachingSession:
        profile = await self._get_student_profile(user_id)

        existing = await self.session_repo.find_active_by_student_and_course(
            profile.id, course_id
        )
        if existing is not None:
            raise ConflictException(
                message="An active session already exists for this course"
            )

        course = await self.course_repo.get(course_id)
        if course is None:
            raise NotFoundException(message="Course not found")

        if lesson_id is not None:
            lesson = await self.lesson_repo.get(lesson_id)
            if lesson is None:
                raise NotFoundException(message="Lesson not found")

        if concept_id is not None:
            concept = await self.concept_repo.get(concept_id)
            if concept is None:
                raise NotFoundException(message="Concept not found")

        now = datetime.now(timezone.utc)
        teaching_session = await self.session_repo.create(
            student_id=profile.id,
            course_id=course_id,
            current_lesson_id=lesson_id,
            current_concept_id=concept_id,
            state=SessionState.ACTIVE,
            context={},
            started_at=now,
            last_activity_at=now,
        )
        return teaching_session

    async def resume_session(self, user_id: str) -> TeachingSession:
        profile = await self._get_student_profile(user_id)
        session = await self.session_repo.find_latest_resumable(profile.id)
        if session is None:
            raise NotFoundException(message="No active or paused session found")

        now = datetime.now(timezone.utc)
        if session.state == SessionState.PAUSED:
            session.state = SessionState.ACTIVE
        session.last_activity_at = now
        await self.session.flush()
        await self.session.refresh(session)
        return session

    async def pause_session(self, session_id: str, user_id: str) -> TeachingSession:
        profile = await self._get_student_profile(user_id)
        session = await self._get_session_owned(session_id, profile.id)

        if session.state != SessionState.ACTIVE:
            raise ValidationException(
                message="Only active sessions can be paused"
            )

        session.state = SessionState.PAUSED
        session.last_activity_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(session)
        return session

    async def end_session(self, session_id: str, user_id: str) -> TeachingSession:
        profile = await self._get_student_profile(user_id)
        session = await self._get_session_owned(session_id, profile.id)

        if session.state in (SessionState.COMPLETED, SessionState.INTERRUPTED):
            raise ValidationException(message="Session is already ended")

        now = datetime.now(timezone.utc)
        session.state = SessionState.COMPLETED
        session.completed_at = now
        session.last_activity_at = now
        await self.session.flush()
        await self.session.refresh(session)
        return session

    async def get_session_history(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20,
        is_admin: bool = False,
        student_id: str | None = None,
    ) -> tuple[list[TeachingSession], int]:
        if is_admin and student_id:
            profile = await self.student_profile_repo.get(student_id)
            if profile is None:
                raise NotFoundException(message="Student profile not found")
            offset = (page - 1) * per_page
            return await self.session_repo.find_by_student(
                profile.id, offset=offset, limit=per_page
            )

        profile = await self._get_student_profile(user_id)
        offset = (page - 1) * per_page
        return await self.session_repo.find_by_student(
            profile.id, offset=offset, limit=per_page
        )

    def get_context(self, session: TeachingSession) -> SessionContext:
        return SessionContext(session)
