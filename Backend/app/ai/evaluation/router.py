from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import success_response
from app.config import settings
from app.evaluation.models import GraphTrace, TeacherMetricsSnapshot
from app.infrastructure.database import get_session
from app.users.models import User

from .metrics import compute_metrics
from .reports import summarize_trace_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=f"{settings.api_prefix}/ai/evaluation",
    tags=["AI Evaluation"],
)


@router.get("/metrics")
async def get_evaluation_metrics(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    try:
        stmt = (
            select(TeacherMetricsSnapshot)
            .order_by(desc(TeacherMetricsSnapshot.created_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        snapshot = result.unique().scalar_one_or_none()

        if snapshot:
            metrics = {
                "total_sessions": snapshot.total_sessions,
                "concepts_taught": snapshot.concepts_taught,
                "concept_mastery_rate": snapshot.concept_mastery_rate,
                "remediation_rate": snapshot.remediation_rate,
                "misconception_detection_rate": snapshot.misconception_detection_rate,
                "prerequisite_routing_frequency": snapshot.prerequisite_routing_frequency,
                "session_completion_rate": snapshot.session_completion_rate,
                "avg_mastery_gain": snapshot.avg_mastery_gain,
                "avg_execution_duration_ms": snapshot.avg_execution_duration_ms,
                "total_model_calls": snapshot.total_model_calls,
                "snapshot_label": snapshot.snapshot_label,
                "snapshot_time": snapshot.created_at.isoformat() if snapshot.created_at else None,
                "breakdown": snapshot.breakdown or {},
            }
        else:
            traces_stmt = select(GraphTrace).order_by(desc(GraphTrace.created_at)).limit(100)
            traces_result = await db.execute(traces_stmt)
            traces = traces_result.unique().scalars().all()
            metrics = compute_metrics(traces)
    except Exception:
        logger.exception("Failed to compute evaluation metrics")
        raise HTTPException(status_code=500, detail="Failed to compute evaluation metrics")

    return success_response(metrics)


@router.get("/traces")
async def get_evaluation_traces(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    scenario: str | None = Query(default=None),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    try:
        stmt = select(GraphTrace).order_by(desc(GraphTrace.created_at))

        if scenario:
            stmt = stmt.where(GraphTrace.scenario_label == scenario)

        count_stmt = select(GraphTrace).order_by(desc(GraphTrace.created_at))
        if scenario:
            count_stmt = count_stmt.where(GraphTrace.scenario_label == scenario)

        count_result = await db.execute(count_stmt)
        total = len(count_result.unique().scalars().all())

        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        records = result.unique().scalars().all()

        traces = [summarize_trace_db(r) for r in records]
    except Exception:
        logger.exception("Failed to fetch evaluation traces")
        raise HTTPException(status_code=500, detail="Failed to fetch evaluation traces")

    return {
        "status": "success",
        "data": traces,
        "meta": {
            "total": total,
            "offset": offset,
            "limit": limit,
        },
    }


@router.get("/scenarios")
async def list_scenarios(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    try:
        from .datasets import SCENARIOS

        scenarios = [
            {
                "label": s.label,
                "concept_title": s.concept_title,
                "expected_action": s.expected_action,
                "expected_nodes": s.expected_nodes,
                "expected_mastery_range": list(s.expected_mastery_range),
            }
            for s in SCENARIOS
        ]
    except Exception:
        logger.exception("Failed to list scenarios")
        raise HTTPException(status_code=500, detail="Failed to list scenarios")

    return success_response(scenarios)
