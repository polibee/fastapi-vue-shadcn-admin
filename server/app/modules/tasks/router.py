import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database.session import get_session
from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.core.tasks.broker import publish_task
from server.app.modules.users.model import User
from .events import record_task_event
from .model import Task, TaskEvent
from .schema import TaskCancelResponse, TaskCreate, TaskEventListResponse, TaskEventRead, TaskListResponse, TaskRead

router = APIRouter(prefix="/api/v1/tasks", tags=["Tasks"], dependencies=[api_rate_limit("tasks")])


def to_task_read(task: Task) -> TaskRead:
    return TaskRead.model_validate({**task.__dict__, "payload": json.loads(task.payload_json)})


@router.get("", response_model=TaskListResponse)
async def list_tasks(offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("tasks.view"))) -> TaskListResponse:
    result = await session.execute(select(Task).order_by(Task.id.desc()).offset(offset).limit(limit))
    total = await session.scalar(select(func.count()).select_from(Task))
    return TaskListResponse(items=[to_task_read(task) for task in result.scalars().all()], total=int(total or 0), offset=offset, limit=limit)


@router.post("", response_model=TaskRead, status_code=201)
async def create_task(request: Request, payload: TaskCreate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("tasks.create"))) -> TaskRead:
    now = datetime.now(timezone.utc)
    task = Task(task_id=str(uuid4()), task_name=payload.task_name, status="pending", payload_json=json.dumps(payload.payload), requested_by=actor.id, request_id=getattr(request.state, "request_id", ""), created_at=now, updated_at=now)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    record_task_event(session, task, "created", "Task created", status=task.status, progress=task.progress)
    try:
        task.broker_job_id = await publish_task(task.task_id, task.task_name)
        task.published_at = datetime.now(timezone.utc) if task.broker_job_id else None
        if task.broker_job_id:
            record_task_event(session, task, "published", "Task published", status=task.status, progress=task.progress)
        await session.commit()
    except Exception:
        task.broker_job_id = None
        task.published_at = None
        await session.commit()
    return to_task_read(task)


@router.post("/{task_id}/cancel", response_model=TaskCancelResponse)
async def cancel_task(task_id: str, session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("tasks.cancel"))) -> TaskCancelResponse:
    task = await session.scalar(select(Task).where(Task.task_id == task_id))
    if task is None:
        raise HTTPException(status_code=404, detail={"code": "task_not_found", "message": "Task not found"})
    if task.status != "pending":
        raise HTTPException(status_code=409, detail={"code": "task_not_cancellable", "message": "Only pending tasks can be cancelled"})
    task.status = "cancelled"
    task.message = "Cancelled before execution"
    task.updated_at = datetime.now(timezone.utc)
    record_task_event(session, task, "cancelled", task.message, status=task.status, progress=task.progress)
    await session.commit()
    return TaskCancelResponse(task_id=task.task_id, status=task.status)


@router.post("/{task_id}/retry", response_model=TaskRead)
async def retry_task(task_id: str, session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("tasks.retry"))) -> TaskRead:
    task = await session.scalar(select(Task).where(Task.task_id == task_id))
    if task is None:
        raise HTTPException(status_code=404, detail={"code": "task_not_found", "message": "Task not found"})
    if task.status not in {"failed", "dead", "cancelled"}:
        raise HTTPException(status_code=409, detail={"code": "task_not_retryable", "message": "Only failed or cancelled tasks can be retried"})
    task.status = "pending"
    task.progress = 0
    task.message = "Retry requested"
    task.broker_job_id = None
    task.published_at = None
    task.updated_at = datetime.now(timezone.utc)
    record_task_event(session, task, "retry_requested", task.message, status=task.status, progress=task.progress)
    await session.commit()
    try:
        retry_job_id = f"{task.task_id}:retry:{uuid4().hex}"
        task.broker_job_id = await publish_task(task.task_id, task.task_name, retry_job_id)
        task.published_at = datetime.now(timezone.utc) if task.broker_job_id else None
        if task.broker_job_id:
            record_task_event(session, task, "published", "Retry published", status=task.status, progress=task.progress)
        await session.commit()
    except Exception:
        task.broker_job_id = None
        task.published_at = None
        await session.commit()
    return to_task_read(task)


@router.get("/{task_id}/events", response_model=TaskEventListResponse)
async def list_task_events(task_id: str, session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("tasks.view"))) -> TaskEventListResponse:
    task = await session.scalar(select(Task).where(Task.task_id == task_id))
    if task is None:
        raise HTTPException(status_code=404, detail={"code": "task_not_found", "message": "Task not found"})
    result = await session.execute(select(TaskEvent).where(TaskEvent.task_id == task.id).order_by(TaskEvent.id.asc()))
    return TaskEventListResponse(items=[TaskEventRead.model_validate(event) for event in result.scalars().all()])
