from __future__ import annotations

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .model import User
from server.app.modules.roles.model import Role


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.roles).selectinload(Role.permissions)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list(self, offset: int, limit: int, search: str | None = None, is_active: bool | None = None, sort_by: str = "id", sort_order: str = "asc", scope_user_id: int | None = None) -> tuple[list[User], int]:
        filters = []
        if search:
            term = f"%{search.strip()}%"
            filters.append(or_(User.username.ilike(term), User.email.ilike(term)))
        if is_active is not None:
            filters.append(User.is_active == is_active)
        if scope_user_id is not None:
            filters.append(User.id == scope_user_id)
        sort_column = {"id": User.id, "username": User.username, "email": User.email}[sort_by]
        query = select(User).options(selectinload(User.roles)).where(*filters).order_by((desc if sort_order == "desc" else asc)(sort_column), User.id.asc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        total = await self.session.scalar(select(func.count()).select_from(User).where(*filters))
        return list(result.scalars().all()), int(total or 0)

    async def create(self, **values) -> User:
        user = User(**values)
        self.session.add(user)
        await self.session.flush()
        return user

    async def delete(self, user_id: int) -> bool:
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        await self.session.delete(user)
        await self.session.flush()
        return True

    async def delete_many(self, user_ids: list[int]) -> list[int]:
        users = list((await self.session.scalars(select(User).where(User.id.in_(user_ids)))).all())
        deleted_ids = [user.id for user in users]
        for user in users:
            await self.session.delete(user)
        await self.session.flush()
        return deleted_ids
