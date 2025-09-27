import uuid
from datetime import datetime, timezone

import tiktoken

from core.infrastructure import SqlLite
from core.models.message import MessageDB, MessageIn, MessageOut, MessageQueryParams


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
    async def get_messages(params: MessageQueryParams):
        db_filters: dict[str, object] = {}

        if params.start_date:
            start = (
                params.start_date.replace(tzinfo=timezone.utc)
                if params.start_date.tzinfo is None
                else params.start_date.astimezone(timezone.utc)
            )
            db_filters["created_at__gte"] = start

        if params.end_date:
            end = (
                params.end_date.replace(tzinfo=timezone.utc)
                if params.end_date.tzinfo is None
                else params.end_date.astimezone(timezone.utc)
            )
            db_filters["created_at__lte"] = end

        if params.user_id:
            db_filters["user_id"] = params.user_id

        if params.aggregate_id:
            db_filters["aggregate_id"] = params.aggregate_id

        return await SqlLite.filter_by(MessageDB, **db_filters)

    @staticmethod
    def _count_message_tokens(content: str, model: str) -> int:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(content))
