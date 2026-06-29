from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload

from app.common.repository import Repository
from app.diagnosis.models import Misconception
from app.teaching.models import TeachingSession
from app.users.models import LinkAuditLog, ParentStudentLink, StudentLinkingCode


class StudentLinkingCodeRepository(Repository[StudentLinkingCode]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(StudentLinkingCode, session)

    async def find_valid_by_code(self, code: str) -> StudentLinkingCode | None:
        now = datetime.now(timezone.utc)
        stmt = select(StudentLinkingCode).where(
            StudentLinkingCode.code == code,
            StudentLinkingCode.expires_at > now,
            StudentLinkingCode.used_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_recent_by_student(self, student_id: str) -> StudentLinkingCode | None:
        now = datetime.now(timezone.utc)
        stmt = (
            select(StudentLinkingCode)
            .where(
                StudentLinkingCode.student_id == student_id,
                StudentLinkingCode.expires_at > now,
                StudentLinkingCode.used_at.is_(None),
            )
            .order_by(StudentLinkingCode.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def increment_failed_attempts(self, code_id: str) -> None:
        stmt = (
            update(StudentLinkingCode)
            .where(StudentLinkingCode.id == code_id)
            .values(failed_attempts=StudentLinkingCode.failed_attempts + 1)
        )
        await self.session.execute(stmt)


class ParentStudentLinkRepository(Repository[ParentStudentLink]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(ParentStudentLink, session)

    async def find_by_parent(self, parent_id: str) -> list[ParentStudentLink]:
        stmt = (
            select(ParentStudentLink)
            .where(
                ParentStudentLink.parent_id == parent_id,
                ParentStudentLink.status == "active",
            )
            .options(joinedload(ParentStudentLink.student))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_by_parent_and_student(
        self, parent_id: str, student_id: str
    ) -> ParentStudentLink | None:
        stmt = select(ParentStudentLink).where(
            ParentStudentLink.parent_id == parent_id,
            ParentStudentLink.student_id == student_id,
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find_active_by_parent_and_student(
        self, parent_id: str, student_id: str
    ) -> ParentStudentLink | None:
        stmt = select(ParentStudentLink).where(
            ParentStudentLink.parent_id == parent_id,
            ParentStudentLink.student_id == student_id,
            ParentStudentLink.status == "active",
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def count_by_student(self, student_id: str, status: str | None = None) -> int:
        conditions = [ParentStudentLink.student_id == student_id]
        if status:
            conditions.append(ParentStudentLink.status == status)
        stmt = select(func.count(ParentStudentLink.id)).where(*conditions)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def find_pending_by_student(self, student_id: str) -> list[ParentStudentLink]:
        stmt = (
            select(ParentStudentLink)
            .where(
                ParentStudentLink.student_id == student_id,
                ParentStudentLink.status == "pending",
            )
            .options(joinedload(ParentStudentLink.parent))
            .order_by(ParentStudentLink.requested_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def approve(self, link_id: str) -> ParentStudentLink | None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(ParentStudentLink)
            .where(ParentStudentLink.id == link_id, ParentStudentLink.status == "pending")
            .values(status="active", approved_at=now)
        )
        await self.session.execute(stmt)
        return await self.get(link_id)

    async def reject(self, link_id: str) -> ParentStudentLink | None:
        stmt = (
            update(ParentStudentLink)
            .where(ParentStudentLink.id == link_id, ParentStudentLink.status == "pending")
            .values(status="rejected")
        )
        await self.session.execute(stmt)
        return await self.get(link_id)


class LinkAuditLogRepository(Repository[LinkAuditLog]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(LinkAuditLog, session)

    async def log(
        self,
        action: str,
        actor_id: str | None = None,
        student_id: str | None = None,
        parent_id: str | None = None,
        parent_email: str | None = None,
        details: str | None = None,
    ) -> LinkAuditLog:
        entry = LinkAuditLog(
            action=action,
            actor_id=actor_id,
            student_id=student_id,
            parent_id=parent_id,
            parent_email=parent_email,
            details=details,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def find_by_student(self, student_id: str) -> list[LinkAuditLog]:
        stmt = (
            select(LinkAuditLog)
            .where(LinkAuditLog.student_id == student_id)
            .order_by(LinkAuditLog.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class MisconceptionRepository(Repository[Misconception]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(Misconception, session)

    async def find_by_student(self, student_id: str) -> list[Misconception]:
        stmt = (
            select(Misconception)
            .where(Misconception.student_id == student_id)
            .order_by(Misconception.detected_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_active_by_student(self, student_id: str) -> list[Misconception]:
        stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == student_id,
                Misconception.is_resolved == False,  # noqa: E712
            )
            .order_by(Misconception.detected_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_knowledge_gaps(self, student_id: str) -> list[Misconception]:
        stmt = (
            select(Misconception)
            .where(
                Misconception.student_id == student_id,
                Misconception.category == "conceptual",
                Misconception.is_resolved == False,  # noqa: E712
            )
            .order_by(Misconception.detected_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())


class ParentTeachingSessionRepository(Repository[TeachingSession]):
    def __init__(self, session) -> None:  # noqa: ANN001
        super().__init__(TeachingSession, session)

    async def find_by_student(
        self, student_id: str, offset: int = 0, limit: int = 20
    ) -> tuple[list[TeachingSession], int]:
        return await self.find(
            TeachingSession.student_id == student_id,
            offset=offset,
            limit=limit,
            order_by=TeachingSession.last_activity_at.desc(),
        )

    async def find_recent_by_student(
        self, student_id: str, days: int = 7
    ) -> list[TeachingSession]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(TeachingSession)
            .where(
                TeachingSession.student_id == student_id,
                TeachingSession.last_activity_at >= cutoff,
            )
            .order_by(TeachingSession.last_activity_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def count_by_student(self, student_id: str) -> int:
        return await self.count(TeachingSession.student_id == student_id)
