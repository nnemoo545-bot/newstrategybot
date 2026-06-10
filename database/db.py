# Copilot prompt:
# "Implement SQLAlchemy async engine/session helper for DATABASE_URL from config. Provide get_engine(), get_session() (async context manager). If DATABASE_URL is sqlite file, use check_same_thread handling synchronous fallback."
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from ..config import settings

# If DATABASE_URL is sqlite:///./trading.db, convert to async driver
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("sqlite:///"):
    async_database_url = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    async_database_url = DATABASE_URL  # assume async-compatible

engine = create_async_engine(async_database_url, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
