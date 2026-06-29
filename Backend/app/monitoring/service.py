from __future__ import annotations

import logging
from typing import Any

from app.monitoring.metrics import MetricsCollector
from app.monitoring.models import AiRequestMetrics, GraphExecutionMetrics

logger = logging.getLogger(__name__)


class MonitoringService:
    def __init__(self, collector: MetricsCollector | None = None) -> None:
        self.collector = collector or MetricsCollector()

    async def track_ai_request(
        self,
        prompt_name: str,
        duration_ms: float,
        token_count: int = 0,
        success: bool = True,
        error: str | None = None,
        guardrail_triggered: bool = False,
        fallback_used: bool = False,
    ) -> None:
        metrics = AiRequestMetrics(
            prompt_name=prompt_name,
            duration_ms=round(duration_ms, 2),
            token_count=token_count,
            success=success,
            error=error,
            guardrail_triggered=guardrail_triggered,
            fallback_used=fallback_used,
        )
        self.collector.record_ai_request(metrics)

    async def track_graph_execution(
        self,
        session_id: str,
        total_duration_ms: float,
        node_durations: dict[str, float] | None = None,
        model_calls: int = 0,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        nodes = node_durations or {}
        metrics = GraphExecutionMetrics(
            session_id=session_id,
            total_duration_ms=round(total_duration_ms, 2),
            node_count=len(nodes),
            node_durations=nodes,
            model_calls=model_calls,
            success=success,
            error=error,
        )
        self.collector.record_graph_execution(metrics)

    def get_summary(self, minutes: int = 60) -> dict[str, Any]:
        return self.collector.get_all_metrics(minutes)

    def get_health_metrics(self) -> dict[str, Any]:
        summary = self.collector.get_all_metrics(5)
        ai_error_rate = summary["error_rates"]["ai_error_rate"]
        endpoint_error_rate = summary["error_rates"]["endpoint_error_rate"]
        ai_latency_p95 = summary["ai_latency"]["p95_ms"]

        status = "healthy"
        if ai_error_rate > 0.1 or endpoint_error_rate > 0.05:
            status = "degraded"
        if ai_error_rate > 0.3 or endpoint_error_rate > 0.15:
            status = "unhealthy"

        return {
            "status": status,
            "ai_latency_p95_ms": ai_latency_p95,
            "ai_error_rate": ai_error_rate,
            "endpoint_error_rate": endpoint_error_rate,
        }
