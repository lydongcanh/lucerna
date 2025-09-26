from pydantic import BaseModel

class LLMMessage(BaseModel):
    trace_id: str
    role: str
    content: str