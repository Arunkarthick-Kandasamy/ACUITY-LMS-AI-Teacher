from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.assessments.service import AssessmentService
from app.common.types import AssessmentType, LessonProgressStatus, QuestionType


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()
    session.flush = AsyncMock()
    return session


class TestAssessmentIntegrationFlow:
    """End-to-end assessment flow test with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_full_assessment_flow(self, mock_session) -> None:
        service = AssessmentService(mock_session)

        mock_profile = MagicMock()
        mock_profile.id = "sp-1"
        mock_profile.user_id = "user-1"

        mock_assessment = MagicMock()
        mock_assessment.id = "assess-1"
        mock_assessment.title = "Chapter 1 Test"
        mock_assessment.description = "Test your knowledge"
        mock_assessment.course_id = "course-1"
        mock_assessment.lesson_id = "lesson-1"
        mock_assessment.module_id = None
        mock_assessment.assessment_type = AssessmentType.CHAPTER_TEST
        mock_assessment.passing_score = 0.7
        mock_assessment.time_limit = 30
        mock_assessment.max_attempts = 2
        mock_assessment.is_published = True
        mock_assessment.created_by = "admin-1"

        mock_question_1 = MagicMock()
        mock_question_1.id = "q-1"
        mock_question_1.assessment_id = "assess-1"
        mock_question_1.question_type = QuestionType.MCQ
        mock_question_1.prompt = "What is 2+2?"
        mock_question_1.options = {"A": "3", "B": "4", "C": "5"}
        mock_question_1.correct_answer = "B"
        mock_question_1.difficulty = 0.5
        mock_question_1.marks = 1.0
        mock_question_1.explanation = "Basic addition"
        mock_question_1.order_index = 0

        mock_question_2 = MagicMock()
        mock_question_2.id = "q-2"
        mock_question_2.assessment_id = "assess-1"
        mock_question_2.question_type = QuestionType.TRUE_FALSE
        mock_question_2.prompt = "The sky is blue."
        mock_question_2.options = None
        mock_question_2.correct_answer = "true"
        mock_question_2.difficulty = 0.3
        mock_question_2.marks = 1.0
        mock_question_2.explanation = "Common knowledge"
        mock_question_2.order_index = 1

        # Step 1: Create assessment
        service.assessment_repo.create = AsyncMock(return_value=mock_assessment)
        result = await service.create_assessment(
            user_id="admin-1",
            title="Chapter 1 Test",
            description="Test your knowledge",
            course_id="course-1",
            assessment_type="chapter_test",
            passing_score=0.7,
        )
        assert result.id == "assess-1"

        # Step 2: Get assessment
        service.assessment_repo.get = AsyncMock(return_value=mock_assessment)
        assessment = await service.get_assessment("assess-1")
        assert assessment is not None

        # Step 3: Student starts attempt
        service._get_student_profile = AsyncMock(return_value=mock_profile)
        service._get_assessment = AsyncMock(return_value=mock_assessment)
        service.attempt_repo.get_max_attempt_number = AsyncMock(return_value=0)

        mock_attempt = MagicMock()
        mock_attempt.id = "attempt-1"
        mock_attempt.assessment_id = "assess-1"
        mock_attempt.student_id = "sp-1"
        mock_attempt.started_at = datetime.now(timezone.utc)
        mock_attempt.completed_at = None
        mock_attempt.score = 0.0
        mock_attempt.percentage = 0.0
        mock_attempt.passed = False
        mock_attempt.attempt_number = 1

        service.attempt_repo.create = AsyncMock(return_value=mock_attempt)
        service.question_repo.find_by_assessment = AsyncMock(
            return_value=[mock_question_1, mock_question_2]
        )

        start_result = await service.start_attempt("assess-1", "user-1")
        assert start_result["attempt_id"] == "attempt-1"
        assert len(start_result["questions"]) == 2

        # Step 4: Submit attempt with mixed answers
        mock_attempt.assessment = mock_assessment
        service.attempt_repo.get = AsyncMock(return_value=mock_attempt)
        service.question_repo.find_by_assessment = AsyncMock(
            return_value=[mock_question_1, mock_question_2]
        )

        responses_data = [
            {"question_id": "q-1", "response": "B"},
            {"question_id": "q-2", "response": "false"},
        ]

        with patch.object(service, '_on_assessment_completed', AsyncMock()):
            submit_result = await service.submit_attempt(
                "attempt-1", "user-1", responses_data
            )

        assert submit_result["total_marks"] == 2.0
        assert submit_result["earned_marks"] == 1.0
        assert submit_result["percentage"] == 50.0
        assert submit_result["passed"] is False

        # Step 5: Get result
        mock_response_1 = MagicMock()
        mock_response_1.question_id = "q-1"
        mock_response_1.response = "B"
        mock_response_1.is_correct = True
        mock_response_1.score = 1.0
        mock_response_1.feedback = "Correct"
        mock_response_1.time_taken_seconds = 30

        mock_response_2 = MagicMock()
        mock_response_2.question_id = "q-2"
        mock_response_2.response = "false"
        mock_response_2.is_correct = False
        mock_response_2.score = 0.0
        mock_response_2.feedback = "Incorrect. Expected: true"
        mock_response_2.time_taken_seconds = 15

        mock_attempt.score = 1.0
        mock_attempt.percentage = 50.0
        mock_attempt.passed = False
        mock_attempt.completed_at = datetime.now(timezone.utc)

        service.response_repo.find_by_attempt = AsyncMock(
            return_value=[mock_response_1, mock_response_2]
        )

        result_data = await service.get_attempt_result("attempt-1", "user-1")
        assert result_data["passed"] is False
        assert result_data["percentage"] == 50.0
        assert len(result_data["responses"]) == 2
        assert result_data["responses"][0]["is_correct"] is True
        assert result_data["responses"][1]["is_correct"] is False

        # Step 6: Verify max attempts tracking
        service.attempt_repo.get_max_attempt_number = AsyncMock(return_value=2)
        with pytest.raises(Exception):
            await service.start_attempt("assess-1", "user-1")
