"""Dashboard controller functions."""
from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Task, TaskPriority, TaskStatus, project_members, Project
from app.schemas.schemas import DashboardStats


async def get_dashboard_stats(db: AsyncSession, current_user) -> DashboardStats:
    """Build dashboard statistics for the current user."""
    # Determine projects the user is part of (member or creator)
    # Only consider active projects
    member_proj_q = (
        select(project_members.c.project_id)
        .select_from(project_members.join(Project, project_members.c.project_id == Project.id))
        .where(project_members.c.user_id == current_user.id, Project.is_active == True)
    )
    member_res = await db.execute(member_proj_q)
    member_ids = [row[0] for row in member_res.fetchall()]

    creator_proj_q = select(Project.id).where(Project.creator_id == current_user.id, Project.is_active == True)
    creator_res = await db.execute(creator_proj_q)
    creator_ids = [row[0] for row in creator_res.fetchall()]

    # Count only projects where the user is an explicit member (matches frontend project list)
    project_ids = set(member_ids)

    # Fetch tasks in user's projects and tasks assigned to user, then merge
    user_tasks = []
    seen = set()

    if project_ids:
        proj_tasks_q = select(Task).where(Task.project_id.in_(list(project_ids)))
        proj_tasks_res = await db.execute(proj_tasks_q)
        for t in proj_tasks_res.scalars().all():
            user_tasks.append(t)
            seen.add(t.id)

    assigned_q = select(Task).where(Task.assigned_to == current_user.id)
    assigned_res = await db.execute(assigned_q)
    for t in assigned_res.scalars().all():
        if t.id not in seen:
            user_tasks.append(t)
            seen.add(t.id)

    total_tasks = len(user_tasks)
    completed_tasks = sum(1 for task in user_tasks if task.status == TaskStatus.DONE)
    pending_tasks = total_tasks - completed_tasks
    overdue_tasks = sum(1 for task in user_tasks if task.is_overdue and task.status != TaskStatus.DONE)

    tasks_by_priority = {
        "high": sum(1 for task in user_tasks if task.priority == TaskPriority.HIGH),
        "medium": sum(1 for task in user_tasks if task.priority == TaskPriority.MEDIUM),
        "low": sum(1 for task in user_tasks if task.priority == TaskPriority.LOW),
    }

    tasks_by_status = {
        "todo": sum(1 for task in user_tasks if task.status == TaskStatus.TODO),
        "in_progress": sum(1 for task in user_tasks if task.status == TaskStatus.IN_PROGRESS),
        "done": sum(1 for task in user_tasks if task.status == TaskStatus.DONE),
    }

    total_projects = len(project_ids)

    return DashboardStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        total_projects=total_projects,
        tasks_by_priority=tasks_by_priority,
        tasks_by_status=tasks_by_status,
    )


async def get_dashboard_debug(db: AsyncSession, current_user):
    """Return debug info for dashboard aggregation"""
    member_proj_q = select(project_members.c.project_id).where(project_members.c.user_id == current_user.id)
    member_res = await db.execute(member_proj_q)
    member_ids = [row[0] for row in member_res.fetchall()]

    creator_proj_q = select(Project.id).where(Project.creator_id == current_user.id)
    creator_res = await db.execute(creator_proj_q)
    creator_ids = [row[0] for row in creator_res.fetchall()]

    project_ids = set(member_ids)

    proj_tasks = []
    if project_ids:
        proj_tasks_q = select(Task).where(Task.project_id.in_(list(project_ids)))
        proj_tasks_res = await db.execute(proj_tasks_q)
        proj_tasks = [t.id for t in proj_tasks_res.scalars().all()]

    assigned_q = select(Task).where(Task.assigned_to == current_user.id)
    assigned_res = await db.execute(assigned_q)
    assigned_tasks = [t.id for t in assigned_res.scalars().all()]

    return {
        "member_project_ids": member_ids,
        "creator_project_ids": creator_ids,
        "project_ids": list(project_ids),
        "proj_task_ids": proj_tasks,
        "assigned_task_ids": assigned_tasks,
    }
