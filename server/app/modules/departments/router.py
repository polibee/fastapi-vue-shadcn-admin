from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.core.audit import record_audit
from server.app.core.database.session import get_session
from server.app.core.i18n import locale_from_request, translate
from server.app.core.permissions import require_permission
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.users.model import User
from .schema import DepartmentBulkDelete, DepartmentBulkDeleteResponse, DepartmentCreate, DepartmentListResponse, DepartmentRead, DepartmentUpdate
from .service import DepartmentService, DuplicateDepartmentError

router = APIRouter(prefix="/api/v1/departments", tags=["Departments"], dependencies=[api_rate_limit("departments")])
def to_department_read(department): return DepartmentRead.model_validate(department)
def error(request: Request, code: str, status_code: int):
    locale = locale_from_request(request)
    return HTTPException(status_code=status_code, detail={"code": code, "message": translate("modules/departments", code, locale)})

@router.get("", response_model=DepartmentListResponse)
async def list_departments(offset: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), search: str | None = Query(None, max_length=100), is_active: bool | None = Query(None), sort_by: str = Query("id", pattern="^(id|name|code)$"), sort_order: str = Query("asc", pattern="^(asc|desc)$"), session: AsyncSession = Depends(get_session), _: User = Depends(require_permission("departments.view"))):
    items, total = await DepartmentService(session).list(offset, limit, search, is_active, sort_by, sort_order)
    return DepartmentListResponse(items=[to_department_read(item) for item in items], total=total, offset=offset, limit=limit)

@router.post("", response_model=DepartmentRead, status_code=201)
async def create_department(request: Request, payload: DepartmentCreate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("departments.create"))):
    try: department = await DepartmentService(session).create(**payload.model_dump())
    except DuplicateDepartmentError as exc: raise error(request, exc.code, 409) from exc
    await record_audit(session, request, actor.id, "create", "department", department.id); return to_department_read(department)

@router.put("/{department_id}", response_model=DepartmentRead)
async def update_department(department_id: int, request: Request, payload: DepartmentUpdate, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("departments.update"))):
    try: department = await DepartmentService(session).update(department_id, **payload.model_dump())
    except DuplicateDepartmentError as exc: raise error(request, exc.code, 409) from exc
    if department is None: raise error(request, "department_not_found", 404)
    await record_audit(session, request, actor.id, "update", "department", department.id); return to_department_read(department)

@router.post("/bulk-delete", response_model=DepartmentBulkDeleteResponse)
async def bulk_delete_departments(request: Request, payload: DepartmentBulkDelete, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("departments.delete"))):
    deleted_ids = await DepartmentService(session).delete_many(payload.ids)
    for department_id in deleted_ids: await record_audit(session, request, actor.id, "delete", "department", department_id, commit=False)
    await session.commit(); return DepartmentBulkDeleteResponse(deleted_ids=deleted_ids)

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(department_id: int, request: Request, session: AsyncSession = Depends(get_session), actor: User = Depends(require_permission("departments.delete"))):
    if not await DepartmentService(session).delete(department_id): raise error(request, "department_not_found", 404)
    await record_audit(session, request, actor.id, "delete", "department", department_id); return Response(status_code=status.HTTP_204_NO_CONTENT)
