from __future__ import annotations

from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from app.ai.evaluation.datasets import (
    MASTERED_STUDENT,
    MISCONCEPTION_CASE,
    PREREQUISITE_GAP_CASE,
    SCENARIOS,
    SCENARIO_MAP,
    STRUGGLING_STUDENT,
    EvaluationScenario,
    build_initial_state,
    get_scenario,
)
from app.ai.evaluation.metrics import compute_metrics
from app.ai.evaluation.reports import (
    format_metrics_report,
    format_multi_scenario_report,
    format_trace_report,
    summarize_trace_db,
)
from app.ai.evaluation.router import router
from app.infrastructure.database import get_session
from app.ai.state import TeacherAction
from app.evaluation.models import GraphTrace


class TestDatasets:
    def test_all_scenarios_defined(self) -> None:
        assert len(SCENARIOS) == 4
        labels = [s.label for s in SCENARIOS]
        assert "mastered_student" in labels
        assert "struggling_student" in labels
        assert "misconception_case" in labels
        assert "prerequisite_gap_case" in labels

    def test_get_scenario_found(self) -> None:
        s = get_scenario("mastered_student")
        assert s is not None
        assert s.label == "mastered_student"

    def test_get_scenario_not_found(self) -> None:
        assert get_scenario("nonexistent") is None

    def test_scenario_map_complete(self) -> None:
        for s in SCENARIOS:
            assert SCENARIO_MAP[s.label] is s

    def test_mastered_student_config(self) -> None:
        s = MASTERED_STUDENT
        assert s.expected_action == "complete_concept"
        assert "evaluate_response" in s.expected_nodes
        assert "diagnose" in s.expected_nodes
        assert "complete_concept" in s.expected_nodes

    def test_struggling_student_config(self) -> None:
        s = STRUGGLING_STUDENT
        assert s.expected_action == "reteach"
        assert s.expected_mastery_range == (0.0, 0.5)

    def test_misconception_case_config(self) -> None:
        s = MISCONCEPTION_CASE
        assert s.expected_action == "example"
        assert "provide_example" in s.expected_nodes

    def test_prerequisite_gap_case_config(self) -> None:
        s = PREREQUISITE_GAP_CASE
        assert s.expected_action == "prerequisite"
        assert len(s.prerequisite_concepts) == 1
        assert s.prerequisite_concepts[0]["label"] == "Variables"

    def test_build_initial_state_no_response(self) -> None:
        s = EvaluationScenario(
            label="test",
            concept_title="Test",
            concept_description="Desc",
            concept_content=[],
            examples=[],
            student_response=None,
            current_action=None,
            mastery_estimate=0.0,
            expected_action="teach",
            expected_nodes=["retrieve_memories", "teach", "ask_question"],
            expected_mastery_range=(0.0, 1.0),
        )
        state = build_initial_state(s)
        assert state["student_response"] is None
        assert state["current_action"] is None
        assert state["mastery_estimate"] == 0.0

    def test_build_initial_state_with_response(self) -> None:
        state = build_initial_state(MASTERED_STUDENT)
        assert state["student_response"] == "A variable stores data that can be changed."
        assert state["current_action"] == "ask_question"
        assert state["session_id"] == "eval-session"
        assert state["student_id"] == "eval-student"
        assert state["concept_title"] == "Variables"

    def test_build_initial_state_prereqs(self) -> None:
        state = build_initial_state(PREREQUISITE_GAP_CASE)
        assert len(state["prerequisite_concepts"]) == 1
        assert state["prerequisite_concepts"][0]["id"] == "con-1"


