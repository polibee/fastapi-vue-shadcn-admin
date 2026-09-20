from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from server.app.core.config import get_settings


def _create_engine() -> AsyncEngine | None:
    database_url = get_settings().database_url
    if not database_url:
        return None
    return create_async_engine(database_url, pool_pre_ping=True)


engine = _create_engine()
SessionFactory = async_sessionmaker(engine, expire_on_commit=False) if engine else None


async def get_session() -> AsyncIterator[AsyncSession]:
    if SessionFactory is None:
        raise DatabaseNotConfiguredError("DATABASE_URL is not configured")
    async with SessionFactory() as session:
        yield session
class DatabaseNotConfiguredError(RuntimeError):
    code = "database_not_configured"

