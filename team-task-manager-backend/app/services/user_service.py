"""
User service - business logic for user operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.models import User, UserRole
from app.schemas.schemas import UserCreate
from app.core.security import hash_password, verify_password


class UserService:
    """Service for user operations"""

    @staticmethod
    async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user.

        Role flow
        ---------
        1. Frontend sends { role: "admin" } or { role: "member" }
        2. Pydantic (UserCreate.normalize_role) normalises casing → lowercase str
        3. Here we convert that string to models.UserRole enum using .value lookup
        4. We pass the ENUM INSTANCE (not .value, not .name) to the ORM column.
           SQLAlchemy with asyncpg knows how to serialise it as the correct
           lowercase string that matches the PostgreSQL enum values.

        NEVER do:
            role = role.name   ← returns 'ADMIN' / 'MEMBER' (uppercase) → DB crash
            role = role.value  ← returns plain str, bypasses ORM enum mapping
        ALWAYS do:
            role = UserRole("admin")  ← gives the enum instance, ORM handles rest
        """

        # ── 1. duplicate-email guard ───────────────────────────────────────────
        existing = await UserService.get_user_by_email(db, user_create.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # ── 2. resolve role to models.UserRole enum instance ──────────────────
        #
        # user_create.role is already normalised to lowercase by Pydantic's
        # @field_validator("role", mode="before") in schemas.py.
        # We just need to bridge schemas.UserRole → models.UserRole via value.
        #
        incoming_role = (user_create.role or "member").strip().lower()

        try:
            role = UserRole(incoming_role)
        except ValueError:
            # Unknown value — safe fallback; log and continue
            print(f"[UserService] WARNING: unknown role '{incoming_role}', "
                  f"defaulting to MEMBER")
            role = UserRole.MEMBER

        # ── 3. debug logging (remove / guard with settings.DEBUG in prod) ──────
        print(f"[UserService.create_user] email={user_create.email!r}")
        print(f"[UserService.create_user] incoming role string : {incoming_role!r}")
        print(f"[UserService.create_user] resolved model enum  : {role!r}  "
              f"(value={role.value!r})")

        # ── 4. hash password ───────────────────────────────────────────────────
        hashed_password = hash_password(user_create.password)

        # ── 5. persist ─────────────────────────────────────────────────────────
        #
        # Pass the enum INSTANCE — NOT role.value / role.name.
        # asyncpg + SQLAlchemy will write the correct lowercase string
        # ('admin' or 'member') that matches the PostgreSQL enum after
        # the migration has been applied.
        #
        db_user = User(
            email=user_create.email,
            full_name=user_create.full_name,
            hashed_password=hashed_password,
            role=role,          # ← enum instance, not role.value / role.name
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        print(f"[UserService.create_user] user created: id={db_user.id}  "
              f"role={db_user.role!r}")
        return db_user

    # ── helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> User | None:
        user = await UserService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def get_all_users(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()