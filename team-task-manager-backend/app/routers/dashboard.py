"""
Dashboard endpoints for statistics
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers import dashboard_controller
from app.core.database import get_db
from app.schemas.schemas import DashboardStats
from app.routers.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard statistics for current user"""
    return await dashboard_controller.get_dashboard_stats(db, current_user)


@router.get("/stats/debug")
async def get_dashboard_debug(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Debug endpoint: return project ids and raw counts for troubleshooting"""
    return await dashboard_controller.get_dashboard_debug(db, current_user)
