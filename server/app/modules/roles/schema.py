from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RoleCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=255)
    data_scope: Literal["all", "self"] = "all"


class RoleUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class RolePermissionsUpdate(BaseModel):
    codes: list[str] = Field(default_factory=list, max_length=100)


class RoleDataScopeUpdate(BaseModel):
    data_scope: Literal["all", "self"]


class RoleBulkDelete(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=50)


class RoleBulkDeleteResponse(BaseModel):
    deleted_ids: list[int]


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    data_scope: Literal["all", "self"]
    permissions: list[str]
    created_at: datetime


class RoleListResponse(BaseModel):
    items: list[RoleRead]
    total: int
    offset: int
    limit: int
