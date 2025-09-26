from fastapi import FastAPI
from service_host.api_routers import messages

app = FastAPI(title="Lucerna API")
app.include_router(messages.router, prefix="/api/v1")