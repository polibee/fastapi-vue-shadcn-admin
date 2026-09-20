import pytest

from server.app.core.events import AuditEvent, publish_audit_event


@pytest.mark.asyncio
async def test_audit_event_publisher_adds_event_without_committing(session):
    event = AuditEvent(actor_id=1, action="delete", resource="user", resource_id=42, request_id="request-42")

    publish_audit_event(session, event)
    await session.flush()

    from server.app.modules.audit.model import AuditLog

    audit = await session.get(AuditLog, 1)
    assert audit is not None
    assert audit.actor_user_id == 1
    assert audit.action == "delete"
    assert audit.resource == "user"
    assert audit.resource_id == 42
    assert audit.request_id == "request-42"
