from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.institutional.models import School, SchoolDomain


class SchoolRepository(Repository[School]):
    def __init__(self, session) -> None:
        super().__init__(School, session)

    async def find_by_code(self, code: str) -> School | None:
        stmt = select(School).where(School.code == code)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_active(self) -> list[School]:
        stmt = select(School).where(School.is_active == True).order_by(School.name)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class SchoolDomainRepository(Repository[SchoolDomain]):
    def __init__(self, session) -> None:
        super().__init__(SchoolDomain, session)

    async def find_by_domain(self, domain: str) -> SchoolDomain | None:
        stmt = select(SchoolDomain).where(SchoolDomain.domain == domain)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_by_school(self, school_id: str) -> list[SchoolDomain]:
        stmt = select(SchoolDomain).where(SchoolDomain.school_id == school_id)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
