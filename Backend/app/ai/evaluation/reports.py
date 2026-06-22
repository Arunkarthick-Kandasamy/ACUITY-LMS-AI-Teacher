from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.ai.evaluation.datasets import SCENARIOS, EvaluationScenario
from app.evaluation.models import GraphTrace


def format_trace_report(trace: dict[str, Any], scenario: EvaluationScenario | None = None) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("AI EVALUATION TRACE REPORT")
    lines.append("=" * 60)

    if scenario:
        lines.append(f"\nScenario: {scenario.label}")
        lines.append(f"Concept: {scenario.concept_title}")
        lines.append(f"Expected action: {scenario.expected_action}")
        lines.append(f"Expected nodes: {' -> '.join(scenario.expected_nodes)}")

    lines.append(f"\n--- Execution ---")
    lines.append(f"Total duration: {trace.get('total_duration_ms', 0):.1f}ms")
    lines.append(f"Model calls: {trace.get('model_calls', 0)}")
    lines.append(f"Token usage: {json.dumps(trace.get('token_usage', {}))}")

    lines.append(f"\n--- Node Transitions ---")
    for i, transition in enumerate(trace.get("node_transitions", []), 1):
        node = transition.get("node", "?")
        duration = transition.get("duration_ms", 0)
        action = transition.get("current_action") or transition.get("recommended_action") or ""
        action_str = f" -> {action}" if action else ""
        lines.append(f"  {i}. {node} ({duration:.1f}ms){action_str}")

    final_state = trace.get("final_state", {})
    lines.append(f"\n--- Final State ---")
    lines.append(f"  Action: {final_state.get('current_action', '?')}")
    lines.append(f"  Mastery: {final_state.get('mastery_estimate', 0.0):.2f}")
    if final_state.get("recommended_action"):
        lines.append(f"  Recommended: {final_state['recommended_action']}")

    if scenario and trace.get("node_transitions"):
        actual_nodes = [t["node"] for t in trace["node_transitions"]]
        expected = scenario.expected_nodes
        passed = actual_nodes == expected
        lines.append(f"\n--- Validation ---")
        lines.append(f"  Expected nodes: {' -> '.join(expected)}")
        lines.append(f"  Actual nodes:   {' -> '.join(actual_nodes)}")
        lines.append(f"  Node sequence match: {'PASS' if passed else 'FAIL'}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_metrics_report(metrics: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("TEACHER METRICS REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    lines.append("--- Key Metrics ---")
    for key in (
        "total_sessions",
        "concept_mastery_rate",
        "remediation_rate",
        "misconception_detection_rate",
        "prerequisite_routing_frequency",
        "session_completion_rate",
        "avg_mastery_gain",
        "avg_execution_duration_ms",
        "total_model_calls",
    ):
        val = metrics.get(key, 0)
        label = key.replace("_", " ").title()
        if isinstance(val, float):
            lines.append(f"  {label}: {val:.2%}" if "rate" in key or "gain" in key else f"  {label}: {val:.2f}")
        else:
            lines.append(f"  {label}: {val}")

    breakdown = metrics.get("breakdown", {})
    if breakdown:
        lines.append("")
        lines.append("--- Breakdown ---")
        for key, val in breakdown.items():
            label = key.replace("_", " ").title()
            lines.append(f"  {label}: {val}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_multi_scenario_report(results: list[tuple[str, dict[str, Any], bool]]) -> str:
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("MULTI-SCENARIO EVALUATION REPORT")
    lines.append("=" * 60)

    passed = sum(1 for _, _, ok in results if ok)
    total = len(results)

    lines.append(f"\nResults: {passed}/{total} passed ({passed / total:.0%})\n" if total else "\nResults: 0/0\n")

    for label, trace, ok in results:
        status = "PASS" if ok else "FAIL"
        dur = trace.get("total_duration_ms", 0)
        calls = trace.get("model_calls", 0)
        final = trace.get("final_state", {}).get("current_action", "?")
        lines.append(f"  [{status}] {label} ({dur:.0f}ms, {calls} calls) -> {final}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def scenario_labels() -> list[str]:
    return [s.label for s in SCENARIOS]


def summarize_trace_db(record: GraphTrace) -> dict[str, Any]:
    return {
        "id": record.id,
        "scenario_label": record.scenario_label,
        "student_id": record.student_id,
        "concept_id": record.concept_id,
        "total_duration_ms": record.total_duration_ms,
        "model_calls": record.model_calls,
        "final_action": record.final_action,
        "final_mastery": record.final_mastery,
        "node_count": len(record.node_transitions),
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }
