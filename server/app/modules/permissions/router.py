from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database.session import get_session
from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User

from .model import Permission
from .schema import PermissionListResponse

router = APIRouter(prefix="/api/v1/permissions", tags=["Permissions"], dependencies=[api_rate_limit("permissions")])


@router.get("", response_model=PermissionListResponse)
async def list_permissions(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(require_permission("roles.view")),
) -> PermissionListResponse:
    items = list((await session.scalars(select(Permission).order_by(Permission.code.asc()))).all())
    total = int((await session.scalar(select(func.count(Permission.id)))) or 0)
    return PermissionListResponse(items=items, total=total)
