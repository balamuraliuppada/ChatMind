from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class MessageResponse(BaseModel):
    id: UUID
    room_id: UUID
    sender_id: UUID
    message: str
    created_at: datetime
    sender_name: str | None = None

    model_config = ConfigDict(from_attributes=True)
