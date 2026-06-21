from __future__ import annotations

from typing import Any


def success_response(data: Any) -> dict:
    return {"status": "success", "data": data}


def paginated_response(
    data: list[Any], total: int, page: int, per_page: int
) -> dict:
    return {
        "status": "success",
        "data": data,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
    }
