from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.assessments.models import (
    Assessment,
    AssessmentAttempt,
    AssessmentQuestion,
    AssessmentResponse,
    QuestionBank,
)
from app.assessments.service import AssessmentService
from app.common.exceptions import NotFoundException, ValidationException
from app.common.types import AssessmentType, QuestionType


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_student_profile() -> MagicMock:
    profile = MagicMock()
    profile.id = "sp-1"
    profile.user_id = "user-1"
    return profile


def _make_assessment(**overrides) -> Assessment:
    defaults = dict(
        id="assess-1",
        title="Test Quiz",
        description=None,
        lesson_id=None,
        module_id=None,
        course_id="course-1",
        assessment_type=AssessmentType.QUIZ,
        passing_score=0.7,
        time_limit=30,
        max_attempts=2,
        is_published=True,
        created_by="user-1",
    )
    defaults.update(overrides)
    return Assessment(**defaults)


def _make_question(**overrides) -> AssessmentQuestion:
    defaults = dict(
        id="q-1",
        assessment_id="assess-1",
        question_type=QuestionType.MCQ,
        prompt="What is 2+2?",
        options={"A": "3", "B": "4", "C": "5"},
        correct_answer="B",
        difficulty=0.5,
        marks=1.0,
        explanation=None,
        order_index=0,
    )
    defaults.update(overrides)
    return AssessmentQuestion(**defaults)


def _make_attempt(**overrides) -> AssessmentAttempt:
    defaults = dict(
        id="attempt-1",
        assessment_id="assess-1",
        student_id="sp-1",
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        score=0.0,
        percentage=0.0,
        passed=False,
        attempt_number=1,
    )
    defaults.update(overrides)
    return AssessmentAttempt(**defaults)


# ---------------------------------------------------------------------------
# AssessmentService
# ---------------------------------------------------------------------------


