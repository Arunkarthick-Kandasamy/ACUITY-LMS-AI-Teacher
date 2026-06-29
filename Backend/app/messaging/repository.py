from __future__ import annotations

from sqlalchemy import func, or_, select, update

from app.common.repository import Repository
from app.messaging.models import Conversation, Message


class ConversationRepository(Repository[Conversation]):
    def __init__(self, session) -> None:
        super().__init__(Conversation, session)

    async def find_by_participant(self, user_id: str) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(or_(Conversation.participant_one == user_id, Conversation.participant_two == user_id))
            .order_by(Conversation.last_message_at.desc().nullslast())
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def find_between(self, user_a: str, user_b: str) -> Conversation | None:
        stmt = select(Conversation).where(
            or_(
                (Conversation.participant_one == user_a) & (Conversation.participant_two == user_b),
                (Conversation.participant_one == user_b) & (Conversation.participant_two == user_a),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


class MessageRepository(Repository[Message]):
    def __init__(self, session) -> None:
        super().__init__(Message, session)

    async def find_by_conversation(self, conversation_id: str, offset: int = 0, limit: int = 50) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def count_unread(self, conversation_id: str, user_id: str) -> int:
        stmt = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != user_id,
            Message.is_read == False,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def mark_read(self, conversation_id: str, user_id: str) -> None:
        from datetime import datetime, timezone
        stmt = (
            update(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.sender_id != user_id,
                Message.is_read == False,
            )
            .values(is_read=True, read_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
