"""Deterministic, resource-aware scaffold templates."""

from server.app.core.resources.contract import FieldType, ResourceDefinition
from server.app.core.generator.plan import build_crud_generation_plan


def _class_name(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in name.split("_"))


def _singular(name: str) -> str:
    return name[:-1] if name.endswith("s") and len(name) > 1 else name


def _sql_type(field_type: FieldType) -> str:
    return {
        FieldType.text: "String(255)",
        FieldType.email: "String(255)",
        FieldType.password: "String(255)",
        FieldType.boolean: "Boolean",
        FieldType.datetime: "DateTime(timezone=True)",
    }[field_type]


def _python_type(field_type: FieldType) -> str:
    return {
        FieldType.text: "str",
        FieldType.email: "str",
        FieldType.password: "str",
        FieldType.boolean: "bool",
        FieldType.datetime: "datetime",
    }[field_type]


def render_generated_files(resource: ResourceDefinition) -> dict[str, str]:
    """Render all files declared by a CRUD plan for one resource."""
    class_name = _class_name(_singular(resource.name))
    module = f"server/app/modules/{resource.name}"
    model_fields = [
        f'    {field.name}: Mapped[{_python_type(field.type)}] = mapped_column({_sql_type(field.type)}, nullable={str(field.nullable).lower()})'
        for field in resource.fields
        if field.name != "id"
    ]
    schema_fields = [
        f"    {field.name}: {_python_type(field.type)}"
        for field in resource.fields
        if not field.readonly and field.name != "password"
    ]
    schema_fields.append("    model_config = ConfigDict(from_attributes=True)")
    model = f'''"""Generated model scaffold for {resource.name}."""
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from server.app.core.database.base import Base


class {class_name}(Base):
    __tablename__ = "{resource.name}"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
{chr(10).join(model_fields)}
'''
    schema = f'''"""Generated schema scaffold for {resource.name}."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class {class_name}Create(BaseModel):
{chr(10).join(schema_fields[:-1]) or "    pass"}


class {class_name}Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
{chr(10).join(schema_fields[:-1])}
'''
    repository = f'''"""Generated repository scaffold for {resource.name}."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import {class_name}


class {class_name}Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, resource_id: int) -> {class_name} | None:
        return await self.session.scalar(select({class_name}).where({class_name}.id == resource_id))

    async def list(self, offset: int, limit: int) -> list[{class_name}]:
        result = await self.session.scalars(select({class_name}).offset(offset).limit(limit))
        return list(result.all())
'''
    service = f'''"""Generated service scaffold for {resource.name}."""
from sqlalchemy.ext.asyncio import AsyncSession

from .repository import {class_name}Repository


class {class_name}Service:
    def __init__(self, session: AsyncSession):
        self.repository = {class_name}Repository(session)

    async def list(self, offset: int, limit: int):
        return await self.repository.list(offset, limit)
'''
    router = f'''"""Generated router scaffold for {resource.name}."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database.session import get_session
from .service import {class_name}Service

router = APIRouter(prefix="{resource.api_base}", tags=["{resource.name}"])


@router.get("")
async def list_{resource.name}(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), session: AsyncSession = Depends(get_session)):
    return await {class_name}Service(session).list(offset, limit)
'''
    page_name = f"{_class_name(resource.name)}Page"
    page = f'''<script setup lang="ts">
import {{ onMounted, ref }} from 'vue'

const items = ref<unknown[]>([])
const loading = ref(false)

onMounted(async () => {{
  loading.value = true
  try {{
    const response = await fetch('{resource.api_base}')
    items.value = await response.json()
  }} finally {{
    loading.value = false
  }}
}})
</script>

<template>
  <section aria-labelledby="{resource.name}-title">
    <h1 id="{resource.name}-title">{page_name}</h1>
    <p v-if="loading">Loading...</p>
    <pre v-else>{{{{ items }}}}</pre>
  </section>
</template>
'''
    test = f'''from server.app.modules.{resource.name}.generated.model import {class_name}


def test_{resource.name}_generated_model_name():
    assert {class_name}.__tablename__ == "{resource.name}"
'''
    files = {
        f"{module}/generated/__init__.py": '"""Generated module scaffolds."""\n',
        f"{module}/generated/model.py": model,
        f"{module}/generated/schema.py": schema,
        f"{module}/generated/repository.py": repository,
        f"{module}/generated/service.py": service,
        f"{module}/generated/router.py": router,
        f"admin/src/components/admin/generated/{page_name}.vue": page,
        f"server/tests/generated/test_{resource.name}.py": test,
    }
    expected = {entry["path"] for entry in build_crud_generation_plan(resource)["files"]}
    if set(files) != expected:
        raise RuntimeError("template paths do not match the generation plan")
    return files
