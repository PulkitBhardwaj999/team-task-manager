"""fix enum case - migrate ADMIN/MEMBER to admin/member

This migration fixes the case mismatch between the PostgreSQL enum values
created in the initial migration (UPPERCASE: ADMIN, MEMBER, LOW, MEDIUM, etc.)
and the SQLAlchemy model enum values (lowercase: admin, member, low, medium, etc.).

PostgreSQL enum values ARE case-sensitive.  The initial migration created them
as 'ADMIN' / 'MEMBER' but the ORM models declare them as 'admin' / 'member',
so every write silently failed the enum constraint and fell back to the default.

Strategy:
  1. Create new enums with lowercase values
  2. ALTER each column to use the new enum (casting via text)
  3. Drop the old uppercase enums

Revision ID: 20260502_0001
Revises: 20260501_0001
Create Date: 2026-05-02 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision: str = "20260502_0001"
down_revision: Union[str, None] = "20260501_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Create lowercase replacement enums
    # ------------------------------------------------------------------
    conn.execute(sa.text(
        "CREATE TYPE userrole_new AS ENUM ('admin', 'member')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskpriority_new AS ENUM ('low', 'medium', 'high')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskstatus_new AS ENUM ('todo', 'in_progress', 'done')"
    ))

    # ------------------------------------------------------------------
    # 2. Migrate each column that uses the old uppercase enum
    # ------------------------------------------------------------------

    # users.role  (ADMIN -> admin, MEMBER -> member)
    conn.execute(sa.text("""
        ALTER TABLE users
            ALTER COLUMN role TYPE userrole_new
            USING lower(role::text)::userrole_new
    """))

    # project_members.role
    conn.execute(sa.text("""
        ALTER TABLE project_members
            ALTER COLUMN role TYPE userrole_new
            USING lower(role::text)::userrole_new
    """))

    # tasks.priority  (LOW -> low, MEDIUM -> medium, HIGH -> high)
    conn.execute(sa.text("""
        ALTER TABLE tasks
            ALTER COLUMN priority TYPE taskpriority_new
            USING lower(priority::text)::taskpriority_new
    """))

    # tasks.status  (TODO -> todo, IN_PROGRESS -> in_progress, DONE -> done)
    conn.execute(sa.text("""
        ALTER TABLE tasks
            ALTER COLUMN status TYPE taskstatus_new
            USING lower(status::text)::taskstatus_new
    """))

    # ------------------------------------------------------------------
    # 3. Drop old uppercase enums and rename new ones into place
    # ------------------------------------------------------------------
    conn.execute(sa.text("DROP TYPE userrole"))
    conn.execute(sa.text("ALTER TYPE userrole_new RENAME TO userrole"))

    conn.execute(sa.text("DROP TYPE taskpriority"))
    conn.execute(sa.text("ALTER TYPE taskpriority_new RENAME TO taskpriority"))

    conn.execute(sa.text("DROP TYPE taskstatus"))
    conn.execute(sa.text("ALTER TYPE taskstatus_new RENAME TO taskstatus"))


def downgrade() -> None:
    conn = op.get_bind()

    # Reverse: create uppercase enums, migrate back, drop lowercase ones
    conn.execute(sa.text(
        "CREATE TYPE userrole_old AS ENUM ('ADMIN', 'MEMBER')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskpriority_old AS ENUM ('LOW', 'MEDIUM', 'HIGH')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskstatus_old AS ENUM ('TODO', 'IN_PROGRESS', 'DONE')"
    ))

    conn.execute(sa.text("""
        ALTER TABLE users
            ALTER COLUMN role TYPE userrole_old
            USING upper(role::text)::userrole_old
    """))
    conn.execute(sa.text("""
        ALTER TABLE project_members
            ALTER COLUMN role TYPE userrole_old
            USING upper(role::text)::userrole_old
    """))
    conn.execute(sa.text("""
        ALTER TABLE tasks
            ALTER COLUMN priority TYPE taskpriority_old
            USING upper(priority::text)::taskpriority_old
    """))
    conn.execute(sa.text("""
        ALTER TABLE tasks
            ALTER COLUMN status TYPE taskstatus_old
            USING upper(status::text)::taskstatus_old
    """))

    conn.execute(sa.text("DROP TYPE userrole"))
    conn.execute(sa.text("ALTER TYPE userrole_old RENAME TO userrole"))

    conn.execute(sa.text("DROP TYPE taskpriority"))
    conn.execute(sa.text("ALTER TYPE taskpriority_old RENAME TO taskpriority"))

    conn.execute(sa.text("DROP TYPE taskstatus"))
    conn.execute(sa.text("ALTER TYPE taskstatus_old RENAME TO taskstatus"))