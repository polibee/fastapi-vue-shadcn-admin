from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_user_list_supports_search_and_status_filters(session):
    from server.app.modules.users.model import User
    from server.app.modules.users.repository import UserRepository

    now = datetime.now(timezone.utc)
    session.add_all([
        User(username="alice", email="alice@example.test", password_hash="x", is_active=True, created_at=now, updated_at=now),
        User(username="bob", email="bob@example.test", password_hash="x", is_active=False, created_at=now, updated_at=now),
    ])
    await session.commit()

    users, total = await UserRepository(session).list(0, 20, search="alice", is_active=True)

    assert total == 1
    assert [user.username for user in users] == ["alice"]
