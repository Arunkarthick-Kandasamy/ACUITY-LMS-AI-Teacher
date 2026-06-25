from __future__ import annotations

import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self) -> None:
        self.from_address = "noreply@acuitylms.com"

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        logger.info(
            "Email stub: to=%s, subject=%s, body=%s",
            to,
            subject,
            body[:100] if body else "",
        )
        return True

    async def send_welcome_email(self, user_email: str) -> bool:
        subject = "Welcome to Acuity LMS"
        body = (
            f"Hello,\n\n"
            f"Welcome to Acuity LMS! Your account has been created successfully.\n\n"
            f"Get started by exploring your courses and beginning your learning journey.\n\n"
            f"Best regards,\nThe Acuity LMS Team"
        )
        return await self.send_email(to=user_email, subject=subject, body=body)

    async def send_assessment_result(self, student_email: str, score: float) -> bool:
        subject = "Your Assessment Result"
        body = (
            f"Hello,\n\n"
            f"Your recent assessment has been graded. Your score: {score:.1%}\n\n"
            f"Log in to Acuity LMS to review detailed feedback and continue learning.\n\n"
            f"Best regards,\nThe Acuity LMS Team"
        )
        return await self.send_email(to=student_email, subject=subject, body=body)
