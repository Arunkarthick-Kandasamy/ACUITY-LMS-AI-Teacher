from __future__ import annotations

from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.ai.nodes.diagnose import diagnose_node


class TestDiagnosisFlow:
    @pytest.mark.asyncio
    async def test_diagnose_node_returns_result(self, mock_gemini_service: AsyncMock) -> None:
        mock_diagnosis = AsyncMock()
        mock_diagnosis.diagnose = AsyncMock(
            return_value=Mock(
                model_dump=Mock(return_value={
                    "diagnosis_type": "minor_error",
                    "misconception": None,
                    "misconception_category": None,
                    "knowledge_gap": None,
                    "prerequisite_concepts": [],
                    "recommended_action": "continue",
                    "evidence": [],
                    "remediation": None,
                })
            )
        )

        state = {
            "concept_title": "Variables",
            "concept_description": "Understanding variables in programming",
            "teaching_content": "A variable stores data.",
            "question": "What is a variable?",
            "student_response": "A variable stores numbers.",
            "mastery_estimate": 0.7,
            "prerequisite_concepts": [],
            "conversation_history": [],
            "errors": [],
        }

        with patch("app.ai.nodes.diagnose.DiagnosisService", return_value=mock_diagnosis):
            result = await diagnose_node(state)

        assert "diagnosis_result" in result

    @pytest.mark.asyncio
    async def test_diagnose_misconception(self, mock_gemini_service: AsyncMock) -> None:
        mock_diagnosis = AsyncMock()
        mock_diagnosis.diagnose = AsyncMock(
            return_value=Mock(
                model_dump=Mock(return_value={
                    "diagnosis_type": "misconception",
                    "misconception": "Thinks variables cannot change value",
                    "misconception_category": "conceptual",
                    "knowledge_gap": None,
                    "prerequisite_concepts": ["Constants"],
                    "recommended_action": "example",
                    "evidence": ["Student said variables are fixed"],
                    "remediation": "Teach that variables can be reassigned",
                })
            )
        )

        state = {
            "concept_title": "Variables",
            "concept_description": "Understanding variables",
            "teaching_content": "Variables are containers for data.",
            "question": "What happens when you reassign a variable?",
            "student_response": "Variables cannot change once set.",
            "mastery_estimate": 0.3,
            "prerequisite_concepts": [{"title": "Constants", "relationship": "related"}],
            "conversation_history": [],
            "errors": [],
        }

        with patch("app.ai.nodes.diagnose.DiagnosisService", return_value=mock_diagnosis):
            result = await diagnose_node(state)

        diag = result.get("diagnosis_result", {})
        assert diag["diagnosis_type"] == "misconception"

    @pytest.mark.asyncio
    async def test_diagnose_knowledge_gap(self, mock_gemini_service: AsyncMock) -> None:
        mock_diagnosis = AsyncMock()
        mock_diagnosis.diagnose = AsyncMock(
            return_value=Mock(
                model_dump=Mock(return_value={
                    "diagnosis_type": "knowledge_gap",
                    "misconception": None,
                    "misconception_category": None,
                    "knowledge_gap": "Missing understanding of basic arithmetic operations",
                    "prerequisite_concepts": ["Arithmetic Basics"],
                    "recommended_action": "prerequisite",
                    "evidence": ["Student cannot compute basic expressions"],
                    "remediation": "Review arithmetic operations before proceeding",
                })
            )
        )

        state = {
            "concept_title": "Algebraic Expressions",
            "concept_description": "Evaluating algebraic expressions",
            "teaching_content": "Substitute values and simplify.",
            "question": "Evaluate 2x + 3 when x = 4",
            "student_response": "I don't know how to do this.",
            "mastery_estimate": 0.1,
            "prerequisite_concepts": [],
            "conversation_history": [],
            "errors": [],
        }

        with patch("app.ai.nodes.diagnose.DiagnosisService", return_value=mock_diagnosis):
            result = await diagnose_node(state)

        diag = result.get("diagnosis_result", {})
        assert diag["diagnosis_type"] == "knowledge_gap"
