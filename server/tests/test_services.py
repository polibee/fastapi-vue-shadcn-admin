import pytest


@pytest.mark.asyncio
async def test_user_service_creates_and_lists_users_in_stable_order(session):
    from server.app.modules.users.service import DuplicateUserError, UserService

    service = UserService(session)
    first = await service.create(username="alpha", email="alpha@example.test", password_hash="hash-a")
    second = await service.create(username="beta", email="beta@example.test", password_hash="hash-b")

    users, total = await service.list(offset=0, limit=20)
    assert [user.id for user in users] == [first.id, second.id]
    assert total == 2

    sorted_users, _ = await service.list(offset=0, limit=20, sort_by="username", sort_order="desc")
    assert [user.username for user in sorted_users] == ["beta", "alpha"]

    with pytest.raises(DuplicateUserError):
        await service.create(username="alpha", email="other@example.test", password_hash="hash-c")


@pytest.mark.asyncio
async def test_role_service_rejects_duplicate_names(session):
    from server.app.modules.roles.service import DuplicateRoleError, RoleService

    service = RoleService(session)
    await service.create(name="admin", description="Administrator")

    with pytest.raises(DuplicateRoleError):
        await service.create(name="admin", description="Duplicate")
