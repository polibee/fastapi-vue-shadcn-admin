from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from .model import Department
from .repository import DepartmentRepository

class DuplicateDepartmentError(Exception): code = "department_already_exists"

class DepartmentService:
    def __init__(self, session: AsyncSession): self.repository = DepartmentRepository(session); self.session = session
    async def list(self, *args, **kwargs): return await self.repository.list(*args, **kwargs)
    async def get(self, department_id): return await self.repository.get_by_id(department_id)
    async def create(self, **values):
        if await self.repository.get_by_code(values["code"]): raise DuplicateDepartmentError
        try:
            department = await self.repository.create(**values); await self.session.commit(); return await self.repository.get_by_id(department.id)
        except IntegrityError as error:
            await self.session.rollback(); raise DuplicateDepartmentError from error
    async def update(self, department_id, **values):
        current = await self.repository.get_by_id(department_id)
        if current is None: return None
        duplicate = await self.repository.get_by_code(values["code"])
        if duplicate is not None and duplicate.id != department_id: raise DuplicateDepartmentError
        try:
            department = await self.repository.update(department_id, **values); await self.session.commit(); return await self.repository.get_by_id(department_id)
        except IntegrityError as error:
            await self.session.rollback(); raise DuplicateDepartmentError from error
    async def delete(self, department_id):
        deleted = await self.repository.delete(department_id)
        if deleted: await self.session.commit()
        return deleted
    async def delete_many(self, ids): return await self.repository.delete_many(sorted(set(ids)))
