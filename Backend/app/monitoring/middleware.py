from __future__ import annotations

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.monitoring.metrics import MetricsCollector


class MonitoringMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, metrics_collector: MetricsCollector | None = None) -> None:
        super().__init__(app)
        self.metrics = metrics_collector or MetricsCollector()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.metrics = self.metrics

        start = time.monotonic()

        try:
            response = await call_next(request)
            duration = (time.monotonic() - start) * 1000

            self.metrics.record_endpoint(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration, 2),
            )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.3f}"

            return response
        except Exception as exc:
            duration = (time.monotonic() - start) * 1000

            self.metrics.record_endpoint(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=round(duration, 2),
                error=str(exc),
            )

            raise
