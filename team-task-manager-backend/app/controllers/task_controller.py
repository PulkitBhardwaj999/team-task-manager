"""Task controller functions."""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schemas import TaskCreate, TaskUpdate
from app.services.task_service import TaskService


async def create_task(db: AsyncSession, current_user, task_create: TaskCreate):
    """Create a task."""
    return await TaskService.create_task(db, current_user, task_create)


async def get_task(db: AsyncSession, task_id: int):
    """Return a task or raise 404."""
    task = await TaskService.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


async def get_project_tasks(
    db: AsyncSession,
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    priority_filter: str = None,
):
    """Return tasks for a project with optional filters."""
    return await TaskService.get_project_tasks(
        db,
        project_id,
        skip,
        limit,
        status_filter,
        priority_filter,
    )


async def update_task(db: AsyncSession, current_user, task_id: int, task_update: TaskUpdate):
    """Update a task."""
    return await TaskService.update_task(db, task_id, current_user, task_update)


async def delete_task(db: AsyncSession, current_user, task_id: int):
    """Delete a task."""
    await TaskService.delete_task(db, task_id, current_user.id)
    return {"message": "Task deleted successfully"}


async def get_my_tasks(db: AsyncSession, current_user, skip: int = 0, limit: int = 100):
    """Return tasks assigned to the current user."""
    return await TaskService.get_user_assigned_tasks(db, current_user.id, skip, limit)


async def search_tasks(db: AsyncSession, project_id: int, q: str, skip: int = 0, limit: int = 100):
    """Search tasks by title or description."""
    return await TaskService.search_tasks(db, project_id, q, skip, limit)


async def get_overdue_tasks(db: AsyncSession, current_user):
    """Return overdue tasks assigned to the current user."""
    return await TaskService.get_overdue_tasks(db, current_user.id)