class TestMetrics:
    def test_empty_traces_returns_zeros(self) -> None:
        metrics = compute_metrics([])
        assert metrics["total_sessions"] == 0
        assert metrics["concept_mastery_rate"] == 0.0
        assert metrics["remediation_rate"] == 0.0
        assert metrics["misconception_detection_rate"] == 0.0

    def test_compute_metrics_with_mixed_traces(self) -> None:
        traces = [
            self._make_trace(
                final_action="complete_concept",
                final_mastery=0.85,
                diagnosis_type="mastered",
                recommended_action="continue",
            ),
            self._make_trace(
                final_action="retrieve_memories",
                final_mastery=0.3,
                diagnosis_type="knowledge_gap",
                recommended_action="reteach",
            ),
            self._make_trace(
                final_action="provide_example",
                final_mastery=0.4,
                diagnosis_type="misconception",
                recommended_action="example",
                misconception=True,
            ),
        ]

        metrics = compute_metrics(traces)
        assert metrics["total_sessions"] == 3
        assert metrics["concept_mastery_rate"] == pytest.approx(1 / 3, rel=1e-2)
        assert metrics["remediation_rate"] == pytest.approx(2 / 3, rel=1e-2)
        assert metrics["misconception_detection_rate"] == pytest.approx(1 / 3, rel=1e-2)
        assert metrics["prerequisite_routing_frequency"] == 0.0
        assert metrics["breakdown"]["mastered_count"] == 1
        assert metrics["breakdown"]["misconception_detected"] == 1
        assert metrics["breakdown"]["reteach_count"] == 1
        assert metrics["breakdown"]["example_count"] == 1

    def test_all_mastered(self) -> None:
        traces = [
            self._make_trace(
                final_action="complete_concept",
                final_mastery=0.9,
                diagnosis_type="mastered",
                recommended_action="continue",
            )
            for _ in range(5)
        ]
        metrics = compute_metrics(traces)
        assert metrics["concept_mastery_rate"] == 1.0
        assert metrics["remediation_rate"] == 0.0
        assert metrics["misconception_detection_rate"] == 0.0
        assert metrics["session_completion_rate"] == 1.0

    def test_all_remediated(self) -> None:
        traces = [
            self._make_trace(
                final_action="retrieve_memories",
                final_mastery=0.3,
                diagnosis_type="knowledge_gap",
                recommended_action="reteach",
            )
            for _ in range(3)
        ]
        metrics = compute_metrics(traces)
        assert metrics["concept_mastery_rate"] == 0.0
        assert metrics["remediation_rate"] == 1.0
        assert metrics["session_completion_rate"] == 0.0

    def test_prerequisite_routing(self) -> None:
        traces = [
            self._make_trace(
                final_action="retrieve_memories",
                final_mastery=0.3,
                diagnosis_type="knowledge_gap",
                recommended_action="prerequisite",
            )
            for _ in range(2)
        ]
        metrics = compute_metrics(traces)
        assert metrics["prerequisite_routing_frequency"] == 1.0

    def test_model_calls_aggregated(self) -> None:
        traces = [
            self._make_trace(
                final_action="complete_concept",
                final_mastery=0.8,
                diagnosis_type="mastered",
                recommended_action="continue",
                model_calls=5,
            ),
            self._make_trace(
                final_action="retrieve_memories",
                final_mastery=0.4,
                diagnosis_type="knowledge_gap",
                recommended_action="reteach",
                model_calls=3,
            ),
        ]
        metrics = compute_metrics(traces)
        assert metrics["total_model_calls"] == 8

    def _make_trace(
        self,
        final_action: str,
        final_mastery: float,
        diagnosis_type: str,
        recommended_action: str,
        model_calls: int = 1,
        misconception: bool = False,
    ) -> GraphTrace:
        trace = GraphTrace(
            id=f"trace-{final_action}-{final_mastery}",
            scenario_label="test",
            student_id="s-1",
            concept_id="c-1",
            trace_data={
                "diagnosis_result": {
                    "diagnosis_type": diagnosis_type,
                },
            },
            node_transitions=[
                {
                    "node": "diagnose",
                    "recommended_action": recommended_action,
                    "duration_ms": 100,
                },
            ],
            total_duration_ms=100 * model_calls,
            token_usage={"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
            model_calls=model_calls,
            final_action=final_action,
            final_mastery=final_mastery,
        )
        return trace


class TestReports:
    def test_format_trace_report_basic(self) -> None:
        trace = {
            "total_duration_ms": 1500.5,
            "model_calls": 3,
            "token_usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
            "node_transitions": [
                {"node": "retrieve_memories", "duration_ms": 200.0},
                {"node": "teach", "duration_ms": 800.0, "current_action": "ask_question"},
                {"node": "ask_question", "duration_ms": 500.0},
            ],
            "final_state": {
                "current_action": "evaluate_response",
                "mastery_estimate": 0.0,
                "recommended_action": None,
            },
        }
        report = format_trace_report(trace, MASTERED_STUDENT)
        assert "AI EVALUATION TRACE REPORT" in report
        assert "mastered_student" in report
        assert "1500.5ms" in report
        assert "retrieve_memories" in report
        assert "teach" in report
        assert "ask_question" in report
        assert "PASS" in report or "FAIL" in report

    def test_format_trace_report_no_scenario(self) -> None:
        trace = {
            "total_duration_ms": 100.0,
            "model_calls": 1,
            "token_usage": {},
            "node_transitions": [],
            "final_state": {"current_action": "complete_concept", "mastery_estimate": 0.9},
        }
        report = format_trace_report(trace)
        assert "AI EVALUATION TRACE REPORT" in report
        assert "Scenario:" not in report

    def test_format_metrics_report(self) -> None:
        metrics = {
            "total_sessions": 10,
            "concept_mastery_rate": 0.7,
            "remediation_rate": 0.3,
            "misconception_detection_rate": 0.1,
            "prerequisite_routing_frequency": 0.05,
            "session_completion_rate": 0.8,
            "avg_mastery_gain": 0.15,
            "avg_execution_duration_ms": 1200.0,
            "total_model_calls": 45,
            "breakdown": {
                "mastered_count": 7,
                "reteach_count": 2,
                "prerequisite_count": 1,
            },
        }
        report = format_metrics_report(metrics)
        assert "TEACHER METRICS REPORT" in report
        assert "70.00%" in report
        assert "30.00%" in report
        assert "Total Sessions: 10" in report

    def test_format_metrics_report_empty(self) -> None:
        metrics = {
            "total_sessions": 0,
            "concept_mastery_rate": 0.0,
            "remediation_rate": 0.0,
            "misconception_detection_rate": 0.0,
            "prerequisite_routing_frequency": 0.0,
            "session_completion_rate": 0.0,
            "avg_mastery_gain": 0.0,
            "avg_execution_duration_ms": 0.0,
            "total_model_calls": 0,
            "breakdown": {},
        }
        report = format_metrics_report(metrics)
        assert "Total Sessions: 0" in report

    def test_format_multi_scenario_report(self) -> None:
        results = [
            ("mastered_student", {"total_duration_ms": 500, "model_calls": 3, "final_state": {"current_action": "complete_concept"}}, True),
            ("struggling_student", {"total_duration_ms": 1200, "model_calls": 5, "final_state": {"current_action": "evaluate_response"}}, False),
        ]
        report = format_multi_scenario_report(results)
        assert "MULTI-SCENARIO EVALUATION REPORT" in report
        assert "1/2 passed" in report
        assert "[PASS]" in report
        assert "[FAIL]" in report

    def test_summarize_trace_db(self) -> None:
        import datetime
        trace = GraphTrace(
            id="t-1",
            scenario_label="mastered_student",
            student_id="s-1",
            concept_id="c-1",
            total_duration_ms=500.0,
            model_calls=3,
            final_action="complete_concept",
            final_mastery=0.85,
            node_transitions=[{}, {}, {}],
            created_at=datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc),
        )
        summary = summarize_trace_db(trace)
        assert summary["id"] == "t-1"
        assert summary["scenario_label"] == "mastered_student"
        assert summary["node_count"] == 3
        assert summary["final_mastery"] == 0.85


