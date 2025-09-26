from fastapi import APIRouter
from core.models import LLMMessage

router = APIRouter()

@router.post("/messages")
async def report_message(message: LLMMessage):
    print(f"Message received: {message.content}")
