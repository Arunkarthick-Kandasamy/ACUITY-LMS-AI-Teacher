from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.auth.dependencies import require_roles
from app.common.types import UserRole
from app.config import settings
from app.users.models import User

from .schemas import EmailRequest, EmailResponse
from .service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{settings.api_prefix}/notifications",
    tags=["Notifications"],
)


@router.post("/email", response_model=EmailResponse)
async def send_email(
    body: EmailRequest,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> EmailResponse:
    service = EmailService()
    success = await service.send_email(
        to=body.to,
        subject=body.subject,
        body=body.body,
    )
    return EmailResponse(
        success=success,
        message="Email sent successfully" if success else "Failed to send email",
        recipient=body.to,
        subject=body.subject,
    )
