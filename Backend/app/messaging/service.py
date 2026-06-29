from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.messaging.models import Conversation, Message
from app.messaging.repository import ConversationRepository, MessageRepository
from app.messaging.schemas import ConversationResponse, MessageResponse
from app.users.models import User
from app.users.repository import UserRepository


class MessagingService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.conv_repo = ConversationRepository(session)
        self.msg_repo = MessageRepository(session)
        self.user_repo = UserRepository(session)

    async def send_message(self, sender: User, receiver_id: str, content: str) -> MessageResponse:
        receiver = await self.user_repo.get(receiver_id)
        if receiver is None:
            raise NotFoundException(message="Recipient not found")

        conv = await self.conv_repo.find_between(sender.id, receiver_id)
        if conv is None:
            conv = Conversation(participant_one=sender.id, participant_two=receiver_id)
            self.session.add(conv)
            await self.session.flush()

        msg = Message(conversation_id=conv.id, sender_id=sender.id, content=content)
        self.session.add(msg)
        conv.last_message_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(msg)
        return MessageResponse.model_validate(msg)

    async def get_conversations(self, user: User) -> list[ConversationResponse]:
        convs = await self.conv_repo.find_by_participant(user.id)
        result = []
        for conv in convs:
            other_id = conv.participant_two if conv.participant_one == user.id else conv.participant_one
            other = await self.user_repo.get(other_id)
            unread = await self.msg_repo.count_unread(conv.id, user.id)
            msgs = await self.msg_repo.find_by_conversation(conv.id, limit=1)
            last_msg = msgs[0].content if msgs else ""
            result.append(ConversationResponse(
                conversation_id=conv.id,
                participant_one=conv.participant_one,
                participant_two=conv.participant_two,
                last_message_at=conv.last_message_at,
                unread_count=unread,
                other_participant_name=other.full_name if other else "Unknown",
                last_message=last_msg,
            ))
        return result

    async def get_messages(self, user: User, conversation_id: str) -> list[MessageResponse]:
        conv = await self.conv_repo.get(conversation_id)
        if conv is None:
            raise NotFoundException(message="Conversation not found")
        if conv.participant_one != user.id and conv.participant_two != user.id:
            raise NotFoundException(message="Access denied")
        await self.msg_repo.mark_read(conversation_id, user.id)
        msgs = await self.msg_repo.find_by_conversation(conversation_id)
        msgs.reverse()
        return [MessageResponse.model_validate(m) for m in msgs]
