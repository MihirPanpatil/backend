# app/api/db/database.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text
from app.api.core.config import settings
from app.api.db.models import Base  # Imports the declarative base from models.py

# Create async engine
ENGINE = create_async_engine(
    settings.DATABASE_URL,  # Already includes asyncpg in the URL
    echo=True,  # Set to False in production
    future=True
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Dependency to get DB session
async def get_db() -> AsyncSession:
    """Dependency that provides db session for each request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def init_models():
    """Initialize database models."""
    async with ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)