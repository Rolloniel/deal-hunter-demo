"""Authentication dependency for extracting user from Supabase JWT."""

from fastapi import Depends, HTTPException, Header
from app.db import get_db


async def get_current_user(authorization: str = Header(None)):
    """Extract and verify user from Authorization Bearer token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ", 1)[1]
    db = get_db()

    try:
        user_response = db.auth.get_user(token)
        return user_response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
