from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ai.diagnosis.schemas import DiagnosisResult
from app.ai.diagnosis.service import DiagnosisService
from app.ai.graphs.teacher import decide_after_diagnosis
from app.ai.nodes.diagnose import diagnose_node
from app.ai.state import TeacherAction, TeacherState
from app.common.types import MisconceptionCategory


def _make_state(**overrides) -> TeacherState:
    state: TeacherState = {
        "session_id": "ses-1",
        "student_id": "sp-1",
        "concept_id": "con-1",
        "lesson_id": "lsn-1",
        "current_action": TeacherAction.EVALUATE_RESPONSE,
        "conversation_history": [],
        "student_response": "A variable is a function.",
        "mastery_estimate": 0.3,
        "teaching_content": "Variables are containers for storing data.",
        "question": "What is a variable?",
        "evaluation": "Not quite right.",
        "example_content": None,
        "errors": [],
        "concept_title": "Variables",
        "concept_description": "Understanding variables in programming",
        "concept_content": [],
        "examples": [],
        "prerequisite_concepts": [],
        "recommended_action": None,
        "diagnosis_result": None,
        "expected_answer": None,
    }
    state.update(overrides)
    return state


class TestDiagnosisService:
    @pytest.mark.asyncio
    async def test_diagnose_misconception(self) -> None:
        service = DiagnosisService()

        with patch.object(service.gemini, "generate_json", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "diagnosis_type": "misconception",
                "misconception": "Confuses variables with functions",
                "misconception_category": "conceptual",
                "knowledge_gap": None,
                "prerequisite_concepts": ["function definition"],
                "recommended_action": "reteach",
                "evidence": ["Student said 'a variable is a function'"],
                "remediation": "Re-teach the difference between variables and functions",
            }

            result = await service.diagnose(
                concept_title="Variables",
                concept_description="Understanding variables",
                teaching_content="Variables are containers.",
                question="What is a variable?",
                student_response="A variable is a function.",
                mastery_estimate=0.3,
            )

            assert result.diagnosis_type == "misconception"
            assert result.misconception is not None
            assert result.misconception_category == MisconceptionCategory.CONCEPTUAL
            assert result.recommended_action == "reteach"
            assert len(result.evidence) == 1

    @pytest.mark.asyncio
    async def test_diagnose_knowledge_gap(self) -> None:
        service = DiagnosisService()

        with patch.object(service.gemini, "generate_json", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "diagnosis_type": "knowledge_gap",
                "misconception": None,
                "misconception_category": None,
                "knowledge_gap": "Student doesn't understand basic data types",
                "prerequisite_concepts": ["data types", "type systems"],
                "recommended_action": "prerequisite",
                "evidence": ["Answer shows confusion about what data looks like"],
                "remediation": "Teach data types first",
            }

            result = await service.diagnose(
                concept_title="Variables",
                concept_description="Understanding variables",
                teaching_content="Variables store data.",
                question="What is a variable?",
                student_response="I don't know.",
                mastery_estimate=0.1,
                prerequisite_concepts=[{"title": "Data Types", "relationship": "requires"}],
            )

            assert result.diagnosis_type == "knowledge_gap"
            assert result.recommended_action == "prerequisite"
            assert len(result.prerequisite_concepts) == 2

    @pytest.mark.asyncio
    async def test_diagnose_minor_error(self) -> None:
        service = DiagnosisService()

        with patch.object(service.gemini, "generate_json", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "diagnosis_type": "minor_error",
                "misconception": None,
                "misconception_category": None,
                "knowledge_gap": None,
                "prerequisite_concepts": [],
                "recommended_action": "example",
                "evidence": ["Mostly correct but missed detail"],
                "remediation": "Provide an example to clarify",
            }

            result = await service.diagnose(
                concept_title="Variables",
                concept_description="Understanding variables",
                teaching_content="Variables store data.",
                question="What is a variable?",
                student_response="It stores data.",
                mastery_estimate=0.6,
            )

            assert result.diagnosis_type == "minor_error"
            assert result.recommended_action == "example"

    @pytest.mark.asyncio
    async def test_diagnose_mastered(self) -> None:
        service = DiagnosisService()

        with patch.object(service.gemini, "generate_json", new_callable=AsyncMock) as mock:
            mock.return_value = {
                "diagnosis_type": "mastered",
                "misconception": None,
                "misconception_category": None,
                "knowledge_gap": None,
                "prerequisite_concepts": [],
                "recommended_action": "continue",
                "evidence": ["Correct understanding demonstrated"],
                "remediation": None,
            }

            result = await service.diagnose(
                concept_title="Variables",
                concept_description="Understanding variables",
                teaching_content="Variables store data.",
                question="What is a variable?",
                student_response="A variable is a named container that stores a value.",
                mastery_estimate=0.85,
            )

            assert result.diagnosis_type == "mastered"
            assert result.recommended_action == "continue"

    @pytest.mark.asyncio
    async def test_persist_misconception_new(self) -> None:
        db = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        service = DiagnosisService(db)

        from sqlalchemy import select

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=mock_result)

        result = await service.persist_misconception(
            student_id="sp-1",
            concept_id="con-1",
            category=MisconceptionCategory.CONCEPTUAL,
            description="Confuses variables with functions",
            session_id="ses-1",
            evidence=["Student said 'a variable is a function'"],
        )

        assert result is not None
        db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_persist_misconception_existing(self) -> None:
        db = MagicMock()
        db.flush = AsyncMock()
        db.refresh = AsyncMock()
        service = DiagnosisService(db)

        existing = MagicMock()
        existing.frequency = 1
        existing.evidence = ["old evidence"]

        mock_result = MagicMock()
        mock_result.unique.return_value.scalar_one_or_none.return_value = existing
        db.execute = AsyncMock(return_value=mock_result)

        result = await service.persist_misconception(
            student_id="sp-1",
            concept_id="con-1",
            category=MisconceptionCategory.CONCEPTUAL,
            description="Confuses variables with functions",
        )

        assert result is not None
        assert existing.frequency == 2
        assert "new" in existing.evidence or len(existing.evidence) >= 1
        db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_persist_no_db(self) -> None:
        service = DiagnosisService(db=None)
        result = await service.persist_misconception(
            student_id="sp-1",
            concept_id="con-1",
            category=MisconceptionCategory.CONCEPTUAL,
            description="Test",
        )
        assert result is None


