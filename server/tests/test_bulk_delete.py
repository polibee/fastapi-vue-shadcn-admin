from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_user_bulk_delete_returns_existing_ids_and_skips_missing(session):
    from sqlalchemy import select

    from server.app.modules.users.model import User
    from server.app.modules.users.service import UserService

    now = datetime.now(timezone.utc)
    session.add_all([
        User(username="bulk-a", email="bulk-a@example.test", password_hash="x", created_at=now, updated_at=now),
        User(username="bulk-b", email="bulk-b@example.test", password_hash="x", created_at=now, updated_at=now),
    ])
    await session.flush()
    ids = list((await session.scalars(select(User).where(User.username.like("bulk-%")))).all())
    deleted = await UserService(session).delete_many([user.id for user in ids] + [999999])
    await session.commit()

    assert sorted(deleted) == sorted(user.id for user in ids)
    assert await session.scalar(select(User).where(User.username == "bulk-a")) is None
