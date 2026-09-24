from typing import Literal
from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database.session import get_session
from server.app.core.audit import record_audit
from server.app.core.i18n import locale_from_request, translate
from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User
from .schema import RoleBulkDelete, RoleBulkDeleteResponse, RoleCreate, RoleDataScopeUpdate, RoleListResponse, RolePermissionsUpdate, RoleRead, RoleUpdate
from .service import DuplicateRoleError, InvalidDataScopeError, InvalidPermissionError, ProtectedRoleError, RoleService

router = APIRouter(prefix="/api/v1/roles", tags=["Roles"], dependencies=[api_rate_limit("roles")])


def to_role_read(role) -> RoleRead:
    return RoleRead.model_validate({
        "id": role.id,
        "name": role.name,
        "description": role.description,
        "data_scope": role.data_scope,
        "permissions": sorted(permission.code for permission in role.permissions),
        "created_at": role.created_at,
    })


@router.get("", response_model=RoleListResponse)
async def list_roles(offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), search: str | None = Query(default=None, max_length=100), sort_by: Literal["id", "name"] = Query(default="id"), sort_order: Literal["asc", "desc"] = Query(default="asc"), session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("roles.view"))) -> RoleListResponse:
    items, total = await RoleService(session).list(offset, limit, search, sort_by, sort_order)
    return RoleListResponse(items=[to_role_read(role) for role in items], total=total, offset=offset, limit=limit)


@router.get("/{role_id}", response_model=RoleRead)
async def read_role(role_id: int, request: Request, session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("roles.view"))) -> RoleRead:
    role = await RoleService(session).get(role_id)
    if role is None:
        from fastapi import HTTPException

        locale = locale_from_request(request)
        raise HTTPException(status_code=404, detail={"code": "role_not_found", "message": translate("modules/roles", "role_not_found", locale)})
    return to_role_read(role)


@router.post("", response_model=RoleRead, status_code=201)
async def create_role(request: Request, payload: RoleCreate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("roles.create"))) -> RoleRead:
    try:
        role = await RoleService(session).create(**payload.model_dump())
        await record_audit(session, request, actor.id, "create", "role", role.id)
        return to_role_read(role)
    except DuplicateRoleError as error:
        from fastapi import HTTPException

        locale = locale_from_request(request)
        raise HTTPException(status_code=409, detail={"code": error.code, "message": translate("modules/roles", error.code, locale)}) from error


@router.put("/{role_id}", response_model=RoleRead)
async def update_role(role_id: int, request: Request, payload: RoleUpdate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("roles.update"))) -> RoleRead:
    try:
        role = await RoleService(session).update_all(role_id, **payload.model_dump())
    except (DuplicateRoleError, InvalidDataScopeError, InvalidPermissionError, ProtectedRoleError) as error:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        status_code = 409 if isinstance(error, (DuplicateRoleError, ProtectedRoleError)) else 400
        raise HTTPException(status_code=status_code, detail={"code": error.code, "message": translate("modules/roles", error.code, locale)}) from error
    if role is None:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "role_not_found", "message": translate("modules/roles", "role_not_found", locale)})
    await record_audit(session, request, actor.id, "update", "role", role.id)
    return to_role_read(role)


@router.put("/{role_id}/permissions", response_model=RoleRead)
async def update_role_permissions(role_id: int, request: Request, payload: RolePermissionsUpdate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("roles.update"))) -> RoleRead:
    try:
        role = await RoleService(session).update_permissions(role_id, payload.codes)
    except InvalidPermissionError as error:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail={"code": error.code, "message": translate("modules/roles", error.code, locale)}) from error
    if role is None:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "role_not_found", "message": translate("modules/roles", "role_not_found", locale)})
    await record_audit(session, request, actor.id, "update_permissions", "role", role.id)
    return to_role_read(role)


@router.put("/{role_id}/data-scope", response_model=RoleRead)
async def update_role_data_scope(role_id: int, request: Request, payload: RoleDataScopeUpdate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("roles.update"))) -> RoleRead:
    try:
        role = await RoleService(session).update_data_scope(role_id, payload.data_scope)
    except InvalidDataScopeError as error:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail={"code": error.code, "message": translate("modules/roles", error.code, locale)}) from error
    if role is None:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "role_not_found", "message": translate("modules/roles", "role_not_found", locale)})
    await record_audit(session, request, actor.id, "update_data_scope", "role", role.id)
    return to_role_read(role)


@router.post("/bulk-delete", response_model=RoleBulkDeleteResponse)
async def bulk_delete_roles(request: Request, payload: RoleBulkDelete, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("roles.delete"))) -> RoleBulkDeleteResponse:
    deleted_ids = await RoleService(session).delete_many(payload.ids)
    for role_id in deleted_ids:
        await record_audit(session, request, actor.id, "delete", "role", role_id, commit=False)
    await session.commit()
    return RoleBulkDeleteResponse(deleted_ids=deleted_ids)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(role_id: int, request: Request, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("roles.delete"))) -> Response:
    try:
        deleted = await RoleService(session).delete(role_id)
    except ProtectedRoleError as error:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=409, detail={"code": error.code, "message": translate("modules/roles", error.code, locale)}) from error
    if not deleted:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "role_not_found", "message": translate("modules/roles", "role_not_found", locale)})
    await record_audit(session, request, actor.id, "delete", "role", role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
