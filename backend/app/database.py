import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


# Environment takes precedence over the untracked local configuration file.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be configured")
try:
    database_url = make_url(DATABASE_URL)
except Exception:
    raise RuntimeError("DATABASE_URL is invalid") from None
if database_url.drivername != "postgresql+asyncpg":
    raise RuntimeError("DATABASE_URL must use postgresql+asyncpg")
if database_url.password in {None, "", "PASSWORD", "CHANGE_ME"}:
    raise RuntimeError("DATABASE_URL requires a non-placeholder password")

engine = create_async_engine(
    DATABASE_URL, echo=False, pool_pre_ping=True, pool_size=10, max_overflow=20
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        print("PostgreSQL connection failed")
        return False