class TestAssessmentService:
    @pytest.mark.asyncio
    async def test_create_assessment(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        service.assessment_repo.create = AsyncMock(
            return_value=_make_assessment()
        )

        result = await service.create_assessment(
            user_id="user-1",
            title="Test Quiz",
            course_id="course-1",
            assessment_type="quiz",
            passing_score=0.7,
        )
        assert result.id == "assess-1"
        assert result.title == "Test Quiz"

    @pytest.mark.asyncio
    async def test_create_assessment_invalid_type(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        with pytest.raises(ValidationException):
            await service.create_assessment(
                user_id="user-1",
                title="Bad",
                course_id="course-1",
                assessment_type="invalid_type",
            )

    @pytest.mark.asyncio
    async def test_get_assessment_not_found(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        service.assessment_repo.get = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await service.get_assessment("nonexistent")

    # ------------------------------------------------------------------
    # Auto-Grading
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_grade_mcq_correct(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(correct_answer="B")
        is_correct, score, feedback = service._grade_question(question, "B")
        assert is_correct is True
        assert score == 1.0
        assert feedback == "Correct"

    @pytest.mark.asyncio
    async def test_grade_mcq_incorrect(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(correct_answer="B")
        is_correct, score, feedback = service._grade_question(question, "A")
        assert is_correct is False
        assert score == 0.0
        assert "Incorrect" in (feedback or "")

    @pytest.mark.asyncio
    async def test_grade_true_false_correct(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.TRUE_FALSE,
            correct_answer="true",
        )
        is_correct, score, feedback = service._grade_question(question, "True")
        assert is_correct is True

    @pytest.mark.asyncio
    async def test_grade_multi_select_correct(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.MULTI_SELECT,
            correct_answer="A,B,C",
        )
        is_correct, score, feedback = service._grade_question(question, "A,B,C")
        assert is_correct is True

    @pytest.mark.asyncio
    async def test_grade_multi_select_partial(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.MULTI_SELECT,
            correct_answer="A,B,C",
        )
        is_correct, score, feedback = service._grade_question(question, "A,B")
        assert is_correct is False

    @pytest.mark.asyncio
    async def test_grade_numeric_exact(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.NUMERIC,
            correct_answer="42",
        )
        is_correct, score, feedback = service._grade_question(question, "42")
        assert is_correct is True

    @pytest.mark.asyncio
    async def test_grade_numeric_tolerance(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.NUMERIC,
            correct_answer="100",
        )
        is_correct, score, feedback = service._grade_question(question, "100.5")
        assert is_correct is True

        is_correct, score, feedback = service._grade_question(question, "102")
        assert is_correct is False

    @pytest.mark.asyncio
    async def test_grade_short_answer(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.SHORT_ANSWER,
            correct_answer="Paris",
        )
        is_correct, score, feedback = service._grade_question(question, "paris!")
        assert is_correct is True

    @pytest.mark.asyncio
    async def test_grade_fill_blank(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        question = _make_question(
            question_type=QuestionType.FILL_BLANK,
            correct_answer="cat; dog",
        )
        is_correct, score, feedback = service._grade_question(question, "dog; cat")
        assert is_correct is True

    # ------------------------------------------------------------------
    # Attempt flow
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_start_attempt_success(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service._get_assessment = AsyncMock(return_value=_make_assessment())
        service.attempt_repo.get_max_attempt_number = AsyncMock(return_value=0)
        service.attempt_repo.create = AsyncMock(
            return_value=_make_attempt()
        )
        service.question_repo.find_by_assessment = AsyncMock(
            return_value=[_make_question()]
        )

        result = await service.start_attempt("assess-1", "user-1")
        assert result["attempt_id"] == "attempt-1"
        assert len(result["questions"]) == 1
        assert result["time_limit"] == 30
        assert result["time_limit_seconds"] == 1800

    @pytest.mark.asyncio
    async def test_start_attempt_not_published(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service._get_assessment = AsyncMock(
            return_value=_make_assessment(is_published=False)
        )
        with pytest.raises(ValidationException, match="not published"):
            await service.start_attempt("assess-1", "user-1")

    @pytest.mark.asyncio
    async def test_start_attempt_max_reached(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service._get_assessment = AsyncMock(return_value=_make_assessment(max_attempts=2))
        service.attempt_repo.get_max_attempt_number = AsyncMock(return_value=2)
        with pytest.raises(ValidationException, match="Maximum attempts"):
            await service.start_attempt("assess-1", "user-1")

    @pytest.mark.asyncio
    async def test_submit_attempt_success(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        attempt = _make_attempt(assessment=_make_assessment())
        service.attempt_repo.get = AsyncMock(return_value=attempt)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service.question_repo.find_by_assessment = AsyncMock(
            return_value=[_make_question(), _make_question(id="q-2")]
        )

        responses_data = [
            {"question_id": "q-1", "response": "B"},
            {"question_id": "q-2", "response": "B"},
        ]

        with patch.object(service, '_on_assessment_completed', AsyncMock()):
            result = await service.submit_attempt("attempt-1", "user-1", responses_data)

        assert result["passed"] is True
        assert result["percentage"] == 100.0
        assert result["score"] == 2.0

    @pytest.mark.asyncio
    async def test_submit_attempt_already_submitted(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        attempt = _make_attempt(completed_at=datetime.now(timezone.utc))
        service.attempt_repo.get = AsyncMock(return_value=attempt)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        with pytest.raises(ValidationException, match="already submitted"):
            await service.submit_attempt("attempt-1", "user-1", [])

    # ------------------------------------------------------------------
    # Integration hooks
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_on_assessment_completed_updates_progress(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        attempt = _make_attempt(
            assessment=_make_assessment(lesson_id="lesson-1"),
            percentage=85.0,
            passed=True,
        )
        service._get_assessment = AsyncMock(return_value=attempt.assessment)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service.progress_service.update_lesson_progress = AsyncMock()
        service.mastery_service.recalculate_mastery = AsyncMock()

        stmt_mock = MagicMock()
        stmt_mock.unique.return_value.scalars.return_value.all.return_value = []
        service.session.execute = AsyncMock(return_value=stmt_mock)

        await service._on_assessment_completed(attempt, "user-1")
        service.progress_service.update_lesson_progress.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_assessment_completed_updates_mastery(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        attempt = _make_attempt(
            assessment=_make_assessment(lesson_id="lesson-1"),
            percentage=85.0,
            passed=True,
        )
        service._get_assessment = AsyncMock(return_value=attempt.assessment)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service.progress_service.update_lesson_progress = AsyncMock()
        service.mastery_service.recalculate_mastery = AsyncMock()

        concept = MagicMock()
        concept.id = "con-1"
        stmt_mock = MagicMock()
        stmt_mock.unique.return_value.scalars.return_value.all.return_value = [concept]
        service.session.execute = AsyncMock(return_value=stmt_mock)

        await service._on_assessment_completed(attempt, "user-1")
        service.mastery_service.recalculate_mastery.assert_called_once_with("sp-1", "con-1")

    @pytest.mark.asyncio
    async def test_on_assessment_completed_updates_pacing(self, mock_session, mock_student_profile) -> None:
        service = AssessmentService(mock_session)
        assessment = _make_assessment()
        attempt = _make_attempt(assessment=assessment, percentage=85.0, passed=True)
        service._get_assessment = AsyncMock(return_value=assessment)
        service._get_student_profile = AsyncMock(return_value=mock_student_profile)
        service.progress_service.update_lesson_progress = AsyncMock()
        service.mastery_service.recalculate_mastery = AsyncMock()

        enrollment = MagicMock()
        enrollment.course_id = "course-1"
        enrollment.id = "enr-1"
        service.enrollment_repo.find_by_student = AsyncMock(return_value=[enrollment])

        schedule = MagicMock()
        schedule.id = "sched-1"
        schedule.pace_status = MagicMock()
        service.schedule_repo.find_by_enrollment = AsyncMock(return_value=schedule)
        service.schedule_repo.update = AsyncMock()

        stmt_mock = MagicMock()
        stmt_mock.unique.return_value.scalars.return_value.all = AsyncMock(return_value=[])
        service.session.execute = AsyncMock(return_value=stmt_mock)

        await service._on_assessment_completed(attempt, "user-1")
        service.schedule_repo.update.assert_called_once()

    # ------------------------------------------------------------------
    # Student profile lookup
    # ------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_get_student_profile_not_found(self, mock_session) -> None:
        service = AssessmentService(mock_session)
        service.student_profile_repo.get_by_user_id = AsyncMock(return_value=None)
        with pytest.raises(NotFoundException):
            await service._get_student_profile("user-x")
