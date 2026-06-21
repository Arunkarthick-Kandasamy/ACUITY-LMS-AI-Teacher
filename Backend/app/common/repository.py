from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get(self, id: str) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def find(
        self,
        *conditions: Any,
        offset: int = 0,
        limit: int = 100,
        order_by: Any | None = None,
    ) -> tuple[Sequence[ModelT], int]:
        stmt = select(self.model).where(*conditions)
        count_stmt = select(func.count()).select_from(self.model).where(*conditions)
        total = await self.session.scalar(count_stmt)

        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all(), total or 0

    async def update(self, id: str, **kwargs: Any) -> ModelT | None:
        instance = await self.get(id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: str) -> bool:
        instance = await self.get(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, *conditions: Any) -> bool:
        stmt = select(self.model).where(*conditions)
        result = await self.session.execute(stmt)
        return result.unique().first() is not None

    async def count(self, *conditions: Any) -> int:
        stmt = select(func.count()).select_from(self.model).where(*conditions)
        return await self.session.scalar(stmt) or 0
