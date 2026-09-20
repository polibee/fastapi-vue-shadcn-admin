import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from server.app.core.auth import create_access_token, hash_password
from server.app.core.database.base import Base
from server.app.modules.audit.model import AuditLog
from server.app.modules.tasks.model import Task
from server.app.modules.roles.model import Permission, Role
from server.app.modules.users.model import User


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db:
        yield db
    await engine.dispose()


@pytest_asyncio.fixture
async def admin_headers(session):
    role = Role(
        name="test-administrator",
        permissions=[
            Permission(code="users.view"),
            Permission(code="users.create"),
            Permission(code="users.delete"),
            Permission(code="users.update"),
            Permission(code="roles.view"),
            Permission(code="roles.create"),
            Permission(code="roles.update"),
            Permission(code="roles.delete"),
            Permission(code="audit.view"),
            Permission(code="tasks.view"),
            Permission(code="tasks.create"),
            Permission(code="tasks.cancel"),
            Permission(code="tasks.retry"),
        ],
    )
    user = User(username="test-admin", email="test-admin@example.test", password_hash=hash_password("secret"), roles=[role])
    session.add(user)
    await session.flush()
    return {"Authorization": f"Bearer {create_access_token(str(user.id))}"}
