"""
Project service - business logic for project operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, func
from sqlalchemy.orm import selectinload
from app.models.models import Project, User, Task, TaskStatus, project_members, UserRole
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectMemberAdd
from fastapi import HTTPException, status


class ProjectService:

    @staticmethod
    async def create_project(db: AsyncSession, creator_id: int, project_create: ProjectCreate) -> Project:
        db_project = Project(
            name=project_create.name,
            description=project_create.description,
            creator_id=creator_id,
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)

        # Add creator as admin member — write the lowercase string value
        await db.execute(
            insert(project_members).values(
                project_id=db_project.id,
                user_id=creator_id,
                role=UserRole.ADMIN.value,   # ← 'admin' not UserRole.ADMIN
            )
        )
        await db.commit()
        return db_project

    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: int) -> Project | None:
        result = await db.execute(
            select(Project)
            .options(
                selectinload(Project.creator),
                selectinload(Project.members),
                selectinload(Project.tasks),
            )
            .where(Project.id == project_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_user_projects(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Project]:
        result = await db.execute(
            select(Project)
            .options(
                selectinload(Project.members),
                selectinload(Project.creator),
                selectinload(Project.tasks),
            )
            .join(project_members)
            .where(project_members.c.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_project(
        db: AsyncSession, project_id: int, user_id: int, project_update: ProjectUpdate
    ) -> Project:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if project.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this project")

        if project_update.name:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> None:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if project.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this project")

        await db.delete(project)
        await db.commit()

    @staticmethod
    async def add_project_member(
        db: AsyncSession, project_id: int, user_id: int, member_add: ProjectMemberAdd
    ) -> Project:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if project.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add members")

        member = (await db.execute(select(User).where(User.id == member_add.user_id))).scalars().first()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        existing = (await db.execute(
            select(project_members.c.user_id).where(
                project_members.c.project_id == project_id,
                project_members.c.user_id == member_add.user_id,
            )
        )).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a project member")

        # Write the lowercase string value for role
        role_value = member_add.role.value if hasattr(member_add.role, 'value') else str(member_add.role).lower()
        await db.execute(
            insert(project_members).values(
                project_id=project_id,
                user_id=member_add.user_id,
                role=role_value,            # ← always lowercase string
            )
        )
        await db.commit()
        return await ProjectService.get_project_by_id(db, project_id)

    @staticmethod
    async def remove_project_member(
        db: AsyncSession, project_id: int, user_id: int, member_id: int
    ) -> Project:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if project.creator_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to remove members")

        member = (await db.execute(select(User).where(User.id == member_id))).scalars().first()
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await db.execute(
            delete(project_members).where(
                project_members.c.project_id == project_id,
                project_members.c.user_id == member_id,
            )
        )
        await db.commit()
        return await ProjectService.get_project_by_id(db, project_id)

    @staticmethod
    async def get_project_progress(db: AsyncSession, project_id: int) -> dict:
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        total = (await db.execute(
            select(func.count()).select_from(Task).where(Task.project_id == project_id)
        )).scalar_one()

        completed = (await db.execute(
            select(func.count()).select_from(Task).where(
                Task.project_id == project_id,
                Task.status == TaskStatus.DONE.value,   # ← lowercase string
            )
        )).scalar_one()

        progress = 0 if total == 0 else (completed / total) * 100

        return {
            "total_tasks": total,
            "completed_tasks": completed,
            "progress_percentage": round(progress, 2),
        }