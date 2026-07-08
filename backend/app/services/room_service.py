import string
import secrets
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from fastapi import HTTPException, status
import jwt
from uuid import uuid4

from app.models.room import Room
from app.models.participant import Participant
from app.schemas.room import RoomCreate, RoomJoin, RoomDetailResponse, RoomResponse, ParticipantResponse
from app.core.config import settings

def generate_room_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(6))

def create_session_token(participant_id: str, room_id: str, display_name: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(participant_id), "room_id": str(room_id), "display_name": display_name}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def create_room(db: AsyncSession, data: RoomCreate) -> RoomDetailResponse:
    # 1. Create room
    room_code = generate_room_code()
    # Check if code exists (unlikely but possible)
    result = await db.execute(select(Room).filter(Room.room_code == room_code))
    if result.scalars().first():
        room_code = generate_room_code()
    
    owner_session = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    new_room = Room(
        room_code=room_code,
        expires_at=expires_at,
        owner_session=owner_session
    )
    db.add(new_room)
    await db.flush()
    
    # 2. Create participant
    participant = Participant(
        room_id=new_room.id,
        display_name=data.display_name,
        session_id=owner_session
    )
    db.add(participant)
    await db.commit()
    await db.refresh(new_room)
    await db.refresh(participant)
    
    # 3. Create token
    token = create_session_token(participant.id, new_room.id, participant.display_name)
    
    return RoomDetailResponse(
        room=RoomResponse.model_validate(new_room),
        participant=ParticipantResponse.model_validate(participant),
        token=token
    )

async def join_room(db: AsyncSession, data: RoomJoin) -> RoomDetailResponse:
    # 1. Find room
    result = await db.execute(select(Room).filter(Room.room_code == data.room_code.upper()))
    room = result.scalars().first()
    
    if not room or not room.active:
        raise HTTPException(status_code=404, detail="Room not found or inactive")
        
    if room.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Room has expired")
        
    # 2. Create participant
    session_id = str(uuid4())
    participant = Participant(
        room_id=room.id,
        display_name=data.display_name,
        session_id=session_id
    )
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    
    # 3. Create token
    token = create_session_token(participant.id, room.id, participant.display_name)
    
    return RoomDetailResponse(
        room=RoomResponse.model_validate(room),
        participant=ParticipantResponse.model_validate(participant),
        token=token
    )

async def get_room_participants(db: AsyncSession, room_id: str) -> list[ParticipantResponse]:
    result = await db.execute(select(Participant).filter(Participant.room_id == room_id))
    participants = result.scalars().all()
    return [ParticipantResponse.model_validate(p) for p in participants]
