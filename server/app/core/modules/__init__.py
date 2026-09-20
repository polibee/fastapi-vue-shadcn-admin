from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True, slots=True)
class ModuleSpec:
    name: str
    register: Callable[[], None] = lambda: None
    boot: Callable[[], None] = lambda: None


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleSpec] = {}

    def register(self, module: ModuleSpec) -> None:
        if module.name in self._modules:
            raise ValueError(f"module already registered: {module.name}")
        self._modules[module.name] = module

    def register_all(self) -> None:
        for module in self._modules.values():
            module.register()

    def boot_all(self) -> None:
        for module in self._modules.values():
            module.boot()

    def names(self) -> list[str]:
        return sorted(self._modules)


def builtin_registry() -> ModuleRegistry:
    registry = ModuleRegistry()
    for name in ("auth", "users", "roles", "permissions", "audit", "tasks"):
        registry.register(ModuleSpec(name))
    return registry


__all__ = ["ModuleRegistry", "ModuleSpec", "builtin_registry"]
