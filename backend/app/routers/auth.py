"""OAuth authentication router using Authlib."""

import logging
from datetime import datetime, timedelta, timezone

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app.config import get_settings
from app.db import get_session
from app.models.tables import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

settings = get_settings()

oauth = OAuth()

# Register Google
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Register GitHub
oauth.register(
    name="github",
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)


def _create_jwt(user_id: str) -> str:
    """Create a signed JWT token for the user."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def _set_auth_cookie(response: RedirectResponse, token: str) -> RedirectResponse:
    """Set httpOnly auth cookie on the response."""
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/",
    )
    return response


@router.get("/google")
async def google_login(request: Request):
    """Redirect to Google OAuth."""
    redirect_uri = f"{settings.backend_url}/auth/callback/google"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback/google", name="google_callback")
async def google_callback(request: Request, session: AsyncSession = Depends(get_session)):
    """Handle Google OAuth callback."""
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        logger.error("Google OAuth error: %s", e)
        return RedirectResponse(f"{settings.frontend_url}/login?error=oauth_failed")

    userinfo = token.get("userinfo", {})
    email = userinfo.get("email")
    if not email:
        return RedirectResponse(f"{settings.frontend_url}/login?error=no_email")

    user = await _get_or_create_user(session, email)
    jwt_token = _create_jwt(str(user.id))
    response = RedirectResponse(f"{settings.frontend_url}/app")
    return _set_auth_cookie(response, jwt_token)


@router.get("/github")
async def github_login(request: Request):
    """Redirect to GitHub OAuth."""
    redirect_uri = f"{settings.backend_url}/auth/callback/github"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/callback/github", name="github_callback")
async def github_callback(request: Request, session: AsyncSession = Depends(get_session)):
    """Handle GitHub OAuth callback."""
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
        logger.error("GitHub OAuth error: %s", e)
        return RedirectResponse(f"{settings.frontend_url}/login?error=oauth_failed")

    # GitHub doesn't return email in token — fetch from API
    resp = await oauth.github.get("user/emails", token=token)
    emails = resp.json()
    primary = next((e["email"] for e in emails if e.get("primary")), None)
    if not primary:
        primary = next((e["email"] for e in emails if e.get("verified")), None)
    if not primary:
        return RedirectResponse(f"{settings.frontend_url}/login?error=no_email")

    user = await _get_or_create_user(session, primary)
    jwt_token = _create_jwt(str(user.id))
    response = RedirectResponse(f"{settings.frontend_url}/app")
    return _set_auth_cookie(response, jwt_token)


@router.get("/me")
async def get_me(request: Request, session: AsyncSession = Depends(get_session)):
    """Return current user info from auth cookie. Used by frontend to check auth state."""
    token = request.cookies.get("auth_token")
    if not token:
        return JSONResponse({"user": None}, status_code=200)

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return JSONResponse({"user": None}, status_code=200)

    user_id = payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        return JSONResponse({"user": None}, status_code=200)

    return {"user": {"id": str(user.id), "email": user.email}}


@router.post("/logout")
async def logout():
    """Clear auth cookie."""
    response = JSONResponse({"success": True})
    response.delete_cookie("auth_token", path="/")
    return response


async def _get_or_create_user(session: AsyncSession, email: str) -> User:
    """Find existing user by email or create a new one."""
    stmt = select(User).where(User.email == email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        return user

    user = User(email=email)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
