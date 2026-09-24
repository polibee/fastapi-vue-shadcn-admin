from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .model import Role
from .repository import RoleRepository
from server.app.modules.permissions.model import Permission


class DuplicateRoleError(Exception):
    code = "role_already_exists"


class InvalidPermissionError(Exception):
    code = "permission_not_found"


class InvalidDataScopeError(Exception):
    code = "data_scope_not_supported"


class RoleService:
    def __init__(self, session: AsyncSession):
        self.repository = RoleRepository(session)
        self.session = session

    async def list(self, offset: int, limit: int, search: str | None = None, sort_by: str = "id", sort_order: str = "asc") -> tuple[list[Role], int]:
        return await self.repository.list(offset, limit, search, sort_by, sort_order)

    async def get(self, role_id: int) -> Role | None:
        return await self.repository.get_by_id(role_id)

    async def create(self, **values) -> Role:
        if await self.repository.get_by_name(values["name"]):
            raise DuplicateRoleError
        try:
            role = await self.repository.create(**values)
            await self.session.commit()
            return await self.repository.get_by_id(role.id)  # type: ignore[return-value]
        except IntegrityError as error:
            await self.session.rollback()
            raise DuplicateRoleError from error

    async def update(self, role_id: int, **values) -> Role | None:
        existing = await self.repository.get_by_id(role_id)
        if existing is None:
            return None
        duplicate = await self.repository.get_by_name(values["name"])
        if duplicate is not None and duplicate.id != role_id:
            raise DuplicateRoleError
        role = await self.repository.update(role_id, **values)
        await self.session.commit()
        return await self.repository.get_by_id(role_id)

    async def delete(self, role_id: int) -> bool:
        deleted = await self.repository.delete(role_id)
        if deleted:
            await self.session.commit()
        return deleted

    async def delete_many(self, role_ids: list[int]) -> list[int]:
        return await self.repository.delete_many(sorted(set(role_ids)))

    async def update_permissions(self, role_id: int, codes: list[str]) -> Role | None:
        role = await self.repository.get_by_id(role_id)
        if role is None:
            return None
        normalized = sorted(set(code.strip() for code in codes if code.strip()))
        if role.name == "administrator":
            permissions = list((await self.session.scalars(select(Permission).order_by(Permission.code.asc()))).all())
        else:
            permissions = list((await self.session.scalars(select(Permission).where(Permission.code.in_(normalized)))).all())
        if role.name != "administrator" and len(permissions) != len(normalized):
            raise InvalidPermissionError
        role.permissions = permissions
        await self.session.commit()
        return await self.repository.get_by_id(role_id)

    async def update_data_scope(self, role_id: int, data_scope: str) -> Role | None:
        if data_scope not in {"all", "self"}:
            raise InvalidDataScopeError
        role = await self.repository.get_by_id(role_id)
        if role is None:
            return None
        role.data_scope = data_scope
        await self.session.commit()
        return await self.repository.get_by_id(role_id)
