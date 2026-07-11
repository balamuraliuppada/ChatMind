import logging
from contextlib import asynccontextmanager
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import router as api_router
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

from app.api.websocket import router as ws_router

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

@app.get("/health/liveness")
async def liveness():
    return {"status": "alive"}

@app.get("/health/readiness")
async def readiness():
    # Can check DB connection here
    return {"status": "ready"}
