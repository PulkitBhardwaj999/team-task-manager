"""
Project service - business logic for project operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, insert, select, and_, func
from sqlalchemy.orm import selectinload
from app.models.models import Project, User, Task, TaskStatus, project_members, UserRole as ModelUserRole
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectMemberAdd
from fastapi import HTTPException, status

class ProjectService:
    """Service for project operations"""
    
    @staticmethod
    async def create_project(db: AsyncSession, creator_id: int, project_create: ProjectCreate) -> Project:
        """Create a new project"""
        db_project = Project(
            name=project_create.name,
            description=project_create.description,
            creator_id=creator_id
        )
        db.add(db_project)
        await db.commit()
        await db.refresh(db_project)
        
        # Add creator as admin member without triggering async lazy loading.
        await db.execute(
            insert(project_members).values(
                project_id=db_project.id,
                user_id=creator_id,
                role=ModelUserRole.ADMIN,
            )
        )
        await db.commit()
        
        return db_project
    
    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: int) -> Project | None:
        """Get project by ID"""
        query = (
            select(Project)
            .options(
                selectinload(Project.creator),
                selectinload(Project.members),
                selectinload(Project.tasks),
            )
            .where(Project.id == project_id)
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    @staticmethod
    async def get_user_projects(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> list[Project]:
        """Get all projects for a user"""
        query = (
            select(Project)
            .options(selectinload(Project.members), selectinload(Project.creator), selectinload(Project.tasks))
            .join(project_members)
            .where(project_members.c.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_project(db: AsyncSession, project_id: int, user_id: int, project_update: ProjectUpdate) -> Project:
        """Update a project"""
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user is creator or admin
        if project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this project"
            )
        
        if project_update.name:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description
        
        await db.commit()
        await db.refresh(project)
        return project
    
    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int, user_id: int) -> None:
        """Delete a project"""
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if user is creator
        if project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this project"
            )
        
        await db.delete(project)
        await db.commit()
    
    @staticmethod
    async def add_project_member(db: AsyncSession, project_id: int, user_id: int, 
                                 member_add: ProjectMemberAdd) -> Project:
        """Add a member to a project"""
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if requester is project creator
        if project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add members"
            )
        
        # Check if user exists
        stmt = select(User).where(User.id == member_add.user_id)
        result = await db.execute(stmt)
        member = result.scalars().first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        membership_query = select(project_members.c.user_id).where(
            project_members.c.project_id == project_id,
            project_members.c.user_id == member_add.user_id,
        )
        membership_result = await db.execute(membership_query)
        if membership_result.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a project member"
            )

        await db.execute(
            insert(project_members).values(
                project_id=project_id,
                user_id=member_add.user_id,
                role=ModelUserRole(member_add.role.value),
            )
        )
        await db.commit()
        return await ProjectService.get_project_by_id(db, project_id)
    
    @staticmethod
    async def remove_project_member(db: AsyncSession, project_id: int, user_id: int, member_id: int) -> Project:
        """Remove a member from a project"""
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if requester is project creator
        if project.creator_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove members"
            )
        
        # Check if user exists
        stmt = select(User).where(User.id == member_id)
        result = await db.execute(stmt)
        member = result.scalars().first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
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
        """Get project progress statistics"""
        project = await ProjectService.get_project_by_id(db, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        total_query = select(func.count()).select_from(Task).where(Task.project_id == project_id)
        total_result = await db.execute(total_query)
        total_tasks = total_result.scalar_one()

        completed_query = select(func.count()).select_from(Task).where(
            Task.project_id == project_id,
            Task.status == TaskStatus.DONE,
        )
        completed_result = await db.execute(completed_query)
        completed_tasks = completed_result.scalar_one()
        
        progress = 0 if total_tasks == 0 else (completed_tasks / total_tasks) * 100
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "progress_percentage": round(progress, 2)
        }
