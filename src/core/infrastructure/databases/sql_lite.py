import os
import pathlib
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./lucerna.db")

# Ensure SQLite folder exists if path is relative
if DATABASE_URL.startswith("sqlite"):
    db_path = DATABASE_URL.split("///")[-1]
    pathlib.Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


async def init_db() -> None:
    from core.models.message import Base  # import models so metadata is populated

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save(instance) -> None:
    async with async_session() as session:
        session.add(instance)
        await session.commit()


async def get_by_id(model, id_: str):
    async with async_session() as session:
        return await session.get(model, id_)


async def filter_by(model, **kwargs):
    """
    Supports both exact filters and extended operators:
    - field=value          → equality
    - field__gte=value     → greater than or equal
    - field__lte=value     → less than or equal
    - field__gt=value      → greater than
    - field__lt=value      → less than
    - field__ne=value      → not equal
    - field__in=[...]      → IN clause
    """

    async with async_session() as session:
        conditions = []
        for key, value in kwargs.items():
            if value is None:
                continue

            if "__" in key:
                field, op = key.split("__", 1)
                column = getattr(model, field)

                if op == "gte":
                    conditions.append(column >= value)
                elif op == "lte":
                    conditions.append(column <= value)
                elif op == "gt":
                    conditions.append(column > value)
                elif op == "lt":
                    conditions.append(column < value)
                elif op == "ne":
                    conditions.append(column != value)
                elif op == "in" and isinstance(value, (list, tuple)):
                    conditions.append(column.in_(value))
            else:
                column = getattr(model, key)
                conditions.append(column == value)

        stmt = select(model)
        if conditions:
            stmt = stmt.filter(and_(*conditions))

        result = await session.execute(stmt)
        return result.scalars().all()
