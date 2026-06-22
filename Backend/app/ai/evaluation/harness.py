from __future__ import annotations

import time
from typing import Any

from app.ai.evaluation.datasets import EvaluationScenario, build_initial_state
from app.ai.graphs.teacher import teacher_graph


async def run_evaluation(
    scenario: EvaluationScenario,
    mock_retrieve_memories: Any = None,
    mock_format_memory_context: Any = None,
    mock_teach: Any = None,
    mock_ask_question: Any = None,
    mock_evaluate_response: Any = None,
    mock_provide_example: Any = None,
    mock_diagnose: Any = None,
) -> dict[str, Any]:
    initial_state = build_initial_state(scenario)

    patchers = _build_patchers(
        retrieve_memories=mock_retrieve_memories,
        format_memory_context=mock_format_memory_context,
        teach=mock_teach,
        ask_question=mock_ask_question,
        evaluate_response=mock_evaluate_response,
        provide_example=mock_provide_example,
        diagnose=mock_diagnose,
    )
    _start_patchers(patchers)
    try:
        trace = await _execute_with_tracing(initial_state)
    finally:
        _stop_patchers(patchers)

    return trace


async def run_evaluation_from_state(
    initial_state: dict[str, Any],
    mocks: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mocks = mocks or {}

    patchers = _build_patchers(
        retrieve_memories=mocks.get("retrieve_memories"),
        format_memory_context=mocks.get("format_memory_context"),
        teach=mocks.get("teach"),
        ask_question=mocks.get("ask_question"),
        evaluate_response=mocks.get("evaluate_response"),
        provide_example=mocks.get("provide_example"),
        diagnose=mocks.get("diagnose"),
    )
    _start_patchers(patchers)
    try:
        trace = await _execute_with_tracing(initial_state)
    finally:
        _stop_patchers(patchers)

    return trace


async def _execute_with_tracing(initial_state: dict[str, Any]) -> dict[str, Any]:
    node_transitions: list[dict[str, Any]] = []
    model_calls = 0
    total_start = time.monotonic()

    async for output in teacher_graph.astream(initial_state):
        for node_name, node_output in output.items():
            duration = 0.0
            if isinstance(node_output, dict):
                duration = node_output.pop("_execution_duration_ms", 0.0)

            entry: dict[str, Any] = {
                "node": node_name,
                "output_keys": list(node_output.keys()) if isinstance(node_output, dict) else [],
                "duration_ms": round(duration, 2),
            }

            if isinstance(node_output, dict):
                for key in ("current_action", "recommended_action", "mastery_estimate"):
                    if key in node_output:
                        entry[key] = node_output[key]

            node_transitions.append(entry)
            model_calls += 1

    total_duration = time.monotonic() - total_start

    final_state = await teacher_graph.ainvoke(initial_state)

    trace: dict[str, Any] = {
        "node_transitions": node_transitions,
        "total_duration_ms": round(total_duration * 1000, 2),
        "model_calls": model_calls,
        "token_usage": _estimate_token_usage(node_transitions, final_state),
        "final_state": {
            "current_action": _safe_str(final_state.get("current_action")),
            "recommended_action": final_state.get("recommended_action"),
            "mastery_estimate": final_state.get("mastery_estimate", 0.0),
            "teaching_content": final_state.get("teaching_content"),
            "question": final_state.get("question"),
            "evaluation": final_state.get("evaluation"),
            "example_content": final_state.get("example_content"),
            "diagnosis_result": final_state.get("diagnosis_result"),
        },
    }

    return trace


def _estimate_token_usage(
    node_transitions: list[dict[str, Any]],
    final_state: dict[str, Any],
) -> dict[str, int]:
    input_tokens = 0
    output_tokens = 0

    for content_key in ("teaching_content", "question", "evaluation", "example_content"):
        val = final_state.get(content_key)
        if val:
            output_tokens += max(1, len(str(val)) // 4)

    conversation = final_state.get("conversation_history", [])
    for entry in conversation:
        content = entry.get("content", "")
        input_tokens += max(1, len(str(content)) // 4)

    return {
        "prompt_tokens": input_tokens or 50,
        "completion_tokens": output_tokens or 20,
        "total_tokens": (input_tokens or 50) + (output_tokens or 20),
    }


def _safe_str(val: Any) -> str:
    if val is None:
        return "none"
    if hasattr(val, "value"):
        return val.value
    return str(val)


def _build_patchers(
    retrieve_memories: Any = None,
    format_memory_context: Any = None,
    teach: Any = None,
    ask_question: Any = None,
    evaluate_response: Any = None,
    provide_example: Any = None,
    diagnose: Any = None,
) -> list[Any]:
    from unittest.mock import patch

    patchers: list[Any] = []

    targets = {
        "app.ai.nodes.retrieve_memories.MemoryService.retrieve_relevant": retrieve_memories,
        "app.ai.nodes.retrieve_memories.MemoryService.format_memory_context": format_memory_context,
        "app.ai.nodes.teach.GeminiService.generate": teach,
        "app.ai.nodes.ask_question.GeminiService.generate": ask_question,
        "app.ai.nodes.evaluate_response.GeminiService.generate_json": evaluate_response,
        "app.ai.nodes.provide_example.GeminiService.generate": provide_example,
        "app.ai.nodes.diagnose.DiagnosisService.diagnose": diagnose,
    }

    for target, mock_obj in targets.items():
        if mock_obj is not None:
            patchers.append(patch(target, new=mock_obj))

    return patchers


def _start_patchers(patchers: list[Any]) -> None:
    for p in patchers:
        p.start()


def _stop_patchers(patchers: list[Any]) -> None:
    for p in patchers:
        p.stop()
