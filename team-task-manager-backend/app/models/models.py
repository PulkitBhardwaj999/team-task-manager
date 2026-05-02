"""
SQLAlchemy models for database tables (SAFE VERSION)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


# ─────────────────────────────────────────────
# ASSOCIATION TABLE
# ─────────────────────────────────────────────

project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "role",
        ENUM(
            UserRole,
            values_callable=lambda x: [e.value for e in x],
            name="userrole",
            create_type=False,
        ),
        nullable=False,
        default=UserRole.MEMBER,
    ),
    Column("created_at", DateTime, default=datetime.utcnow),
)


# ─────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    role = Column(
        ENUM(
            UserRole,
            values_callable=lambda x: [e.value for e in x],
            name="userrole",
            create_type=False,
        ),
        nullable=False,
        default=UserRole.MEMBER,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ✅ SAFE: NO cascade in many-to-many
    projects = relationship(
        "Project",
        secondary=project_members,
        back_populates="members"
    )

    # ✅ SAFE: one-to-many can have delete-orphan
    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.creator_id",
        cascade="all, delete-orphan"
    )

    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_user",
        foreign_keys="Task.assigned_to"
    )


# ─────────────────────────────────────────────
# PROJECT MODEL
# ─────────────────────────────────────────────

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[creator_id]
    )

    # ✅ SAFE: NO cascade here
    members = relationship(
        "User",
        secondary=project_members,
        back_populates="projects"
    )

    # ✅ SAFE: delete project → delete tasks
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────
# TASK MODEL
# ─────────────────────────────────────────────

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    priority = Column(
        ENUM(TaskPriority, name="taskpriority", create_type=False),
        nullable=False,
        default=TaskPriority.MEDIUM,
    )

    status = Column(
        ENUM(TaskStatus, name="taskstatus", create_type=False),
        nullable=False,
        default=TaskStatus.TODO,
    )

    due_date = Column(DateTime, nullable=True)
    is_overdue = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")

    assigned_user = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_to]
    )

    @property
    def assigned_user_name(self):
        from sqlalchemy import inspect
        try:
            insp = inspect(self)
            if "assigned_user" in getattr(insp, "unloaded", set()):
                return None
        except Exception:
            pass
        return self.assigned_user.full_name if self.assigned_user else None