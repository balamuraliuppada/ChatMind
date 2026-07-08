import socketio
import jwt
from sqlalchemy.future import select
from app.database.database import AsyncSessionLocal
from app.models.participant import Participant
from app.models.message import Message
from app.models.room import Room
from app.core.config import settings

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

async def get_participant(sid: str, room_id: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Participant).filter(Participant.socket_id == sid, Participant.room_id == room_id))
        return result.scalars().first()

@sio.on('connect')
async def connect(sid, environ, auth):
    try:
        # Extract token from auth
        token = auth.get("token") if auth else None
        if not token:
            # Try to get from cookies
            cookie = environ.get("HTTP_COOKIE", "")
            for c in cookie.split(";"):
                if "chatminds_session" in c:
                    token = c.split("=")[1].strip()
                    break

        if not token:
            return False

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        participant_id = payload.get("sub")
        room_id = payload.get("room_id")

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Participant).filter(Participant.id == participant_id))
            participant = result.scalars().first()
            if not participant:
                return False
                
            display_name = participant.display_name
            participant.socket_id = sid
            await db.commit()
            
            sio.enter_room(sid, str(room_id))
            
            # Save session data in socket
            async with sio.session(sid) as session:
                session['participant_id'] = str(participant_id)
                session['room_id'] = str(room_id)
                session['display_name'] = display_name

            await sio.emit('user_joined', {'participant_id': str(participant_id), 'display_name': display_name}, room=str(room_id))

    except Exception as e:
        return False

@sio.on('disconnect')
async def disconnect(sid):
    async with sio.session(sid) as session:
        participant_id = session.get('participant_id')
        room_id = session.get('room_id')
        display_name = session.get('display_name')
        
        if room_id:
            sio.leave_room(sid, room_id)
            await sio.emit('user_left', {'participant_id': participant_id, 'display_name': display_name}, room=room_id)

@sio.on('message')
async def handle_message(sid, data):
    async with sio.session(sid) as session:
        participant_id = session.get('participant_id')
        room_id = session.get('room_id')
        display_name = session.get('display_name')
        
        msg_text = data.get('message')
        client_id = data.get('id')
        if not msg_text or not room_id or not participant_id:
            return

        async with AsyncSessionLocal() as db:
            import uuid
            new_msg_id = uuid.UUID(client_id) if client_id else uuid.uuid4()
            new_message = Message(
                id=new_msg_id,
                room_id=room_id,
                sender_id=participant_id,
                message=msg_text
            )
            db.add(new_message)
            await db.flush()
            
            # Extract attributes before commit to avoid async lazy-loading errors
            msg_id = str(new_message.id)
            from datetime import datetime, timezone
            msg_created_at = new_message.created_at.isoformat() if new_message.created_at else datetime.now(timezone.utc).isoformat()
            
            await db.commit()

            await sio.emit('new_message', {
                'id': msg_id,
                'room_id': room_id,
                'sender_id': participant_id,
                'sender_name': display_name,
                'message': msg_text,
                'created_at': msg_created_at
            }, room=str(room_id))

@sio.on('typing')
async def handle_typing(sid, data):
    async with sio.session(sid) as session:
        room_id = session.get('room_id')
        display_name = session.get('display_name')
        participant_id = session.get('participant_id')
        
        if room_id:
            is_typing = data.get('is_typing', False)
            await sio.emit('user_typing', {
                'participant_id': participant_id,
                'display_name': display_name,
                'is_typing': is_typing
            }, room=room_id, skip_sid=sid)
