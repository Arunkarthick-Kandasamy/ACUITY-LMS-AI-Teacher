from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user, require_roles
from app.common.response import success_response
from app.common.types import UserRole
from app.config import settings
from app.infrastructure.database import get_session
from app.knowledge_graph.schemas import (
    DeleteMessage,
    KnowledgeEdgeCreate,
    KnowledgeEdgeResponse,
    PrerequisiteNode,
    PrerequisiteResponse,
)
from app.knowledge_graph.service import KnowledgeGraphService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/knowledge-graph", tags=["Knowledge Graph"])

admin_only = require_roles(UserRole.ADMIN)


@router.post("/edges", status_code=201)
async def create_edge(
    body: KnowledgeEdgeCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(admin_only),
) -> dict:
    service = KnowledgeGraphService(session)
    edge = await service.create_edge(**body.model_dump())
    return success_response(KnowledgeEdgeResponse.model_validate(edge).model_dump(mode="json"))


@router.delete("/edges/{edge_id}")
async def delete_edge(
    edge_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(admin_only),
) -> dict:
    service = KnowledgeGraphService(session)
    await service.delete_edge(edge_id)
    return success_response(DeleteMessage(message="Edge deleted successfully").model_dump())


@router.get("/concepts/{concept_id}/prerequisites")
async def get_prerequisites(
    concept_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = KnowledgeGraphService(session)
    node, prerequisites = await service.get_prerequisites(concept_id)
    return success_response(
        PrerequisiteResponse(
            concept_id=concept_id,
            concept_title=node.label if node else "",
            prerequisites=[PrerequisiteNode(**p) for p in prerequisites],
        ).model_dump(mode="json")
    )
