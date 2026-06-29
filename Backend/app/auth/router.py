from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    VerifyEmailRequest,
)
from app.auth.service import AuthService
from app.common.response import success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/auth", tags=["Authentication"])


def _build_token_response(
    access_token: str, refresh_token: str, user: User
) -> TokenResponse:
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse(
            user_id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            country=user.country,
            preferred_language=user.preferred_language,
            is_verified=user.is_verified,
            created_at=user.created_at,
        ),
    )


@router.post("/register", status_code=201)
async def register(
    body: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    access_token, refresh_token, user = await service.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        role=body.role,
        date_of_birth=body.date_of_birth,
        country=body.country,
        preferred_language=body.preferred_language,
    )
    return {
        "status": "success",
        "data": _build_token_response(access_token, refresh_token, user).model_dump(
            mode="json"
        ),
    }


@router.post("/verify-email")
async def verify_email(
    body: VerifyEmailRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    await service.verify_email(raw_token=body.token)
    return {
        "status": "success",
        "data": MessageResponse(message="Email verified successfully").model_dump(),
    }


@router.get("/verify-email")
async def verify_email_get(
    token: str = Query(...),
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    await service.verify_email(raw_token=token)
    return {
        "status": "success",
        "data": MessageResponse(message="Email verified successfully").model_dump(),
    }


@router.post("/resend-verification")
async def resend_verification(
    body: ResendVerificationRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    msg = await service.resend_verification(email=body.email)
    return {
        "status": "success",
        "data": MessageResponse(message=msg).model_dump(),
    }


@router.post("/login")
async def login(
    body: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    access_token, refresh_token, user = await service.login(
        email=body.email, password=body.password, role=body.role
    )
    return {
        "status": "success",
        "data": _build_token_response(access_token, refresh_token, user).model_dump(
            mode="json"
        ),
    }


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    new_access, new_refresh = await service.refresh(body.refresh_token)
    return {
        "status": "success",
        "data": {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "Bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        },
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    await service.logout(current_user.id)
    return {
        "status": "success",
        "data": MessageResponse(message="Logged out successfully").model_dump(),
    }


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    await service.forgot_password(email=body.email)
    return {
        "status": "success",
        "data": MessageResponse(
            message="If the email exists, a reset link has been sent"
        ).model_dump(),
    }


@router.get("/csrf-token")
async def get_csrf_token(response: Response) -> dict:
    token = secrets.token_hex(32)
    response.set_cookie(key="csrf_token", value=token, httponly=True, samesite="strict", secure=False)
    return {"status": "success", "data": {"csrf_token": token}}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    service = AuthService(session)
    await service.reset_password(token=body.token, new_password=body.new_password)
    return {
        "status": "success",
        "data": MessageResponse(message="Password reset successfully").model_dump(),
    }


@router.get("/export-data")
async def export_data(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AuthService(session)
    data = await service.export_user_data(current_user.id)
    return success_response(data)


@router.post("/delete-account")
async def delete_account(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AuthService(session)
    await service.delete_account(current_user.id)
    return success_response(
        MessageResponse(message="Account deleted successfully").model_dump()
    )
