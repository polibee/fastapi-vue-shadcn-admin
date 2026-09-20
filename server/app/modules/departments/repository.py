from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from .model import Department

class DepartmentRepository:
    def __init__(self, session: AsyncSession): self.session = session
    async def get_by_id(self, department_id: int): return await self.session.scalar(select(Department).where(Department.id == department_id))
    async def get_by_code(self, code: str): return await self.session.scalar(select(Department).where(Department.code == code))
    async def list(self, offset, limit, search, is_active, sort_by, sort_order):
        filters = []
        if search:
            term = f"%{search.strip()}%"
            filters.append(or_(Department.name.ilike(term), Department.code.ilike(term)))
        if is_active is not None: filters.append(Department.is_active == is_active)
        sort_column = {"id": Department.id, "name": Department.name, "code": Department.code}[sort_by]
        order = desc if sort_order == "desc" else asc
        result = await self.session.execute(select(Department).where(*filters).order_by(order(sort_column), Department.id.asc()).offset(offset).limit(limit))
        total = await self.session.scalar(select(func.count()).select_from(Department).where(*filters))
        return list(result.scalars().all()), int(total or 0)
    async def create(self, **values):
        department = Department(**values); self.session.add(department); await self.session.flush(); return department
    async def update(self, department_id, **values):
        department = await self.get_by_id(department_id)
        if department is None: return None
        for key, value in values.items(): setattr(department, key, value)
        await self.session.flush(); return department
    async def delete(self, department_id):
        department = await self.get_by_id(department_id)
        if department is None: return False
        await self.session.delete(department); await self.session.flush(); return True
    async def delete_many(self, ids):
        departments = list((await self.session.scalars(select(Department).where(Department.id.in_(ids)))).all())
        deleted_ids = [department.id for department in departments]
        for department in departments: await self.session.delete(department)
        await self.session.flush(); return deleted_ids
