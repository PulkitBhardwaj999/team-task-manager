"""
Database configuration and session management
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from .config import settings

# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()

async def get_db() -> AsyncSession:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Verify database connectivity on startup.

    Schema changes are managed by Alembic migrations.
    """
    async with engine.connect():
        return

async def close_db():
    """Close database connections"""
    await engine.dispose()
