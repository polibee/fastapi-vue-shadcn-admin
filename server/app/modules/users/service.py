from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .model import User
from .repository import UserRepository
from server.app.modules.roles.model import Role


class DuplicateUserError(Exception):
    code = "user_already_exists"


class InvalidRoleError(Exception):
    code = "role_not_found"


class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.session = session

    async def list(self, offset: int, limit: int, search: str | None = None, is_active: bool | None = None, sort_by: str = "id", sort_order: str = "asc", scope_user_id: int | None = None) -> tuple[list[User], int]:
        return await self.repository.list(offset, limit, search, is_active, sort_by, sort_order, scope_user_id)

    async def create(self, **values) -> User:
        if await self.repository.get_by_username(values["username"]) or await self.repository.get_by_email(values["email"]):
            raise DuplicateUserError
        try:
            user = await self.repository.create(**values)
            await self.session.commit()
            return await self.repository.get_by_id(user.id)  # type: ignore[return-value]
        except IntegrityError as error:
            await self.session.rollback()
            raise DuplicateUserError from error

    async def delete(self, user_id: int) -> bool:
        deleted = await self.repository.delete(user_id)
        if deleted:
            await self.session.commit()
        return deleted

    async def delete_many(self, user_ids: list[int]) -> list[int]:
        return await self.repository.delete_many(sorted(set(user_ids)))

    async def update_roles(self, user_id: int, names: list[str]) -> User | None:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            return None
        normalized = sorted(set(name.strip() for name in names if name.strip()))
        roles = list((await self.session.scalars(select(Role).where(Role.name.in_(normalized)))).all())
        if len(roles) != len(normalized):
            raise InvalidRoleError
        user.roles = roles
        await self.session.commit()
        return await self.repository.get_by_id(user_id)
