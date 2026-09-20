import asyncio

from sqlalchemy import insert, select

from server.app.core.auth import hash_password
from server.app.core.database.session import SessionFactory
from server.app.modules.permissions.model import Permission, role_permissions
from server.app.modules.roles.model import Role
from server.app.modules.users.model import User, user_roles

DEMO_USERNAME = "integration-admin"
DEMO_EMAIL = "integration-admin@example.test"
DEMO_PASSWORD = "integration-password"
DEMO_PERMISSIONS = ("users.view", "users.create", "users.update", "users.delete", "roles.view", "roles.create", "roles.update", "roles.delete", "audit.view", "tasks.view", "tasks.create", "tasks.cancel", "tasks.retry", "departments.view", "departments.create", "departments.update", "departments.delete")


async def seed_demo_admin() -> None:
    if SessionFactory is None:
        raise RuntimeError("DATABASE_URL must be configured before seeding the demo admin")

    async with SessionFactory() as session:
        user = await session.scalar(select(User).where(User.username == DEMO_USERNAME))
        if user is None:
            user = User(username=DEMO_USERNAME, email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD), is_active=True)
            session.add(user)
        else:
            user.password_hash = hash_password(DEMO_PASSWORD)
            user.is_active = True

        role = await session.scalar(select(Role).where(Role.name == "administrator"))
        if role is None:
            role = Role(name="administrator", description="Development administrator")
            session.add(role)
        await session.flush()
        existing_link = await session.scalar(
            select(user_roles.c.user_id).where(user_roles.c.user_id == user.id, user_roles.c.role_id == role.id)
        )
        if existing_link is None:
            await session.execute(insert(user_roles).values(user_id=user.id, role_id=role.id))

        await session.flush()
        for code in DEMO_PERMISSIONS:
            permission = await session.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=f"Development permission: {code}")
                session.add(permission)
                await session.flush()
            role_link = await session.scalar(
                select(role_permissions.c.role_id).where(
                    role_permissions.c.role_id == role.id,
                    role_permissions.c.permission_id == permission.id,
                )
            )
            if role_link is None:
                await session.execute(insert(role_permissions).values(role_id=role.id, permission_id=permission.id))

        await session.commit()
        print(f"Seeded development admin: {DEMO_USERNAME}")


if __name__ == "__main__":
    asyncio.run(seed_demo_admin())


