from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from app.common.types import UserRole


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255, pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., max_length=150)
    role: UserRole
    date_of_birth: date | None = None
    country: str | None = Field(None, max_length=100)
    preferred_language: str = Field(default="en", max_length=10)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: UserRole
    country: str | None = None
    preferred_language: str = "en"
    is_verified: bool = False
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class MessageResponse(BaseModel):
    message: str
