import pytest
from sqlalchemy.ext.asyncio import create_async_engine


def test_database_url_dialect_supports_postgres_and_mysql():
    from server.app.core.introspection import database_dialect

    assert database_dialect("postgresql+asyncpg://user:pass@host/db") == "postgresql"
    assert database_dialect("mysql+aiomysql://user:pass@host/db") == "mysql"
    with pytest.raises(ValueError):
        database_dialect("oracle+oracledb://user:pass@host/db")


def test_introspection_router_contract_is_read_only_and_permission_protected():
    from server.app.core.introspection_router import router

    route = next(route for route in router.routes if route.path == "/api/v1/admin/introspection")

    assert route.methods == {"GET"}
    assert router.prefix == "/api/v1/admin/introspection"
    assert route.dependant.dependencies


def test_resource_compatibility_report_is_deterministic():
    from server.app.core.introspection import build_resource_compatibility

    report = build_resource_compatibility(
        {
            "tables": [{"name": "roles", "columns": [{"name": "id"}, {"name": "name"}]}],
            "views": [],
        }
    )

    roles = next(item for item in report if item["resource"] == "roles")
    users = next(item for item in report if item["resource"] == "users")
    assert roles == {"resource": "roles", "table": "roles", "status": "drift", "missingColumns": ["description"], "extraColumns": []}
    assert users["status"] == "missing_table"


@pytest.mark.asyncio
async def test_introspect_database_is_read_only_and_returns_schema_metadata():
    from server.app.core.introspection import introspect_database

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.exec_driver_sql("CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(64) NOT NULL)")
        await connection.exec_driver_sql("CREATE TABLE user_roles (user_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id))")
        await connection.exec_driver_sql("CREATE UNIQUE INDEX ix_users_username ON users (username)")
        await connection.exec_driver_sql("CREATE VIEW active_users AS SELECT id, username FROM users")

    result = await introspect_database(engine)

    assert result["dialect"] == "sqlite"
    users = next(table for table in result["tables"] if table["name"] == "users")
    assert [column["name"] for column in users["columns"]] == ["id", "username"]
    assert users["indexes"][0]["unique"] is True
    user_roles = next(table for table in result["tables"] if table["name"] == "user_roles")
    assert user_roles["foreignKeys"][0]["referredTable"] == "users"
    assert result["views"] == ["active_users"]
    await engine.dispose()


@pytest.mark.asyncio
async def test_introspect_database_url_disposes_engine_after_read():
    from server.app.core.introspection import introspect_database_url

    result = await introspect_database_url("sqlite+aiosqlite:///:memory:")

    assert result["dialect"] == "sqlite"
    assert result["tables"] == []
