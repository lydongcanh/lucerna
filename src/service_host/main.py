from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.infrastructure.databases.sql_lite import init_db
from service_host.api_routers import messages

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Lucerna API", lifespan=lifespan)

app.include_router(messages.router, prefix="/api/v1")