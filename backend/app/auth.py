"""Authentication: JWT cookie verification and user extraction."""

from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.config import get_settings
from app.db import get_session
from app.models.tables import User


class AuthenticatedUser:
    """Lightweight user object returned from auth dependency."""
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> AuthenticatedUser:
    """Extract and verify user from auth_token cookie."""
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Verify user still exists
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return AuthenticatedUser(id=str(user.id), email=user.email)
