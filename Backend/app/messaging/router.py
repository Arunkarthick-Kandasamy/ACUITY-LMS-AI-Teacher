from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.common.response import success_response
from app.config import settings
from app.infrastructure.database import get_session
from app.messaging.schemas import SendMessageRequest
from app.messaging.service import MessagingService
from app.users.models import User

router = APIRouter(prefix=f"{settings.api_prefix}/messaging", tags=["Messaging"])


@router.post("/send")
async def send_message(
    body: SendMessageRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = MessagingService(session)
    msg = await service.send_message(current_user, body.receiver_id, body.content)
    return success_response(msg.model_dump(mode="json"))


@router.get("/conversations")
async def list_conversations(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = MessagingService(session)
    convs = await service.get_conversations(current_user)
    return success_response([c.model_dump(mode="json") for c in convs])


@router.get("/conversations/{conversation_id}")
async def get_conversation_messages(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    service = MessagingService(session)
    msgs = await service.get_messages(current_user, conversation_id)
    return success_response([m.model_dump(mode="json") for m in msgs])
