from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth.dependencies import get_current_active_user, get_current_user, require_roles
from app.auth.service import _hash_token
from app.common.exceptions import UnauthorizedException
from app.common.types import UserRole
from app.config import settings
from app.main import app
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.password import hash_password, verify_password
from app.users.models import User

# ---------------------------------------------------------------------------
# Unit — Password Hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_and_verify(self) -> None:
        password = "SecureP@ss123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("SecureP@ss123")
        assert not verify_password("WrongP@ss456", hashed)

    def test_weak_password_raises(self) -> None:
        from app.common.exceptions import ValidationException
        from app.security.password import validate_password_strength

        with pytest.raises(ValidationException) as exc:
            validate_password_strength("short")
        assert "weak" in exc.value.message.lower() or "password" in exc.value.message.lower()


# ---------------------------------------------------------------------------
# Unit — JWT
# ---------------------------------------------------------------------------

class TestJWT:
    def test_create_and_decode_access_token(self) -> None:
        token = create_access_token(subject="user-123", email="test@test.com", role="student")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@test.com"
        assert payload["role"] == "student"
        assert payload["type"] == "access"

    def test_create_and_decode_refresh_token(self) -> None:
        token = create_refresh_token(subject="user-123", jti="jti-456")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"
        assert payload["jti"] == "jti-456"
        assert payload["type"] == "refresh"

    def test_invalid_token_raises(self) -> None:
        with pytest.raises(UnauthorizedException) as exc:
            decode_token("invalid.token.here")
        assert exc.value.code == "INVALID_TOKEN"

    def test_expired_token_raises(self) -> None:
        from jose import jwt as jose_jwt

        from app.security.config import security_settings

        expired_payload = {
            "sub": "user-123",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jose_jwt.encode(
            expired_payload,
            security_settings.secret_key,
            algorithm=security_settings.algorithm,
        )
        with pytest.raises(UnauthorizedException) as exc:
            decode_token(expired_token)
        assert exc.value.code == "INVALID_TOKEN"

    def test_token_uses_correct_secret(self) -> None:
        from jose import jwt as jose_jwt

        wrong_secret_token = jose_jwt.encode(
            {"sub": "test", "type": "access", "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
            "wrong-secret",
            algorithm="HS256",
        )
        with pytest.raises(UnauthorizedException):
            decode_token(wrong_secret_token)


# ---------------------------------------------------------------------------
# Unit — Auth Service (mocked)
# ---------------------------------------------------------------------------

class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_success(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        from app.auth.service import AuthService

        service = AuthService(mock_session)
        service.user_repo.get_by_email = AsyncMock(return_value=None)
        service.user_repo.create = AsyncMock(
            return_value=User(
                id="new-uuid",
                email="new@test.com",
                password_hash="hashed",
                full_name="New User",
                role=UserRole.STUDENT,
                is_active=True,
            )
        )

        access_token, refresh_token, user = await service.register(
            email="new@test.com",
            password="SecureP@ss123",
            full_name="New User",
            role=UserRole.STUDENT,
        )
        assert user.email == "new@test.com"
        assert user.role == UserRole.STUDENT
        assert mock_session.add.called
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self) -> None:
        mock_session = MagicMock()
        from app.auth.service import AuthService
        from app.common.exceptions import ConflictException

        service = AuthService(mock_session)
        service.user_repo.get_by_email = AsyncMock(
            return_value=User(
                id="existing",
                email="dup@test.com",
                password_hash="hash",
                full_name="Existing",
                role=UserRole.STUDENT,
                is_active=True,
            )
        )

        with pytest.raises(ConflictException) as exc:
            await service.register(
                email="dup@test.com",
                password="SecureP@ss123",
                full_name="Dup",
                role=UserRole.STUDENT,
            )
        assert exc.value.code == "EMAIL_EXISTS"

    @pytest.mark.asyncio
    async def test_login_success(self) -> None:
        mock_session = MagicMock()
        mock_session.flush = AsyncMock()

        from app.auth.service import AuthService
        from app.security.password import hash_password

        hashed = hash_password("SecureP@ss123")
        mock_user = User(
            id="user-id",
            email="user@test.com",
            password_hash=hashed,
            full_name="Test User",
            role=UserRole.STUDENT,
            is_active=True,
        )

        service = AuthService(mock_session)
        service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        access_token, refresh_token, user = await service.login(
            email="user@test.com", password="SecureP@ss123"
        )
        assert user.id == "user-id"
        assert access_token is not None
        assert refresh_token is not None
        assert user.is_active

    @pytest.mark.asyncio
    async def test_login_wrong_password(self) -> None:
        mock_session = MagicMock()
        from app.auth.service import AuthService
        from app.common.exceptions import UnauthorizedException
        from app.security.password import hash_password

        hashed = hash_password("CorrectP@ss123")
        mock_user = User(
            id="user-id",
            email="user@test.com",
            password_hash=hashed,
            full_name="Test User",
            role=UserRole.STUDENT,
            is_active=True,
        )

        service = AuthService(mock_session)
        service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(UnauthorizedException) as exc:
            await service.login(email="user@test.com", password="WrongP@ss456")
        assert exc.value.code == "INVALID_CREDENTIALS"

    @pytest.mark.asyncio
    async def test_login_inactive_user(self) -> None:
        mock_session = MagicMock()
        from app.auth.service import AuthService
        from app.common.exceptions import ForbiddenException
        from app.security.password import hash_password

        hashed = hash_password("SecureP@ss123")
        mock_user = User(
            id="user-id",
            email="user@test.com",
            password_hash=hashed,
            full_name="Test User",
            role=UserRole.STUDENT,
            is_active=False,
        )

        service = AuthService(mock_session)
        service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(ForbiddenException) as exc:
            await service.login(email="user@test.com", password="SecureP@ss123")
        assert exc.value.code == "ACCOUNT_INACTIVE"

    @pytest.mark.asyncio
    async def test_hash_token_consistency(self) -> None:
        token = "some-random-token-string"
        h1 = _hash_token(token)
        h2 = _hash_token(token)
        assert h1 == h2
        assert len(h1) == 64  # SHA256 hex


# ---------------------------------------------------------------------------
# Integration — Auth API via TestClient
# ---------------------------------------------------------------------------

class TestAuthAPI:
    @pytest.mark.skip(reason="requires live database")
    @pytest.mark.asyncio
    async def test_register_validation_email(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                f"{settings.api_prefix}/auth/register",
                json={
                    "email": "not-an-email",
                    "password": "SecureP@ss123",
                    "full_name": "Test User",
                    "role": "student",
                },
            )
            assert resp.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="requires live database")
    async def test_register_validation_weak_password(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                f"{settings.api_prefix}/auth/register",
                json={
                    "email": "test@test.com",
                    "password": "weak",
                    "full_name": "Test User",
                    "role": "student",
                },
            )
            assert resp.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="requires live database")
    async def test_login_validation_empty_body(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                f"{settings.api_prefix}/auth/login",
                json={},
            )
            assert resp.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="requires live database")
    async def test_forgot_password_returns_same_message(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                f"{settings.api_prefix}/auth/forgot-password",
                json={"email": "nonexistent@test.com"},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] == "success"
            assert "reset link" in body["data"]["message"].lower()

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="requires live database")
    async def test_auth_routes_require_body(self) -> None:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                f"{settings.api_prefix}/auth/register",
                json={},
            )
            assert resp.status_code == 422
