import re
from typing import Any

from server.app.core.resources.contract import ResourceDefinition


class InvalidResourceNameError(ValueError):
    pass


_RESOURCE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")


def _pascal_name(name: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in name.split("_"))


def build_crud_generation_plan(resource: ResourceDefinition) -> dict[str, Any]:
    if not _RESOURCE_NAME.fullmatch(resource.name):
        raise InvalidResourceNameError(resource.name)

    module = f"server/app/modules/{resource.name}"
    page_name = f"{_pascal_name(resource.name)}Page.vue"
    return {
        "schemaVersion": "1.0",
        "generatorVersion": "1.0",
        "resource": resource.name,
        "module": module,
        "permissions": sorted(set(resource.permissions.values())),
        "files": [
            {"path": f"{module}/generated/__init__.py", "overwrite": "never"},
            {"path": f"{module}/generated/model.py", "overwrite": "never"},
            {"path": f"{module}/generated/schema.py", "overwrite": "never"},
            {"path": f"{module}/generated/repository.py", "overwrite": "never"},
            {"path": f"{module}/generated/service.py", "overwrite": "never"},
            {"path": f"{module}/generated/router.py", "overwrite": "never"},
            {"path": f"admin/src/components/admin/generated/{page_name}", "overwrite": "never"},
            {"path": f"server/tests/generated/test_{resource.name}.py", "overwrite": "never"},
        ],
    }


def build_registered_crud_generation_plan(name: str) -> dict[str, Any]:
    """Build a plan for a resource registered in the application manifest registry."""
    from server.app.core.resources.definitions import RESOURCE_DEFINITIONS

    resource = RESOURCE_DEFINITIONS.get(name)
    if resource is None:
        raise KeyError(name)
    return build_crud_generation_plan(resource)
