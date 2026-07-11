import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.future import select
from datetime import datetime, timezone
import jwt
from uuid import UUID
import uuid

from app.database.database import AsyncSessionLocal
from app.models.message import Message
from app.models.participant import Participant
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Maps room_id -> list of WebSockets
        self.active_connections: dict[str, list[WebSocket]] = {}
        # Maps websocket -> participant info
        self.connection_info: dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, room_id: str, participant_id: str, display_name: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        self.connection_info[websocket] = {
            "participant_id": participant_id,
            "display_name": display_name,
            "room_id": room_id
        }
        
        # Fire and forget DB update for socket_id
        asyncio.create_task(self.update_socket_id(participant_id, str(id(websocket))))

        # Broadcast user joined
        await self.broadcast(room_id, {
            "type": "user_joined",
            "participant_id": participant_id,
            "display_name": display_name
        })

    async def disconnect(self, websocket: WebSocket):
        info = self.connection_info.get(websocket)
        if info:
            room_id = info["room_id"]
            if room_id in self.active_connections:
                if websocket in self.active_connections[room_id]:
                    self.active_connections[room_id].remove(websocket)
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
            
            del self.connection_info[websocket]
            
            await self.broadcast(room_id, {
                "type": "user_left",
                "participant_id": info["participant_id"],
                "display_name": info["display_name"]
            })
            return info
        return None

    async def broadcast(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            # Create a copy of the list to safely iterate
            for connection in list(self.active_connections[room_id]):
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    # Force disconnect bad connection
                    await self.disconnect(connection)
                    
    async def update_socket_id(self, participant_id: str, socket_id: str):
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Participant).filter(Participant.id == participant_id))
                participant = result.scalars().first()
                if participant:
                    participant.socket_id = socket_id
                    await db.commit()
        except Exception as e:
            logger.error(f"Failed to update socket_id: {e}")

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    try:
        # Validate token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        participant_id = payload.get("sub")
        room_id = payload.get("room_id")
        display_name = payload.get("display_name", "Unknown User")
        
        if not participant_id or not room_id:
            await websocket.close(code=4001, reason="Invalid token payload")
            return
            
    except jwt.PyJWTError:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return
    except Exception as e:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    await manager.connect(websocket, room_id, participant_id, display_name)

    try:
        while True:
            # Wait for any message from the client
            data = await websocket.receive_text()
            try:
                parsed_data = json.loads(data)
            except json.JSONDecodeError:
                continue
                
            event_type = parsed_data.get("type")
            
            if event_type == "message":
                msg_text = parsed_data.get("message")
                client_id = parsed_data.get("id")
                
                if not msg_text:
                    continue
                    
                async with AsyncSessionLocal() as db:
                    new_msg_id = UUID(client_id) if client_id else uuid.uuid4()
                    new_message = Message(
                        id=new_msg_id,
                        room_id=room_id,
                        sender_id=participant_id,
                        message=msg_text
                    )
                    db.add(new_message)
                    await db.flush()
                    
                    msg_id_str = str(new_message.id)
                    msg_created_at = new_message.created_at.isoformat() if new_message.created_at else datetime.now(timezone.utc).isoformat()
                    
                    await db.commit()

                # Broadcast to all users in the room
                await manager.broadcast(room_id, {
                    "type": "new_message",
                    "id": msg_id_str,
                    "room_id": room_id,
                    "sender_id": participant_id,
                    "sender_name": display_name,
                    "message": msg_text,
                    "created_at": msg_created_at
                })
                
            elif event_type == "typing":
                is_typing = parsed_data.get("is_typing", False)
                await manager.broadcast(room_id, {
                    "type": "typing",
                    "participant_id": participant_id,
                    "display_name": display_name,
                    "is_typing": is_typing
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(websocket)
