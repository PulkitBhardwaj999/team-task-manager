"""
Task management endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskDetailResponse
from app.controllers import task_controller
from app.routers.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(
    task_create: TaskCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task"""
    return await task_controller.create_task(db, current_user, task_create)

@router.get("/project/{project_id}", response_model=list[TaskResponse])
async def get_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: str = Query(None, alias="status"),
    priority_filter: str = Query(None, alias="priority"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get tasks for a project with optional filters"""
    return await task_controller.get_project_tasks(
        db, project_id, skip, limit, status_filter, priority_filter
    )

@router.get("/search/{project_id}", response_model=list[TaskResponse])
async def search_tasks(
    project_id: int,
    q: str = Query(...),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search tasks by title or description"""
    return await task_controller.search_tasks(db, project_id, q, skip, limit)

@router.get("/overdue", response_model=list[TaskResponse])
async def get_overdue_tasks(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overdue tasks for current user"""
    return await task_controller.get_overdue_tasks(db, current_user)

@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    task_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID"""
    return await task_controller.get_task(db, task_id)

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a task"""
    return await task_controller.update_task(db, current_user, task_id, task_update)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task"""
    return await task_controller.delete_task(db, current_user, task_id)

@router.get("/", response_model=list[TaskResponse])
async def get_my_tasks(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tasks assigned to current user"""
    return await task_controller.get_my_tasks(db, current_user, skip, limit)
