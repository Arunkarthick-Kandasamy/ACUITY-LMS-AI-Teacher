from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt as jose_jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_roles
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.common.types import UserRole
from app.config import settings
from app.main import app
from app.security.config import security_settings
from app.users.models import User


def _make_user(role: UserRole, is_active: bool = True) -> User:
    return User(
        id="user-id",
        email="user@test.com",
        password_hash="hash",
        full_name="Test User",
        role=role,
        is_active=is_active,
    )


# ---------------------------------------------------------------------------
# Unit — RequireRoles Dependency
# ---------------------------------------------------------------------------

class TestRequireRoles:
    @pytest.mark.asyncio
    async def test_allows_correct_role(self) -> None:
        dependency = require_roles(UserRole.ADMIN, UserRole.PARENT)
        user = _make_user(UserRole.ADMIN)
        result = await dependency(user)
        assert result is user

    @pytest.mark.asyncio
    async def test_denies_wrong_role(self) -> None:
        dependency = require_roles(UserRole.ADMIN)
        user = _make_user(UserRole.STUDENT)
        with pytest.raises(ForbiddenException) as exc:
            await dependency(user)
        assert exc.value.code == "INSUFFICIENT_ROLE"

class TestGetCurrentActiveUser:
    @pytest.mark.asyncio
    async def test_denies_inactive_user(self) -> None:
        from app.auth.dependencies import get_current_active_user

        user = _make_user(UserRole.STUDENT, is_active=False)
        with pytest.raises(ForbiddenException) as exc:
            await get_current_active_user(current_user=user)
        assert exc.value.code == "ACCOUNT_INACTIVE"

    @pytest.mark.asyncio
    async def test_allows_active_user(self) -> None:
        from app.auth.dependencies import get_current_active_user

        user = _make_user(UserRole.STUDENT, is_active=True)
        result = await get_current_active_user(current_user=user)
        assert result is user


# ---------------------------------------------------------------------------
# Unit — GetCurrentUser Dependency
# ---------------------------------------------------------------------------

class TestGetTokenFromHeader:
    @pytest.mark.asyncio
    async def test_missing_header(self) -> None:
        from app.auth.dependencies import get_token_from_header

        with pytest.raises(UnauthorizedException) as exc:
            await get_token_from_header(authorization="")
        assert exc.value.code == "INVALID_AUTH_HEADER"

    @pytest.mark.asyncio
    async def test_invalid_scheme(self) -> None:
        from app.auth.dependencies import get_token_from_header

        with pytest.raises(UnauthorizedException) as exc:
            await get_token_from_header(authorization="Basic abc123")
        assert exc.value.code == "INVALID_AUTH_HEADER"

    @pytest.mark.asyncio
    async def test_valid_scheme(self) -> None:
        from app.auth.dependencies import get_token_from_header

        token = await get_token_from_header(authorization="Bearer my.jwt.token")
        assert token == "my.jwt.token"


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_invalid_token_type(self) -> None:
        from app.security.jwt import create_refresh_token

        refresh_token = create_refresh_token(subject="user-id", jti="jti-1")
        mock_session = MagicMock()
        user_repo = MagicMock()
        user_repo.get = AsyncMock()

        # We test decode failure directly in test_auth.py; here verify
        # that a non-access token is rejected
        with pytest.raises(UnauthorizedException) as exc:
            await get_current_user(token=refresh_token, session=mock_session)
        assert exc.value.code == "INVALID_TOKEN_TYPE"


# ---------------------------------------------------------------------------
# Integration — RBAC via API
# ---------------------------------------------------------------------------

class TestAuthRBACIntegration:
    @pytest.mark.skip(reason="requires live database")
    @pytest.mark.asyncio
    async def test_access_without_token(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"{settings.api_prefix}/auth/me")
            assert resp.status_code in (401, 403, 404)

    @pytest.mark.skip(reason="requires live database")
    @pytest.mark.asyncio
    async def test_access_with_expired_token(self) -> None:
        payload = {
            "sub": "user-id",
            "email": "user@test.com",
            "role": "student",
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(days=1),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jose_jwt.encode(payload, security_settings.secret_key, algorithm=security_settings.algorithm)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                f"{settings.api_prefix}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert resp.status_code in (401, 404)

    @pytest.mark.skip(reason="requires live database")
    @pytest.mark.asyncio
    async def test_malformed_token(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(
                f"{settings.api_prefix}/auth/me",
                headers={"Authorization": "Bearer definitely.not.a.valid.jwt"},
            )
            assert resp.status_code in (401, 404)
