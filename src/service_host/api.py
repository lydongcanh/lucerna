from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

from core.infrastructure.databases.sql_lite import init_db
from service_host.api_routers import messages
from service_host.ui import create_dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Lucerna API", lifespan=lifespan)

app.include_router(messages.router, prefix="/api/v1")

dash_app = create_dashboard()
app.mount("/dashboard", WSGIMiddleware(dash_app.server))
