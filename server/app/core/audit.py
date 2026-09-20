from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.events import AuditEvent, publish_audit_event
from server.app.core.middleware.request_id import ensure_request_id


async def record_audit(
    session: AsyncSession,
    request: Request,
    actor_id: int | None,
    action: str,
    resource: str,
    resource_id: int | None = None,
    *,
    commit: bool = True,
) -> None:
    publish_audit_event(session, AuditEvent(actor_id, action, resource, resource_id, ensure_request_id(request)))
    if commit:
        await session.commit()
