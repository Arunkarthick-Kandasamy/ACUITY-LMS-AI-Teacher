from __future__ import annotations

import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.evaluation.router import router as ai_evaluation_router
from app.ai.router import router as ai_router
from app.analytics.router import router as analytics_router
from app.assessments.router import router as assessments_router
from app.auth.router import router as auth_router
from app.common.context import request_id_var
from app.common.exceptions import AppException
from app.config import settings
from app.content_ingestion.router import router as content_ingestion_router
from app.course_admin.router import router as course_admin_router
from app.curriculum.router import router as curriculum_router
from app.enrollment.router import router as enrollment_router
from app.gamification.router import router as gamification_router
from app.health.router import router as health_router
from app.infrastructure.database import close_db, init_db
from app.infrastructure.logging import get_logger, setup_logging
from app.institutional.router import router as institutional_router
from app.knowledge_graph.router import router as knowledge_graph_router
from app.mastery.router import router as mastery_router
from app.messaging.router import router as messaging_router
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.moderation.router import router as moderation_router
from app.notifications.router import router as notifications_router
from app.pacing.router import router as pacing_router
from app.parent_dashboard.router import router as parent_dashboard_router
from app.parental_controls.router import router as parental_controls_router
from app.payments.router import router as payments_router
from app.progress.router import router as progress_router
from app.reports.router import router as reports_router
from app.teacher.router import router as teacher_router
from app.teaching_sessions.router import router as teaching_sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Starting application", extra={"version": settings.app_version})
    await init_db()
    logger.info("Database connection established")
    yield
    await close_db()
    logger.info("Application stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    token = request_id_var.set(request_id)

    start_time = time.time()

    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details or [],
            },
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = get_logger(__name__)
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": [],
            },
        },
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(curriculum_router)
app.include_router(knowledge_graph_router)
app.include_router(enrollment_router)
app.include_router(progress_router)
app.include_router(mastery_router)
app.include_router(pacing_router)
app.include_router(teaching_sessions_router)
app.include_router(ai_router)
app.include_router(ai_evaluation_router)
app.include_router(parent_dashboard_router)
app.include_router(content_ingestion_router)
app.include_router(course_admin_router)
app.include_router(reports_router)
app.include_router(assessments_router)
app.include_router(analytics_router)
app.include_router(teacher_router)
app.include_router(notifications_router)
app.include_router(parental_controls_router)
app.include_router(messaging_router)
app.include_router(moderation_router)
app.include_router(institutional_router)
app.include_router(gamification_router)
app.include_router(payments_router)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


@app.get("/")
async def root() -> dict:
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
