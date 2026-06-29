from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.common.exceptions import ForbiddenException, NotFoundException
from app.common.types import LessonProgressStatus, UserRole
from app.curriculum.models import Course
from app.diagnosis.models import Misconception
from app.enrollment.repository import EnrollmentRepository
from app.mastery.repository import MasteryRecordRepository
from app.progress.repository import LessonProgressRepository
from app.teaching.models import Attempt, TeachingSession
from app.users.models import StudentProfile, User
from app.users.repository import StudentProfileRepository, UserRepository

from .repository import (
    TeacherCourseAssignmentRepository,
    TeacherStudentAssignmentRepository,
)
from .schemas import (
    AttemptItem,
    MasteryConceptItem,
    MasterySummaryResponse,
    MisconceptionItem,
    ProgressSummaryResponse,
    SessionItem,
    TeacherCourseResponse,
    TeacherDashboardResponse,
    TeacherStudentResponse,
)


class TeacherService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.student_assign_repo = TeacherStudentAssignmentRepository(session)
        self.course_assign_repo = TeacherCourseAssignmentRepository(session)
        self.student_profile_repo = StudentProfileRepository(session)
        self.user_repo = UserRepository(session)
        self.mastery_repo = MasteryRecordRepository(session)
        self.progress_repo = LessonProgressRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)

    async def _verify_teacher_access(
        self, current_user: User, student_id: str
    ) -> StudentProfile:
        if current_user.role == UserRole.ADMIN:
            profile = await self.student_profile_repo.get(student_id)
            if profile is None:
                raise NotFoundException(message="Student not found")
            return profile

        link = await self.student_assign_repo.find_by_teacher_and_student(
            current_user.id, student_id
        )
        if link is None:
            raise ForbiddenException(
                message="You are not assigned to this student"
            )
        return link.student

    async def list_students(self, current_user: User) -> list[TeacherStudentResponse]:
        if current_user.role == UserRole.ADMIN:
            profiles = await self.student_profile_repo.find()
            result = []
            for profile in profiles:
                user = await self.user_repo.get(profile.user_id)
                enrollments = await self.enrollment_repo.find_by_student(profile.id)
                records = await self.mastery_repo.find_by_student(profile.id)
                avg_mastery = (
                    round(sum(r.mastery_level for r in records) / len(records), 4)
                    if records
                    else 0.0
                )
                session_stmt = (
                    select(TeachingSession)
                    .where(TeachingSession.student_id == profile.id)
                    .order_by(TeachingSession.last_activity_at.desc())
                    .limit(1)
                )
                session_result = await self.session.execute(session_stmt)
                last_session = session_result.unique().scalar_one_or_none()

                result.append(
                    TeacherStudentResponse(
                        student_id=profile.id,
                        full_name=user.full_name if user else "Unknown",
                        email=user.email if user else "",
                        grade_level=profile.grade_level,
                        active_courses=len(enrollments),
                        overall_mastery_avg=avg_mastery,
                        last_active=last_session.last_activity_at if last_session else None,
                        current_streak_days=profile.current_streak_days,
                    )
                )
            return result

        assignments = await self.student_assign_repo.find_by_teacher(current_user.id)
        result = []
        for assignment in assignments:
            profile = assignment.student
            user = await self.user_repo.get(profile.user_id)
            enrollments = await self.enrollment_repo.find_by_student(profile.id)
            records = await self.mastery_repo.find_by_student(profile.id)
            avg_mastery = (
                round(sum(r.mastery_level for r in records) / len(records), 4)
                if records
                else 0.0
            )
            session_stmt = (
                select(TeachingSession)
                .where(TeachingSession.student_id == profile.id)
                .order_by(TeachingSession.last_activity_at.desc())
                .limit(1)
            )
            session_result = await self.session.execute(session_stmt)
            last_session = session_result.unique().scalar_one_or_none()

            result.append(
                TeacherStudentResponse(
                    student_id=profile.id,
                    full_name=user.full_name if user else "Unknown",
                    email=user.email if user else "",
                    grade_level=profile.grade_level,
                    active_courses=len(enrollments),
                    overall_mastery_avg=avg_mastery,
                    last_active=last_session.last_activity_at if last_session else None,
                    current_streak_days=profile.current_streak_days,
                    assigned_at=assignment.assigned_at,
                )
            )
        return result

    async def get_student_progress(
        self, current_user: User, student_id: str
    ) -> ProgressSummaryResponse:
        profile = await self._verify_teacher_access(current_user, student_id)
        progresses = await self.progress_repo.find_by_student(profile.id)

        total = len(progresses)
        completed = sum(
            1 for p in progresses if p.status == LessonProgressStatus.COMPLETED
        )
        in_progress = sum(
            1 for p in progresses if p.status == LessonProgressStatus.IN_PROGRESS
        )
        completion_pct = round((completed / total * 100) if total > 0 else 0.0, 1)

        return ProgressSummaryResponse(
            total_lessons=total,
            completed_lessons=completed,
            in_progress_lessons=in_progress,
            completion_percentage=completion_pct,
        )

    async def get_student_mastery(
        self, current_user: User, student_id: str
    ) -> MasterySummaryResponse:
        profile = await self._verify_teacher_access(current_user, student_id)
        records = await self.mastery_repo.find_by_student(profile.id)

        total = len(records)
        mastered = sum(1 for r in records if r.mastery_level >= 0.8)
        in_progress = sum(1 for r in records if 0.0 < r.mastery_level < 0.8)
        not_started = sum(1 for r in records if r.mastery_level <= 0.0)
        avg = round(sum(r.mastery_level for r in records) / total, 4) if total > 0 else 0.0

        concepts = []
        for r in records:
            concept_title = r.concept.title if hasattr(r, "concept") and r.concept else None
            concepts.append(
                MasteryConceptItem(
                    concept_id=r.concept_id,
                    concept_title=concept_title,
                    mastery_level=r.mastery_level,
                    total_attempts=r.total_attempts,
                    consecutive_correct=r.consecutive_correct,
                    last_attempted_at=r.last_attempted_at,
                )
            )

        return MasterySummaryResponse(
            total_concepts=total,
            mastered_concepts=mastered,
            in_progress_concepts=in_progress,
            not_started_concepts=not_started,
            average_mastery=avg,
            concepts=concepts,
        )

    async def get_student_misconceptions(
        self, current_user: User, student_id: str
    ) -> list[MisconceptionItem]:
        profile = await self._verify_teacher_access(current_user, student_id)
        stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == profile.id,
                Misconception.is_resolved.is_(False),
            )
            .options(joinedload(Misconception.concept))
        )
        result = await self.session.execute(stmt)
        misconceptions = result.unique().scalars().all()

        items = []
        for m in misconceptions:
            concept_title = m.concept.title if hasattr(m, "concept") and m.concept else None
            items.append(
                MisconceptionItem(
                    misconception_id=m.id,
                    concept_id=m.concept_id,
                    concept_title=concept_title,
                    category=m.category.value if hasattr(m.category, "value") else str(m.category),
                    description=m.description,
                    detected_at=m.detected_at,
                    frequency=m.frequency,
                    is_resolved=m.is_resolved,
                )
            )
        return items

    async def get_student_sessions(
        self,
        current_user: User,
        student_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[SessionItem], int]:
        profile = await self._verify_teacher_access(current_user, student_id)
        count_stmt = (
            select(func.count())
            .select_from(TeachingSession)
            .where(TeachingSession.student_id == profile.id)
        )
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(TeachingSession)
            .where(TeachingSession.student_id == profile.id)
            .order_by(TeachingSession.last_activity_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        sessions = result.unique().scalars().all()

        items = []
        for s in sessions:
            course_title = None
            course_stmt = select(Course).where(Course.id == s.course_id)
            course_result = await self.session.execute(course_stmt)
            course = course_result.unique().scalar_one_or_none()
            if course:
                course_title = course.title

            items.append(
                SessionItem(
                    session_id=s.id,
                    course_id=s.course_id,
                    course_title=course_title,
                    state=s.state.value if hasattr(s.state, "value") else str(s.state),
                    started_at=s.started_at,
                    last_activity_at=s.last_activity_at,
                )
            )
        return items, total

    async def get_student_attempts(
        self,
        current_user: User,
        student_id: str,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AttemptItem], int]:
        profile = await self._verify_teacher_access(current_user, student_id)
        count_stmt = (
            select(func.count())
            .select_from(Attempt)
            .where(Attempt.student_id == profile.id)
        )
        total = await self.session.scalar(count_stmt) or 0

        stmt = (
            select(Attempt)
            .where(Attempt.student_id == profile.id)
            .order_by(Attempt.attempted_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        attempts = result.unique().scalars().all()

        items = []
        for a in attempts:
            concept_title = None
            from app.curriculum.models import Exercise

            ex_stmt = select(Exercise).where(Exercise.id == a.exercise_id)
            ex_result = await self.session.execute(ex_stmt)
            exercise = ex_result.unique().scalar_one_or_none()
            if exercise and exercise.concept:
                concept_title = exercise.concept.title

            items.append(
                AttemptItem(
                    attempt_id=a.id,
                    exercise_id=a.exercise_id,
                    is_correct=a.is_correct,
                    score=a.score,
                    attempted_at=a.attempted_at,
                    concept_title=concept_title,
                )
            )
        return items, total

    async def list_courses(self, current_user: User) -> list[TeacherCourseResponse]:
        if current_user.role == UserRole.ADMIN:
            stmt = select(Course).where(Course.is_published.is_(True))
            result = await self.session.execute(stmt)
            courses = result.unique().scalars().all()
            return [
                TeacherCourseResponse(
                    course_id=c.id,
                    title=c.title,
                    code=c.code,
                    role="admin",
                )
                for c in courses
            ]

        assignments = await self.course_assign_repo.find_by_teacher(current_user.id)
        items = []
        for a in assignments:
            course = a.course
            items.append(
                TeacherCourseResponse(
                    course_id=course.id,
                    title=course.title,
                    code=course.code,
                    role=a.role,
                    assigned_at=a.assigned_at,
                )
            )
        return items

    async def get_dashboard(self, current_user: User) -> TeacherDashboardResponse:
        students = await self.list_students(current_user)
        courses = await self.list_courses(current_user)

        student_ids = [s.student_id for s in students]
        recent_sessions = []
        for sid in student_ids:
            sessions, _ = await self.get_student_sessions(
                current_user, sid, offset=0, limit=3
            )
            recent_sessions.extend(sessions)

        recent_sessions.sort(
            key=lambda s: s.last_activity_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )
        recent_sessions = recent_sessions[:10]

        return TeacherDashboardResponse(
            total_students=len(students),
            total_courses=len(courses),
            students=students,
            recent_sessions=recent_sessions,
        )
