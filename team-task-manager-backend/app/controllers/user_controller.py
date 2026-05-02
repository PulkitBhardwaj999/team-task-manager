"""User controller functions."""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    """Return all users."""
    return await UserService.get_all_users(db, skip, limit)


async def get_user(db: AsyncSession, user_id: int):
    """Return one user or raise 404."""
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

