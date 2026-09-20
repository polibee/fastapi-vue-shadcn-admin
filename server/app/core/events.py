from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from server.app.modules.audit.model import AuditLog


@dataclass(frozen=True)
class AuditEvent:
    actor_id: int | None
    action: str
    resource: str
    resource_id: int | None
    request_id: str


def publish_audit_event(session: AsyncSession, event: AuditEvent) -> AuditLog:
    audit = AuditLog(
        actor_user_id=event.actor_id,
        action=event.action,
        resource=event.resource,
        resource_id=event.resource_id,
        request_id=event.request_id,
        created_at=datetime.now(timezone.utc),
    )
    session.add(audit)
    return audit
