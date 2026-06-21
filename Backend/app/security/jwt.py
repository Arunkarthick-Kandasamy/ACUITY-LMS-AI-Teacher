from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from jose import JWTError, jwt

from app.common.exceptions import UnauthorizedException
from app.security.config import security_settings


def create_access_token(subject: str, email: str, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "email": email,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + security_settings.access_token_expire,
    }
    return jwt.encode(payload, security_settings.secret_key, algorithm=security_settings.algorithm)


def create_refresh_token(subject: str, jti: str) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "jti": jti,
        "type": "refresh",
        "iat": now,
        "exp": now + security_settings.refresh_token_expire,
    }
    return jwt.encode(payload, security_settings.secret_key, algorithm=security_settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(
            token, security_settings.secret_key, algorithms=[security_settings.algorithm]
        )
        return payload
    except JWTError:
        raise UnauthorizedException(message="Invalid or expired token", code="INVALID_TOKEN") from None
