import uuid
from datetime import datetime, timezone

import tiktoken

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
            token_count=MessageService._count_message_tokens(
                message_in.content, message_in.llm_model
            ),
            created_at=datetime.now(timezone.utc),
        )
        await SqlLite.save(message)
        return message

    @staticmethod
    async def get_message(message_id: str):
        return await SqlLite.get_by_id(MessageDB, message_id)

    @staticmethod
    async def get_messages(**filters):
        db_filters = {}

        # Handle time range mapping
        if "start_date" in filters:
            start = filters.pop("start_date")
            if start:
                db_filters["created_at__gte"] = datetime.fromisoformat(start)

        if "end_date" in filters:
            end = filters.pop("end_date")
            if end:
                db_filters["created_at__lte"] = datetime.fromisoformat(end)

        # Keep remaining filters (user_id, aggregate_id, etc.)
        for key, value in filters.items():
            if value:
                db_filters[key] = value

        return await SqlLite.filter_by(MessageDB, **db_filters)

    @staticmethod
    def _count_message_tokens(content: str, model: str) -> int:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(content))
