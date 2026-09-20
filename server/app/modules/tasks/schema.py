from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    task_name: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any] = Field(default_factory=dict)


class TaskRead(BaseModel):
    id: int
    task_id: str
    task_name: str
    status: str
    progress: int
    message: str | None
    attempts: int
    max_attempts: int
    started_at: datetime | None
    error_message: str | None
    payload: dict[str, Any]
    requested_by: int | None
    request_id: str
    broker_job_id: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    items: list[TaskRead]
    total: int
    offset: int
    limit: int


class TaskCancelResponse(BaseModel):
    task_id: str
    status: str


class TaskEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    message: str | None
    status: str | None
    progress: int | None
    created_at: datetime


class TaskEventListResponse(BaseModel):
    items: list[TaskEventRead]
