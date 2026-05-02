"""
Project management endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, 
    ProjectDetailResponse, ProjectMemberAdd
)
from app.controllers import project_controller
from app.routers.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_create: ProjectCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    return await project_controller.create_project(db, current_user, project_create)

@router.get("/", response_model=list[ProjectDetailResponse])
async def get_my_projects(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all projects for current user"""
    return await project_controller.get_my_projects(db, current_user, skip, limit)

@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project by ID"""
    return await project_controller.get_project(db, current_user, project_id)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a project"""
    return await project_controller.update_project(
        db,
        current_user,
        project_id,
        project_update,
    )

@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    return await project_controller.delete_project(db, current_user, project_id)

@router.post("/{project_id}/members", response_model=ProjectDetailResponse)
async def add_project_member(
    project_id: int,
    member_add: ProjectMemberAdd,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a member to project"""
    return await project_controller.add_project_member(
        db,
        current_user,
        project_id,
        member_add,
    )

@router.delete("/{project_id}/members/{member_id}", response_model=ProjectDetailResponse)
async def remove_project_member(
    project_id: int,
    member_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member from project"""
    return await project_controller.remove_project_member(
        db,
        current_user,
        project_id,
        member_id,
    )

@router.get("/{project_id}/progress", response_model=dict)
async def get_project_progress(
    project_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project progress statistics"""
    return await project_controller.get_project_progress(db, project_id)
