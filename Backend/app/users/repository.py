from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.users.models import StudentProfile, User


class UserRepository(Repository[User]):
    def __init__(self, session):  # noqa: ANN001
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class StudentProfileRepository(Repository[StudentProfile]):
    def __init__(self, session):  # noqa: ANN001
        super().__init__(StudentProfile, session)

    async def get_by_user_id(self, user_id: str) -> StudentProfile | None:
        stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