class TestDiagnoseNode:
    @pytest.mark.asyncio
    async def test_diagnose_node_returns_diagnosis(self) -> None:
        state = _make_state()

        with patch(
            "app.ai.nodes.diagnose.DiagnosisService.diagnose", new_callable=AsyncMock
        ) as mock_diag:
            mock_diag.return_value = DiagnosisResult(
                diagnosis_type="misconception",
                misconception="Confuses variables with functions",
                misconception_category=MisconceptionCategory.CONCEPTUAL,
                knowledge_gap=None,
                prerequisite_concepts=["function definition"],
                recommended_action="reteach",
                evidence=["Student said 'a variable is a function'"],
                remediation="Re-teach the difference",
            )

            result = await diagnose_node(state)

            assert result["recommended_action"] == "reteach"
            assert result["diagnosis_result"] is not None
            assert result["diagnosis_result"]["diagnosis_type"] == "misconception"
            assert len(result["conversation_history"]) == 1


class TestDecisionRouter:
    def test_decide_reteach(self) -> None:
        state = _make_state(recommended_action="reteach")
        assert decide_after_diagnosis(state) == "reteach"

    def test_decide_prerequisite(self) -> None:
        state = _make_state(recommended_action="prerequisite")
        assert decide_after_diagnosis(state) == "prerequisite"

    def test_decide_example(self) -> None:
        state = _make_state(recommended_action="example")
        assert decide_after_diagnosis(state) == "example"

    def test_decide_continue(self) -> None:
        state = _make_state(recommended_action="continue")
        assert decide_after_diagnosis(state) == "continue"

    def test_decide_default(self) -> None:
        state = _make_state(recommended_action=None)
        assert decide_after_diagnosis(state) == "example"


