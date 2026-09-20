from typing import Any

from server.app.core.cache.redis import get_json, set_json
from .contract import compile_manifest
from .definitions import RESOURCE_DEFINITIONS


class ResourceNotFoundError(LookupError):
    pass


RESOURCE_MANIFEST_CACHE_KEY = "admin:resource-manifests:v2"


def get_resource_manifest(name: str) -> dict[str, Any]:
    definition = RESOURCE_DEFINITIONS.get(name)
    if definition is None:
        raise ResourceNotFoundError(name)
    return compile_manifest(definition)


def list_resource_manifests() -> list[dict[str, Any]]:
    return [get_resource_manifest(name) for name in RESOURCE_DEFINITIONS]


async def list_resource_manifests_cached() -> list[dict[str, Any]]:
    cached = await get_json(RESOURCE_MANIFEST_CACHE_KEY)
    if isinstance(cached, list) and all(isinstance(item, dict) for item in cached):
        return cached
    manifests = list_resource_manifests()
    await set_json(RESOURCE_MANIFEST_CACHE_KEY, manifests, ttl_seconds=300)
    return manifests
