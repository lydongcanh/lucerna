from datetime import datetime, timezone
from typing import Optional

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MessageDB(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True, nullable=False)
    aggregate_id = Column(String, index=True, nullable=True)
    llm_model = Column(String, nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )


class MessageIn(BaseModel):
    user_id: str
    aggregate_id: Optional[str]
    llm_model: str
    role: str
    content: str


class MessageOut(MessageIn):
    id: str
    token_count: int
    created_at: datetime


class MessageQueryParams(BaseModel):
    start_date: Optional[datetime] = Query(
        None, description="Start of time range (UTC)"
    )
    end_date: Optional[datetime] = Query(None, description="End of time range (UTC)")
    user_id: Optional[str] = Query(None, description="Filter by user id")
    aggregate_id: Optional[str] = Query(None, description="Filter by aggregation id")
