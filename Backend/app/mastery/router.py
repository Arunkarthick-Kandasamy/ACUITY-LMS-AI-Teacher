from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.mastery.schemas import MasteryResponse, MasterySummaryResponse
from app.mastery.service import MasteryService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Mastery"])


@router.get("/mastery")
async def get_mastery_overview(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = MasteryService(session)
    records = await service.get_overview(user_id=current_user.id)
    items = []
    for r in records:
        concept_title = r.concept.title if hasattr(r, "concept") and r.concept else None
        items.append(
            MasteryResponse(
                record_id=r.id,
                student_id=r.student_id,
                concept_id=r.concept_id,
                concept_title=concept_title,
                mastery_level=r.mastery_level,
                total_attempts=r.total_attempts,
                consecutive_correct=r.consecutive_correct,
                last_attempted_at=r.last_attempted_at,
            ).model_dump(mode="json")
        )
    return success_response(items)


@router.get("/mastery/concepts/{concept_id}")
async def get_mastery_by_concept(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = MasteryService(session)
    record = await service.get_by_concept(
        concept_id=concept_id, user_id=current_user.id
    )
    if record is None:
        return success_response(
            MasteryResponse(
                record_id="",
                student_id="",
                concept_id=concept_id,
                mastery_level=0.0,
                total_attempts=0,
                consecutive_correct=0,
            ).model_dump(mode="json")
        )
    concept_title = record.concept.title if hasattr(record, "concept") and record.concept else None
    return success_response(
        MasteryResponse(
            record_id=record.id,
            student_id=record.student_id,
            concept_id=record.concept_id,
            concept_title=concept_title,
            mastery_level=record.mastery_level,
            total_attempts=record.total_attempts,
            consecutive_correct=record.consecutive_correct,
            last_attempted_at=record.last_attempted_at,
        ).model_dump(mode="json")
    )


@router.get("/mastery/courses/{course_id}")
async def get_course_mastery_summary(
    course_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = MasteryService(session)
    records = await service.get_course_summary(
        course_id=course_id, user_id=current_user.id
    )
    items = []
    total = 0.0
    for r in records:
        concept_title = r.concept.title if hasattr(r, "concept") and r.concept else None
        items.append(
            MasteryResponse(
                record_id=r.id,
                student_id=r.student_id,
                concept_id=r.concept_id,
                concept_title=concept_title,
                mastery_level=r.mastery_level,
                total_attempts=r.total_attempts,
                consecutive_correct=r.consecutive_correct,
                last_attempted_at=r.last_attempted_at,
            ).model_dump(mode="json")
        )
        total += r.mastery_level

    count = len(items)
    return success_response(
        MasterySummaryResponse(
            course_id=course_id,
            total_concepts=count,
            mastered_concepts=sum(1 for r in records if r.mastery_level >= 0.8),
            average_mastery=round(total / count, 4) if count > 0 else 0.0,
            concepts=items,
        ).model_dump(mode="json")
    )
