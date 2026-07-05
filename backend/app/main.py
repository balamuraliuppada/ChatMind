import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.core.config import settings
from app.api.endpoints import router as api_router
from app.socket.events import sio
from app.database.database import engine, Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.tasks.cleanup import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    logger.info("Starting up ChatMinds API")
    async with engine.begin() as conn:
        # In production use Alembic, but for this demo we'll sync models
        await conn.run_sync(Base.metadata.create_all)
    
    start_scheduler()
    
    yield
    # On shutdown
    logger.info("Shutting down ChatMinds API")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO ASGI app
sio_asgi_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='socket.io'
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health/liveness")
async def liveness():
    return {"status": "alive"}

@app.get("/health/readiness")
async def readiness():
    # Can check DB connection here
    return {"status": "ready"}
