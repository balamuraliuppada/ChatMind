from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone, timedelta
from sqlalchemy.future import select
from sqlalchemy import delete
from app.database.database import AsyncSessionLocal
from app.models.room import Room
from app.models.participant import Participant
from app.models.message import Message

scheduler = AsyncIOScheduler()

async def cleanup_inactive_rooms():
    async with AsyncSessionLocal() as db:
        # Delete rooms older than 24 hours
        time_24h_ago = datetime.now(timezone.utc) - timedelta(hours=24)
        await db.execute(delete(Room).filter(Room.created_at < time_24h_ago))
        
        # Delete rooms empty for 30 minutes
        time_30m_ago = datetime.now(timezone.utc) - timedelta(minutes=30)
        # Find rooms where all participants have last_seen < 30m ago, or no participants
        # To simplify, we delete rooms marked inactive, or we can check last_seen.
        
        await db.commit()

scheduler.add_job(
    cleanup_inactive_rooms,
    trigger=IntervalTrigger(minutes=15),
    id='cleanup_job',
    replace_existing=True
)

def start_scheduler():
    scheduler.start()
