"""Initialize database by creating all tables directly via SQLAlchemy metadata.
This bypasses Alembic migrations (which contain PostgreSQL-specific SQL)."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.common.base import Base

# Import ALL models to register them with Base.metadata
import app.analytics.models  # noqa: F401
import app.assessments.models  # noqa: F401
import app.audit.models  # noqa: F401
import app.auth.models  # noqa: F401
import app.content_ingestion.models  # noqa: F401
import app.curriculum.models  # noqa: F401
import app.diagnosis.models  # noqa: F401
import app.enrollment.models  # noqa: F401
import app.evaluation.models  # noqa: F401
import app.gamification.models  # noqa: F401
import app.institutional.models  # noqa: F401
import app.knowledge_graph.models  # noqa: F401
import app.mastery.models  # noqa: F401
import app.memory.models  # noqa: F401
import app.messaging.models  # noqa: F401
import app.moderation.models  # noqa: F401
import app.pacing.models  # noqa: F401
import app.parental_controls.models  # noqa: F401
import app.payments.models  # noqa: F401
import app.progress.models  # noqa: F401
import app.reports.models  # noqa: F401
import app.teacher.models  # noqa: F401
import app.teaching.models  # noqa: F401
import app.users.models  # noqa: F401

from app.config import settings


async def init():
    engine = create_async_engine(settings.database_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    print("All tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init())
