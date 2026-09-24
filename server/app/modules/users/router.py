from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.database.session import get_session
from server.app.core.auth import hash_password
from server.app.core.passwords import validate_password
from server.app.core.audit import record_audit
from server.app.core.i18n import locale_from_request, translate
from server.app.core.permissions import can_access_user, require_permission, user_data_scope
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User
from .schema import UserBulkDelete, UserBulkDeleteResponse, UserCreate, UserListResponse, UserRead, UserRolesUpdate
from .service import DuplicateUserError, InvalidRoleError, UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"], dependencies=[api_rate_limit("users", fail_closed=True)])


def ensure_data_scope(request: Request, actor: User, user_id: int) -> None:
    if can_access_user(actor, user_id):
        return
    locale = locale_from_request(request)
    raise HTTPException(status_code=403, detail={"code": "data_scope_denied", "message": translate("modules/users", "data_scope_denied", locale)})


def to_user_read(user) -> UserRead:
    return UserRead.model_validate({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "roles": sorted(role.name for role in user.roles),
        "created_at": user.created_at,
    })


@router.get("", response_model=UserListResponse)
async def list_users(offset: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100), search: str | None = Query(default=None, max_length=100), is_active: bool | None = Query(default=None), sort_by: Literal["id", "username", "email"] = Query(default="id"), sort_order: Literal["asc", "desc"] = Query(default="asc"), session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("users.view"))) -> UserListResponse:
    scope_user_id = actor.id if user_data_scope(actor) == "self" else None
    items, total = await UserService(session).list(offset, limit, search, is_active, sort_by, sort_order, scope_user_id)
    return UserListResponse(items=[to_user_read(user) for user in items], total=total, offset=offset, limit=limit)


@router.post("", response_model=UserRead, status_code=201)
async def create_user(request: Request, payload: UserCreate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("users.create"))) -> UserRead:
    try:
        data = payload.model_dump(exclude_none=True)
        if data.get("password"):
            data["password_hash"] = hash_password(validate_password(data.pop("password")))
        user = await UserService(session).create(**data)
        await record_audit(session, request, actor.id, "create", "user", user.id)
        return to_user_read(user)
    except DuplicateUserError as error:
        from fastapi import HTTPException

        locale = locale_from_request(request)
        raise HTTPException(status_code=409, detail={"code": error.code, "message": translate("modules/users", error.code, locale)}) from error


@router.put("/{user_id}/roles", response_model=UserRead)
async def update_user_roles(user_id: int, request: Request, payload: UserRolesUpdate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("users.update"))) -> UserRead:
    ensure_data_scope(request, actor, user_id)
    try:
        user = await UserService(session).update_roles(user_id, payload.roles)
    except InvalidRoleError as error:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail={"code": error.code, "message": translate("modules/users", error.code, locale)}) from error
    if user is None:
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": translate("modules/users", "user_not_found", locale)})
    await record_audit(session, request, actor.id, "update_roles", "user", user.id)
    return to_user_read(user)


@router.post("/bulk-delete", response_model=UserBulkDeleteResponse)
async def bulk_delete_users(request: Request, payload: UserBulkDelete, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("users.delete"))) -> UserBulkDeleteResponse:
    for user_id in payload.ids:
        ensure_data_scope(request, actor, user_id)
    deleted_ids = await UserService(session).delete_many(payload.ids)
    for user_id in deleted_ids:
        await record_audit(session, request, actor.id, "delete", "user", user_id, commit=False)
    await session.commit()
    return UserBulkDeleteResponse(deleted_ids=deleted_ids)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, request: Request, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("users.delete"))) -> Response:
    ensure_data_scope(request, actor, user_id)
    if not await UserService(session).delete(user_id):
        locale = locale_from_request(request)
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail={"code": "user_not_found", "message": translate("modules/users", "user_not_found", locale)})
    await record_audit(session, request, actor.id, "delete", "user", user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
