from fastapi import APIRouter, Depends, HTTPException

from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User
from .registry import ResourceNotFoundError, get_resource_manifest, list_resource_manifests_cached

router = APIRouter(prefix="/api/v1/admin/resources", tags=["Resources"], dependencies=[api_rate_limit("resources")])


@router.get("")
async def list_resources(_: User = Depends(require_permission("users.view"))) -> dict[str, object]:
    return {"items": await list_resource_manifests_cached()}


@router.get("/{name}")
async def get_resource(name: str, _: User = Depends(require_permission("users.view"))) -> dict[str, object]:
    try:
        return get_resource_manifest(name)
    except ResourceNotFoundError as error:
        raise HTTPException(status_code=404, detail={"code": "resource_not_found", "message": "Resource not found"}) from error
