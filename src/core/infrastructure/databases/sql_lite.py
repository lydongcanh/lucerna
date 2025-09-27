import os
import pathlib
from select import select
from sqlalchemy import select
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
    # Import models so metadata is populated
    from core.models.message import Base

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
    async with async_session() as session:
        stmt = select(model).filter_by(**kwargs)
        result = await session.execute(stmt)
        return result.scalars().all()
