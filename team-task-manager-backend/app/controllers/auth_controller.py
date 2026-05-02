"""Authentication controller functions."""
from datetime import timedelta
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.schemas import (
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserLogin,
)
from app.services.user_service import UserService


async def get_current_user(
    authorization: str = Header(None),
    token: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Resolve the authenticated user from a bearer token."""
    auth_token = token
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization[7:]

    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
        )

    payload = decode_token(auth_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await UserService.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def signup(user_create: UserCreate, db: AsyncSession):
    """Create a new user account."""
    return await UserService.create_user(db, user_create)


async def login(credentials: UserLogin, db: AsyncSession) -> TokenResponse:
    """Authenticate a user and return access/refresh tokens."""
    user = await UserService.authenticate_user(db, credentials.email, credentials.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {"sub": str(user.id), "email": user.email}
    access_token = create_access_token(
        data=token_payload,
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data=token_payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def refresh_token(token_data: TokenRefresh, db: AsyncSession) -> TokenResponse:
    """Issue a new access token from a valid refresh token."""
    payload = decode_token(token_data.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = await UserService.get_user_by_id(db, int(user_id))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=token_data.refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


async def get_current_user_info(current_user, db: AsyncSession):
    """Return the latest persisted data for the current user."""
    return current_user
