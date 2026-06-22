from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MetricEntry:
    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime | None = None
    unit: str = "ms"

    def __post_init__(self) -> None:
        if self.timestamp is None:
            from datetime import timezone

            self.timestamp = datetime.now(timezone.utc)


@dataclass
class AiRequestMetrics:
    prompt_name: str
    duration_ms: float
    token_count: int = 0
    success: bool = True
    error: str | None = None
    guardrail_triggered: bool = False
    fallback_used: bool = False


@dataclass
class GraphExecutionMetrics:
    session_id: str
    total_duration_ms: float
    node_count: int = 0
    node_durations: dict[str, float] = field(default_factory=dict)
    model_calls: int = 0
    success: bool = True
    error: str | None = None


@dataclass
class EndpointMetrics:
    method: str
    path: str
    status_code: int
    duration_ms: float
    user_id: str | None = None
    error: str | None = None
