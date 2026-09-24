import asyncio
import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine


pytestmark = pytest.mark.integration
ROOT = Path(__file__).parents[2]


def test_clean_postgres_migration_and_restore_rehearsal_contract():
    """Run only when an isolated TEST_DATABASE_URL is explicitly provided."""
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for the PostgreSQL rehearsal")
    if "sqlite" in database_url.lower():
        pytest.fail("TEST_DATABASE_URL must point to PostgreSQL, not SQLite")

    env = os.environ.copy()
    env["DATABASE_URL"] = database_url
    env["ENVIRONMENT"] = "test"
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=True,
    )

    async def verify_schema() -> None:
        engine = create_async_engine(database_url)
        try:
            async with engine.connect() as connection:
                tables = await connection.run_sync(lambda sync: set(inspect(sync).get_table_names()))
                assert {"users", "roles", "permissions", "role_permissions", "alembic_version"}.issubset(tables)
                permission = await connection.scalar(text("SELECT code FROM permissions WHERE code = 'health.detail'"))
                assert permission == "health.detail"
        finally:
            await engine.dispose()

    asyncio.run(verify_schema())
