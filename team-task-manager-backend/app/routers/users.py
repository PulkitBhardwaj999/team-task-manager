"""
User management endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import UserResponse
from app.controllers import user_controller
from app.routers.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users"""
    return await user_controller.get_all_users(db, skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID"""
    return await user_controller.get_user(db, user_id)
