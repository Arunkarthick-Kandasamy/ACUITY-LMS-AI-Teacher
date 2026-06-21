from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.common.types import UserRole
from app.infrastructure.database import get_session
from app.security.jwt import decode_token
from app.users.models import User
from app.users.repository import UserRepository


async def get_token_from_header(authorization: str = Header(..., alias="Authorization")) -> str:
    if not authorization.startswith("Bearer "):
        raise UnauthorizedException(
            message="Invalid authorization header format", code="INVALID_AUTH_HEADER"
        )
    return authorization.removeprefix("Bearer ")


async def get_current_user(
    token: str = Depends(get_token_from_header),
    session: AsyncSession = Depends(get_session),
) -> User:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedException(
            message="Invalid token type. Use an access token.", code="INVALID_TOKEN_TYPE"
        )

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException(
            message="Token missing subject claim", code="INVALID_TOKEN"
        )

    user_repo = UserRepository(session)
    user = await user_repo.get(user_id)
    if user is None:
        raise UnauthorizedException(message="User not found", code="USER_NOT_FOUND")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise ForbiddenException(
            message="Account is deactivated. Contact an administrator.",
            code="ACCOUNT_INACTIVE",
        )
    return current_user


def require_roles(*allowed_roles: UserRole):
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(
                message=f"Requires one of these roles: {', '.join(r.value for r in allowed_roles)}",
                code="INSUFFICIENT_ROLE",
            )
        return current_user

    return role_checker
