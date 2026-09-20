from fastapi import APIRouter, Depends, HTTPException

from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User

from .plan import build_registered_crud_generation_plan

router = APIRouter(prefix="/api/v1/admin/generator", tags=["Generator"], dependencies=[api_rate_limit("generator")])


@router.get("/plans/{resource}")
async def read_crud_generation_plan(
    resource: str,
    _: User = Depends(require_permission("users.view")),
) -> dict[str, object]:
    try:
        return build_registered_crud_generation_plan(resource)
    except KeyError as error:
        raise HTTPException(status_code=404, detail={"code": "resource_not_found", "message": "Resource not found"}) from error
