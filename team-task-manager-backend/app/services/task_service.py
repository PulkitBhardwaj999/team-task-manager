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


# ✅ ENUM FIX HELPERS
def _model_priority(priority) -> str:
    try:
        return TaskPriority(str(priority).lower()).value
    except:
        return TaskPriority.MEDIUM.value


def _model_status(task_status) -> str:
    try:
        return TaskStatus(str(task_status).lower()).value
    except:
        return TaskStatus.TODO.value


class TaskService:

    @staticmethod
    async def create_task(db: AsyncSession, current_user, task_create: TaskCreate) -> Task:

        project = (await db.execute(
            select(Project).where(Project.id == task_create.project_id)
        )).scalars().first()

        if not project:
            raise HTTPException(404, "Project not found")

        membership = (await db.execute(
            select(project_members.c.user_id).where(
                project_members.c.project_id == task_create.project_id,
                project_members.c.user_id == current_user.id
            )
        )).first()

        if not membership and project.creator_id != current_user.id:
            raise HTTPException(403, "Not authorized")

        def _to_naive_utc(dt):
            if not dt:
                return None
            return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt

        assigned_id = getattr(task_create, 'assigned_to', None) or getattr(task_create, 'assigned_to_id', None)

        # ✅ FIXED ENUM HERE
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            project_id=task_create.project_id,
            assigned_to=assigned_id,
            priority=_model_priority(task_create.priority),  # ✅ always lowercase
            status=TaskStatus.TODO.value,
            due_date=_to_naive_utc(task_create.due_date)
        )

        # overdue check
        if db_task.due_date and db_task.due_date < datetime.utcnow():
            db_task.is_overdue = True

        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)

        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.id == db_task.id)
        )

        return result.scalars().first()


    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, current_user, task_update: TaskUpdate) -> Task:

        task = await TaskService.get_task_by_id(db, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        project = task.project

        membership = (await db.execute(
            select(project_members.c.user_id).where(
                project_members.c.project_id == task.project_id,
                project_members.c.user_id == current_user.id
            )
        )).first()

        is_authorized = membership or project.creator_id == current_user.id or task.assigned_to == current_user.id

        if not is_authorized:
            raise HTTPException(403, "Not authorized")

        if task_update.title:
            task.title = task_update.title

        if task_update.description is not None:
            task.description = task_update.description

        # ✅ FIX ENUM HERE ALSO
        if task_update.priority:
            task.priority = _model_priority(task_update.priority)

        if task_update.status:
            task.status = _model_status(task_update.status)

        if task_update.due_date is not None:
            def _to_naive(dt):
                if not dt:
                    return None
                return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt

            task.due_date = _to_naive(task_update.due_date)

            if task.due_date and task.due_date < datetime.utcnow():
                task.is_overdue = True
            else:
                task.is_overdue = False

        new_assigned = getattr(task_update, 'assigned_to', None) or getattr(task_update, 'assigned_to_id', None)

        if new_assigned is not None:
            task.assigned_to = new_assigned

        await db.commit()
        await db.refresh(task)

        return task


    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.id == task_id)
        )
        return result.scalars().first()


    @staticmethod
    async def get_project_tasks(db: AsyncSession, project_id: int, skip: int = 0,
                               limit: int = 100, status: Optional[str] = None,
                               priority: Optional[str] = None) -> list[Task]:

        query = select(Task).options(selectinload(Task.assigned_user)).where(Task.project_id == project_id)

        if status:
            query = query.where(Task.status == TaskStatus(status).value)

        if priority:
            query = query.where(Task.priority == TaskPriority(priority).value)

        query = query.offset(skip).limit(limit).order_by(desc(Task.created_at))

        result = await db.execute(query)
        return result.scalars().all()


    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> None:

        task = await TaskService.get_task_by_id(db, task_id)

        if not task:
            raise HTTPException(404, "Task not found")

        project = (await db.execute(
            select(Project.creator_id).where(Project.id == task.project_id)
        )).scalar_one_or_none()

        if project != user_id:
            raise HTTPException(403, "Not authorized")

        await db.delete(task)
        await db.commit()


    @staticmethod
    async def get_user_assigned_tasks(db: AsyncSession, user_id: int, skip: int = 0,
                                     limit: int = 100) -> list[Task]:

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
    async def search_tasks(db: AsyncSession, project_id: int, search_term: str,
                          skip: int = 0, limit: int = 100) -> list[Task]:

        result = await db.execute(
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(
                and_(
                    Task.project_id == project_id,
                    (Task.title.ilike(f"%{search_term}%")) |
                    (Task.description.ilike(f"%{search_term}%"))
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
                    Task.status != TaskStatus.DONE.value
                )
            )
        )

        return result.scalars().all()