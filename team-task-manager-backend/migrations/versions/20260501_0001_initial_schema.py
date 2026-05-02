"""initial schema

Revision ID: 20260501_0001
Revises:
Create Date: 2026-05-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "20260501_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    user_role_enum = ENUM("ADMIN", "MEMBER", name="userrole")
    task_priority_enum = ENUM("LOW", "MEDIUM", "HIGH", name="taskpriority")
    task_status_enum = ENUM("TODO", "IN_PROGRESS", "DONE", name="taskstatus")

    user_role_enum.create(op.get_bind(), checkfirst=True)
    task_priority_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)

    user_role = ENUM("ADMIN", "MEMBER", name="userrole", create_type=False)
    task_priority = ENUM("LOW", "MEDIUM", "HIGH", name="taskpriority", create_type=False)
    task_status = ENUM("TODO", "IN_PROGRESS", "DONE", name="taskstatus", create_type=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)

    op.create_table(
        "project_members",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "user_id"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("assigned_to", sa.Integer(), nullable=True),
        sa.Column("priority", task_priority, nullable=False),
        sa.Column("status", task_status, nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("is_overdue", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tasks_id"), "tasks", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_id"), table_name="tasks")
    op.drop_table("tasks")
    op.drop_table("project_members")
    op.drop_index(op.f("ix_projects_id"), table_name="projects")
    op.drop_table("projects")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")

    ENUM(name="taskstatus").drop(op.get_bind(), checkfirst=True)
    ENUM(name="taskpriority").drop(op.get_bind(), checkfirst=True)
    ENUM(name="userrole").drop(op.get_bind(), checkfirst=True)
