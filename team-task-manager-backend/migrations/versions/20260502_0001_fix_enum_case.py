"""fix enum case - lowercase all enum values in PostgreSQL

Root cause: the initial migration created PostgreSQL enums with UPPERCASE
values ('ADMIN', 'MEMBER', 'LOW', 'MEDIUM', 'HIGH', 'TODO', 'IN_PROGRESS',
'DONE') but the SQLAlchemy models declare them with lowercase values
('admin', 'member', 'low', 'medium', 'high', 'todo', 'in_progress', 'done').

PostgreSQL ENUM values are case-sensitive. Every write from the ORM was
sending lowercase strings against an UPPERCASE-only enum, causing:
  - "invalid input value for enum userrole: 'admin'" (or 'member')
  - 500 errors + transaction rollbacks
  - The browser sees no response → reports a fake CORS error

Fix: migrate all enum columns to lowercase values without data loss.

Revision ID: 20260502_0001
Revises: 20260501_0001
Create Date: 2026-05-02 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "20260502_0001"
down_revision: Union[str, None] = "20260501_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------ #
    # Step 1 – create new lowercase enum types                            #
    # ------------------------------------------------------------------ #
    conn.execute(sa.text(
        "CREATE TYPE userrole_new      AS ENUM ('admin', 'member')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskpriority_new  AS ENUM ('low', 'medium', 'high')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskstatus_new    AS ENUM ('todo', 'in_progress', 'done')"
    ))

    # ------------------------------------------------------------------ #
    # Step 2 – migrate each column (UPPERCASE → lowercase via lower())    #
    # ------------------------------------------------------------------ #

    # users.role
    conn.execute(sa.text("""
        ALTER TABLE users
            ALTER COLUMN role
            TYPE userrole_new
            USING lower(role::text)::userrole_new
    """))

    # project_members.role
    conn.execute(sa.text("""
        ALTER TABLE project_members
            ALTER COLUMN role
            TYPE userrole_new
            USING lower(role::text)::userrole_new
    """))

    # tasks.priority
    conn.execute(sa.text("""
        ALTER TABLE tasks
            ALTER COLUMN priority
            TYPE taskpriority_new
            USING lower(priority::text)::taskpriority_new
    """))

    # tasks.status  (IN_PROGRESS → in_progress needs the underscore preserved)
    # lower() on 'IN_PROGRESS' gives 'in_progress' — correct.
    conn.execute(sa.text("""
        ALTER TABLE tasks
            ALTER COLUMN status
            TYPE taskstatus_new
            USING lower(status::text)::taskstatus_new
    """))

    # ------------------------------------------------------------------ #
    # Step 3 – drop old UPPERCASE types and rename new ones into place    #
    # ------------------------------------------------------------------ #
    conn.execute(sa.text("DROP TYPE userrole"))
    conn.execute(sa.text("ALTER TYPE userrole_new     RENAME TO userrole"))

    conn.execute(sa.text("DROP TYPE taskpriority"))
    conn.execute(sa.text("ALTER TYPE taskpriority_new RENAME TO taskpriority"))

    conn.execute(sa.text("DROP TYPE taskstatus"))
    conn.execute(sa.text("ALTER TYPE taskstatus_new   RENAME TO taskstatus"))


def downgrade() -> None:
    """Reverse: lowercase → UPPERCASE (data is uppercased with upper())."""
    conn = op.get_bind()

    conn.execute(sa.text(
        "CREATE TYPE userrole_old     AS ENUM ('ADMIN', 'MEMBER')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskpriority_old AS ENUM ('LOW', 'MEDIUM', 'HIGH')"
    ))
    conn.execute(sa.text(
        "CREATE TYPE taskstatus_old   AS ENUM ('TODO', 'IN_PROGRESS', 'DONE')"
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
    conn.execute(sa.text("ALTER TYPE userrole_old     RENAME TO userrole"))

    conn.execute(sa.text("DROP TYPE taskpriority"))
    conn.execute(sa.text("ALTER TYPE taskpriority_old RENAME TO taskpriority"))

    conn.execute(sa.text("DROP TYPE taskstatus"))
    conn.execute(sa.text("ALTER TYPE taskstatus_old   RENAME TO taskstatus"))