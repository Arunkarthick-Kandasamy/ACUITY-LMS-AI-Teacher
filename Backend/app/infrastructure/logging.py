from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger

from app.common.context import request_id_var
from app.config import settings


class RequestIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get() or "-"
        return True


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)

    if settings.is_development:
        fmt = (
            "%(asctime)s | %(levelname)-8s | %(request_id)s | "
            "%(name)s:%(funcName)s:%(lineno)d | %(message)s"
        )
        handler.setFormatter(logging.Formatter(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    else:
        fmt = (
            "%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d %(request_id)s %(message)s"
        )
        handler.setFormatter(jsonlogger.JsonFormatter(fmt=fmt, timestamp=True))

    handler.addFilter(RequestIDFilter())

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        handlers=[handler],
        force=True,
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
