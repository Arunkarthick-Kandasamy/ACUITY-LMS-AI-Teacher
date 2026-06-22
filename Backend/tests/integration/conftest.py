from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.users.models import User


@pytest.fixture
def mock_gemini_service() -> AsyncMock:
    gemini = AsyncMock()
    gemini.generate = AsyncMock(
        return_value="This is a mock teaching response about the concept. "
        "It explains the key ideas in a clear and engaging way."
    )
    gemini.generate_json = AsyncMock(
        return_value={
            "score": 0.85,
            "feedback": "Good understanding shown.",
            "understanding": "strong",
        }
    )
    return gemini


@pytest.fixture
def mock_diagnosis_service() -> AsyncMock:
    diagnosis = AsyncMock()
    diagnosis.diagnose = AsyncMock(
        return_value=Mock(
            diagnosis_type="minor_error",
            misconception=None,
            misconception_category=None,
            knowledge_gap=None,
            prerequisite_concepts=[],
            recommended_action="continue",
            evidence=[],
            remediation=None,
        )
    )
    return diagnosis


@pytest.fixture
def mock_memory_service() -> AsyncMock:
    memory = AsyncMock()
    memory.retrieve_relevant = AsyncMock(
        return_value=Mock(
            observations=[],
            relevant_memories=[],
            recurring_misconceptions=[],
            learning_signals=[],
        )
    )
    memory.format_memory_context = AsyncMock(
        return_value="No prior observations for this student."
    )
    memory.extract_and_store = AsyncMock(return_value=[])
    return memory


@pytest.fixture
def mock_guardrail_service() -> AsyncMock:
    guardrail = AsyncMock()
    guardrail.check_json_response = AsyncMock(
        return_value=Mock(
            passed=True,
            data={
                "score": 0.85,
                "feedback": "Good understanding.",
                "understanding": "strong",
            },
            warnings=[],
            fallback_used=False,
        )
    )
    guardrail.check_text_response = AsyncMock(
        return_value=Mock(
            passed=True,
            data="Mock teaching response content.",
            warnings=[],
            fallback_used=False,
        )
    )
    return guardrail
