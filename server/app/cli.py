"""Unified developer CLI for the admin platform foundation."""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Sequence

from server.app.core.health import check_database, check_redis
from server.app.core.modules import builtin_registry


async def _health_payload() -> dict[str, object]:
    database, redis = await asyncio.gather(check_database(), check_redis())
    return {"status": "ok" if database and redis else "degraded", "database": database, "redis": redis}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="admin", description="FastAPI Vue Admin developer CLI")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("modules", help="list registered modules")
    subparsers.add_parser("health", help="check database and Redis health")
    generate = subparsers.add_parser("generate", help="delegate to the CRUD generator")
    generate.add_argument("resource")
    generate.add_argument("--root")
    generate.add_argument("--write", action="store_true")
    generate.add_argument("--check", action="store_true")
    subparsers.add_parser("sdk", help="show the TypeScript SDK generation command")
    subparsers.add_parser("telemetry", help="show in-process telemetry metrics")
    subparsers.add_parser("doctor", help="run read-only platform diagnostics")
    migrate = subparsers.add_parser("migrate", help="run Alembic migrations")
    migrate.add_argument("revision", nargs="?", default="head")
    migrate.add_argument("--root", type=Path, default=Path.cwd())
    migrate.add_argument("--dry-run", action="store_true")
    for name, help_text in (("seed", "seed development data"), ("worker", "start the background task worker"), ("scheduler", "start scheduled task recovery")):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    if args.command == "modules":
        print(json.dumps(builtin_registry().names(), ensure_ascii=False))
        return 0
    if args.command == "health":
        print(json.dumps(asyncio.run(_health_payload()), ensure_ascii=False))
        return 0
    if args.command == "sdk":
        print("pnpm --dir admin generate:sdk")
        return 0
    if args.command == "telemetry":
        from server.app.core.telemetry import metrics

        print(json.dumps(metrics.snapshot(), ensure_ascii=False))
        return 0
    if args.command == "doctor":
        from server.app.core.config import get_settings
        from server.app.core.production_guard import ProductionConfigurationError, validate_production_settings
        from server.app.core.telemetry import metrics

        health = asyncio.run(_health_payload())
        settings = get_settings()
        production_issues: list[str] = []
        try:
            validate_production_settings(settings)
        except ProductionConfigurationError as error:
            production_issues.append(error.code)
        payload = {
            "status": "ok" if health["status"] == "ok" and not production_issues else "degraded",
            "health": health,
            "modules": builtin_registry().names(),
            "telemetry": metrics.snapshot(),
            "security": {
                "jwt_secret_configured": settings.jwt_secret != "development-only-change-me",
                "trusted_hosts_enabled": settings.trusted_hosts_enabled,
                "production_issues": production_issues,
            },
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0 if payload["status"] == "ok" else 1
    if args.command == "migrate":
        if args.dry_run:
            print(json.dumps({"command": "migrate", "revision": args.revision, "dry_run": True}, ensure_ascii=False))
            return 0
        from alembic import command
        from alembic.config import Config

        command.upgrade(Config(str(args.root / "alembic.ini")), args.revision)
        return 0
    if args.command == "seed":
        if args.dry_run:
            print(json.dumps({"command": "seed", "dry_run": True}, ensure_ascii=False))
            return 0
        from server.scripts.seed_demo_admin import seed_demo_admin

        asyncio.run(seed_demo_admin())
        return 0
    if args.command in {"worker", "scheduler"}:
        if args.dry_run:
            print(json.dumps({"command": args.command, "dry_run": True}, ensure_ascii=False))
            return 0
        from server.worker.tasks_worker import run_scheduler, run_worker

        (run_scheduler if args.command == "scheduler" else run_worker)()
        return 0
    if args.command == "generate":
        from server.app.core.generator.cli import main as generator_main

        delegated = [args.resource]
        if args.root:
            delegated.extend(["--root", args.root])
        if args.write:
            delegated.append("--write")
        if args.check:
            delegated.append("--check")
        return generator_main(delegated)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
