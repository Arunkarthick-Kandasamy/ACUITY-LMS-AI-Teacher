from __future__ import annotations

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


class TestHealthEndpoint:
    async def test_health_returns_ok_when_db_connected(
        self, client: AsyncClient, mock_db_healthy: None
    ) -> None:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "ok"
        assert body["data"]["components"]["database"] == "connected"
        assert body["data"]["version"] != ""

    async def test_health_returns_degraded_when_db_disconnected(
        self, client: AsyncClient, mock_db_unhealthy: None
    ) -> None:
        response = await client.get("/api/v1/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "degraded"
        assert body["data"]["components"]["database"] == "disconnected"

    async def test_health_returns_valid_json(
        self, client: AsyncClient, mock_db_healthy: None
    ) -> None:
        response = await client.get("/api/v1/health")

        assert response.headers["content-type"] == "application/json"

        body = response.json()
        data = body["data"]
        assert "status" in data
        assert "version" in data
        assert "components" in data


class TestHealthRouter:
    def test_router_tags(self) -> None:
        from app.health.router import router

        assert "health" in router.tags

    def test_router_paths(self) -> None:
        from app.health.router import router

        paths = [r.path for r in router.routes]
        assert "/api/v1/health" in paths

    @pytest.mark.asyncio
    async def test_health_check_uses_check_db_health(self) -> None:
        with patch("app.health.router.check_db_health") as mock_check:
            mock_check.return_value = True
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/health")
                assert response.status_code == 200
                mock_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_degraded_with_failed_db(self) -> None:
        with patch("app.health.router.check_db_health") as mock_check:
            mock_check.return_value = False
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/api/v1/health")
                body = response.json()
                assert body["data"]["status"] == "degraded"
