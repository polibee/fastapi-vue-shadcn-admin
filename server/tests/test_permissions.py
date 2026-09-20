import pytest

from server.app.core.permissions import can_access_user, user_data_scope, user_has_permission
from server.app.modules.roles.model import Permission, Role
from server.app.modules.users.model import User


@pytest.mark.asyncio
async def test_user_permission_is_granted_through_role(session):
    user = User(username="admin", email="admin@example.test", password_hash="hash")
    role = Role(name="administrator")
    role.permissions.append(Permission(code="users.view", description="View users"))
    user.roles.append(role)
    session.add(user)
    await session.flush()

    assert user_has_permission(user, "users.view") is True
    assert user_has_permission(user, "users.delete") is False


@pytest.mark.asyncio
async def test_self_data_scope_limits_access_to_the_current_user(session):
    user = User(username="scoped", email="scoped@example.test", password_hash="hash")
    role = Role(name="self-only", data_scope="self")
    user.roles.append(role)
    session.add(user)
    await session.flush()

    assert user_data_scope(user) == "self"
    assert can_access_user(user, user.id) is True
    assert can_access_user(user, user.id + 1) is False
