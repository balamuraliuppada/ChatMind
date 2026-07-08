# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, Response, status
from app.schemas.room import RoomCreate, RoomJoin, RoomDetailResponse, ParticipantResponse
from app.schemas.chat import MessageResponse
from app.services import room_service
from app.api.deps import DbSession, get_current_user_payload, get_session_token
from app.models.message import Message
# pyrefly: ignore [missing-import]
from sqlalchemy.future import select

router = APIRouter()

@router.post("/rooms", response_model=RoomDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_room(data: RoomCreate, db: DbSession, response: Response):
    result = await room_service.create_room(db, data)
    response.set_cookie(
        key="chatminds_session",
        value=result.token,
        httponly=True,
        max_age=24 * 60 * 60,
        samesite="none",
        secure=True
    )
    return result

@router.post("/rooms/join", response_model=RoomDetailResponse)
async def join_room(data: RoomJoin, db: DbSession, response: Response):
    result = await room_service.join_room(db, data)
    response.set_cookie(
        key="chatminds_session",
        value=result.token,
        httponly=True,
        max_age=24 * 60 * 60,
        samesite="none",
        secure=True
    )
    return result

@router.get("/rooms/me", response_model=RoomDetailResponse)
async def get_current_room(
    db: DbSession, 
    payload: dict = Depends(get_current_user_payload),
    token: str = Depends(get_session_token)
):
    participant_id = payload.get("sub")
    room_id = payload.get("room_id")
    
    from app.models.room import Room
    from app.models.participant import Participant
    
    room_result = await db.execute(select(Room).filter(Room.id == room_id))
    room = room_result.scalars().first()
    
    part_result = await db.execute(select(Participant).filter(Participant.id == participant_id))
    participant = part_result.scalars().first()
    
    from app.schemas.room import RoomResponse
    
    if not room or not participant or not room.active:
        # pyrefly: ignore [missing-import]
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Room or participant not found")
        
    return RoomDetailResponse(
        room=RoomResponse.model_validate(room),
        participant=ParticipantResponse.model_validate(participant),
        token=token
    )

@router.post("/rooms/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_room(
    response: Response
):
    response.delete_cookie("chatminds_session")
    return None

@router.get("/rooms/{room_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    room_id: str,
    db: DbSession,
    payload: dict = Depends(get_current_user_payload)
):
    # Verify user is in room
    if str(payload.get("room_id")) != str(room_id):
        # pyrefly: ignore [missing-import]
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Not authorized for this room")
        
    result = await db.execute(
        select(Message)
        .filter(Message.room_id == room_id)
        .order_by(Message.created_at.asc())
        .limit(100)
    )
    messages = result.scalars().all()
    return [MessageResponse.model_validate(m) for m in messages]
