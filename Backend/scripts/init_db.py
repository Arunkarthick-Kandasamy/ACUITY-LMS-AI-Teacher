"""Initialize the SQLite database by creating all tables defined in models."""

from __future__ import annotations

from sqlalchemy import create_engine

from app.common.base import Base

# Ensure all models are registered
import app.audit.models  # noqa: F401
import app.auth.models  # noqa: F401
import app.content_ingestion.models  # noqa: F401
import app.curriculum.models  # noqa: F401
import app.diagnosis.models  # noqa: F401
import app.enrollment.models  # noqa: F401
import app.evaluation.models  # noqa: F401
import app.knowledge_graph.models  # noqa: F401
import app.mastery.models  # noqa: F401
import app.memory.models  # noqa: F401
import app.reports.models  # noqa: F401
import app.teaching.models  # noqa: F401
import app.users.models  # noqa: F401

SYNC_DATABASE_URL = "sqlite:///./acuity.db"


def main() -> None:
    engine = create_engine(SYNC_DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")
    engine.dispose()


if __name__ == "__main__":
    main()
