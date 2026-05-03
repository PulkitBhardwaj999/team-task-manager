"""
Task service - business logic for task operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import Optional
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.models.models import Task, Project, TaskStatus, TaskPriority, project_members
from app.schemas.schemas import TaskCreate, TaskUpdate
from fastapi import HTTPException, status


# ─────────────────────────────────────────────────────────────────────────────
# ENUM HELPERS
#
# The Task model columns are declared as ENUM(*values, create_type=False) where
# values are the lowercase strings ('low', 'medium', 'high', 'todo', ...).
# SQLAlchemy with asyncpg expects to receive EXACTLY those strings when writing.
#
# These helpers accept anything (enum instance, string 'MEDIUM', string 'medium')
# and always return the correct lowercase string value.
# ─────────────────────────────────────────────────────────────────────────────

def _priority_value(priority) -> str:
    """Return the lowercase DB string for a priority (enum or str)."""
    if isinstance(priority, TaskPriority):
        return priority.value          # 'low' / 'medium' / 'high'
    try:
        return TaskPriority(str(priority).lower()).value
    except ValueError:
        return TaskPriority.MEDIUM.value


def _status_value(task_status) -> str:
    """Return the lowercase DB string for a status (enum or str)."""
    if isinstance(task_status, TaskStatus):
        return task_status.value       # 'todo' / 'in_progress' / 'done'
    try:
        return TaskStatus(str(task_status).lower()).value
    except ValueError:
        return TaskStatus.TODO.value


def _to_naive_utc(dt: datetime | None) -> datetime | None:
    """Convert any datetime to naive UTC (strip tzinfo)."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


class TaskService:

    # ── CREATE ────────────────────────────────────────────────────────────────

    @staticmethod
    async def create_task(db: AsyncSession, current_user, task_create: TaskCreate) -> Task:

        # 1. Project must exist
        project = (await db.execute(
            select(Project).where(Project.id == task_create.project_id)
        )).scalars().first()

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # 2. Requester must be a member or the creator
        membership = (await db.execute(
            select(project_members.c.user_id).where(
                project_members.c.project_id == task_create.project_id,
                project_members.c.user_id == current_user.id,
            )
        )).first()

        if not membership and project.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create tasks in this project")

        # 3. Resolve assigned_to — accept both field names from clients
        assigned_id = (
            getattr(task_create, "assigned_to_id", None)
            or getattr(task_create, "assigned_to", None)
        )

        # 4. Build the task — pass LOWERCASE STRINGS to the ENUM columns
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            project_id=task_create.project_id,
            assigned_to=assigned_id,
            priority=_priority_value(task_create.priority),   # ← always lowercase str
            status=_status_value(TaskStatus.TODO),             # ← always lowercase str
            due_date=_to_naive_utc(task_create.due_date),
        )

        if db_task.due_date and db_task.due_date < datetime.utcnow():
            db_task.is_overdue = True

        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

        # 5. Re-fetch with eager-loaded assignee so response has assigned_user_name
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.id == db_task.id)
        )
        return result.scalars().first()

    # ── UPDATE ────────────────────────────────────────────────────────────────

    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, current_user, task_update: TaskUpdate) -> Task:

        task = await TaskService.get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        project = task.project

        membership = (await db.execute(
            select(project_members.c.user_id).where(
                project_members.c.project_id == task.project_id,
                project_members.c.user_id == current_user.id,
            )
        )).first()

        is_authorized = (
            membership is not None
            or project.creator_id == current_user.id
            or task.assigned_to == current_user.id
        )
        if not is_authorized:
            raise HTTPException(status_code=403, detail="Not authorized to update this task")

        # Apply updates — always write lowercase strings to enum columns
        if task_update.title is not None:
            task.title = task_update.title

        if task_update.description is not None:
            task.description = task_update.description

        if task_update.priority is not None:
            task.priority = _priority_value(task_update.priority)

        if task_update.status is not None:
            task.status = _status_value(task_update.status)

        if task_update.due_date is not None:
            new_due = _to_naive_utc(task_update.due_date)
            task.due_date = new_due
            task.is_overdue = bool(new_due and new_due < datetime.utcnow())

        # Accept assigned_to or assigned_to_id
        new_assigned = (
            getattr(task_update, "assigned_to_id", None)
            or getattr(task_update, "assigned_to", None)
        )
        if new_assigned is not None:
            task.assigned_to = new_assigned

        await db.commit()
        await db.refresh(task)

        # Re-fetch with eager-loaded assignee
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.id == task.id)
        )
        return result.scalars().first()

    # ── READ ──────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
        result = await db.execute(
            select(Task)
            .options(
                selectinload(Task.assigned_user),
                selectinload(Task.project),
            )
            .where(Task.id == task_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_project_tasks(
        db: AsyncSession,
        project_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        priority: Optional[str] = None,
    ) -> list[Task]:

        query = (
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.project_id == project_id)
        )

        if status:
            query = query.where(Task.status == _status_value(status))

        if priority:
            query = query.where(Task.priority == _priority_value(priority))

        query = query.offset(skip).limit(limit).order_by(desc(Task.created_at))
        result = await db.execute(query)
        return result.scalars().all()

    # ── DELETE ────────────────────────────────────────────────────────────────

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> None:

        task = await TaskService.get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        creator_id = (await db.execute(
            select(Project.creator_id).where(Project.id == task.project_id)
        )).scalar_one_or_none()

        if creator_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this task")

        await db.delete(task)
        await db.commit()

    # ── MY TASKS / SEARCH / OVERDUE ───────────────────────────────────────────

    @staticmethod
    async def get_user_assigned_tasks(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Task]:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.assigned_to == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(desc(Task.created_at))
        )
        return result.scalars().all()

    @staticmethod
    async def search_tasks(
        db: AsyncSession,
        project_id: int,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(
                and_(
                    Task.project_id == project_id,
                    Task.title.ilike(f"%{search_term}%")
                    | Task.description.ilike(f"%{search_term}%"),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_overdue_tasks(db: AsyncSession, user_id: int) -> list[Task]:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(
                and_(
                    Task.assigned_to == user_id,
                    Task.is_overdue == True,
                    Task.status != _status_value(TaskStatus.DONE),
                )
            )
        )
        return result.scalars().all()