from __future__ import annotations

from typing import Any

from pydantic import BaseModel, EmailStr


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    cc: list[EmailStr] | None = None
    bcc: list[EmailStr] | None = None
    attachments: list[dict[str, Any]] | None = None


class EmailResponse(BaseModel):
    success: bool
    message: str
    recipient: str
    subject: str
