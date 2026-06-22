from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.ai.diagnosis.schemas import DiagnosisResult
from app.ai.evaluators.mastery import estimate_mastery_from_score, is_mastered
from app.ai.graphs.teacher import decide_after_evaluation, decide_entry
from app.ai.memory.schemas import MemoryContext
from app.ai.nodes.ask_question import ask_question_node
from app.ai.nodes.complete_concept import complete_concept_node
from app.ai.nodes.evaluate_response import evaluate_response_node
from app.ai.nodes.provide_example import provide_example_node
from app.ai.nodes.teach import teach_node
from app.ai.state import TeacherAction, TeacherState


def _make_initial_state(**overrides) -> TeacherState:
    state: TeacherState = {
        "session_id": "ses-1",
        "student_id": "sp-1",
        "concept_id": "con-1",
        "lesson_id": "lsn-1",
        "current_action": None,
        "conversation_history": [],
        "student_response": None,
        "mastery_estimate": 0.0,
        "teaching_content": None,
        "question": None,
        "evaluation": None,
        "example_content": None,
        "errors": [],
        "concept_title": "Variables",
        "concept_description": "Understanding variables in programming",
        "concept_content": [
            {"content_type": "explanation", "content": "A variable is a container for storing data values."}
        ],
        "examples": [],
    }
    state.update(overrides)
    return state


def _make_empty_memory_context() -> MemoryContext:
    return MemoryContext(
        observations=[],
        relevant_memories=[],
        recurring_misconceptions=[],
        learning_signals=[],
    )


class TestEntryDecider:
    def test_no_response_starts_retrieve_memories(self) -> None:
        state = _make_initial_state()
        assert decide_entry(state) == "retrieve_memories"

    def test_with_response_goes_evaluate(self) -> None:
        state = _make_initial_state(
            student_response="My answer",
            current_action=TeacherAction.ASK_QUESTION,
        )
        assert decide_entry(state) == "evaluate_response"

    def test_with_response_and_already_evaluating(self) -> None:
        state = _make_initial_state(
            student_response="My answer",
            current_action=TeacherAction.EVALUATE_RESPONSE,
        )
        assert decide_entry(state) == "evaluate_response"


class TestEvaluationDecider:
    def test_always_routes_to_diagnose(self) -> None:
        state = _make_initial_state(mastery_estimate=0.85)
        assert decide_after_evaluation(state) == "diagnose"

    def test_low_mastery_still_routes_to_diagnose(self) -> None:
        state = _make_initial_state(mastery_estimate=0.4)
        assert decide_after_evaluation(state) == "diagnose"

    def test_default_zero_routes_to_diagnose(self) -> None:
        state = _make_initial_state()
        assert decide_after_evaluation(state) == "diagnose"


class TestMasteryEvaluator:
    def test_estimate_from_score(self) -> None:
        assert estimate_mastery_from_score(0.9) == 0.9
        assert estimate_mastery_from_score(0.0) == 0.0
        assert estimate_mastery_from_score(1.0) == 1.0
        assert estimate_mastery_from_score(-0.1) == 0.0
        assert estimate_mastery_from_score(1.5) == 1.0

    def test_is_mastered(self) -> None:
        assert is_mastered(0.7) is True
        assert is_mastered(0.69) is False
        assert is_mastered(0.5) is False


