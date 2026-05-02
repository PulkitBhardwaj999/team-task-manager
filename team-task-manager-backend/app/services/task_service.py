"""
Task service - business logic for task operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import Optional
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from app.models.models import Task, Project, TaskStatus, TaskPriority, project_members
from app.schemas.schemas import TaskCreate, TaskUpdate
from fastapi import HTTPException, status


def _model_priority(priority) -> TaskPriority:
    return priority if isinstance(priority, TaskPriority) else TaskPriority(priority.value)


def _model_status(task_status) -> TaskStatus:
    return task_status if isinstance(task_status, TaskStatus) else TaskStatus(task_status.value)


class TaskService:
    """Service for task operations"""
    
    @staticmethod
    async def create_task(db: AsyncSession, current_user, task_create: TaskCreate) -> Task:
        """Create a new task"""
        # Check if project exists and user is a member
        project_query = select(Project).where(Project.id == task_create.project_id)
        project_result = await db.execute(project_query)
        project = project_result.scalars().first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        membership_query = select(project_members.c.user_id).where(
            project_members.c.project_id == task_create.project_id,
            project_members.c.user_id == current_user.id,
        )
        membership_result = await db.execute(membership_query)
        is_member = membership_result.first() is not None
        if not is_member and project.creator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create tasks in this project"
            )
        
        def _to_naive_utc(dt: datetime | None) -> datetime | None:
            if dt is None:
                return None
            # If dt is timezone-aware, convert to UTC and drop tzinfo to store as naive UTC
            if dt.tzinfo is not None:
                return dt.astimezone(timezone.utc).replace(tzinfo=None)
            # assume naive datetimes are already UTC
            return dt

        # Validate assigned user (if provided)
        assigned_id = getattr(task_create, 'assigned_to', None) or getattr(task_create, 'assigned_to_id', None)
        if assigned_id is not None:
            # Determine if requester has admin privileges for this project
            is_project_admin = False
            if project.creator_id == current_user.id:
                is_project_admin = True
            else:
                role_q = select(project_members.c.role).where(
                    project_members.c.project_id == task_create.project_id,
                    project_members.c.user_id == current_user.id,
                )
                role_res = await db.execute(role_q)
                role_row = role_res.first()
                if role_row and role_row[0] and str(role_row[0]).lower() == 'admin':
                    is_project_admin = True

            # Only project admins (or creator) can assign to others; members may assign to themselves
            if assigned_id != current_user.id and not is_project_admin:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project admins can assign tasks to other users")
            # Verify assigned user is part of the project or is the creator
            assign_mem_q = select(project_members.c.user_id).where(
                project_members.c.project_id == task_create.project_id,
                project_members.c.user_id == assigned_id,
            )
            assign_res = await db.execute(assign_mem_q)
            assign_is_member = assign_res.first() is not None or project.creator_id == assigned_id
            if not assign_is_member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user is not a member of the project")

        # Create task
        db_task = Task(
            title=task_create.title,
            description=task_create.description,
            project_id=task_create.project_id,
            assigned_to=assigned_id,
            priority=_model_priority(task_create.priority),
            due_date=_to_naive_utc(task_create.due_date)
        )
        
        # Check if overdue (compare as naive UTC datetimes)
        due_naive = _to_naive_utc(task_create.due_date)
        if due_naive and due_naive < datetime.utcnow():
            db_task.is_overdue = True
        
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        # Re-query with eager-loaded assigned_user to ensure response serialization
        query = (
            select(Task)
            .options(selectinload(Task.assigned_user))
            .where(Task.id == db_task.id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_task_by_id(db: AsyncSession, task_id: int) -> Task | None:
        """Get task by ID"""
        query = (
            select(Task)
            .options(
                selectinload(Task.project).selectinload(Project.members),
                selectinload(Task.assigned_user),
            )
            .where(Task.id == task_id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_project_tasks(db: AsyncSession, project_id: int, skip: int = 0, 
                               limit: int = 100, status: Optional[str] = None, 
                               priority: Optional[str] = None) -> list[Task]:
        """Get tasks for a project with filters"""
        query = select(Task).options(selectinload(Task.assigned_user)).where(Task.project_id == project_id)
        
        if status:
            query = query.where(Task.status == TaskStatus(status))
        if priority:
            query = query.where(Task.priority == TaskPriority(priority))
        
        query = query.offset(skip).limit(limit).order_by(desc(Task.created_at))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, current_user, 
                         task_update: TaskUpdate) -> Task:
        """Update a task"""
        task = await TaskService.get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        project = task.project
        membership_query = select(project_members.c.user_id).where(
            project_members.c.project_id == task.project_id,
            project_members.c.user_id == current_user.id,
        )
        membership_result = await db.execute(membership_query)
        is_member = membership_result.first() is not None
        is_authorized = is_member or project.creator_id == current_user.id or task.assigned_to == current_user.id
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this task"
            )
        
        # Update fields
        if task_update.title:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.priority:
            task.priority = _model_priority(task_update.priority)
        if task_update.status:
            task.status = _model_status(task_update.status)
        if task_update.due_date is not None:
            # Normalize incoming datetime to naive UTC for storage and comparison
            def _to_naive_utc_local(dt: datetime | None) -> datetime | None:
                if dt is None:
                    return None
                if dt.tzinfo is not None:
                    return dt.astimezone(timezone.utc).replace(tzinfo=None)
                return dt

            new_due = _to_naive_utc_local(task_update.due_date)
            task.due_date = new_due
            # Update overdue status comparing naive UTC
            if new_due and new_due < datetime.utcnow():
                task.is_overdue = True
            else:
                task.is_overdue = False
        # Handle assigned_to updates (only admins can assign to others)
        new_assigned = getattr(task_update, 'assigned_to', None) or getattr(task_update, 'assigned_to_id', None)
        if new_assigned is not None:
            # Check project-specific admin status (creator or project admin)
            is_project_admin = False
            if project.creator_id == current_user.id:
                is_project_admin = True
            else:
                role_q = select(project_members.c.role).where(
                    project_members.c.project_id == task.project_id,
                    project_members.c.user_id == current_user.id,
                )
                role_res = await db.execute(role_q)
                role_row = role_res.first()
                if role_row and role_row[0] and str(role_row[0]).lower() == 'admin':
                    is_project_admin = True

            if new_assigned != current_user.id and not is_project_admin:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only project admins can assign tasks to other users")
            # Verify assignee is member of project
            assign_q = select(project_members.c.user_id).where(
                project_members.c.project_id == task.project_id,
                project_members.c.user_id == new_assigned,
            )
            assign_res = await db.execute(assign_q)
            assign_is_member = assign_res.first() is not None or project.creator_id == new_assigned
            if not assign_is_member:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assigned user is not a member of the project")
            task.assigned_to = new_assigned
        
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> None:
        """Delete a task"""
        task = await TaskService.get_task_by_id(db, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        project_query = select(Project.creator_id).where(Project.id == task.project_id)
        project_result = await db.execute(project_query)
        creator_id = project_result.scalar_one_or_none()

        if creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this task"
            )
        
        await db.delete(task)
        await db.commit()
    
    @staticmethod
    async def get_user_assigned_tasks(db: AsyncSession, user_id: int, skip: int = 0, 
                                      limit: int = 100) -> list[Task]:
        """Get tasks assigned to a user"""
        query = select(Task).options(selectinload(Task.assigned_user)).where(Task.assigned_to == user_id).offset(skip).limit(limit).order_by(desc(Task.created_at))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def search_tasks(db: AsyncSession, project_id: int, search_term: str, 
                          skip: int = 0, limit: int = 100) -> list[Task]:
        """Search tasks by title or description"""
        query = select(Task).options(selectinload(Task.assigned_user)).where(
            and_(
                Task.project_id == project_id,
                (Task.title.ilike(f"%{search_term}%")) | 
                (Task.description.ilike(f"%{search_term}%"))
            )
        ).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_overdue_tasks(db: AsyncSession, user_id: int) -> list[Task]:
        """Get overdue tasks for a user"""
        query = select(Task).options(selectinload(Task.assigned_user)).where(
            and_(
                Task.assigned_to == user_id,
                Task.is_overdue == True,
                Task.status != TaskStatus.DONE
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
