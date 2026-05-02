"""Project controller functions."""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import ProjectCreate, ProjectMemberAdd, ProjectUpdate
from app.services.project_service import ProjectService


async def create_project(db: AsyncSession, current_user, project_create: ProjectCreate):
    """Create a project for the current user."""
    return await ProjectService.create_project(db, current_user.id, project_create)


async def get_my_projects(db: AsyncSession, current_user, skip: int = 0, limit: int = 100):
    """Return projects for the current user."""
    return await ProjectService.get_user_projects(db, current_user.id, skip, limit)


async def get_project(db: AsyncSession, current_user, project_id: int):
    """Return project detail after membership authorization."""
    project = await ProjectService.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    is_member = any(member.id == current_user.id for member in project.members)
    if not is_member and project.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project",
        )

    return project


async def update_project(
    db: AsyncSession,
    current_user,
    project_id: int,
    project_update: ProjectUpdate,
):
    """Update a project."""
    return await ProjectService.update_project(
        db,
        project_id,
        current_user.id,
        project_update,
    )


async def delete_project(db: AsyncSession, current_user, project_id: int):
    """Delete a project."""
    await ProjectService.delete_project(db, project_id, current_user.id)
    return {"message": "Project deleted successfully"}


async def add_project_member(
    db: AsyncSession,
    current_user,
    project_id: int,
    member_add: ProjectMemberAdd,
):
    """Add a member to a project."""
    return await ProjectService.add_project_member(
        db,
        project_id,
        current_user.id,
        member_add,
    )


async def remove_project_member(
    db: AsyncSession,
    current_user,
    project_id: int,
    member_id: int,
):
    """Remove a member from a project."""
    return await ProjectService.remove_project_member(
        db,
        project_id,
        current_user.id,
        member_id,
    )


async def get_project_progress(db: AsyncSession, project_id: int):
    """Return project progress statistics."""
    return await ProjectService.get_project_progress(db, project_id)

