from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .model import Role


class RoleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def get_by_id(self, role_id: int) -> Role | None:
        result = await self.session.execute(select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def list(self, offset: int, limit: int, search: str | None = None, sort_by: str = "id", sort_order: str = "asc") -> tuple[list[Role], int]:
        filters = [Role.name.ilike(f"%{search.strip()}%") if search else True]
        sort_column = {"id": Role.id, "name": Role.name}[sort_by]
        result = await self.session.execute(select(Role).options(selectinload(Role.permissions)).where(*filters).order_by((desc if sort_order == "desc" else asc)(sort_column), Role.id.asc()).offset(offset).limit(limit))
        total = await self.session.scalar(select(func.count()).select_from(Role).where(*filters))
        return list(result.scalars().all()), int(total or 0)

    async def create(self, **values) -> Role:
        role = Role(**values)
        self.session.add(role)
        await self.session.flush()
        return role

    async def delete(self, role_id: int) -> bool:
        role = await self.get_by_id(role_id)
        if role is None:
            return False
        await self.session.delete(role)
        await self.session.flush()
        return True

    async def delete_many(self, role_ids: list[int]) -> list[int]:
        roles = list((await self.session.scalars(select(Role).where(Role.id.in_(role_ids)))).all())
        deleted_ids = [role.id for role in roles]
        for role in roles:
            await self.session.delete(role)
        await self.session.flush()
        return deleted_ids
