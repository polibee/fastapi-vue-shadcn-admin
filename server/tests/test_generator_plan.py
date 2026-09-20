import ast
import json
import sys

import pytest


def test_crud_generation_plan_is_deterministic_and_protects_manual_code():
    from server.app.core.generator.plan import build_crud_generation_plan
    from server.app.core.resources.definitions import USER_RESOURCE

    plan = build_crud_generation_plan(USER_RESOURCE)

    assert plan == {
        "schemaVersion": "1.0",
        "generatorVersion": "1.0",
        "resource": "users",
        "module": "server/app/modules/users",
        "permissions": ["users.create", "users.delete", "users.update", "users.view"],
        "files": [
            {"path": "server/app/modules/users/generated/__init__.py", "overwrite": "never"},
            {"path": "server/app/modules/users/generated/model.py", "overwrite": "never"},
            {"path": "server/app/modules/users/generated/schema.py", "overwrite": "never"},
            {"path": "server/app/modules/users/generated/repository.py", "overwrite": "never"},
            {"path": "server/app/modules/users/generated/service.py", "overwrite": "never"},
            {"path": "server/app/modules/users/generated/router.py", "overwrite": "never"},
            {"path": "admin/src/components/admin/generated/UsersPage.vue", "overwrite": "never"},
            {"path": "server/tests/generated/test_users.py", "overwrite": "never"},
        ],
    }
    assert build_crud_generation_plan(USER_RESOURCE) == plan


def test_crud_generation_plan_rejects_unsafe_resource_names():
    from server.app.core.generator.plan import InvalidResourceNameError, build_crud_generation_plan
    from server.app.core.resources.contract import ResourceDefinition

    resource = ResourceDefinition(name="../users", label="x", label_plural="x", api_base="/x", permissions={})

    with pytest.raises(InvalidResourceNameError):
        build_crud_generation_plan(resource)


def test_registered_resource_plan_resolves_by_name():
    from server.app.core.generator.plan import build_registered_crud_generation_plan

    plan = build_registered_crud_generation_plan("roles")

    assert plan["resource"] == "roles"
    assert plan["module"] == "server/app/modules/roles"


def test_generator_cli_prints_registered_plan(capsys, monkeypatch):
    from server.app.core.generator.cli import main

    monkeypatch.setattr(sys, "argv", ["crud-generator", "users"])

    assert main() == 0
    assert json.loads(capsys.readouterr().out)["resource"] == "users"


def test_generator_dry_run_does_not_write_files(tmp_path):
    from server.app.core.generator.executor import execute_crud_generation
    from server.app.core.generator.plan import build_registered_crud_generation_plan

    result = execute_crud_generation(build_registered_crud_generation_plan("users"), tmp_path, dry_run=True)

    assert result["dryRun"] is True
    assert all(item["status"] == "would_create" for item in result["files"])
    assert list(tmp_path.rglob("*")) == []


def test_generator_write_is_idempotent_and_never_overwrites(tmp_path):
    from server.app.core.generator.executor import execute_crud_generation
    from server.app.core.generator.plan import build_registered_crud_generation_plan

    plan = build_registered_crud_generation_plan("roles")
    first = execute_crud_generation(plan, tmp_path)
    existing = tmp_path / "server/app/modules/roles/generated/model.py"
    existing.write_text("manual code\n", encoding="utf-8")
    second = execute_crud_generation(plan, tmp_path)

    assert first["created"] == 8
    assert second["created"] == 0
    assert second["skipped"] == 8
    assert existing.read_text(encoding="utf-8") == "manual code\n"


def test_generator_rejects_paths_outside_root(tmp_path):
    from server.app.core.generator.executor import UnsafeGenerationPathError, execute_crud_generation

    plan = {"resource": "users", "files": [{"path": "../outside.py", "overwrite": "never"}]}

    with pytest.raises(UnsafeGenerationPathError):
        execute_crud_generation(plan, tmp_path)


def test_generator_cli_requires_explicit_write_flag(tmp_path, capsys, monkeypatch):
    from server.app.core.generator.cli import main

    monkeypatch.setattr(sys, "argv", ["crud-generator", "users", "--root", str(tmp_path), "--write"])

    assert main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["created"] == 8
    assert (tmp_path / "server/app/modules/users/generated/model.py").exists()


def test_generated_templates_are_resource_specific():
    from server.app.core.generator.templates import render_generated_files
    from server.app.core.resources.definitions import USER_RESOURCE

    files = render_generated_files(USER_RESOURCE)

    assert "class User(Base):" in files["server/app/modules/users/generated/model.py"]
    assert "username: str" in files["server/app/modules/users/generated/schema.py"]
    assert 'prefix="/api/v1/users"' in files["server/app/modules/users/generated/router.py"]
    assert "UsersPage" in files["admin/src/components/admin/generated/UsersPage.vue"]
    for path, content in files.items():
        if path.endswith(".py"):
            ast.parse(content, filename=path)


def test_generated_output_check_validates_scaffolds_without_wiring_them(tmp_path):
    from server.app.core.generator.executor import execute_crud_generation
    from server.app.core.generator.plan import build_registered_crud_generation_plan
    from server.app.core.generator.validator import validate_generated_output

    plan = build_registered_crud_generation_plan("users")
    execute_crud_generation(plan, tmp_path)

    result = validate_generated_output(plan, tmp_path)

    assert result["valid"] is True
    assert all(item["status"] == "ok" for item in result["files"])


def test_generated_output_check_reports_contract_break(tmp_path):
    from server.app.core.generator.executor import execute_crud_generation
    from server.app.core.generator.plan import build_registered_crud_generation_plan
    from server.app.core.generator.validator import validate_generated_output

    plan = build_registered_crud_generation_plan("roles")
    execute_crud_generation(plan, tmp_path)
    router = tmp_path / "server/app/modules/roles/generated/router.py"
    router.write_text(router.read_text(encoding="utf-8").replace("/api/v1/roles", "/api/v1/wrong"), encoding="utf-8")

    result = validate_generated_output(plan, tmp_path)

    assert result["valid"] is False
    assert any(item["status"] == "contract_error" for item in result["files"])


def test_generator_cli_check_returns_failure_for_missing_output(tmp_path, capsys, monkeypatch):
    from server.app.core.generator.cli import main

    monkeypatch.setattr(sys, "argv", ["crud-generator", "users", "--root", str(tmp_path), "--check"])

    assert main() == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False


def test_generator_router_exposes_read_only_plan_endpoint():
    from server.app.core.generator.router import router

    route = next(route for route in router.routes if route.path == "/api/v1/admin/generator/plans/{resource}")

    assert route.methods == {"GET"}
    assert route.dependant.dependencies