class TestNodes:
    @pytest.mark.asyncio
    async def test_teach_node(self) -> None:
        state = _make_initial_state()
        with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Variables are containers for storing data..."

            result = await teach_node(state)

            assert result["current_action"] == TeacherAction.ASK_QUESTION
            assert result["teaching_content"] is not None
            assert len(result["conversation_history"]) == 1
            assert result["conversation_history"][0]["role"] == "teacher"

    @pytest.mark.asyncio
    async def test_teach_node_with_content(self) -> None:
        state = _make_initial_state(
            concept_content=[
                {"content_type": "explanation", "content": "Detailed explanation here."},
                {"content_type": "example", "content": "Example content here."},
            ]
        )
        with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Teaching content..."

            result = await teach_node(state)

            assert result["teaching_content"] == "Teaching content..."
            mock_gen.assert_called_once()

    @pytest.mark.asyncio
    async def test_teach_node_with_history(self) -> None:
        state = _make_initial_state(
            conversation_history=[
                {"role": "teacher", "content": "Previous teaching"},
                {"role": "student", "content": "Previous answer"},
            ]
        )
        with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "New teaching content..."

            result = await teach_node(state)

            assert len(result["conversation_history"]) == 3

    @pytest.mark.asyncio
    async def test_ask_question_node(self) -> None:
        state = _make_initial_state(teaching_content="Variables are containers for data.")
        with patch("app.ai.nodes.ask_question.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "What is a variable?"

            result = await ask_question_node(state)

            assert result["current_action"] == TeacherAction.EVALUATE_RESPONSE
            assert result["question"] == "What is a variable?"
            assert len(result["conversation_history"]) == 1

    @pytest.mark.asyncio
    async def test_ask_question_with_history(self) -> None:
        state = _make_initial_state(
            teaching_content="Some content",
            conversation_history=[{"role": "teacher", "content": "Hello"}],
        )
        with patch("app.ai.nodes.ask_question.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Test question?"

            result = await ask_question_node(state)

            assert len(result["conversation_history"]) == 2

    @pytest.mark.asyncio
    async def test_evaluate_response_node(self) -> None:
        state = _make_initial_state(
            teaching_content="Variables are containers.",
            question="What is a variable?",
            student_response="A variable stores data.",
        )
        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = {
                "score": 0.85,
                "feedback": "Good answer! You understand variables.",
                "understanding": "strong",
            }

            result = await evaluate_response_node(state)

            assert result["mastery_estimate"] == 0.85
            assert result["evaluation"] is not None
            assert result["student_response"] is None
            assert len(result["conversation_history"]) == 2

    @pytest.mark.asyncio
    async def test_evaluate_response_low_score(self) -> None:
        state = _make_initial_state(
            teaching_content="Content",
            question="Question?",
            student_response="Wrong answer.",
        )
        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json", new_callable=AsyncMock
        ) as mock_gen:
            mock_gen.return_value = {
                "score": 0.3,
                "feedback": "Not quite right.",
                "understanding": "weak",
            }

            result = await evaluate_response_node(state)

            assert result["mastery_estimate"] == 0.3

    @pytest.mark.asyncio
    async def test_provide_example_node(self) -> None:
        state = _make_initial_state(
            concept_title="Variables",
            concept_description="Understanding variables",
            examples=[
                {"content": "x = 5", "explanation": "Assigns value 5 to variable x"},
            ],
        )
        with patch("app.ai.nodes.provide_example.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Here is an example of a variable..."

            result = await provide_example_node(state)

            assert result["current_action"] == TeacherAction.ASK_QUESTION
            assert result["example_content"] is not None
            assert len(result["conversation_history"]) == 1

    @pytest.mark.asyncio
    async def test_provide_example_no_examples(self) -> None:
        state = _make_initial_state(
            concept_title="Variables",
            concept_description="Understanding variables",
            examples=[],
        )
        with patch("app.ai.nodes.provide_example.GeminiService.generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "Here is an example..."

            result = await provide_example_node(state)

            assert result["current_action"] == TeacherAction.ASK_QUESTION

    @pytest.mark.asyncio
    async def test_complete_concept_node(self) -> None:
        state = _make_initial_state(
            conversation_history=[{"role": "teacher", "content": "Previous message"}],
        )

        result = await complete_concept_node(state)

        assert result["current_action"] == TeacherAction.COMPLETE_CONCEPT
        assert len(result["conversation_history"]) == 2
        assert "Great job" in result["conversation_history"][-1]["content"]


class TestGraphIntegration:
    @pytest.mark.asyncio
    async def test_full_graph_teach_then_ask(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_initial_state()

        with patch(
            "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
            new_callable=AsyncMock,
        ) as mock_retrieve:
            mock_retrieve.return_value = _make_empty_memory_context()
            with patch(
                "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                new_callable=AsyncMock,
            ) as mock_format:
                mock_format.return_value = "No prior observations."
                with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_teach:
                    mock_teach.return_value = "Teaching about variables..."
                    with patch("app.ai.nodes.ask_question.GeminiService.generate", new_callable=AsyncMock) as mock_q:
                        mock_q.return_value = "What is a variable?"

                        result = await teacher_graph.ainvoke(state)

                        assert result["teaching_content"] is not None
                        assert result["question"] is not None
                        assert result["current_action"] == TeacherAction.EVALUATE_RESPONSE

    @pytest.mark.asyncio
    async def test_graph_evaluate_then_diagnose_then_complete(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_initial_state(
            current_action=TeacherAction.ASK_QUESTION,
            student_response="A variable stores data.",
            teaching_content="Variables are containers.",
            question="What is a variable?",
        )

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json", new_callable=AsyncMock
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.9,
                "feedback": "Excellent!",
                "understanding": "strong",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose", new_callable=AsyncMock
            ) as mock_diag:
                mock_diag.return_value = DiagnosisResult(
                    diagnosis_type="mastered",
                    misconception=None,
                    misconception_category=None,
                    knowledge_gap=None,
                    prerequisite_concepts=[],
                    recommended_action="continue",
                    evidence=["correct understanding"],
                    remediation=None,
                )

                result = await teacher_graph.ainvoke(state)

                assert result["mastery_estimate"] >= 0.7
                assert result["current_action"] == TeacherAction.COMPLETE_CONCEPT

    @pytest.mark.asyncio
    async def test_graph_evaluate_then_example_then_question(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_initial_state(
            current_action=TeacherAction.ASK_QUESTION,
            student_response="I don't know.",
            teaching_content="Variables are containers.",
            question="What is a variable?",
            concept_title="Variables",
            concept_description="Understanding variables",
            examples=[{"content": "x = 5", "explanation": "Example"}],
        )

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json", new_callable=AsyncMock
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.3,
                "feedback": "Not quite.",
                "understanding": "weak",
            }
            with patch("app.ai.nodes.provide_example.GeminiService.generate", new_callable=AsyncMock) as mock_ex:
                mock_ex.return_value = "Here is an example..."
                with patch("app.ai.nodes.ask_question.GeminiService.generate", new_callable=AsyncMock) as mock_q:
                    mock_q.return_value = "New question?"

                    result = await teacher_graph.ainvoke(state)

                    assert result["mastery_estimate"] == 0.3
                    assert result["example_content"] is not None
                    assert result["question"] is not None
                    # After example + new question, graph waits for student response
                    assert result["current_action"] == TeacherAction.EVALUATE_RESPONSE

    @pytest.mark.asyncio
    async def test_graph_preserves_conversation_history(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_initial_state(
            conversation_history=[
                {"role": "teacher", "content": "Welcome!"},
            ],
        )

        with patch(
            "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
            new_callable=AsyncMock,
        ) as mock_retrieve:
            mock_retrieve.return_value = _make_empty_memory_context()
            with patch(
                "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                new_callable=AsyncMock,
            ) as mock_format:
                mock_format.return_value = "No prior observations."
                with patch("app.ai.nodes.teach.GeminiService.generate", new_callable=AsyncMock) as mock_teach:
                    mock_teach.return_value = "Teaching..."
                    with patch("app.ai.nodes.ask_question.GeminiService.generate", new_callable=AsyncMock) as mock_q:
                        mock_q.return_value = "Question?"

                        result = await teacher_graph.ainvoke(state)

                        assert len(result["conversation_history"]) >= 2
                        assert result["conversation_history"][0]["content"] == "Welcome!"
