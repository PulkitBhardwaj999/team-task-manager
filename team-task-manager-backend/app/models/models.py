"""
SQLAlchemy models for database tables
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


# ─────────────────────────────────────────────
# ENUMS
# All values are lowercase to match the PostgreSQL enum values
# created by migration 20260502_0001_fix_enum_case
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


# Helper: extracts the .value from each enum member so that
# SQLAlchemy/asyncpg writes the lowercase string ('admin', 'medium', etc.)
# instead of the enum .name ('ADMIN', 'MEDIUM') which would fail against
# the lowercase PostgreSQL enums created by the fix_enum_case migration.
def _enum_values(enum_class):
    return [e.value for e in enum_class]


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
            *_enum_values(UserRole),    # 'admin', 'member'
            name="userrole",
            create_type=False,
        ),
        nullable=False,
        default=UserRole.MEMBER.value,
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
            *_enum_values(UserRole),    # 'admin', 'member'
            name="userrole",
            create_type=False,
        ),
        nullable=False,
        default=UserRole.MEMBER.value,
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    projects = relationship(
        "Project",
        secondary=project_members,
        back_populates="members",
    )

    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.creator_id",
        cascade="all, delete-orphan",
    )

    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_user",
        foreign_keys="Task.assigned_to",
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
        foreign_keys=[creator_id],
    )

    members = relationship(
        "User",
        secondary=project_members,
        back_populates="projects",
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
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
        ENUM(
            *_enum_values(TaskPriority),    # 'low', 'medium', 'high'
            name="taskpriority",
            create_type=False,
        ),
        nullable=False,
        default=TaskPriority.MEDIUM.value,
    )

    status = Column(
        ENUM(
            *_enum_values(TaskStatus),      # 'todo', 'in_progress', 'done'
            name="taskstatus",
            create_type=False,
        ),
        nullable=False,
        default=TaskStatus.TODO.value,
    )

    due_date = Column(DateTime, nullable=True)
    is_overdue = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")

    assigned_user = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_to],
    )

    @property
    def assigned_user_name(self) -> str | None:
        """Return the assignee's full name without triggering lazy IO."""
        from sqlalchemy import inspect as sa_inspect
        try:
            state = sa_inspect(self)
            if "assigned_user" in getattr(state, "unloaded", set()):
                return None
        except Exception:
            pass
        return self.assigned_user.full_name if self.assigned_user else None