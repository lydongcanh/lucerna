from fastapi import APIRouter, Depends, Response

from core.application.message_service import MessageService
from core.models import MessageIn, MessageOut, MessageQueryParams

router = APIRouter()


@router.post("/messages", response_model=MessageOut)
async def report_message(message: MessageIn):
    return await MessageService.create_message(message)


@router.get("/messages/{message_id}", response_model=MessageOut)
async def get_message(message_id: str):
    message = await MessageService.get_message(message_id)
    return Response(status_code=404) if message is None else message


@router.get("/messages", response_model=list[MessageOut])
async def get_messages(params: MessageQueryParams = Depends()):
    return await MessageService.get_messages(params)
