from __future__ import annotations

import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from app.monitoring.models import (
    AiRequestMetrics,
    EndpointMetrics,
    GraphExecutionMetrics,
    MetricEntry,
)

logger = logging.getLogger(__name__)


class MetricsCollector:
    def __init__(self) -> None:
        self.ai_requests: list[AiRequestMetrics] = []
        self.graph_executions: list[GraphExecutionMetrics] = []
        self.endpoint_metrics: list[EndpointMetrics] = []
        self.custom_metrics: list[MetricEntry] = []
        self._max_entries = 10_000

    def record_ai_request(self, metrics: AiRequestMetrics) -> None:
        self.ai_requests.append(metrics)
        if len(self.ai_requests) > self._max_entries:
            self.ai_requests = self.ai_requests[-self._max_entries :]
        logger.debug(
            "AI request [%s]: %.1fms, tokens=%d, success=%s",
            metrics.prompt_name,
            metrics.duration_ms,
            metrics.token_count,
            metrics.success,
        )

    def record_graph_execution(self, metrics: GraphExecutionMetrics) -> None:
        self.graph_executions.append(metrics)
        if len(self.graph_executions) > self._max_entries:
            self.graph_executions = self.graph_executions[-self._max_entries :]
        logger.debug(
            "Graph execution [%s]: %.1fms, %d nodes, %d model calls",
            metrics.session_id,
            metrics.total_duration_ms,
            metrics.node_count,
            metrics.model_calls,
        )

    def record_endpoint(self, metrics: EndpointMetrics) -> None:
        self.endpoint_metrics.append(metrics)
        if len(self.endpoint_metrics) > self._max_entries:
            self.endpoint_metrics = self.endpoint_metrics[-self._max_entries :]

    def record_custom(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        entry = MetricEntry(name=name, value=value, tags=tags or {})
        self.custom_metrics.append(entry)
        if len(self.custom_metrics) > self._max_entries:
            self.custom_metrics = self.custom_metrics[-self._max_entries :]

    def get_ai_latency_summary(self, minutes: int = 60) -> dict[str, Any]:
        cutoff = time.time() - minutes * 60
        recent = [m for m in self.ai_requests if self._to_timestamp(m) > cutoff]

        if not recent:
            return {"avg_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "p99_ms": 0.0, "count": 0}

        durations = sorted(m.duration_ms for m in recent)
        n = len(durations)
        return {
            "avg_ms": round(sum(durations) / n, 2),
            "p50_ms": round(durations[n // 2], 2),
            "p95_ms": round(durations[int(n * 0.95)], 2),
            "p99_ms": round(durations[int(n * 0.99)], 2),
            "count": n,
        }

    def get_token_usage_summary(self, minutes: int = 60) -> dict[str, Any]:
        cutoff = time.time() - minutes * 60
        recent = [m for m in self.ai_requests if self._to_timestamp(m) > cutoff]
        total_tokens = sum(m.token_count for m in recent)
        return {
            "total_tokens": total_tokens,
            "avg_tokens_per_request": round(total_tokens / len(recent), 1) if recent else 0,
            "request_count": len(recent),
        }

    def get_graph_execution_summary(self, minutes: int = 60) -> dict[str, Any]:
        cutoff = time.time() - minutes * 60
        recent = [m for m in self.graph_executions if self._to_timestamp(m, "graph") > cutoff]

        if not recent:
            return {"avg_duration_ms": 0.0, "count": 0, "error_rate": 0.0}

        durations = [m.total_duration_ms for m in recent]
        errors = sum(1 for m in recent if not m.success)
        return {
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "avg_model_calls": round(sum(m.model_calls for m in recent) / len(recent), 1),
            "avg_nodes": round(sum(m.node_count for m in recent) / len(recent), 1),
            "count": len(recent),
            "error_rate": round(errors / len(recent), 4),
        }

    def get_error_rate_summary(self, minutes: int = 60) -> dict[str, Any]:
        cutoff = time.time() - minutes * 60
        recent_ai = [m for m in self.ai_requests if self._to_timestamp(m) > cutoff]
        recent_endpoints = [m for m in self.endpoint_metrics if self._to_timestamp(m, "endpoint") > cutoff]

        ai_total = len(recent_ai)
        ai_errors = sum(1 for m in recent_ai if not m.success)
        ep_total = len(recent_endpoints)
        ep_errors = sum(1 for m in recent_endpoints if m.status_code >= 500)

        return {
            "ai_error_rate": round(ai_errors / ai_total, 4) if ai_total else 0.0,
            "ai_error_count": ai_errors,
            "ai_total": ai_total,
            "endpoint_error_rate": round(ep_errors / ep_total, 4) if ep_total else 0.0,
            "endpoint_error_count": ep_errors,
            "endpoint_total": ep_total,
        }

    def get_all_metrics(self, minutes: int = 60) -> dict[str, Any]:
        return {
            "ai_latency": self.get_ai_latency_summary(minutes),
            "token_usage": self.get_token_usage_summary(minutes),
            "graph_execution": self.get_graph_execution_summary(minutes),
            "error_rates": self.get_error_rate_summary(minutes),
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }

    def clear(self) -> None:
        self.ai_requests.clear()
        self.graph_executions.clear()
        self.endpoint_metrics.clear()
        self.custom_metrics.clear()

    def _to_timestamp(
        self, metric: AiRequestMetrics | GraphExecutionMetrics | EndpointMetrics, kind: str = "ai"
    ) -> float:
        ts = getattr(metric, "timestamp", None)
        if ts is not None:
            return ts.timestamp()
        return time.time()

    @classmethod
    def create_timer(cls) -> tuple[float, Callable[[], float]]:
        start = time.monotonic()
        return start, lambda: (time.monotonic() - start) * 1000


from collections.abc import Callable
