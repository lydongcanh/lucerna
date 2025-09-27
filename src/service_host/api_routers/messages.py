from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel

from core.application.message_service import MessageService
from core.models import MessageIn, MessageOut

router = APIRouter()


class MessageQueryParams(BaseModel):
    start_date: Optional[datetime] = Query(
        None, description="Start of time range (UTC)"
    )
    end_date: Optional[datetime] = Query(None, description="End of time range (UTC)")
    user_id: Optional[str] = Query(None, description="Filter by user id")
    aggregate_id: Optional[str] = Query(None, description="Filter by aggregation id")


@router.post("/messages", response_model=MessageOut)
async def report_message(message: MessageIn):
    return await MessageService.create_message(message)


@router.get("/messages/{message_id}", response_model=MessageOut)
async def get_message(message_id: str):
    message = await MessageService.get_message(message_id)
    return Response(status_code=404) if message is None else message


@router.get("/messages", response_model=list[MessageOut])
async def get_messages(params: MessageQueryParams = Depends()):
    return await MessageService.get_messages(**params.dict(exclude_none=True))
