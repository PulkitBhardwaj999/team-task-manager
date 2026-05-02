"""
Authentication and user management endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import (
    UserCreate, UserLogin, TokenResponse, UserResponse, 
    TokenRefresh
)
from app.controllers import auth_controller

router = APIRouter(prefix="/auth", tags=["Auth"])

# ===== Dependencies =====

get_current_user = auth_controller.get_current_user

# ===== Endpoints =====

@router.post("/signup", response_model=UserResponse)
async def signup(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Sign up a new user"""
    return await auth_controller.signup(user_create, db)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user"""
    return await auth_controller.login(credentials, db)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Refresh access token"""
    return await auth_controller.refresh_token(token_data, db)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    return await auth_controller.get_current_user_info(current_user, db)
