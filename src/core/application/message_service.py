import uuid
import tiktoken
from datetime import datetime, timezone

from core.infrastructure import SqlLite
from core.models.message import MessageDB, MessageIn, MessageOut


class MessageService:
    @staticmethod
    async def create_message(message_in: MessageIn) -> MessageOut:
        message = MessageDB(
            id=str(uuid.uuid4()),
            user_id=message_in.user_id,
            aggregate_id=message_in.aggregate_id,
            llm_model=message_in.llm_model,
            role=message_in.role,
            content=message_in.content,
            token_count=MessageService._count_message_tokens(message_in.content, message_in.llm_model),
            created_at=datetime.now(timezone.utc),
        )
        await SqlLite.save(message)
        return message


    @staticmethod
    async def get_message(message_id: str):
        return await SqlLite.get_by_id(MessageDB, message_id)


    @staticmethod
    async def get_messages(**filters):
        return await SqlLite.filter_by(MessageDB, **filters)


    @staticmethod
    def _count_message_tokens(content: str, model: str) -> int:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(content))
