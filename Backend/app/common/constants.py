from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------

DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# ---------------------------------------------------------------------------
# Rate limiting (future use)
# ---------------------------------------------------------------------------

DEFAULT_RATE_LIMIT: int = 60
DEFAULT_RATE_LIMIT_WINDOW_SECONDS: int = 60
LOGIN_RATE_LIMIT: int = 5
LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 60

# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

SESSION_IDLE_TIMEOUT_MINUTES: int = 30
MAX_CONCURRENT_SESSIONS: int = 1

# ---------------------------------------------------------------------------
# Mastery
# ---------------------------------------------------------------------------

MASTERY_THRESHOLD: float = 0.7
MASTERY_WINDOW_SIZE: int = 10

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DB_POOL_SIZE: int = int(os.environ.get("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW: int = int(os.environ.get("DB_MAX_OVERFLOW", "10"))
DB_POOL_RECYCLE_SECONDS: int = 3600

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT: str = os.path.dirname(BASE_DIR)
