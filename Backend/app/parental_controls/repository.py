from __future__ import annotations

from sqlalchemy import select

from app.common.repository import Repository
from app.parental_controls.models import ParentalControl, SleepSchedule


class ParentalControlRepository(Repository[ParentalControl]):
    def __init__(self, session) -> None:
        super().__init__(ParentalControl, session)

    async def find_by_student(self, student_id: str) -> ParentalControl | None:
        stmt = select(ParentalControl).where(ParentalControl.student_id == student_id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class SleepScheduleRepository(Repository[SleepSchedule]):
    def __init__(self, session) -> None:
        super().__init__(SleepSchedule, session)

    async def find_by_student(self, student_id: str) -> list[SleepSchedule]:
        stmt = select(SleepSchedule).where(SleepSchedule.student_id == student_id).order_by(SleepSchedule.day_of_week)
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())
