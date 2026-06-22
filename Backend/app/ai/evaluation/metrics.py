from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta, timezone
from typing import Any

from app.evaluation.models import GraphTrace, TeacherMetricsSnapshot


def compute_metrics(traces: Sequence[GraphTrace]) -> dict[str, Any]:
    if not traces:
        return _empty_metrics()

    total = len(traces)
    completed = sum(1 for t in traces if _is_completed(t))
    reteach_count = sum(1 for t in traces if _has_action(t, "reteach"))
    prerequisite_count = sum(1 for t in traces if _has_action(t, "prerequisite"))
    example_count = sum(1 for t in traces if _has_action(t, "example"))
    continue_count = sum(1 for t in traces if _has_action(t, "continue"))
    mastered = sum(1 for t in traces if t.final_mastery >= 0.7)
    misconception_detected = sum(
        1
        for t in traces
        if t.trace_data.get("diagnosis_result", {}).get("diagnosis_type") == "misconception"
    )

    remediation_count = reteach_count + prerequisite_count + example_count
    total_model_calls = sum(t.model_calls for t in traces)
    total_duration = sum(t.total_duration_ms for t in traces)

    return {
        "total_sessions": total,
        "concepts_taught": _count_unique_concepts(traces),
        "concept_mastery_rate": round(mastered / total, 4) if total else 0.0,
        "remediation_rate": round(remediation_count / total, 4) if total else 0.0,
        "misconception_detection_rate": round(misconception_detected / total, 4) if total else 0.0,
        "prerequisite_routing_frequency": round(prerequisite_count / total, 4) if total else 0.0,
        "session_completion_rate": round(completed / total, 4) if total else 0.0,
        "avg_mastery_gain": _avg_mastery_gain(traces),
        "avg_execution_duration_ms": round(total_duration / total, 2) if total else 0.0,
        "total_model_calls": total_model_calls,
        "breakdown": {
            "reteach_count": reteach_count,
            "prerequisite_count": prerequisite_count,
            "example_count": example_count,
            "continue_count": continue_count,
            "mastered_count": mastered,
            "misconception_detected": misconception_detected,
        },
    }


async def compute_and_store_metrics(
    traces: Sequence[GraphTrace],
    db_session: Any,
    label: str | None = None,
) -> TeacherMetricsSnapshot:
    metrics = compute_metrics(traces)

    now = datetime.now(timezone.utc)
    snapshot = TeacherMetricsSnapshot(
        snapshot_label=label or f"metrics-{now.strftime('%Y%m%d-%H%M%S')}",
        period_start=now - timedelta(hours=1),
        period_end=now,
        **{k: v for k, v in metrics.items() if k != "breakdown"},
        breakdown=metrics.get("breakdown"),
    )

    db_session.add(snapshot)
    await db_session.flush()
    return snapshot


def compute_metrics_from_snapshots(
    snapshots: Sequence[TeacherMetricsSnapshot],
) -> dict[str, Any]:
    if not snapshots:
        return _empty_metrics()

    latest = snapshots[-1]
    return {
        "total_sessions": latest.total_sessions,
        "concept_mastery_rate": latest.concept_mastery_rate,
        "remediation_rate": latest.remediation_rate,
        "misconception_detection_rate": latest.misconception_detection_rate,
        "prerequisite_routing_frequency": latest.prerequisite_routing_frequency,
        "session_completion_rate": latest.session_completion_rate,
        "avg_mastery_gain": latest.avg_mastery_gain,
        "avg_execution_duration_ms": latest.avg_execution_duration_ms,
        "total_model_calls": latest.total_model_calls,
        "snapshot_label": latest.snapshot_label,
        "snapshot_time": latest.created_at.isoformat() if latest.created_at else None,
    }


def _is_completed(trace: GraphTrace) -> bool:
    final = trace.final_action
    return final == "complete_concept" or (
        trace.trace_data.get("final_state", {}).get("current_action") == "complete_concept"
    )


def _has_action(trace: GraphTrace, action: str) -> bool:
    for transition in trace.node_transitions:
        if transition.get("recommended_action") == action:
            return True
    return trace.final_action == action


def _count_unique_concepts(traces: Sequence[GraphTrace]) -> int:
    concepts = set()
    for t in traces:
        if t.concept_id:
            concepts.add(t.concept_id)
    return len(concepts)


def _avg_mastery_gain(traces: Sequence[GraphTrace]) -> float:
    gains = [t.final_mastery for t in traces]
    if not gains:
        return 0.0
    return round(sum(gains) / len(gains), 4)


def _empty_metrics() -> dict[str, Any]:
    return {
        "total_sessions": 0,
        "concepts_taught": 0,
        "concept_mastery_rate": 0.0,
        "remediation_rate": 0.0,
        "misconception_detection_rate": 0.0,
        "prerequisite_routing_frequency": 0.0,
        "session_completion_rate": 0.0,
        "avg_mastery_gain": 0.0,
        "avg_execution_duration_ms": 0.0,
        "total_model_calls": 0,
        "breakdown": {
            "reteach_count": 0,
            "prerequisite_count": 0,
            "example_count": 0,
            "continue_count": 0,
            "mastered_count": 0,
            "misconception_detected": 0,
        },
    }
