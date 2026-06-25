from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.assessments.schemas import (
    AssessmentCreate,
    AssessmentDetail,
    AssessmentResponse,
    AssessmentUpdate,
    AttemptHistoryItem,
    AttemptResultResponse,
    AttemptStartResponse,
    QuestionAnswer,
    QuestionBankCreate,
    QuestionBankResponse,
    QuestionCreate,
    QuestionPublic,
    QuestionResponse,
    QuestionUpdate,
    SubmitRequest,
    SubmitResponse,
)
from app.assessments.service import AssessmentService
from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import paginated_response, success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}", tags=["Assessments"])


# ------------------------------------------------------------------
# Admin Assessment CRUD
# ------------------------------------------------------------------

@router.post("/assessments", status_code=201)
async def create_assessment(
    body: AssessmentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    assessment = await service.create_assessment(
        user_id=current_user.id, **body.model_dump()
    )
    return success_response(
        AssessmentResponse(
            id=assessment.id,
            title=assessment.title,
            description=assessment.description,
            lesson_id=assessment.lesson_id,
            module_id=assessment.module_id,
            course_id=assessment.course_id,
            assessment_type=assessment.assessment_type.value,
            passing_score=assessment.passing_score,
            time_limit=assessment.time_limit,
            max_attempts=assessment.max_attempts,
            is_published=assessment.is_published,
            created_by=assessment.created_by,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        ).model_dump(mode="json")
    )


@router.put("/assessments/{assessment_id}")
async def update_assessment(
    assessment_id: str,
    body: AssessmentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    assessment = await service.update_assessment(
        assessment_id, **{k: v for k, v in body.model_dump().items() if v is not None}
    )
    return success_response(
        AssessmentResponse(
            id=assessment.id,
            title=assessment.title,
            description=assessment.description,
            lesson_id=assessment.lesson_id,
            module_id=assessment.module_id,
            course_id=assessment.course_id,
            assessment_type=assessment.assessment_type.value,
            passing_score=assessment.passing_score,
            time_limit=assessment.time_limit,
            max_attempts=assessment.max_attempts,
            is_published=assessment.is_published,
            created_by=assessment.created_by,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        ).model_dump(mode="json")
    )


@router.delete("/assessments/{assessment_id}", status_code=204)
async def delete_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    service = AssessmentService(session)
    await service.delete_assessment(assessment_id)


@router.get("/assessments")
async def get_assessments(
    course_id: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    if current_user.role == UserRole.ADMIN:
        assessments = (
            await service.get_assessments_by_course(course_id)
            if course_id
            else await service.get_all_assessments()
        )
    else:
        assessments = await service.get_available_assessments(current_user.id)

    items = []
    for a in assessments:
        questions = await service.get_questions(a.id)
        items.append(
            AssessmentResponse(
                id=a.id,
                title=a.title,
                description=a.description,
                lesson_id=a.lesson_id,
                module_id=a.module_id,
                course_id=a.course_id,
                assessment_type=a.assessment_type.value,
                passing_score=a.passing_score,
                time_limit=a.time_limit,
                max_attempts=a.max_attempts,
                is_published=a.is_published,
                created_by=a.created_by,
                question_count=len(questions),
                created_at=a.created_at,
                updated_at=a.updated_at,
            ).model_dump(mode="json")
        )
    return success_response(items)


# ------------------------------------------------------------------
# Admin Question CRUD
# ------------------------------------------------------------------

@router.post("/assessments/{assessment_id}/questions", status_code=201)
async def create_question(
    assessment_id: str,
    body: QuestionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    question = await service.create_question(
        assessment_id=assessment_id, **body.model_dump(exclude={"assessment_id"})
    )
    return success_response(
        QuestionResponse(
            id=question.id,
            assessment_id=question.assessment_id,
            question_type=question.question_type.value,
            prompt=question.prompt,
            options=question.options,
            difficulty=question.difficulty,
            marks=question.marks,
            explanation=question.explanation,
            order_index=question.order_index,
            created_at=question.created_at,
        ).model_dump(mode="json")
    )


@router.put("/questions/{question_id}")
async def update_question(
    question_id: str,
    body: QuestionUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    question = await service.update_question(
        question_id, **{k: v for k, v in body.model_dump().items() if v is not None}
    )
    return success_response(
        QuestionResponse(
            id=question.id,
            assessment_id=question.assessment_id,
            question_type=question.question_type.value,
            prompt=question.prompt,
            options=question.options,
            difficulty=question.difficulty,
            marks=question.marks,
            explanation=question.explanation,
            order_index=question.order_index,
            created_at=question.created_at,
        ).model_dump(mode="json")
    )


@router.delete("/questions/{question_id}", status_code=204)
async def delete_question(
    question_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    service = AssessmentService(session)
    await service.delete_question(question_id)


@router.get("/assessments/{assessment_id}/questions")
async def get_questions(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    questions = await service.get_questions(assessment_id)
    items = []
    for q in questions:
        items.append(
            QuestionResponse(
                id=q.id,
                assessment_id=q.assessment_id,
                question_type=q.question_type.value,
                prompt=q.prompt,
                options=q.options,
                difficulty=q.difficulty,
                marks=q.marks,
                explanation=q.explanation,
                order_index=q.order_index,
                created_at=q.created_at,
            ).model_dump(mode="json")
        )
    return success_response(items)


# ------------------------------------------------------------------
# Question Bank
# ------------------------------------------------------------------

@router.post("/question-bank", status_code=201)
async def create_bank_question(
    body: QuestionBankCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    item = await service.create_bank_question(**body.model_dump())
    return success_response(
        QuestionBankResponse(
            id=item.id,
            course_id=item.course_id,
            lesson_id=item.lesson_id,
            concept_id=item.concept_id,
            question_type=item.question_type.value,
            prompt=item.prompt,
            options=item.options,
            difficulty=item.difficulty,
            marks=item.marks,
            explanation=item.explanation,
            tags=item.tags,
            created_at=item.created_at,
            updated_at=item.updated_at,
        ).model_dump(mode="json")
    )


@router.get("/question-bank")
async def get_bank_questions(
    course_id: str | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    items = await service.get_bank_questions(course_id)
    result = []
    for item in items:
        result.append(
            QuestionBankResponse(
                id=item.id,
                course_id=item.course_id,
                lesson_id=item.lesson_id,
                concept_id=item.concept_id,
                question_type=item.question_type.value,
                prompt=item.prompt,
                options=item.options,
                difficulty=item.difficulty,
                marks=item.marks,
                explanation=item.explanation,
                tags=item.tags,
                created_at=item.created_at,
                updated_at=item.updated_at,
            ).model_dump(mode="json")
        )
    return success_response(result)


@router.put("/question-bank/{question_id}")
async def update_bank_question(
    question_id: str,
    body: QuestionBankCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    service = AssessmentService(session)
    item = await service.update_bank_question(
        question_id, **{k: v for k, v in body.model_dump().items() if v is not None}
    )
    return success_response(
        QuestionBankResponse(
            id=item.id,
            course_id=item.course_id,
            lesson_id=item.lesson_id,
            concept_id=item.concept_id,
            question_type=item.question_type.value,
            prompt=item.prompt,
            options=item.options,
            difficulty=item.difficulty,
            marks=item.marks,
            explanation=item.explanation,
            tags=item.tags,
            created_at=item.created_at,
            updated_at=item.updated_at,
        ).model_dump(mode="json")
    )


@router.delete("/question-bank/{question_id}", status_code=204)
async def delete_bank_question(
    question_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
) -> None:
    service = AssessmentService(session)
    await service.delete_bank_question(question_id)


# ------------------------------------------------------------------
# Student: Assessment details
# ------------------------------------------------------------------

@router.get("/assessments/available")
async def get_available_assessments(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    assessments = await service.get_available_assessments(current_user.id)
    items = []
    for a in assessments:
        questions = await service.get_questions(a.id)
        items.append(
            AssessmentResponse(
                id=a.id,
                title=a.title,
                description=a.description,
                lesson_id=a.lesson_id,
                module_id=a.module_id,
                course_id=a.course_id,
                assessment_type=a.assessment_type.value,
                passing_score=a.passing_score,
                time_limit=a.time_limit,
                max_attempts=a.max_attempts,
                is_published=a.is_published,
                created_by=a.created_by,
                question_count=len(questions),
                created_at=a.created_at,
                updated_at=a.updated_at,
            ).model_dump(mode="json")
        )
    return success_response(items)


@router.get("/assessments/{assessment_id}")
async def get_assessment_detail(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    assessment = await service.get_assessment_detail(assessment_id)
    questions = await service.get_questions(assessment_id)
    return success_response(
        AssessmentDetail(
            id=assessment.id,
            title=assessment.title,
            description=assessment.description,
            lesson_id=assessment.lesson_id,
            module_id=assessment.module_id,
            course_id=assessment.course_id,
            assessment_type=assessment.assessment_type.value,
            passing_score=assessment.passing_score,
            time_limit=assessment.time_limit,
            max_attempts=assessment.max_attempts,
            is_published=assessment.is_published,
            question_count=len(questions),
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
        ).model_dump(mode="json")
    )


# ------------------------------------------------------------------
# Student: Attempt flow
# ------------------------------------------------------------------

@router.post("/assessments/{assessment_id}/start", status_code=201)
async def start_assessment(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    result = await service.start_attempt(assessment_id, current_user.id)
    return success_response(result)


@router.post("/attempts/{attempt_id}/submit")
async def submit_attempt(
    attempt_id: str,
    body: SubmitRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    result = await service.submit_attempt(
        attempt_id,
        current_user.id,
        [r.model_dump() for r in body.responses],
    )
    return success_response(result)


@router.get("/attempts/{attempt_id}/result")
async def get_attempt_result(
    attempt_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    result = await service.get_attempt_result(attempt_id, current_user.id)
    return success_response(result)


@router.get("/assessments/history")
async def get_assessment_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = AssessmentService(session)
    items, total = await service.get_attempt_history(
        current_user.id, page=page, per_page=per_page
    )
    return paginated_response(items, total, page, per_page)
