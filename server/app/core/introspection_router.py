from fastapi import APIRouter, Depends

from server.app.core.database.session import DatabaseNotConfiguredError, engine
from server.app.core.introspection import build_resource_compatibility, introspect_database
from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User

router = APIRouter(prefix="/api/v1/admin/introspection", tags=["Introspection"], dependencies=[api_rate_limit("introspection")])


@router.get("")
async def read_database_introspection(
    _: User = Depends(require_permission("users.view")),
) -> dict[str, object]:
    if engine is None:
        raise DatabaseNotConfiguredError("DATABASE_URL is not configured")
    return await introspect_database(engine)


@router.get("/compatibility")
async def read_database_compatibility(
    _: User = Depends(require_permission("users.view")),
) -> dict[str, object]:
    if engine is None:
        raise DatabaseNotConfiguredError("DATABASE_URL is not configured")
    introspection = await introspect_database(engine)
    return {"items": build_resource_compatibility(introspection)}
