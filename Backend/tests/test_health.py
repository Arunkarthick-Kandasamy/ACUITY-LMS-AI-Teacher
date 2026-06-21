from __future__ import annotations

from httpx import AsyncClient


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
