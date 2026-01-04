from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.config import get_settings

settings = get_settings()

# Synchronous engine for migrations
sync_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    echo=settings.environment == "development",
)

# Asynchronous engine for FastAPI
async_engine = create_async_engine(
    settings.async_database_url,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    echo=settings.environment == "development",
)

# Session factories
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# For Alembic migrations
def get_sync_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()