"""Safe execution of deterministic CRUD generation plans.

The executor is deliberately small: it only writes paths declared by a plan,
creates missing files, and never overwrites an existing file.
"""

from pathlib import Path
from typing import Any


class UnsafeGenerationPathError(ValueError):
    pass


def _safe_target(root: Path, relative_path: str) -> Path:
    target = (root / relative_path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise UnsafeGenerationPathError(relative_path) from exc
    return target


def _render_content(relative_path: str, resource: str) -> str:
    from server.app.core.generator.templates import render_generated_files
    from server.app.core.resources.definitions import RESOURCE_DEFINITIONS

    definition = RESOURCE_DEFINITIONS.get(resource)
    if definition is None:
        raise KeyError(resource)
    return render_generated_files(definition)[relative_path]


def execute_crud_generation(
    plan: dict[str, Any], root: str | Path, *, dry_run: bool = False
) -> dict[str, Any]:
    """Execute a plan under *root* without ever overwriting existing files."""
    root_path = Path(root).resolve()
    resource = str(plan["resource"])
    results: list[dict[str, str]] = []

    for entry in plan["files"]:
        relative_path = str(entry["path"])
        target = _safe_target(root_path, relative_path)
        if target.exists():
            results.append({"path": relative_path, "status": "skipped"})
            continue
        if dry_run:
            results.append({"path": relative_path, "status": "would_create"})
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_render_content(relative_path, resource), encoding="utf-8", newline="\n")
        results.append({"path": relative_path, "status": "created"})

    return {
        "resource": resource,
        "dryRun": dry_run,
        "created": sum(item["status"] == "created" for item in results),
        "skipped": sum(item["status"] == "skipped" for item in results),
        "files": results,
    }