class TestHarness:
    @pytest.mark.asyncio
    async def test_run_evaluation_captures_trace(self) -> None:
        from app.ai.evaluation.harness import run_evaluation

        scenario = MASTERED_STUDENT

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.85,
                "feedback": "Good answer!",
                "understanding": "strong",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose",
                new_callable=AsyncMock,
            ) as mock_diag:
                mock_diag.return_value = self._make_diagnosis_result(
                    diagnosis_type="mastered",
                    recommended_action="continue",
                )

                trace = await run_evaluation(scenario)

                assert "node_transitions" in trace
                assert "total_duration_ms" in trace
                assert "model_calls" in trace
                assert "token_usage" in trace
                assert "final_state" in trace
                assert len(trace["node_transitions"]) >= 2

    @pytest.mark.asyncio
    async def test_run_evaluation_struggling_student(self) -> None:
        from app.ai.evaluation.harness import run_evaluation

        scenario = STRUGGLING_STUDENT

        with patch(
            "app.ai.nodes.evaluate_response.GeminiService.generate_json",
            new_callable=AsyncMock,
        ) as mock_eval:
            mock_eval.return_value = {
                "score": 0.3,
                "feedback": "Not quite right.",
                "understanding": "weak",
            }
            with patch(
                "app.ai.nodes.diagnose.DiagnosisService.diagnose",
                new_callable=AsyncMock,
            ) as mock_diag:
                mock_diag.return_value = self._make_diagnosis_result(
                    diagnosis_type="knowledge_gap",
                    recommended_action="reteach",
                )
                with patch(
                    "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant",
                    new_callable=AsyncMock,
                ) as mock_ret:
                    mock_ret.return_value = self._make_memory_context()
                    with patch(
                        "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context",
                        new_callable=AsyncMock,
                    ) as mock_fmt:
                        mock_fmt.return_value = "No prior observations."
                        with patch(
                            "app.ai.nodes.teach.GeminiService.generate",
                            new_callable=AsyncMock,
                        ) as mock_teach:
                            mock_teach.return_value = "Re-teaching content..."
                            with patch(
                                "app.ai.nodes.ask_question.GeminiService.generate",
                                new_callable=AsyncMock,
                            ) as mock_q:
                                mock_q.return_value = "What is a variable?"

                                trace = await run_evaluation(scenario)

                                assert trace["final_state"]["current_action"] in (
                                    "evaluate_response", "ask_question"
                                )

    @pytest.mark.asyncio
    async def test_run_evaluation_from_state(self) -> None:
        from app.ai.evaluation.harness import run_evaluation_from_state

        state = {
            "session_id": "test",
            "student_id": "test",
            "concept_id": "test",
            "lesson_id": "test",
            "current_action": "ask_question",
            "conversation_history": [],
            "student_response": "A variable stores data.",
            "mastery_estimate": 0.0,
            "teaching_content": "Variables are containers.",
            "question": "What is a variable?",
            "evaluation": None,
            "example_content": None,
            "errors": [],
            "concept_title": "Variables",
            "concept_description": "Test",
            "concept_content": [],
            "examples": [],
            "prerequisite_concepts": [],
            "recommended_action": None,
            "diagnosis_result": None,
            "expected_answer": None,
            "memory_context": None,
            "memory_observations": [],
        }

        mocks = {
            "evaluate_response": AsyncMock(
                return_value={
                    "score": 0.9,
                    "feedback": "Excellent!",
                    "understanding": "strong",
                }
            ),
            "diagnose": AsyncMock(
                return_value=self._make_diagnosis_result(
                    diagnosis_type="mastered",
                    recommended_action="continue",
                )
            ),
        }

        trace = await run_evaluation_from_state(state, mocks)

        assert "node_transitions" in trace
        assert "final_state" in trace

    def _make_diagnosis_result(self, diagnosis_type: str, recommended_action: str):
        from app.ai.diagnosis.schemas import DiagnosisResult

        return DiagnosisResult(
            diagnosis_type=diagnosis_type,
            misconception=None,
            misconception_category=None,
            knowledge_gap=None if diagnosis_type != "knowledge_gap" else "Missing prerequisite understanding",
            prerequisite_concepts=[],
            recommended_action=recommended_action,
            evidence=["analysis"],
            remediation=None,
        )

    def _make_memory_context(self):
        from app.ai.memory.schemas import MemoryContext

        return MemoryContext(
            observations=[],
            relevant_memories=[],
            recurring_misconceptions=[],
            learning_signals=[],
        )


