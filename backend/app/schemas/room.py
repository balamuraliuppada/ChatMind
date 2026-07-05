from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime

class RoomCreate(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=50)

class RoomJoin(BaseModel):
    room_code: str = Field(..., min_length=6, max_length=6)
    display_name: str = Field(..., min_length=1, max_length=50)

class RoomResponse(BaseModel):
    id: UUID
    room_code: str
    expires_at: datetime
    active: bool

    model_config = ConfigDict(from_attributes=True)

class ParticipantResponse(BaseModel):
    id: UUID
    display_name: str
    joined_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RoomDetailResponse(BaseModel):
    room: RoomResponse
    participant: ParticipantResponse
    token: str # Session token
