from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.auth.models import EmailVerificationToken, PasswordResetToken, RefreshToken
from app.common.repository import Repository


class RefreshTokenRepository(Repository[RefreshToken]):
    def __init__(self, session):  # noqa: ANN001
        super().__init__(RefreshToken, session)

    async def get_valid_by_hash(self, token_hash: str) -> RefreshToken | None:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > now,
            RefreshToken.revoked_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def revoke_all_for_user(self, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None)
        )
        result = await self.session.execute(stmt)
        tokens = result.unique().scalars().all()
        for token in tokens:
            token.revoked_at = now
        await self.session.flush()


class PasswordResetTokenRepository(Repository[PasswordResetToken]):
    def __init__(self, session):  # noqa: ANN001
        super().__init__(PasswordResetToken, session)

    async def get_valid_by_hash(self, token_hash: str) -> PasswordResetToken | None:
        now = datetime.now(timezone.utc)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.expires_at > now,
            PasswordResetToken.used_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def mark_used(self, token_id: str) -> None:
        token = await self.get(token_id)
        if token is not None:
            token.used_at = datetime.now(timezone.utc)
            await self.session.flush()


class EmailVerificationTokenRepository(Repository[EmailVerificationToken]):
    def __init__(self, session):  # noqa: ANN001
        super().__init__(EmailVerificationToken, session)

    async def get_valid_by_hash(self, token_hash: str) -> EmailVerificationToken | None:
        now = datetime.now(timezone.utc)
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.expires_at > now,
            EmailVerificationToken.used_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def mark_used(self, token_id: str) -> None:
        token = await self.get(token_id)
        if token is not None:
            token.used_at = datetime.now(timezone.utc)
            await self.session.flush()

    async def revoke_all_for_user(self, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user_id,
            EmailVerificationToken.used_at.is_(None),
        )
        result = await self.session.execute(stmt)
        tokens = result.unique().scalars().all()
        for token in tokens:
            token.used_at = now
        await self.session.flush()
