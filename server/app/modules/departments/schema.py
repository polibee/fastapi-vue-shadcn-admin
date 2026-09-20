from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class DepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    code: str = Field(min_length=1, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=255)
    is_active: bool = True

class DepartmentUpdate(DepartmentCreate):
    pass

class DepartmentBulkDelete(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=50)

class DepartmentBulkDeleteResponse(BaseModel):
    deleted_ids: list[int]

class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime

class DepartmentListResponse(BaseModel):
    items: list[DepartmentRead]
    total: int
    offset: int
    limit: int
