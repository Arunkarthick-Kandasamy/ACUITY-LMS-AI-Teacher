from __future__ import annotations

from sqlalchemy import JSON, TypeDecorator


class JSONB(JSON):
    """JSONB alias that works with both PostgreSQL and SQLite."""


class ArrayAsJson(TypeDecorator):
    """Stores a Python list as a JSON string — works with any database."""

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        return value if value is not None else []
