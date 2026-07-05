# pyrefly: ignore [missing-import]
from fastapi import Depends, HTTPException, status, Request
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
import jwt
from app.database.database import get_db
from app.core.config import settings
from typing import Annotated

DbSession = Annotated[AsyncSession, Depends(get_db)]

def get_session_token(request: Request) -> str:
    token = request.cookies.get("chatminds_session")
    if not token:
        # Also check Authorization header as fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return token

def get_current_user_payload(token: str = Depends(get_session_token)) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
