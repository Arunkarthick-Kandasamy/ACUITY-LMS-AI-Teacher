from __future__ import annotations

import hashlib
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
)
from app.auth.repository import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
)
from app.common.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.logging import get_logger
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.security.password import hash_password, verify_password
from app.users.models import StudentProfile, User
from app.users.repository import UserRepository

logger = get_logger(__name__)

VERIFICATION_TOKEN_EXPIRE_HOURS = 24


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.refresh_token_repo = RefreshTokenRepository(session)
        self.reset_token_repo = PasswordResetTokenRepository(session)
        self.verification_token_repo = EmailVerificationTokenRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        full_name: str,
        role: UserRole,
        date_of_birth: date | None = None,
        country: str | None = None,
        preferred_language: str = "en",
    ) -> tuple[str, str, User]:
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise ConflictException(
                message="A user with this email already exists", code="EMAIL_EXISTS"
            )

        password_hash = hash_password(password)
        user = await self.user_repo.create(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
            date_of_birth=date_of_birth,
            country=country,
            preferred_language=preferred_language,
        )

        if role == UserRole.STUDENT:
            student_profile = StudentProfile(user_id=user.id)
            self.session.add(student_profile)
            await self.session.flush()

        jti = str(uuid.uuid4())
        access_token = create_access_token(
            subject=str(user.id), email=user.email, role=user.role.value
        )
        refresh_token = create_refresh_token(subject=str(user.id), jti=jti)

        now = datetime.now(timezone.utc)
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(refresh_token),
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        self.session.add(refresh_token_record)

        raw_vtoken = str(uuid.uuid4())
        vtoken_hash = _hash_token(raw_vtoken)
        verification = EmailVerificationToken(
            user_id=user.id,
            token_hash=vtoken_hash,
            expires_at=now + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS),
        )
        self.session.add(verification)

        await self.session.flush()

        verification_link = (
            f"{settings.api_prefix}/auth/verify-email?token={raw_vtoken}"
            if settings.is_development
            else f"https://app.acuitylms.com/verify-email?token={raw_vtoken}"
        )
        logger.info(
            "User %s registered (role=%s). Verification: %s",
            user.id,
            role.value,
            verification_link,
        )

        return access_token, refresh_token, user

    async def verify_email(self, raw_token: str) -> None:
        token_hash = _hash_token(raw_token)
        stored = await self.verification_token_repo.get_valid_by_hash(token_hash)
        if stored is None:
            raise UnauthorizedException(
                message="Invalid or expired verification token",
                code="INVALID_VERIFICATION_TOKEN",
            )

        user = await self.user_repo.get(stored.user_id)
        if user is None:
            raise NotFoundException(message="User not found", code="USER_NOT_FOUND")

        stored.used_at = datetime.now(timezone.utc)
        user.is_verified = True
        await self.session.flush()

    async def resend_verification(self, email: str) -> str:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            msg = "If the email exists, a verification link has been sent"
            logger.info("Verification resend requested for unknown email: %s", email)
            return msg

        if user.is_verified:
            msg = "Email is already verified"
            logger.info("Verification resend requested for already-verified user %s", user.id)
            return msg

        await self.verification_token_repo.revoke_all_for_user(user.id)

        raw_token = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        verification = EmailVerificationToken(
            user_id=user.id,
            token_hash=_hash_token(raw_token),
            expires_at=now + timedelta(hours=VERIFICATION_TOKEN_EXPIRE_HOURS),
        )
        self.session.add(verification)
        await self.session.flush()

        verification_link = (
            f"{settings.api_prefix}/auth/verify-email?token={raw_token}"
            if settings.is_development
            else f"https://app.acuitylms.com/verify-email?token={raw_token}"
        )
        logger.info(
            "New verification token for user %s: %s",
            user.id,
            verification_link,
        )

        return "If the email exists, a verification link has been sent"

    async def login(self, email: str, password: str) -> tuple[str, str, User]:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            raise UnauthorizedException(
                message="Invalid email or password", code="INVALID_CREDENTIALS"
            )

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException(
                message="Invalid email or password", code="INVALID_CREDENTIALS"
            )

        if not user.is_active:
            raise ForbiddenException(
                message="Account is deactivated. Contact an administrator.",
                code="ACCOUNT_INACTIVE",
            )

        jti = str(uuid.uuid4())
        access_token = create_access_token(
            subject=str(user.id), email=user.email, role=user.role.value
        )
        refresh_token = create_refresh_token(subject=str(user.id), jti=jti)

        now = datetime.now(timezone.utc)
        token_hash = _hash_token(refresh_token)
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        self.session.add(refresh_token_record)
        await self.session.flush()

        return access_token, refresh_token, user

    async def refresh(self, refresh_token_str: str) -> tuple[str, str]:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise UnauthorizedException(
                message="Invalid token type", code="INVALID_TOKEN"
            )

        token_hash = _hash_token(refresh_token_str)
        stored = await self.refresh_token_repo.get_valid_by_hash(token_hash)
        if stored is None:
            raise UnauthorizedException(
                message="Refresh token is invalid or has been revoked",
                code="INVALID_REFRESH_TOKEN",
            )

        user = await self.user_repo.get(stored.user_id)
        if user is None:
            raise UnauthorizedException(message="User not found", code="USER_NOT_FOUND")

        stored.revoked_at = datetime.now(timezone.utc)

        jti = str(uuid.uuid4())
        new_access_token = create_access_token(
            subject=str(user.id), email=user.email, role=user.role.value
        )
        new_refresh_token = create_refresh_token(subject=str(user.id), jti=jti)

        now = datetime.now(timezone.utc)
        new_token_record = RefreshToken(
            user_id=user.id,
            token_hash=_hash_token(new_refresh_token),
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )
        self.session.add(new_token_record)
        await self.session.flush()

        return new_access_token, new_refresh_token

    async def logout(self, user_id: str) -> None:
        await self.refresh_token_repo.revoke_all_for_user(user_id)

    async def forgot_password(self, email: str) -> str | None:
        user = await self.user_repo.get_by_email(email)
        if user is None:
            return None

        raw_token = str(uuid.uuid4())
        token_hash = _hash_token(raw_token)
        now = datetime.now(timezone.utc)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(hours=settings.password_reset_token_expire_hours),
        )
        self.session.add(reset_token)
        await self.session.flush()

        logger.info(
            "Password reset token generated for user %s (dev token: %s)",
            user.id,
            raw_token,
        )
        return raw_token

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        token_hash = _hash_token(raw_token)
        stored = await self.reset_token_repo.get_valid_by_hash(token_hash)
        if stored is None:
            raise UnauthorizedException(
                message="Invalid or expired reset token", code="INVALID_RESET_TOKEN"
            )

        user = await self.user_repo.get(stored.user_id)
        if user is None:
            raise UnauthorizedException(message="User not found", code="USER_NOT_FOUND")

        stored.used_at = datetime.now(timezone.utc)
        user.password_hash = hash_password(new_password)

        await self.refresh_token_repo.revoke_all_for_user(user.id)
        await self.session.flush()

    async def export_user_data(self, user_id: str) -> dict:
        from app.users.repository import StudentProfileRepository
        user = await self.user_repo.get(user_id)
        if user is None:
            raise NotFoundException(message="User not found")
        profile_repo = StudentProfileRepository(self.session)
        profile = await profile_repo.get_by_user_id(user_id)
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "date_of_birth": str(user.date_of_birth) if user.date_of_birth else None,
                "country": user.country,
                "preferred_language": user.preferred_language,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "profile": {
                "grade_level": profile.grade_level if profile else None,
                "current_streak_days": profile.current_streak_days if profile else 0,
            } if profile else None,
        }

    async def delete_account(self, user_id: str) -> None:
        user = await self.user_repo.get(user_id)
        if user is None:
            raise NotFoundException(message="User not found")
        user.is_active = False
        user.email = f"deleted_{user_id}@deleted.acuity"
        await self.refresh_token_repo.revoke_all_for_user(user.id)
        await self.session.flush()
