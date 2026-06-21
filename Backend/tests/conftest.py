from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_db_healthy() -> None:
    with patch("app.api.routes.health.check_db_health") as mock:
        mock.return_value = True
        yield


@pytest.fixture
def mock_db_unhealthy() -> None:
    with patch("app.api.routes.health.check_db_health") as mock:
        mock.return_value = False
        yield