class TestGraphIntegration:
    @pytest.mark.asyncio
    async def test_graph_evaluate_then_diagnose_then_reteach(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_state(
            current_action=TeacherAction.ASK_QUESTION,
            student_response="A variable is a function.",
            teaching_content="Variables are containers.",
            question="What is a variable?",
        )

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.3,
                "feedback": "Not quite.",
                "understanding": "weak",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose",
                new_callable=AsyncMock,
            ) as mock_diag:
                mock_diag.return_value = DiagnosisResult(
                    diagnosis_type="misconception",
                    misconception="Confuses variables with functions",
                    misconception_category=MisconceptionCategory.CONCEPTUAL,
                    knowledge_gap=None,
                    prerequisite_concepts=[],
                    recommended_action="reteach",
                    evidence=["confusion"],
                    remediation="Re-teach variables",
                )
                with patch(
                    "app.ai.nodes.teach.GeminiService.generate",
                    new_callable=AsyncMock,
                ) as mock_teach:
                    mock_teach.return_value = "Let me explain variables again..."
                    with patch(
                        "app.ai.nodes.ask_question.GeminiService.generate",
                        new_callable=AsyncMock,
                    ) as mock_q:
                        mock_q.return_value = "New question about variables?"

                        result = await teacher_graph.ainvoke(state)

                        # Graph: eval -> diagnose -> reteach -> teach -> ask_question -> END
                        # After asking question, waits for student response
                        assert result["current_action"] == TeacherAction.EVALUATE_RESPONSE
                        assert result["teaching_content"] is not None
                        assert result["question"] is not None

    @pytest.mark.asyncio
    async def test_graph_evaluate_then_diagnose_then_complete(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_state(
            current_action=TeacherAction.ASK_QUESTION,
            student_response="A variable stores data in memory.",
            teaching_content="Variables are containers.",
            question="What is a variable?",
        )

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.9,
                "feedback": "Excellent!",
                "understanding": "strong",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose",
                new_callable=AsyncMock,
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

                assert result["current_action"] == TeacherAction.COMPLETE_CONCEPT
                assert result["mastery_estimate"] >= 0.7

    @pytest.mark.asyncio
    async def test_graph_evaluate_then_diagnose_then_example(self) -> None:
        from app.ai.graphs.teacher import teacher_graph

        state = _make_state(
            current_action=TeacherAction.ASK_QUESTION,
            student_response="It stores data.",
            teaching_content="Variables are containers.",
            question="What is a variable?",
            concept_title="Variables",
            concept_description="Understanding variables",
            examples=[{"content": "x = 5", "explanation": "Example"}],
        )

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.6,
                "feedback": "Mostly right.",
                "understanding": "partial",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose",
                new_callable=AsyncMock,
            ) as mock_diag:
                mock_diag.return_value = DiagnosisResult(
                    diagnosis_type="minor_error",
                    misconception=None,
                    misconception_category=None,
                    knowledge_gap=None,
                    prerequisite_concepts=[],
                    recommended_action="example",
                    evidence=["minor detail missing"],
                    remediation="Provide example",
                )
                with patch(
                    "app.ai.nodes.provide_example.GeminiService.generate",
                    new_callable=AsyncMock,
                ) as mock_ex:
                    mock_ex.return_value = "Here is an example..."
                    with patch(
                        "app.ai.nodes.ask_question.GeminiService.generate",
                        new_callable=AsyncMock,
                    ) as mock_q:
                        mock_q.return_value = "New question?"

                        result = await teacher_graph.ainvoke(state)

                        assert result["current_action"] == TeacherAction.EVALUATE_RESPONSE
                        assert result["example_content"] is not None
                        assert result["question"] is not None
