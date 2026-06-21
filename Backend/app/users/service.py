from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException
from app.common.types import UserRole
from app.security.password import hash_password
from app.users.models import StudentProfile, User
from app.users.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)

    async def create_user(
        self, email: str, password: str, full_name: str, role: UserRole
    ) -> User:
        existing = await self.repo.get_by_email(email)
        if existing is not None:
            raise ConflictException(
                message="A user with this email already exists", code="EMAIL_EXISTS"
            )

        password_hash = hash_password(password)
        user = await self.repo.create(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
        )

        if role == UserRole.STUDENT:
            profile = StudentProfile(user_id=user.id)
            self.session.add(profile)
            await self.session.flush()

        return user

    async def get_user(self, user_id: str) -> User | None:
        return await self.repo.get(user_id)

    async def update_user(self, user_id: str, **kwargs) -> User | None:
        return await self.repo.update(user_id, **kwargs)
