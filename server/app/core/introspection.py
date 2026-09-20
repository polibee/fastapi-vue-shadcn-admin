"""Read-only SQLAlchemy database schema introspection.

This module only calls SQLAlchemy Inspector metadata APIs. It does not emit
DDL, mutate rows, or run migrations.
"""

from typing import Any

from sqlalchemy.engine import Connection
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect


_SUPPORTED_DIALECTS = {"postgresql", "mysql", "sqlite"}


def database_dialect(database_url: str) -> str:
    dialect = make_url(database_url).get_backend_name()
    if dialect not in _SUPPORTED_DIALECTS:
        raise ValueError(f"unsupported database dialect: {dialect}")
    return dialect


def build_resource_compatibility(introspection: dict[str, Any]) -> list[dict[str, Any]]:
    """Compare registered resource fields with introspected table columns."""
    from server.app.core.resources.definitions import RESOURCE_DEFINITIONS

    tables = {table["name"]: {column["name"] for column in table.get("columns", [])} for table in introspection.get("tables", [])}
    report: list[dict[str, Any]] = []
    for resource_name, resource in sorted(RESOURCE_DEFINITIONS.items()):
        expected = {field.database_name or field.name for field in resource.fields}
        actual = tables.get(resource_name)
        if actual is None:
            report.append({"resource": resource_name, "table": resource_name, "status": "missing_table", "missingColumns": sorted(expected), "extraColumns": []})
            continue
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        report.append({"resource": resource_name, "table": resource_name, "status": "ok" if not missing else "drift", "missingColumns": missing, "extraColumns": extra})
    return report


def _collect_schema(connection: Connection, schema: str | None) -> list[dict[str, Any]]:
    inspector = inspect(connection)
    tables: list[dict[str, Any]] = []
    for table_name in sorted(inspector.get_table_names(schema=schema)):
        primary_key = inspector.get_pk_constraint(table_name, schema=schema).get("constrained_columns") or []
        primary_key_names = set(primary_key)
        columns = []
        for column in inspector.get_columns(table_name, schema=schema):
            columns.append(
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": bool(column.get("nullable", True)),
                    "default": column.get("default"),
                    "primaryKey": column["name"] in primary_key_names,
                    "autoincrement": column.get("autoincrement"),
                }
            )
        indexes = []
        for index in inspector.get_indexes(table_name, schema=schema):
            indexes.append(
                {
                    "name": index["name"],
                    "unique": bool(index.get("unique", False)),
                    "columns": list(index.get("column_names") or []),
                }
            )
        foreign_keys = []
        for foreign_key in inspector.get_foreign_keys(table_name, schema=schema):
            foreign_keys.append(
                {
                    "name": foreign_key.get("name"),
                    "columns": list(foreign_key.get("constrained_columns") or []),
                    "referredTable": foreign_key.get("referred_table"),
                    "referredSchema": foreign_key.get("referred_schema"),
                    "referredColumns": list(foreign_key.get("referred_columns") or []),
                }
            )
        tables.append(
            {
                "name": table_name,
                "schema": schema,
                "columns": columns,
                "primaryKey": list(primary_key),
                "indexes": sorted(indexes, key=lambda item: item["name"]),
                "foreignKeys": sorted(foreign_keys, key=lambda item: item["name"] or ""),
            }
        )
    return tables


async def introspect_database(engine: AsyncEngine, schema: str | None = None) -> dict[str, Any]:
    """Return stable table metadata using a read-only SQLAlchemy connection."""
    async with engine.connect() as connection:
        tables = await connection.run_sync(_collect_schema, schema)
        views = await connection.run_sync(lambda sync_connection: sorted(inspect(sync_connection).get_view_names(schema=schema)))
    return {
        "dialect": engine.dialect.name,
        "schema": schema,
        "tables": tables,
        "views": views,
    }


async def introspect_database_url(database_url: str, schema: str | None = None) -> dict[str, Any]:
    """Introspect one URL and dispose its engine in the same event loop."""
    database_dialect(database_url)
    engine = create_async_engine(database_url, pool_pre_ping=True)
    try:
        return await introspect_database(engine, schema)
    finally:
        await engine.dispose()
