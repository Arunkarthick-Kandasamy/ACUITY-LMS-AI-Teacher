from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    receiver_id: str
    content: str


class MessageResponse(BaseModel):
    message_id: str
    conversation_id: str
    sender_id: str
    content: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationResponse(BaseModel):
    conversation_id: str
    participant_one: str
    participant_two: str
    last_message_at: datetime | None = None
    unread_count: int = 0
    other_participant_name: str = ""
    last_message: str = ""

    model_config = {"from_attributes": True}


class MarkReadResponse(BaseModel):
    message: str
