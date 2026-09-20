import json

from server.app.core.modules import ModuleRegistry, ModuleSpec
from server.app.cli import main


def test_module_registry_registers_and_boots_modules() -> None:
    events: list[str] = []
    registry = ModuleRegistry()
    registry.register(ModuleSpec("demo", register=lambda: events.append("register"), boot=lambda: events.append("boot")))

    registry.register_all()
    registry.boot_all()

    assert registry.names() == ["demo"]
    assert events == ["register", "boot"]


def test_admin_modules_command_lists_core_modules(capsys) -> None:
    assert main(["modules"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert "users" in output
    assert "roles" in output


def test_admin_help_is_available(capsys) -> None:
    assert main(["--help"]) == 0
    assert "health" in capsys.readouterr().out


def test_admin_infrastructure_commands_have_dry_run_contract(capsys) -> None:
    for command in ("migrate", "seed", "worker", "scheduler"):
        assert main([command, "--dry-run"]) == 0
        output = json.loads(capsys.readouterr().out)
        assert output["command"] == command
        assert output["dry_run"] is True


def test_admin_doctor_is_read_only_and_reports_platform_status(monkeypatch, capsys) -> None:
    from server.app import cli

    async def healthy():
        return {"status": "ok", "database": True, "redis": True}

    monkeypatch.setattr(cli, "_health_payload", healthy)
    assert main(["doctor"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "ok"
    assert "users" in output["modules"]
    assert isinstance(output["security"]["jwt_secret_configured"], bool)
