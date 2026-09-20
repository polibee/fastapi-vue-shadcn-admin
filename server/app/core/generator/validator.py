"""Read-only validation for generated CRUD scaffolds."""

import ast
from pathlib import Path
from typing import Any

from .executor import _safe_target
from .plan import build_registered_crud_generation_plan


def validate_generated_output(plan: dict[str, Any], root: str | Path) -> dict[str, Any]:
    """Check generated files and resource-specific contracts without importing them."""
    root_path = Path(root).resolve()
    resource = str(plan["resource"])
    definition = build_registered_crud_generation_plan(resource)
    expected_prefix = next(
        entry["path"] for entry in definition["files"] if entry["path"].endswith("/router.py")
    )
    results: list[dict[str, str]] = []

    for entry in plan["files"]:
        relative_path = str(entry["path"])
        target = _safe_target(root_path, relative_path)
        if not target.is_file():
            results.append({"path": relative_path, "status": "missing"})
            continue
        source = target.read_text(encoding="utf-8")
        if target.suffix == ".py":
            try:
                ast.parse(source, filename=relative_path)
            except SyntaxError as error:
                results.append({"path": relative_path, "status": "invalid_python", "detail": str(error)})
                continue
        if relative_path == expected_prefix and f'prefix="/api/v1/{resource}"' not in source:
            results.append({"path": relative_path, "status": "contract_error", "detail": "router prefix mismatch"})
            continue
        if relative_path.endswith("/model.py") and f'__tablename__ = "{resource}"' not in source:
            results.append({"path": relative_path, "status": "contract_error", "detail": "table name mismatch"})
            continue
        results.append({"path": relative_path, "status": "ok"})

    return {
        "resource": resource,
        "valid": all(item["status"] == "ok" for item in results),
        "files": results,
    }
