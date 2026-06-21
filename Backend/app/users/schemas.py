from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.common.types import UserRole


class UserResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: str | None = None
    is_active: bool | None = None
