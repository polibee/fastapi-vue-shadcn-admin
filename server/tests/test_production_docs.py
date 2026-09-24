from pathlib import Path


ROOT = Path(__file__).parents[2]


def test_production_runbooks_and_acceptance_script_cover_required_operations():
    chinese = (ROOT / "docs/生产部署与回滚.md").read_text(encoding="utf-8")
    english = (ROOT / "docs/production-deployment-and-rollback.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts/production-acceptance.ps1").read_text(encoding="utf-8")

    for term in ("ENVIRONMENT", "DATABASE_URL", "REDIS_URL", "alembic upgrade head", "pg_dump", "pg_restore", "Worker", "Scheduler"):
        assert term.lower() in chinese.lower()
        assert term.lower() in english.lower()
    assert "回滚" in chinese
    assert "rollback" in english.lower()
    assert "read-only" in script.lower()
    assert "TEST_DATABASE_URL" in script
    assert "CheckOpenApi" in script
    assert "integration-password" not in script
