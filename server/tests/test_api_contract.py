import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select


@pytest.mark.asyncio
async def test_users_and_roles_openapi_contract_and_crud(session, admin_headers):
    from server.app.core.database.session import get_session
    from server.app.main import app

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            openapi = (await client.get("/openapi.json")).json()
            assert "/api/v1/users" in openapi["paths"]
            assert "/api/v1/roles" in openapi["paths"]

            created = await client.post("/api/v1/roles", json={"name": "admin", "description": "Administrator"}, headers=admin_headers)
            assert created.status_code == 201
            assert created.headers["x-request-id"]
            duplicate = await client.post("/api/v1/roles", json={"name": "admin", "description": "Duplicate"}, headers=admin_headers)
            assert duplicate.status_code == 409
            assert duplicate.json()["code"] == "role_already_exists"

            user = await client.post("/api/v1/users", json={"username": "alpha", "email": "alpha@example.test", "password_hash": "hash"}, headers=admin_headers)
            assert user.status_code == 201
            user_id = user.json()["id"]
            listing = await client.get("/api/v1/users?offset=0&limit=20", headers=admin_headers)
            assert listing.status_code == 200
            assert listing.json()["total"] == 2
            assert any(item["username"] == "alpha" for item in listing.json()["items"])

            roles = await client.get("/api/v1/roles?offset=0&limit=20", headers=admin_headers)
            assert roles.status_code == 200
            administrator = next(item for item in roles.json()["items"] if item["name"] == "test-administrator")
            assert "users.view" in administrator["permissions"]
            updated_role = await client.put(
                "/api/v1/roles/1/permissions",
                json={"codes": ["users.view", "roles.update", "users.delete", "users.update", "audit.view", "tasks.view", "tasks.create", "tasks.cancel", "tasks.retry"]},
                headers=admin_headers,
            )
            assert updated_role.status_code == 200
            assert updated_role.json()["permissions"] == ["audit.view", "roles.update", "tasks.cancel", "tasks.create", "tasks.retry", "tasks.view", "users.delete", "users.update", "users.view"]
            updated_user = await client.put(
                f"/api/v1/users/{user_id}/roles",
                json={"roles": ["test-administrator"]},
                headers=admin_headers,
            )
            assert updated_user.status_code == 200
            assert updated_user.json()["roles"] == ["test-administrator"]
            deleted_user = await client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert deleted_user.status_code == 204
            missing_user = await client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
            assert missing_user.status_code == 404
            from server.app.modules.audit.model import AuditLog

            audits = list((await session.scalars(select(AuditLog))).all())
            assert any(audit.action == "create" and audit.resource == "role" and audit.actor_user_id == 1 for audit in audits)
            assert all(audit.request_id for audit in audits)
            audit_listing = await client.get("/api/v1/audit-logs", headers=admin_headers)
            assert audit_listing.status_code == 200
            assert any(item["resource"] == "role" for item in audit_listing.json()["items"])
            filtered_audit_listing = await client.get("/api/v1/audit-logs?search=role&offset=0&limit=1", headers=admin_headers)
            assert filtered_audit_listing.status_code == 200
            assert filtered_audit_listing.json()["total"] >= 1
            assert len(filtered_audit_listing.json()["items"]) == 1
            assert all("role" in f"{item['action']} {item['resource']}".lower() for item in filtered_audit_listing.json()["items"])
            task = await client.post("/api/v1/tasks", json={"task_name": "demo.sync", "payload": {"dry_run": True}}, headers=admin_headers)
            assert task.status_code == 201
            assert task.json()["status"] == "pending"
            cancelled = await client.post(f"/api/v1/tasks/{task.json()['task_id']}/cancel", headers=admin_headers)
            assert cancelled.status_code == 200
            assert cancelled.json()["status"] == "cancelled"
            task_listing = await client.get("/api/v1/tasks", headers=admin_headers)
            assert task_listing.status_code == 200
            assert task_listing.json()["items"][0]["task_name"] == "demo.sync"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_retry_task_requeues_failed_task(session, admin_headers, monkeypatch):
    from server.app.core.database.session import get_session
    from server.app.main import app
    from server.app.modules.tasks.model import Task

    async def override_session():
        yield session

    published = []

    async def fake_publish(task_id: str, task_name: str, job_id: str | None = None) -> str:
        published.append((task_id, task_name, job_id))
        return f"job-{task_id}"

    monkeypatch.setattr("server.app.modules.tasks.router.publish_task", fake_publish)
    task = Task(
        task_id="failed-retry-task",
        task_name="demo.retry",
        status="failed",
        progress=10,
        message="failed",
        payload_json="{}",
        requested_by=1,
        request_id="test-request",
        created_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
        updated_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    session.add(task)
    await session.commit()

    app.dependency_overrides[get_session] = override_session
    try:
        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(f"/api/v1/tasks/{task.task_id}/retry", headers=admin_headers)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert response.json()["broker_job_id"] == f"job-{task.task_id}"
    assert len(published) == 1
    assert published[0][0:2] == (task.task_id, task.task_name)
    assert published[0][2].startswith(f"{task.task_id}:retry:")


@pytest.mark.asyncio
async def test_crud_without_database_returns_stable_503(monkeypatch):
    import server.app.core.database.session as database_session
    from server.app.main import app

    monkeypatch.setattr(database_session, "SessionFactory", None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/users")

    assert response.status_code == 503
    assert response.json()["code"] == "database_not_configured"


@pytest.mark.asyncio
async def test_validation_errors_have_stable_machine_code(session, admin_headers):
    from server.app.core.database.session import get_session
    from server.app.main import app

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/roles", json={"name": ""}, headers=admin_headers)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 422
    assert response.json()["code"] == "validation_error"


@pytest.mark.asyncio
async def test_conflict_error_uses_requested_locale(session, admin_headers):
    from server.app.core.database.session import get_session
    from server.app.main import app

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/api/v1/roles", json={"name": "admin"}, headers=admin_headers)
            response = await client.post("/api/v1/roles", json={"name": "admin"}, headers={**admin_headers, "Accept-Language": "zh-CN"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409
    assert response.json() == {"code": "role_already_exists", "message": "角色已存在"}