class TestRouter:
    def test_router_prefix(self) -> None:
        assert router.prefix == "/api/v1/ai/evaluation"

    def test_router_tags(self) -> None:
        assert "AI Evaluation" in router.tags

    def test_routes_registered(self) -> None:
        routes = [r.path for r in router.routes]
        assert "/api/v1/ai/evaluation/metrics" in routes
        assert "/api/v1/ai/evaluation/traces" in routes
        assert "/api/v1/ai/evaluation/scenarios" in routes

    @pytest.mark.asyncio
    async def test_scenarios_endpoint(self) -> None:
        from httpx import ASGITransport, AsyncClient

        from app.auth.dependencies import get_current_active_user
        from app.main import app

        async def _override_session():
            return AsyncMock()

        async def _override_user():
            return Mock()

        app.dependency_overrides[get_session] = _override_session
        app.dependency_overrides[get_current_active_user] = _override_user

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/ai/evaluation/scenarios")

            assert response.status_code == 200, response.text
            data = response.json()
            assert data["status"] == "success"
            scenarios = data["data"]
            assert len(scenarios) >= 4
            labels = [s["label"] for s in scenarios]
            assert "mastered_student" in labels
            assert "struggling_student" in labels
            assert "misconception_case" in labels
            assert "prerequisite_gap_case" in labels

        app.dependency_overrides.clear()
