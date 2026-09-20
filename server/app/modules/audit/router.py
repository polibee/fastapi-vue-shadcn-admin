from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database.session import get_session
from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User
from .model import AuditLog
from .schema import AuditLogListResponse

router = APIRouter(prefix="/api/v1/audit-logs", tags=["Audit"], dependencies=[api_rate_limit("audit")])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None, min_length=1, max_length=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_permission("audit.view")),
) -> AuditLogListResponse:
    statement = select(AuditLog)
    count_statement = select(func.count()).select_from(AuditLog)
    if search:
        pattern = f"%{search.strip()}%"
        predicate = or_(
            AuditLog.action.ilike(pattern),
            AuditLog.resource.ilike(pattern),
            AuditLog.request_id.ilike(pattern),
        )
        statement = statement.where(predicate)
        count_statement = count_statement.where(predicate)
    result = await session.execute(statement.order_by(AuditLog.id.desc()).offset(offset).limit(limit))
    total = await session.scalar(count_statement)
    return AuditLogListResponse(items=list(result.scalars().all()), total=int(total or 0), offset=offset, limit=limit)
