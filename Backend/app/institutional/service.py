from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, NotFoundException
from app.institutional.models import School, SchoolDomain
from app.institutional.repository import SchoolDomainRepository, SchoolRepository
from app.institutional.schemas import SchoolResponse


class InstitutionalService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.school_repo = SchoolRepository(session)
        self.domain_repo = SchoolDomainRepository(session)

    async def create_school(self, name: str, code: str, address: str | None, phone: str | None, domains: list[str]) -> SchoolResponse:
        existing = await self.school_repo.find_by_code(code)
        if existing:
            raise ConflictException(message="School with this code already exists")
        school = School(name=name, code=code, address=address, phone=phone)
        self.session.add(school)
        await self.session.flush()
        for d in domains:
            self.session.add(SchoolDomain(school_id=school.id, domain=d))
        await self.session.flush()
        resp = SchoolResponse.model_validate(school)
        resp.domains = domains
        return resp

    async def list_schools(self, active_only: bool = False) -> list[SchoolResponse]:
        schools = await self.school_repo.find_active() if active_only else await self.school_repo.list()
        result = []
        for school in schools:
            doms = await self.domain_repo.find_by_school(school.id)
            resp = SchoolResponse.model_validate(school)
            resp.domains = [d.domain for d in doms]
            result.append(resp)
        return result

    async def get_school(self, school_id: str) -> SchoolResponse:
        school = await self.school_repo.get(school_id)
        if school is None:
            raise NotFoundException(message="School not found")
        doms = await self.domain_repo.find_by_school(school.id)
        resp = SchoolResponse.model_validate(school)
        resp.domains = [d.domain for d in doms]
        return resp

    async def update_school(self, school_id: str, name: str | None, address: str | None, phone: str | None, is_active: bool | None) -> SchoolResponse:
        school = await self.school_repo.get(school_id)
        if school is None:
            raise NotFoundException(message="School not found")
        if name is not None:
            school.name = name
        if address is not None:
            school.address = address
        if phone is not None:
            school.phone = phone
        if is_active is not None:
            school.is_active = is_active
        await self.session.flush()
        return await self.get_school(school_id)

    async def add_domain(self, school_id: str, domain: str, is_primary: bool) -> SchoolResponse:
        school = await self.school_repo.get(school_id)
        if school is None:
            raise NotFoundException(message="School not found")
        existing = await self.domain_repo.find_by_domain(domain)
        if existing:
            raise ConflictException(message="Domain already registered")
        self.session.add(SchoolDomain(school_id=school_id, domain=domain, is_primary=is_primary))
        await self.session.flush()
        return await self.get_school(school_id)
