"""
Database connection and session management
PostgreSQL + PostGIS via SQLAlchemy async
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency: get database session"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """Health check: verify database connectivity"""
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception:
        return False
