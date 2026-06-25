from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Ensure all models are registered with the Base metadata
import app.audit.models  # noqa: F401
import app.content_ingestion.models  # noqa: F401
import app.curriculum.models  # noqa: F401
import app.diagnosis.models  # noqa: F401
import app.enrollment.models  # noqa: F401
import app.knowledge_graph.models  # noqa: F401
import app.mastery.models  # noqa: F401
import app.memory.models  # noqa: F401
import app.evaluation.models  # noqa: F401
import app.reports.models  # noqa: F401
import app.teaching.models  # noqa: F401
import app.analytics.models  # noqa: F401
import app.assessments.models  # noqa: F401
import app.users.models  # noqa: F401
from app.config import settings

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    global engine, async_session_factory

    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def close_db() -> None:
    global engine

    if engine is not None:
        await engine.dispose()
        engine = None


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_health() -> bool:
    if engine is None:
        return False

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

