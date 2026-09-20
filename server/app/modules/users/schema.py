from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: str = Field(min_length=3, max_length=255)
    password: str | None = Field(default=None, min_length=1, max_length=255)
    password_hash: str | None = Field(default=None, min_length=1, max_length=255)

    @model_validator(mode="after")
    def require_password_input(self):
        if not self.password and not self.password_hash:
            raise ValueError("password or password_hash is required")
        return self


class UserRolesUpdate(BaseModel):
    roles: list[str] = Field(default_factory=list, max_length=50)


class UserBulkDelete(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=50)


class UserBulkDeleteResponse(BaseModel):
    deleted_ids: list[int]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool
    roles: list[str]
    created_at: datetime


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
    offset: int
    limit: int
