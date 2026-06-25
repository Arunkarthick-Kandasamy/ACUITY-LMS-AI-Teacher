from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response

from app.main import app


class TestSecurityHeadersMiddleware:
    @pytest.mark.asyncio
    async def test_adds_security_headers(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.headers.get("X-Content-Type-Options") == "nosniff"
            assert response.headers.get("X-Frame-Options") == "DENY"
            assert response.headers.get("X-XSS-Protection") == "1; mode=block"
            assert response.headers.get("Strict-Transport-Security") == "max-age=31536000; includeSubDomains"
            assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    @pytest.mark.asyncio
    async def test_request_id_header_added(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert "X-Request-ID" in response.headers

    @pytest.mark.asyncio
    async def test_process_time_header_added(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert "X-Process-Time" in response.headers

    @pytest.mark.asyncio
    async def test_content_type_header(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.headers.get("content-type") == "application/json"


class TestRateLimitMiddleware:
    @pytest.mark.asyncio
    async def test_allows_requests_under_limit(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            for _ in range(5):
                response = await client.get("/")
                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_blocks_after_limit_direct(self) -> None:
        from app.middleware.rate_limit import RateLimitMiddleware

        app_instance = MagicMock()
        middleware = RateLimitMiddleware(app_instance, max_requests=3, window_seconds=60)

        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"

        call_next = AsyncMock(return_value=Response("ok", status_code=200))

        for _ in range(3):
            response = await middleware.dispatch(request, call_next)
            assert response.status_code == 200

        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(request, call_next)
        assert "Too many" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_per_ip(self) -> None:
        from app.middleware.rate_limit import RateLimitMiddleware

        app_instance = MagicMock()
        middleware = RateLimitMiddleware(app_instance, max_requests=2, window_seconds=60)
        call_next = AsyncMock(return_value=Response("ok", status_code=200))

        client_a = MagicMock(spec=Request)
        client_a.client.host = "10.0.0.1"

        client_b = MagicMock(spec=Request)
        client_b.client.host = "10.0.0.2"

        for _ in range(2):
            resp = await middleware.dispatch(client_a, call_next)
            assert resp.status_code == 200

        resp = await middleware.dispatch(client_b, call_next)
        assert resp.status_code == 200

        with pytest.raises(Exception) as exc_info:
            await middleware.dispatch(client_a, call_next)
        assert "Too many" in str(exc_info.value)

        resp = await middleware.dispatch(client_b, call_next)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_window_expiry_allows_new_requests(self) -> None:
        from app.middleware.rate_limit import RateLimitMiddleware

        app_instance = MagicMock()
        middleware = RateLimitMiddleware(app_instance, max_requests=1, window_seconds=0)

        request = MagicMock(spec=Request)
        request.client.host = "127.0.0.1"
        call_next = AsyncMock(return_value=Response("ok", status_code=200))

        resp = await middleware.dispatch(request, call_next)
        assert resp.status_code == 200
