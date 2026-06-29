from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.common.types import UserRole
from app.parental_controls.models import ParentalControl
from app.parental_controls.repository import ParentalControlRepository
from app.parental_controls.schemas import ParentalControlResponse
from app.users.models import User
from app.users.repository import StudentProfileRepository


class ParentalControlService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = ParentalControlRepository(session)
        self.profile_repo = StudentProfileRepository(session)

    async def get_controls(self, current_user: User, student_id: str) -> ParentalControlResponse:
        if current_user.role not in (UserRole.PARENT, UserRole.ADMIN):
            profile = await self.profile_repo.get_by_user_id(current_user.id)
            if profile is None or profile.id != student_id:
                raise NotFoundException(message="Access denied")
        controls = await self.repo.find_by_student(student_id)
        if controls is None:
            controls = ParentalControl(student_id=student_id)
            self.session.add(controls)
            await self.session.flush()
        return ParentalControlResponse.model_validate(controls)

    async def update_controls(self, current_user: User, student_id: str, data: dict) -> ParentalControlResponse:
        if current_user.role not in (UserRole.PARENT, UserRole.ADMIN):
            raise NotFoundException(message="Access denied")
        controls = await self.repo.find_by_student(student_id)
        if controls is None:
            controls = ParentalControl(student_id=student_id)
            self.session.add(controls)
        for key, value in data.items():
            if value is not None:
                setattr(controls, key, value)
        await self.session.flush()
        await self.session.refresh(controls)
        return ParentalControlResponse.model_validate(controls)
