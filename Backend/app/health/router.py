from fastapi import APIRouter

from app.config import settings
from app.infrastructure.database import check_db_health

router = APIRouter(tags=["health"])

@router.get("/api/v1/health")
async def health_check() -> dict:
    db_healthy = await check_db_health()

    components = {
        "database": "connected" if db_healthy else "disconnected",
    }

    all_healthy = all(v == "connected" for v in components.values())

    return {
        "status": "success",
        "data": {
            "status": "ok" if all_healthy else "degraded",
            "version": settings.app_version,
            "components": components,
        },
    }
