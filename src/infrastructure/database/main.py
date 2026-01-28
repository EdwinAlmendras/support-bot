from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.infrastructure.database.models import Base
import os

DB_PATH = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data/bot.db")
# Fix for some postgres connection strings (e.g. from Heroku/Supabase) relying on explicit driver
if DB_PATH.startswith("postgres://"):
    DB_PATH = DB_PATH.replace("postgres://", "postgresql+asyncpg://", 1)
elif DB_PATH.startswith("postgresql://") and "+asyncpg" not in DB_PATH:
     DB_PATH = DB_PATH.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(DB_PATH, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from typing import AsyncGenerator

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
