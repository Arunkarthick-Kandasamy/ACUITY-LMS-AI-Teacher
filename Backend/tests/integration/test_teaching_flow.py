from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.ai.nodes.teach import teach_node
from app.ai.nodes.ask_question import ask_question_node
from app.ai.nodes.evaluate_response import evaluate_response_node
from app.ai.nodes.provide_example import provide_example_node
from app.ai.nodes.complete_concept import complete_concept_node


class TestTeachingFlow:
    @pytest.mark.asyncio
    async def test_teach_node_produces_content(self, mock_gemini_service: AsyncMock) -> None:
        state = {
            "concept_title": "Variables",
            "concept_description": "Understanding variables in programming",
            "concept_content": [{"content": "A variable stores data.", "content_type": "explanation"}],
            "conversation_history": [],
            "memory_context": "No prior observations.",
        }

        with patch(
            "app.ai.nodes.teach.GeminiService.generate",
            mock_gemini_service.generate,
        ):
            result = await teach_node(state)

        assert "teaching_content" in result
        assert result["teaching_content"] is not None
        assert len(result["teaching_content"]) > 20

    @pytest.mark.asyncio
    async def test_teach_node_with_history(self, mock_gemini_service: AsyncMock) -> None:
        state = {
            "concept_title": "Functions",
            "concept_description": "Reusable blocks of code",
            "concept_content": [{"content": "Functions encapsulate logic.", "content_type": "explanation"}],
            "conversation_history": [
                {"role": "assistant", "content": "Let me explain functions..."},
                {"role": "user", "content": "Can you give an example?"},
            ],
            "memory_context": "Student previously struggled with variables.",
        }

        with patch(
            "app.ai.nodes.teach.GeminiService.generate",
            mock_gemini_service.generate,
        ):
            result = await teach_node(state)

        assert "teaching_content" in result

    @pytest.mark.asyncio
    async def test_ask_question_node(self, mock_gemini_service: AsyncMock) -> None:
        state = {
            "teaching_content": "Variables store data that can be changed during program execution.",
        }

        with patch(
            "app.ai.nodes.ask_question.GeminiService.generate",
            mock_gemini_service.generate,
        ):
            result = await ask_question_node(state)

        assert "question" in result
        assert result["question"] is not None

    @pytest.mark.asyncio
    async def test_evaluate_response_node(self, mock_gemini_service: AsyncMock) -> None:
        state = {
            "concept_title": "Variables",
            "teaching_content": "Variables store data.",
            "question": "What is a variable?",
            "student_response": "A variable stores data that can change.",
            "conversation_history": [],
        }

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            mock_gemini_service.generate_json,
        ):
            result = await evaluate_response_node(state)

        assert "evaluation" in result
        assert result["evaluation"] is not None

    @pytest.mark.asyncio
    async def test_provide_example_node(self, mock_gemini_service: AsyncMock) -> None:
        state = {
            "concept_title": "Variables",
            "concept_description": "Data storage in programming",
            "example_content": [{"content": "x = 5", "explanation": "Assigns 5 to x"}],
        }

        with patch(
            "app.ai.nodes.provide_example.GeminiService.generate",
            mock_gemini_service.generate,
        ):
            result = await provide_example_node(state)

        assert "example_content" in result

    @pytest.mark.asyncio
    async def test_complete_concept_node(self) -> None:
        state = {
            "concept_title": "Variables",
            "teaching_content": "Variables store data.",
            "question": "What is a variable?",
            "student_response": "A variable stores data.",
            "evaluation": {"score": 0.9, "feedback": "Excellent!", "understanding": "strong"},
            "conversation_history": [],
            "errors": [],
            "current_action": None,
        }

        result = await complete_concept_node(state)

        assert result.get("current_action") == "complete_concept"
